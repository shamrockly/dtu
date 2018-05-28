#coding:utf-8  
import SocketServer  
from SocketServer import StreamRequestHandler as SRH  
from time import ctime  
import os, sys, socket, errno, time, binascii
import struct
import config, db
import csv
  
reload(sys)  
sys.setdefaultencoding('utf8')  

global  counter
counter = 0

# =============================================
# Support functions
# =============================================
def get_bit(Val, N):
    return (Val >> N) & 1

def mod_bit(Int, N, V):
    if V == 1:
        return set_bit(Int, N)
    else:
        return clear_bit(Int, N)
	
def set_bit(Val, N):
    return Val | (1<<N)
	
def clear_bit(Val, N):
    return Val & (~(1<<N))

def i2h(num):
    v = int(num)
    s = "%04x" % v
    return s.upper()

def crc16(HexString, Invert=True):
    x = bytearray(binascii.unhexlify(HexString))
    a = 0xFFFF
    b = 0xA001
    for byte in x:
        a ^= byte #ord(byte)
        for i in range(8):
            last = a % 2
            a >>= 1
            if last == 1:
                a ^= b
    s = i2h(a)
    if Invert == True:
        return s[2:4]+s[0:2] 
    else:
        return s

def get_cur_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def select_nth(nth, cmdLength):
     if nth == cmdLength:
         new_nth = 0
     else:
         new_nth = nth + 1
     return new_nth

def get_real_value_h(value):
    v = int(value)
    (real,) = struct.unpack('>h',struct.pack('>H', v))
    return real

def get_real_value_l(value):
    v = int(value)
    (real,) = struct.unpack('>l',struct.pack('>L', v))
    return real

# =============================================
# make set commands
# =============================================
def make_set_cmd(startAddr, cmdData):
    n = len(cmdData)
    cmd = ""
    if n == 0:
        pass
    elif n == 1:
        cmd = construct_cmd(6, startAddr, 1, cmdData[0])
    else:
        cmd = construct_cmd(10, startAddr, n, cmdData)
    return cmd

def construct_cmd_3(StartAddress, NumOfRegister):
    return construct_cmd(3, StartAddress, NumOfRegister, [])
	 
def construct_cmd_6(StartAddress, Data):
     return construct_cmd(6, StartAddress, 1, Data)
	 
def construct_cmd(Type, StartAddress, NumOfRegister, Data):
    cmd = ""
    if Type == 3:
        #read cmd:01, 03, startAddress, length, crcCode
        #response:01, 03, num of words, data1, ..., crcCode
        cmd = "0103" + i2h(StartAddress) + i2h(NumOfRegister)
    elif Type == 6:
        #write cmd:01, 06, startAddress, highByte, lowByte, crcCode
        #response:same as cmd
        cmd = "0106" + i2h(StartAddress) + i2h(Data)
    elif Type == 10:
        #write cmd:01, 10, startAddress, NumOfRegister, NumOfBytes, data1, data2, ..., crcCode
        #response:same as cmd
        NumOfBytes = "%02x" % (len(Data)*2)
        sHexData = ""
        for i in Data:
            sHexData = sHexData + i2h(i)
        cmd = "0110" + i2h(StartAddress) + i2h(NumOfRegister) + NumOfBytes + sHexData
    else:
        print "Function code is wrong. Only support 3, 6, 10."

    if cmd == "":
        return ""
    else:
        crcCode = crc16(cmd)
        return cmd+crcCode

# =============================================
# check set configuration
# =============================================
def check_set_cmds(dtu):
    results = config.DB.query('select * from dtu_config where dtu_name=$dtu_name and status=1', vars={'dtu_name':dtu})
    print "===", results, len(results)
    Flag = False
    setTime = ""
    cmds = []
    if (len(results)!=0):
        data = results[0]
        print "data: ", data
        setTime = data.get("time")
        cmd = data.get("cmd")
        status = data.get("status")
        if (cmd != ""):
            cmds = cmd.split(',')
            Flag = True
    return (Flag, setTime, cmds)

