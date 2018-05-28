#coding:utf-8  
import SocketServer  
from SocketServer import StreamRequestHandler as SRH  
from time import ctime  
import os, sys, socket, errno, time, binascii

import config, db
  
reload(sys)  
sys.setdefaultencoding('utf8')  


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
    return (d_name_addr, d_addr_name)

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
        return cmd
    else:
        crcCode = crc16(cmd)
        return cmd+crcCode

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

def make_cmds(dtu, data):
    (dna, dan) = get_name_address_table(dtu)
    cmds = []
    setData = {}
    if (len(data) != 0):
        for x in data:
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
        print "===== setData content： ", setData
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
    return cmds

print make_cmds("dtu1001", [('over_voltage_1', 100)])