def check_set_params(dtu_name, mapTable):
    #return (True, ["0106012C000049FF"])
    print "================= check set commands ================="
    (dna, dan) = mapTable
    cmds = []
    setData = {}
    flag = False

    results = config.DB.query('select * from dtu_config_tablev2 where dtu_name=$dtu_name',vars={'dtu_name':dtu_name})
    #print "===", results
    if (len(results)!=0):
        data = results[0]
        data.pop("dtu_name")
        setTime = data.get("updatetime")
        data.pop("updatetime")

        print "======check_set_params: ", data
        for x in data.items():
            (k, v) = x
            if v != None:
                r = dna.get(k)
                if r != None:
                    flag = True
                    (Type, addr, n) = r
                    if Type == 'normal':
                        setData[addr] = int(float(v) * n)
                    elif Type == 'bit':
                        curV = setData.get(addr)
                        if curV == None:
                            setData[addr] = mod_bit(0, n, int(v))
                        else:
                            setData[addr] = mod_bit(curV, n, int(v))
                    else:
                        pass
        #print "===== setData content： ", setData
        if flag == True:
            tmp = [(k,setData[k]) for k in sorted(setData.keys())] 

            cmdData = []
            length = len(tmp)
            i = 0
            while i < length:
                (curAddr, curValue) = tmp[i]

                if i == 0:
                    start = curAddr
                    preAddr = curAddr - 1

                if curAddr == preAddr + 1:
                    preAddr = curAddr
                    cmdData.append(curValue)
                else:
                    cmd = make_set_cmd(start, cmdData)
                    cmds.append(cmd)

                    cmdData = []
                    start = curAddr
                    preAddr = curAddr
                    cmdData.append(curValue)

                i = i + 1

                if i == length:
                    cmd = make_set_cmd(start, cmdData)
                    cmds.append(cmd)
                
        print "set cmds:", cmds
    #==ly== add function: prepare the commands 
    return (flag, setTime, cmds)

#===============================
# Prepare Map Table
#===============================
def parse_parameter(parameter_name, parameter_value):
    addr = []
    Type = ''
    if (parameter_value!=None):
        tmparray = parameter_value.split(',')
        Type = tmparray[0]
        if Type == 'normal':
            addr = [int(tmparray[1]), int(tmparray[2])]
        elif Type == 'bit':
            addr = [int(tmparray[1]), int(tmparray[2])]
        else:
            pass
    return (Type, parameter_name, addr)
    

def add_name_address_to_table(dna, dan, data):
    (Type, Name, Addr) = data
    tmp = []
    if Type == 'normal':
        [A1, A2] = Addr
        dna[Name] = (Type, A1, A2)
        dan[A1] = [(Type, Name, A2)]
    elif Type == 'bit':
        [A1, A2] = Addr
        dna[Name] = (Type, A1, A2)
        x = dan.get(A1)
        if x == None:
            dan[A1] = [(Type, Name, A2)]
        else:
            tmp = x
            tmp.append((Type, Name, A2))
            dan[A1] = tmp
    else:
        pass
    return (dna, dan)

def get_name_address_table(dtu_name):
    # get the map table from the database
    d_name_addr = {}
    d_addr_name = {}
    results = config.DB.query('select * from dtu_basic_infov2 where dtu_name=$dtu_name',vars={'dtu_name':dtu_name})
    if (len(results)!=0):
        data=results[0]
        print data.items()
        for param in data.items():
            (p_name, p_value) = param
            if isinstance(p_value, basestring):
                p_res = parse_parameter(p_name, p_value)
                (d_name_addr, d_addr_name) = add_name_address_to_table(d_name_addr, d_addr_name, p_res)        
        
        print "========start dic======="
        print d_name_addr
        print "========================"
        print d_addr_name
        print "=========end dic========"
    return (d_name_addr, d_addr_name)

def get_name_by_address(address, table):
    (dna, dan) = table
    names = dan.get(address)
    return (address, names)

def get_address_by_name(name, table):
    (dna, dan) = table
    address = dna.get(name)
    return (name, address)

#=========================================
# Check History Event
#=========================================
def get_event_discription():
    return {
    'flag_switch_main': ("母联开", "母联合"),
    'flag_switch_entry_1': ("I段进线开", "I段进线合"),
    'flag_switch_entry_2': ("II段进线开", "II段进线合"),
    'flag_switch_mcr_1': ("磁控1出线开", "磁控1出线合"),
    'flag_switch_mcr_2': ("磁控2出线开", "磁控2出线合"),
    'flag_lock_status': ("DSP闭锁标志 0", "DSP闭锁标志 1"),
    'flag_null_status': ("NULL标志 0", "NULL标志 1"),
    'flag_voltage_over_1': ("I段过压 0", "I段过压 1"),
    'flag_voltage_under_1': ("I段欠压 0", "I段欠压 1"),
    'flag_threshold_over_1': ("I段越限 0", "I段越限 1"),
    'flag_current_over_1': ("I段过流 0", "I段过流 1"),
    'flag_current_unblance_1': ("I段不平衡 0", "I段不平衡 1"),
    'flag_sampling_error_1': ("I段采样故障 0", "I段采样故障 1"),
    'flag_sampling_warning_1': ("I段采样报警 0", "I段采样报警 1"),
    'flag_switch_gas_1': ("III段进线开关闭合 0", "III段进线开关闭合 1"),
    'flag_prediction_1': ("磁控1报警  0", "磁控1报警  1"),
    'flag_high_temperature_1': ("磁控1故障 0", "磁控1故障 1"),
    'flag_voltage_over_2': ("II段过压 0", "II段过压 1"),
    'flag_voltage_under_2': ("II段欠压 0", "II段欠压 1"),
    'flag_threshold_over_2': ("II段越限 0", "II段越限 1"),
    'flag_current_over_2': ("II段过流 0", "II段过流 1"),
    'flag_current_unblance_2': ("II段电流不平衡 0", "II段电流不平衡 1"),
    'flag_sampling_error_2': ("II段采样故障 0", "II段采样故障 1"),
    'flag_sampling_warning_2': ("II段采样报警 0", "II段采样报警 1"),
    'flag_switch_gas_2': ("2#母联开关 0", "2#母联开关 1"),
    'flag_prediction_2': ("磁控2报警  0", "磁控2报警  1"),
    'flag_high_temperature_2': ("磁控2故障 0", "磁控2故障 1"),
    'flag_magnetic_reset': ("磁控复位标志 0", "磁控复位标志 1"),
    'flag_power_factor_1': ("I段过功率因数 0", "I段过功率因数 1"),
    'flag_power_factor_2': ("Ⅱ段过功率因数 0", "Ⅱ段过功率因数 1"),
    'flag_entry_error_1': ("I段进线开关错误 0", "I段进线开关错误 1"),
    'flag_entry_error_2': ("II段进线开关错误 0", "II段进线开关错误 1") }


def get_bit_info(address, bitNth, bitValue, mapTable, textTable):
    (dna, dan) = mapTable
    list = dan.get(address)
    name = ""
    des = ""
    for i in list:
        (x, y, z) = i
        if z == bitNth:
            name = y
            des = "-"
            # The description is moved to web client
            #tmp = textTable.get(name)
            #if tmp != None:
            #    (text0, text1) = tmp
            #    if bitValue == 1:
            #        des = text1
            #    else:
            #        des = text0
            break
    return [name, des, address, bitNth, bitValue]

def check_event(dtu, address, preInfo, curInfo, mapTable):
    textTable = get_event_discription()
    (preTime, pre) = preInfo
    (curTime, cur) = curInfo
    if pre != cur:
        for i in range(0, 15):
            bit_pre = get_bit(pre, i)
            bit_curr = get_bit(cur, i)
            if (bit_pre != bit_curr):
                res = get_bit_info(address, i, bit_curr, mapTable, textTable) 
                print "===== event (close: 0-> 1) or (open: 1 -> 0)  ====", res
                config.DB.insert('dtu_event', dtu_name=dtu, time = curTime, var_name = res[0], 
                                              var_value = bit_curr, event_description = res[1])
            else:
                #==== Here is test data, will remove =======
                #res = get_bit_info(address, i, bit_curr, mapTable, textTable)
                #config.DB.insert('dtu_event', dtu_name=dtu, time = curTime, var_name = res[0],
                #                              var_value = bit_curr, event_description = res[1])

                pass

def check_events(dtu, curTime, data, preCircleData, mapTable):
    print "===========check history event=============="
    if len(preCircleData) != 3:
        return 'error'

    curCircleData = {}
    circleAddess = preCircleData[0]
    preTime = preCircleData[1]
    preValues = preCircleData[2]
    for addr in circleAddess:
        curValue = data.get(addr)
        curCircleData[addr] = curValue
        preValue = preValues.get(addr)
        if (curValue != None and preValue != None):
            check_event(dtu, addr, (preTime, preValue), (curTime, curValue), mapTable)
    #print "preCircleData: ", preCircleData
    #print "curCircleData: ", [circleAddess, curTime, curCircleData]
    return [circleAddess, curTime, curCircleData]

#===============================
# socket receive function
# Type: "ok-dtu", "ok-normal", "ok-noData", "error"
# Data: list or error_msg
#===============================
def try_receive(handler):
    try:
        data = handler.request.recv(1024)

        if not data:
            print "connection is closed: ", handler.client_address[0]
            try:
                handler.request.close()
                return ("ok-close", handler)
            except IOError as e:
                return ("error", e)
        else:
            cur_time = get_cur_time()
            print "=========try_receive: %s RECV from %s" % (cur_time,handler.client_address[0])
            print "=========try_recevie data: ", data

            if data[0:3] == "dtu":
                return ("ok-dtu", data)
            else:
                sData = data.encode('hex')
                sData.strip()
                #print "try_receive(sData): ", sData
                return ("ok-normal", sData)             
    except IOError as e:
        if e.errno == errno.EWOULDBLOCK:
            #print "try_receive: error message EWOULDBLOCK is received. It means no data is received."
            return ("ok-noData", [])
        else:
            print "try_receive: other error message is received. It is ", e
            return ("error", e)

#===============================
# Output: (Type, Data)
# Type: "ok-03", "0k-06", "ok-10", "error"
# Data: list or error_msg
#===============================
def handle_data(dtu, cmd, data):
    data.strip()
    #print "===cmd:  ", cmd
    #print "===data: ", data
    cmd2 = cmd[2:4]
    data2 = data[2:4]
    if (cmd2 == "03" and data2 == "03"):
        startAddress = int(cmd[4:8], 16)
        lengthAddress = int(cmd[8:12], 16)
        lengthByte = int(data[4:6], 16)
        print "p_startAddress: ", startAddress
        print "p_lengthAddress: ", lengthAddress
        print "p_lengthByte: ", lengthByte
        #if (lengthByte == 2*lengthAddress and len(data) == 2*lengthByte+10):
        if (len(data) == 2*lengthByte+10):
            i_data = 0
            i_address = 0
            result = {}
            curLengthAddress = lengthByte/2
            if (curLengthAddress < lengthAddress):
                adjustLengthAddress = curLengthAddress
            else:
                adjustLengthAddress = lengthAddress

            while i_address < adjustLengthAddress:
                address = startAddress + i_address
                #===== alt 1:
                #sValue = "\\x" + data[6+i_data:8+i_data] + "\\x" + data[8+i_data:10+i_data]
                #value0 = int(sValue, 16)
                #(value,) = struct.unpack('>h',struct.pack('>H', value0))
                #===== alt 2:
                sValue = data[6+i_data:10+i_data]
                value = int(sValue, 16)

                #print i_address, " ", i_data, " ", address, " ", sValue
                result[address] = value
                i_address = i_address + 1
                i_data = i_data + 4
            print "p_parase result: ", result
            ###################my code#########################
            ''''if cmp(dtu, 'dtu1003') == 0:
                with open('example.csv', 'a') as f:
	    	    writer = csv.writer(f)	             	
	    	    mywritedata = result
	    	    writer.writerow(mywritedata) '''
	    ###################my code#########################
            return ("ok_03", result)
        else:
            print "Byte length is not same as cmd length"
            print "length: ", lengthAddress, lengthByte, len(data)
            return ("error", "len_not_match")
    elif (cmd2 == "06" and data2 == "06"):
        ucmd = cmd.upper()
        udata = data.upper()
        if ucmd == udata:
            return ("ok_06", [])
        else:
            return ("nok-06", [])
    elif (cmd2 == "10" and data2 == "10"):
        return ("ok_10", [])
    else:
        print "p_data is not align with cmd: ", cmd[2:4], data[2:4]
        return ("error", "cmd_not_match")

#===============================
### Output: (Type, Data)
### Type: "ok-cmd-fin", "ok-cmd-not-fin", "ok-set-params", "error"
### Data: list
#===============================
def handle_cmd(handler, dtu, cmd, preCircleData, mapTable):
    global  counter
    cmd1 = cmd.decode('hex')
    handler.request.send(cmd1)
    print "===========send cmd: ", cmd
    n = 0
    resType = ""
    curCircleData = []
    while True:
        (Type, data) = try_receive(handler)
        if Type == "ok-normal":
            (res, outData) = handle_data(dtu, cmd, data)
            if res == "ok_03":
                curTime = write_to_database(dtu, outData, 'dtu_table1v2', mapTable)
                curCircleData = check_events(dtu, curTime, outData, preCircleData, mapTable)
                resType = "ok-cmd-fin"
                 ###################my code#############
                if cmp(dtu, 'dtu1003') == 0:
                    counter = counter + 1
                    with open('example.csv', 'a') as f:
	    	        writer = csv.writer(f)	             	
	    	        mywritedata = list(outData.values())
	    	        mywritedata.append(counter)
	    	        writer.writerow(mywritedata) 
	    	    ###################my code#############
                break   
            elif res == "error":
                resType = "ok-cmd-not-fin"
                if n == 3:
                    break
                else:
                    n = n+1
                    time.sleep(1)
            else:
                resType = "ok-cmd-fin"
                break
        elif (Type == "error" or Type == "ok-close"):
            resType == "error"
            break
        else:
            if n == 3:
                resType = "ok-cmd-not-fin"
                break
            else:
                n = n + 1
                time.sleep(1)
    return (resType, cmd, curCircleData)

def handle_set_cmds(handler, dtu, setTime, cmds, mapTable):
    print "======== handle set params cmds: ", cmds
    resType = ""
    while len(cmds) > 0:
        cmd = cmds[0]
        cmd1 = cmd.decode('hex')
        handler.request.send(cmd1)
        print "=====send set cmd: ", cmd
        n = 0
        while True:
            (Type, data) = try_receive(handler)
            if Type == "ok-normal":
                (res, outData) = handle_data(dtu, cmd, data)
                #print "################ ", res, outData
                if res == "ok_03":
                    write_to_database(dtu, outData, 'dtu_config_tablev2', mapTable)
                    resType = "ok-cmd-fin"
                    break
                elif res == "error":
                    resType = "ok-cmd-not-fin"
                    if n == 3:
                        break
                    else:
                        n = n+1
                        time.sleep(1)
                else:
                    resType = "ok-cmd-fin"
                    break
                print "set cmd res: ", res
            elif (Type == "error" or Type == "ok-close"):
                return ("error", cmds)
            else:
                if n == 3:
                    break
                else:
                    time.sleep(1)
                    n = n + 1
        time.sleep(1)
        cmds.remove(cmd)
    print "======== handle set params cmds ok ========================== "
    #==ly== add function: if all params are configured successfully, clear the record in database
    #config.DB.delete('dtu_config',where='dtu_name=$dtu',vars={'dtu':dtu})
    if resType  == "ok-cmd-fin":
        n = config.DB.update('dtu_config', where='dtu_name=$dtu and time=$setTime', vars={'dtu':dtu, 'setTime':setTime}, \
                         status = 0, time_fin= get_cur_time())
        #print("n=" + str(n))

    return (resType, [])

#=====================================
# write data to database
#=====================================
def write_to_database(dtu, data, table, mapTable):
    newKV = {}
    for kv in data.items():
        (address, v) = kv
        (newAddress, names) = get_name_by_address(address, mapTable)
        if (names == None or newAddress == None):
            #print "name or address is none: ", name, address
            pass
        else:
            #print "new names: ", names
            for x in names:
                (Type, name, n) = x
                if Type == 'normal':
                    newKV[name] = v / float(n)
                elif Type == 'bit':
                    newKV[name] = get_bit(v, n) 
                else:
                    pass
    
    #print "======write data to database==============="
    #print newKV
    #print "==========================================="
    (Time, insertCmd) = make_db_insert_cmd(table, dtu, newKV)
    #print insertCmd
    exec insertCmd
    return Time

def make_db_insert_cmd(Table, DTU, KeyValue):
    Time = get_cur_time()
    Cmd0 = "config.DB.insert(\'" + Table + "\', dtu_name=\'" + DTU + "\', updatetime=\'" + Time + "\'"
    Cmd1 = ""
    for kv in KeyValue.items():
        (k, v) = kv
        Cmd1 = Cmd1 + ", " + k + "=" + str(v)
    return (Time, Cmd0 + Cmd1 + ")")

# ==============================
# Main Server
# ==============================
class Servers(SRH):  
    def handle(self):  
        print 'got connection from: ', self.client_address
        self.wfile.write('connection %s:%s at %s succeedi!' % (host, port, ctime()))
        self.request.setblocking(0)
        dtu = ""
        Type = ""	
        mapTable = ({}, {})
	

        cmdList = []
        cmdLength = 0

        circleAddress = []
        circleData = []

        nth = 0
        try_times = 0
        interval = 0
	
        while True:
            Type = ""

            if dtu == "":
                (Type, data) = try_receive(self)
                if Type == "ok-dtu":
                    dtu = data
                    
                    print('\033[1;31;43m ****************+++++++++++++++++++++++++++++dtu is:+++++++++++++++++++++++++++++ \033[0m!')
                    print "dtu: ", dtu
                    ###################my code#############
                    with open('example.csv', 'a') as f:
	    	        writer = csv.writer(f)	             	
	    	        mywritedata = [dtu]
	    	        writer.writerow(mywritedata) 
	    	    ###################my code#############
                    mapTable = get_name_address_table(dtu)
                    if dtu == "dtu1001":           
                        cmdList = ["01030000002F0416"]
                        cmdLength = len(cmdList)-1
                        circleAddress = [30, 31]
                        circleData = [circleAddress, get_cur_time(), {}]
                        interval = 5
                    elif dtu == "dtu1003":           
                        cmdList = ["01030000002F0416"]
                        cmdLength = len(cmdList)-1
                        circleAddress = [30, 31]
                        circleData = [circleAddress, get_cur_time(), {}]
                        interval = 5
		    else:
                        dtu = ""
                        pass
                elif (Type == "error" or Type == "ok-close"):
                    break
                else:
                    #print "error during waiting for dtu: ", Type, data
                    dtu = ""
                    time.sleep(2)
            else:
                #==ly== add function: check setting parameters
                (setFlag, setTime, setCmds) = check_set_cmds(dtu)
                if setFlag == True:
                    (Type, res) = handle_set_cmds(self, dtu, setTime, setCmds, mapTable)
                    if Type == "error":
                        break
                    time.sleep(1)

                if interval == 5:
                    interval = 0
                    cmd = cmdList[nth]
                    (Type, tmpData, tmpCircleData) = handle_cmd(self, dtu, cmd, circleData, mapTable)
                    ###################my code############
                    '''if cmp(dtu, 'dtu1003') == 0:
                        with open('example.csv', 'a') as f:
	    	    	    writer = csv.writer(f)	             	
	    	    	    mywritedata = [Type, tmpData, tmpCircleData]
	    	            writer.writerow(mywritedata) ''' 
	    	    ###################my code############  
                    if Type == "ok-cmd-fin":
                        try_times = 0
                        circleData = tmpCircleData
                        nth = select_nth(nth, cmdLength)
                    elif Type == "ok-cmd-not-fin":
                        print "current cmd is not finished, try again: ", cmd
                        if try_times == 2:
                            try_times = 0
                            nth = select_nth(nth, cmdLength)
                        else:
                            try_times = try_times + 1
                    else:
                        break
                else:
                    interval = interval + 1
                    time.sleep(1)
	   


#host = '127.0.0.1'
#host='ec2-35-166-81-188.us-west-2.compute.amazonaws.com'
host='10.0.0.210'
port = 8001
addr = (host, port)
print 'server is running....'  
class EchoServer(SocketServer.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True
    def __init__(self, server_address, RequestHandlerClass):
        """Set up an initially empty mapping between a user' s nickname
        and the file-like object used to send data to that user."""
        SocketServer.ThreadingTCPServer.__init__(self, server_address, RequestHandlerClass)
#server = SocketServer.ThreadingTCPServer(addr, Servers) 
server = EchoServer(addr, Servers) 
server.serve_forever() 

