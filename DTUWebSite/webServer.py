# -*- coding: utf-8 -*-
import web
import datetime, config
import hashlib
import model
import db
import threading, sys
import LOG
import random
from cStringIO import StringIO
from os import path
import uuid
import time
import makeCmd
import json
import struct

'''
web服务器入口
'''

cookieName = "captcha-account-save"
cookieID = "captcha-USERID-save"
TIMEOUT= 3600

render1 = web.template.render('templates/dtu1001')
render2 = web.template.render('templates/dtu1002')
render21 = web.template.render('templates/dtu1002/pywebsocket/mod_pywebsocket')
render3 = web.template.render('templates/dtu1003')

dtuid1 = 'dtu1001'
dtuid2 = 'dtu1002'
dtuid3 = 'dtu1003'

urls = (
    '/js','js',
    '/dtu1001','dtu1001_page1',
    '/dtu1001/','dtu1001_page1',
    '/dtu1001/page1','dtu1001_page1',
    '/dtu1001/page2','dtu1001_page2',
    '/dtu1001/page3','dtu1001_page3',
    '/dtu1001/page33','dtu1001_page33',
    '/dtu1001/page4','dtu1001_page4',
    '/dtu1001/pageX','dtu1001_pageX',
    '/dtu1002','dtu1002_pageX',
    '/dtu1002/','dtu1002_pageX',
    '/dtu1002/runoob_websocket','runoob_websocket',
    '/dtu1002/runoob_websocket.*','runoob_websocket',
    '/dtu1003','dtu1003_page1',
    '/dtu1003/','dtu1003_page1',
    '/dtu1003/page1','dtu1003_page1',
    '/dtu1003/page2','dtu1003_page2',
    '/dtu1003/page3','dtu1003_page3',
    '/dtu1003/page33','dtu1003_page33',
    '/dtu1003/page4','dtu1003_page4',
    '/dtu1003/pageX','dtu1003_pageX'
)
    
_controllersDir = path.abspath(path.dirname(__file__))
_webDir = path.dirname(_controllersDir)
#for local
#_fontsDir = path.join(path.dirname(_webDir),'python')
#for centos
_fontsDir = path.join(path.dirname(_webDir),'code')
_fontsDir = path.join(_fontsDir,'web')
_fontsDir = path.join(_fontsDir,'fonts') 
_chars = 'ABCDEFJHJKMNPQRSTUVWXY'

def isInteger(num):
    try:
        t = int(num)
        return True
    except ValueError:
        return False
		
def get_cur_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def insert_cmds(dtuid, outCmd):
    config.DB.insert('dtu_config',dtu_name=dtuid,cmd=outCmd,status=1,time=get_cur_time())

def float_dtu(string):
    try:
        v = float(string)
    except:
        print 'float error, string is: ', string
        v = 0
    return v
	
def get_real_value(value, factor):
    v = int(float(value) * factor)
    (real,) = struct.unpack('>l',struct.pack('>L', v))
    return real/float(factor)

def get_real_value_h(value, factor):
    v = int(float(value) * factor)
    (real,) = struct.unpack('>h',struct.pack('>H', v))
    return real/float(factor)

class dtu1001_page1:
    def GET(self):
        dtuid = dtuid1
        input = web.input(reset1=0, reset2=0, mcr_angle_set_1=-1, mcr_angle_set_2=-1, mcr_auto_flag_set_1=-1, mcr_auto_flag_set_2=-1)
        reset1 = input.reset1
        reset2 = input.reset2
        mcr_angle_set_1 = input.mcr_angle_set_1
        mcr_angle_set_2 = input.mcr_angle_set_2
        mcr_auto_flag_set_1 = input.mcr_auto_flag_set_1
        mcr_auto_flag_set_2 = input.mcr_auto_flag_set_2

        if int(reset1) == 1:
            data=[("reset_mcr1",1)]
            outCmd = makeCmd.make_cmds(dtuid, data)
            insert_cmds(dtuid, outCmd)
        if int(reset2) == 1:
            data=[("reset_mcr2",1)]
            outCmd = makeCmd.make_cmds(dtuid, data)
            insert_cmds(dtuid, outCmd)

        if ((int(mcr_auto_flag_set_1)!=-1) and (int(mcr_auto_flag_set_2)!=-1)):
            data=[("mcr_auto_flag_set_1", int(mcr_auto_flag_set_1)),
                  ("mcr_auto_flag_set_2", int(mcr_auto_flag_set_2)),
                  ("mcr_auto_flag_change",1),
                  ("mcr_auto_flag_store",0)]
            if mcr_angle_set_1 != "":
                if int(mcr_angle_set_1)!=-1:
                    data.append(("mcr_angle_set_1",int(mcr_angle_set_1)))
            if mcr_angle_set_2 != "":
                if int(mcr_angle_set_2)!=-1:
                    data.append(("mcr_angle_set_2",int(mcr_angle_set_2)))
            #change the automode.....
            outCmd = makeCmd.make_cmds(dtuid, data)
            insert_cmds(dtuid, outCmd)
			
        dtuinfo = config.DB.query('select * from dtu_table1v2 where dtu_name=$dtuid order by updatetime desc limit 1',vars={'dtuid':dtuid})
        resultarray = []

        if(len(dtuinfo)==0):
            resultarray = [-1 for i in range(0,44)]
        else:
            queryres = dtuinfo[0]
            flag_voltage_1=(int(queryres['flag_voltage_over_1']) + int(queryres['flag_voltage_under_1']) + int(queryres['flag_threshold_over_1']))
            flag_current_1=(int(queryres['flag_current_over_1']) + int(queryres['flag_current_unblance_1']))
            flag_sampling_1=(int(queryres['flag_sampling_error_1']) + int(queryres['flag_sampling_warning_1']))
            flag_prediction_1=queryres['flag_prediction_1']
            flag_high_temperature_1=queryres['flag_high_temperature_1']
            flag_manul_auto_1=queryres['mcr_auto_flag_set_1']
            flag_manul_auto_2=queryres['mcr_auto_flag_set_2']
            flag_voltage_2=(int(queryres['flag_voltage_over_2']) + int(queryres['flag_voltage_under_2']) + int(queryres['flag_threshold_over_2']))
            flag_current_2=(int(queryres['flag_current_over_2']) + int(queryres['flag_current_unblance_2']))
            flag_sampling_2=(int(queryres['flag_sampling_error_2']) + int(queryres['flag_sampling_warning_2']))
            flag_prediction_2=queryres['flag_prediction_2']
            flag_high_temperature_2=queryres['flag_high_temperature_2']

            voltage_1=queryres['voltage_1']
            current_1=queryres['current_1']
            active_power_1=get_real_value(float_dtu(queryres['active_power_hign_1'])*65536+float_dtu(queryres['active_power_low_1']), 10)
            reactive_power_1=get_real_value(float_dtu(queryres['reactive_power_high_1'])*65536+float_dtu(queryres['reactive_power_low_1']), 10)
            power_factor_1=get_real_value_h(queryres['power_factor_1'], 100)

            voltage_2=queryres['voltage_2']
            current_2=queryres['current_2']
            active_power_2=get_real_value(float_dtu(queryres['active_power_hign_2'])*65536+float_dtu(queryres['active_power_low_2']), 10)
            reactive_power_2=get_real_value(float_dtu(queryres['reactive_power_high_2'])*65536+float_dtu(queryres['reactive_power_low_2']), 10)
            power_factor_2=get_real_value_h(queryres['power_factor_2'], 100)

            voltage_3=queryres['voltage_3']
            current_3=queryres['current_3']
            active_power_3=get_real_value(float_dtu(queryres['active_power_hign_3'])*65536+float_dtu(queryres['active_power_low_3']), 10)
            reactive_power_3=get_real_value(float_dtu(queryres['reactive_power_high_3'])*65536+float_dtu(queryres['reactive_power_low_3']), 10)
            power_factor_3=get_real_value_h(queryres['power_factor_3'], 100)
			
            mcr_voltage_1=queryres['mcr_voltage_A_1']
            mcr_current_A_1=queryres['mcr_current_A_1']
            mcr_current_B_1=queryres['mcr_current_B_1']
            mcr_current_C_1=queryres['mcr_current_C_1']
            mcr_operating_angle_1=queryres['mcr_operating_angle_1']
            mcr_voltage_2=queryres['mcr_voltage_A_2']
            mcr_current_A_2=queryres['mcr_current_A_2']
            mcr_current_B_2=queryres['mcr_current_B_2']
            mcr_current_C_2=queryres['mcr_current_C_2']
            mcr_operating_angle_2=queryres['mcr_operating_angle_2']
            flag_switch_entry_1=queryres['flag_switch_entry_1']
            flag_switch_gas_1=queryres['flag_switch_gas_1']
            flag_switch_entry_2=queryres['flag_switch_entry_2']
            flag_switch_mcr_1=queryres['flag_switch_mcr_1']
            flag_switch_mcr_2=queryres['flag_switch_mcr_2']
            flag_switch_main=queryres['flag_switch_main']
            flag_switch_gas_2=queryres['flag_switch_gas_2']

            updatetime=queryres['updatetime']
            a=time.mktime(updatetime.timetuple()) 
            b=time.time()
            delttime = b-a
            if(delttime>30):
                resultarray = [0 for i in range(0,44)]
            else: 
                resultarray.append(flag_voltage_1)  #0
                resultarray.append(flag_current_1)
                resultarray.append(flag_sampling_1)
                resultarray.append(flag_prediction_1)
                resultarray.append(flag_high_temperature_1)
                resultarray.append(flag_manul_auto_1) #5
                resultarray.append(flag_manul_auto_2)
                resultarray.append(flag_voltage_2)
                resultarray.append(flag_current_2)
                resultarray.append(flag_sampling_2)
                resultarray.append(flag_prediction_2) #10
                resultarray.append(flag_high_temperature_2)
                resultarray.append(voltage_1)
                resultarray.append(current_1)
                resultarray.append(active_power_1)
                resultarray.append(reactive_power_1) #15
                resultarray.append(power_factor_1)
                resultarray.append(voltage_2)
                resultarray.append(current_2)
                resultarray.append(active_power_2)
                resultarray.append(reactive_power_2) #20
                resultarray.append(power_factor_2)
                resultarray.append(voltage_3)
                resultarray.append(current_3)
                resultarray.append(active_power_3)
                resultarray.append(reactive_power_3) #25
                resultarray.append(power_factor_3)
                resultarray.append(mcr_voltage_1)
                resultarray.append(mcr_current_A_1)
                resultarray.append(mcr_current_B_1)
                resultarray.append(mcr_current_C_1)  #30
                resultarray.append(mcr_operating_angle_1)
                resultarray.append(mcr_voltage_2)
                resultarray.append(mcr_current_A_2)
                resultarray.append(mcr_current_B_2)
                resultarray.append(mcr_current_C_2) #35
                resultarray.append(mcr_operating_angle_2)
                resultarray.append(flag_switch_entry_1)
                resultarray.append(flag_switch_gas_1)
                resultarray.append(flag_switch_entry_2)
                resultarray.append(flag_switch_mcr_1) #40
                resultarray.append(flag_switch_mcr_2)
                resultarray.append(flag_switch_main)
                resultarray.append(flag_switch_gas_2)
        
        dtuinfo2 = config.DB.query('select project_name,product_model,product_code from dtu_basic_infov2 where dtu_name=$dtuid',vars={'dtuid':dtuid})
        if(len(dtuinfo2)==0):
            resultarray.append("No Project")
            resultarray.append("*********")
            resultarray.append("*********")
            curtime=get_cur_time()
            resultarray.append(curtime)
        else:
            queryres2 = dtuinfo2[0]
            project_name=queryres2['project_name']
            product_model=queryres2['product_model']
            product_code=queryres2['product_code']
            resultarray.append(project_name)
            resultarray.append(product_model)
            resultarray.append(product_code)
            curtime=get_cur_time()
            resultarray.append(curtime)
        return render1.page1(resultarray, dtuid)

class dtu1001_page2:
    def GET(self):
        dtuid = dtuid1
        
        eventhistory = config.DB.query('select * from dtu_event where dtu_name=$dtuid order by time desc;', vars={'dtuid':dtuid})
        dtuinfo = config.DB.query('select * from dtu_event where dtu_name=$dtuid order by time desc limit 1',vars={'dtuid':dtuid})
		
        if(len(dtuinfo)==0):
            resultarray = dtuinfo
        else:
            item = dtuinfo[0]
            print item
            eventTime = item['time']
            resultarray = config.DB.query('select * from dtu_event where dtu_name=$dtuid and time=$etime;', vars={'dtuid':dtuid, 'etime':eventTime})

        return render1.page2(resultarray,eventhistory,dtuid)

class dtu1001_page3:
    def GET(self):
        dtuid = dtuid1

        paremarray = web.input()
        starttime=paremarray.starttime
        endtime=paremarray.endtime

        if(starttime=='-1' or starttime==None or endtime=='-1' or endtime==None):
            historyinfo = config.DB.query("select power_factor_1,power_factor_2,power_factor_3,voltage_1,voltage_2,voltage_3,current_1,current_2,current_3, mcr_voltage_A_1, mcr_voltage_B_1, mcr_voltage_C_1, mcr_voltage_A_2, mcr_voltage_B_2, mcr_voltage_C_2, mcr_current_A_1,mcr_current_B_1,mcr_current_C_1,mcr_current_A_2,mcr_current_B_2,mcr_current_C_2,updatetime from dtu_table1v2 order by updatetime desc limit 50")
        else:
            starttime = web.input().starttime
            endtime = web.input().endtime
            historyinfo = config.DB.query("select power_factor_1,power_factor_2,power_factor_3,voltage_1,voltage_2,voltage_3,current_1,current_2,current_3, mcr_voltage_A_1, mcr_voltage_B_1, mcr_voltage_C_1, mcr_voltage_A_2, mcr_voltage_B_2, mcr_voltage_C_2, mcr_current_A_1,mcr_current_B_1,mcr_current_C_1,mcr_current_A_2,mcr_current_B_2,mcr_current_C_2,updatetime from dtu_table1v2 where updatetime>='"+starttime+"' and updatetime<='"+endtime+"'")

        result = historyinfo
        power_factor_1_array = []
        power_factor_2_array=[]
        power_factor_3_array=[]
        voltage_1_array=[]
        voltage_2_array=[]
        voltage_3_array=[]
        current_1_array=[]
        current_2_array=[]
        current_3_array=[]
        mcr_voltage_A_1_array=[]
        mcr_voltage_B_1_array=[]
        mcr_voltage_C_1_array=[]
        mcr_voltage_A_2_array=[]
        mcr_voltage_B_2_array=[]
        mcr_voltage_C_2_array=[]
        mcr_current_A_1_array=[]
        mcr_current_B_1_array=[]
        mcr_current_C_1_array=[]
        mcr_current_A_2_array=[]
        mcr_current_B_2_array=[]
        mcr_current_C_2_array=[]
        updatetime_array=[]
        for item in result:
            power_factor_1_array.append(get_real_value_h(float_dtu(item['power_factor_1']), 100))
            power_factor_2_array.append(get_real_value_h(float_dtu(item['power_factor_2']), 100))
            power_factor_3_array.append(get_real_value_h(float_dtu(item['power_factor_3']), 100))
            voltage_1_array.append(float_dtu(item['voltage_1']))
            voltage_2_array.append(float_dtu(item['voltage_2']))
            voltage_3_array.append(float_dtu(item['voltage_3']))
            current_1_array.append(float_dtu(item['current_1']))
            current_2_array.append(float_dtu(item['current_2']))
            current_3_array.append(float_dtu(item['current_3']))
            mcr_voltage_A_1_array.append(float_dtu(item['mcr_voltage_A_1']))
            mcr_voltage_B_1_array.append(float_dtu(item['mcr_voltage_B_1']))
            mcr_voltage_C_1_array.append(float_dtu(item['mcr_voltage_C_1']))
            mcr_voltage_A_2_array.append(float_dtu(item['mcr_voltage_A_2']))
            mcr_voltage_B_2_array.append(float_dtu(item['mcr_voltage_B_2']))
            mcr_voltage_C_2_array.append(float_dtu(item['mcr_voltage_C_2']))
            mcr_current_A_1_array.append(float_dtu(item['mcr_current_A_1']))
            mcr_current_B_1_array.append(float_dtu(item['mcr_current_B_1']))
            mcr_current_C_1_array.append(float_dtu(item['mcr_current_C_1']))
            mcr_current_A_2_array.append(float_dtu(item['mcr_current_A_2']))
            mcr_current_B_2_array.append(float_dtu(item['mcr_current_B_2']))
            mcr_current_C_2_array.append(float_dtu(item['mcr_current_C_2']))
            updatetime_array.append(str(item['updatetime']))

        return render1.page3(power_factor_1_array,power_factor_2_array,power_factor_3_array,voltage_1_array,voltage_2_array,voltage_3_array,current_1_array,current_2_array,current_3_array,mcr_voltage_A_1_array,mcr_voltage_B_1_array,mcr_voltage_C_1_array,mcr_voltage_A_2_array,mcr_voltage_B_2_array,mcr_voltage_C_2_array,mcr_current_A_1_array,mcr_current_B_1_array,mcr_current_C_1_array,mcr_current_A_2_array,mcr_current_B_2_array,mcr_current_C_2_array,updatetime_array, dtuid)

class dtu1001_page33:
    def GET(self):
        dtuid = dtuid1
        paremarray = web.input()
        starttime=paremarray.starttime
        endtime=paremarray.endtime

        if(starttime=='-1' or starttime==None or endtime=='-1' or endtime==None):
            historyinfo = config.DB.query("select power_factor_1,power_factor_2,power_factor_3,voltage_1,voltage_2,voltage_3,current_1,current_2,current_3, mcr_voltage_A_1, mcr_voltage_B_1, mcr_voltage_C_1, mcr_voltage_A_2, mcr_voltage_B_2, mcr_voltage_C_2, mcr_current_A_1,mcr_current_B_1,mcr_current_C_1,mcr_current_A_2,mcr_current_B_2,mcr_current_C_2,updatetime from dtu_table1v2 order by updatetime desc limit 50")
            print historyinfo
        else:
            starttime = web.input().starttime
            endtime = web.input().endtime
            historyinfo = config.DB.query("select power_factor_1,power_factor_2,power_factor_3,voltage_1,voltage_2,voltage_3,current_1,current_2,current_3, mcr_voltage_A_1, mcr_voltage_B_1, mcr_voltage_C_1, mcr_voltage_A_2, mcr_voltage_B_2, mcr_voltage_C_2, mcr_current_A_1,mcr_current_B_1,mcr_current_C_1,mcr_current_A_2,mcr_current_B_2,mcr_current_C_2,updatetime from dtu_table1v2 where updatetime>='"+starttime+"' and updatetime<='"+endtime+"'")
            print historyinfo

        result = historyinfo
        power_factor_1_array = []
        power_factor_2_array=[]
        power_factor_3_array=[]
        voltage_1_array=[]
        voltage_2_array=[]
        voltage_3_array=[]
        current_1_array=[]
        current_2_array=[]
        current_3_array=[]
        mcr_voltage_A_1_array=[]
        mcr_voltage_B_1_array=[]
        mcr_voltage_C_1_array=[]
        mcr_voltage_A_2_array=[]
        mcr_voltage_B_2_array=[]
        mcr_voltage_C_2_array=[]
        mcr_current_A_1_array=[]
        mcr_current_B_1_array=[]
        mcr_current_C_1_array=[]
        mcr_current_A_2_array=[]
        mcr_current_B_2_array=[]
        mcr_current_C_2_array=[]
        updatetime_array=[]
		
        for item in result:
            power_factor_1_array.append(get_real_value_h(float_dtu(item['power_factor_1']), 100))
            power_factor_2_array.append(get_real_value_h(float_dtu(item['power_factor_2']), 100))
            power_factor_3_array.append(get_real_value_h(float_dtu(item['power_factor_3']), 100))
            voltage_1_array.append(float_dtu(item['voltage_1']))
            voltage_2_array.append(float_dtu(item['voltage_2']))
            voltage_3_array.append(float_dtu(item['voltage_3']))
            current_1_array.append(float_dtu(item['current_1']))
            current_2_array.append(float_dtu(item['current_2']))
            current_3_array.append(float_dtu(item['current_3']))
            mcr_voltage_A_1_array.append(float_dtu(item['mcr_voltage_A_1']))
            mcr_voltage_B_1_array.append(float_dtu(item['mcr_voltage_B_1']))
            mcr_voltage_C_1_array.append(float_dtu(item['mcr_voltage_C_1']))
            mcr_voltage_A_2_array.append(float_dtu(item['mcr_voltage_A_2']))
            mcr_voltage_B_2_array.append(float_dtu(item['mcr_voltage_B_2']))
            mcr_voltage_C_2_array.append(float_dtu(item['mcr_voltage_C_2']))
            mcr_current_A_1_array.append(float_dtu(item['mcr_current_A_1']))
            mcr_current_B_1_array.append(float_dtu(item['mcr_current_B_1']))
            mcr_current_C_1_array.append(float_dtu(item['mcr_current_C_1']))
            mcr_current_A_2_array.append(float_dtu(item['mcr_current_A_2']))
            mcr_current_B_2_array.append(float_dtu(item['mcr_current_B_2']))
            mcr_current_C_2_array.append(float_dtu(item['mcr_current_C_2']))
            updatetime_array.append(str(item['updatetime']))
			
        resultReturn={
            'power_factor_1_array':power_factor_1_array,
            'power_factor_2_array':power_factor_2_array,
            'power_factor_3_array':power_factor_3_array,
            'voltage_1_array':voltage_1_array,
            'voltage_2_array':voltage_2_array,
            'voltage_3_array':voltage_3_array,
            'current_1_array':current_1_array,
            'current_2_array':current_2_array,
            'current_3_array':current_3_array,
            'mcr_voltage_A_1_array':mcr_voltage_A_1_array,
            'mcr_voltage_B_1_array':mcr_voltage_B_1_array,
            'mcr_voltage_C_1_array':mcr_voltage_C_1_array,
            'mcr_voltage_A_2_array':mcr_voltage_A_2_array,
            'mcr_voltage_B_2_array':mcr_voltage_B_2_array,
            'mcr_voltage_C_2_array':mcr_voltage_C_2_array,
            'mcr_current_A_1_array':mcr_current_A_1_array,
            'mcr_current_B_1_array':mcr_current_B_1_array,
            'mcr_current_C_1_array':mcr_current_C_1_array,
            'mcr_current_A_2_array':mcr_current_A_2_array,
            'mcr_current_B_2_array':mcr_current_B_2_array,
            'mcr_current_C_2_array':mcr_current_C_2_array,
            'updatetime_array':updatetime_array
        }
        resultReturn = json.dumps(resultReturn)
        return resultReturn

            
class dtu1001_page4:
    def GET(self):
        dtuid = dtuid1
        outCmd = "010300320022641C"
        #delete config table:dtu_config_tablev2
        config.DB.delete('dtu_config_tablev2', where='dtu_name=$dtuid',vars={'dtuid':dtuid})
        cmdinfo = config.DB.query('select * from dtu_config where dtu_name=$dtuid and status=1 and cmd=$readcmd;',vars={'dtuid':dtuid, 'readcmd':outCmd});
        if (len(cmdinfo)==0):
            insert_cmds(dtuid, outCmd)
        resultarray = []
        for i in range(0,35):
            resultarray.append(-1)
        return render1.page4(resultarray ,dtuid)
    def POST(self):
        dtuid = dtuid1
        input = web.input(type=-1)
        type = input.type
        resultarray = [-1 for i in range(0,35)]
        if(int(type)==-1):
            return render1.page4(resultarray,dtuid)

        if(int(type)==1):
            #config start，compose the cmd, insert into dtu_config , and status=1
            data=[("store_config",1),('over_voltage_1',web.input().over_voltage_1),
               ('over_current_1',web.input().over_current_1),
               ('target_power_fator_1',web.input().target_power_fator_1),
               ('upper_voltage_1',web.input().upper_voltage_1),
               ('capacity_1',web.input().capacity_1),
               ('bus_PT_1',web.input().bus_PT_1),
               ('lower_voltage_1',web.input().lower_voltage_1),
               ('time_delay_1',web.input().time_delay_1),
               ('bus_CT_1',web.input().bus_CT_1),
               ('under_voltage_1',web.input().under_voltage_1),
               ('stable_time_1',web.input().stable_time_1),
               ('mcr_PT_1',web.input().mcr_PT_1),
               ('switch_on_threshold_1',web.input().switch_on_threshold_1),
               ('max_operating_angle_1',web.input().max_operating_angle_1),
               ('mcr_CT_1',web.input().mcr_CT_1),
               ('unbalanced_threshold_1',web.input().unbalanced_threshold_1),
               ('upper_power_factor_1',web.input().upper_power_factor_1),
               ('time_delay_power_fator_1',web.input().time_delay_power_fator_1),
               ('over_voltage_2',web.input().over_voltage_2),
               ('over_current_2',web.input().over_current_2),
               ('target_power_fator_2',web.input().target_power_fator_2),
               ('upper_voltage_2',web.input().upper_voltage_2),
               ('capacity_2',web.input().capacity_2),
               ('bus_PT_2',web.input().bus_PT_2),
               ('lower_voltage_2',web.input().lower_voltage_2),
               ('time_delay_2',web.input().time_delay_2),
               ('bus_CT_2',web.input().bus_CT_2),
               ('under_voltage_2',web.input().under_voltage_2),
               ('stable_time_2',web.input().stable_time_2),
               ('mcr_PT_2',web.input().mcr_PT_2),
               ('switch_on_threshold_2',web.input().switch_on_threshold_2),
               ('max_operating_angle_2',web.input().max_operating_angle_2),
               ('mcr_CT_2',web.input().mcr_CT_2),
               ('unbalanced_threshold_2',web.input().unbalanced_threshold_2)]
            outCmd = makeCmd.make_cmds(dtuid, data)
            outCmd=outCmd + ',010300320022641C'
            insert_cmds(dtuid, outCmd)
            #delete config table:dtu_config_tablev2
            config.DB.delete('dtu_config_tablev2', where='dtu_name=$dtuid',vars={'dtuid':dtuid})
            return render1.page4(resultarray,dtuid)
        if(int(type)==9):
            outCmd = "010300320022641C"
            #delete config table:dtu_config_tablev2
            config.DB.delete('dtu_config_tablev2', where='dtu_name=$dtuid',vars={'dtuid':dtuid})
            cmdinfo = config.DB.query('select * from dtu_config where dtu_name=$dtuid and status=1 and cmd=$readcmd;',vars={'dtuid':dtuid, 'readcmd':outCmd});
            if (len(cmdinfo)==0):
                insert_cmds(dtuid, outCmd)
            return render1.page4(resultarray,dtuid)
        if(int(type)==0):
            #read configs
            #outCmd = "010300320022641C"
            #config.DB.insert('dtu_config',dtu_name=dtuid,cmd=outCmd,status=1,time=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
            dtuinfo = config.DB.query('select * from dtu_config_tablev2 where dtu_name=$dtuid order by updatetime desc limit 1;',vars={'dtuid':dtuid});
            if(len(dtuinfo)==0):
                outCmd = "010300320022641C"
                cmdinfo = config.DB.query('select * from dtu_config where dtu_name=$dtuid and status=1 and cmd=$readcmd;',vars={'dtuid':dtuid, 'readcmd':outCmd});
                if (len(cmdinfo)==0):
                    insert_cmds(dtuid, outCmd)
                return render1.page4(resultarray,dtuid)
            queryres = dtuinfo[0]
            over_voltage_1=queryres['over_voltage_1']
            over_current_1=queryres['over_current_1']
            target_power_fator_1=queryres['target_power_fator_1']
            upper_voltage_1=queryres['upper_voltage_1']
            capacity_1=queryres['capacity_1']
            bus_PT_1=queryres['bus_PT_1']
            lower_voltage_1=queryres['lower_voltage_1']
            time_delay_1=queryres['time_delay_1']
            bus_CT_1=queryres['bus_CT_1']
            under_voltage_1=queryres['under_voltage_1']
            stable_time_1=queryres['stable_time_1']
            mcr_PT_1=queryres['mcr_PT_1']
            switch_on_threshold_1=queryres['switch_on_threshold_1']
            max_operating_angle_1=queryres['max_operating_angle_1']
            mcr_CT_1=queryres['mcr_CT_1']
            unbalanced_threshold_1=queryres['unbalanced_threshold_1']
            upper_power_factor_1=queryres['upper_power_factor_1']
            time_delay_power_fator_1=queryres['time_delay_power_fator_1']
            over_voltage_2=queryres['over_voltage_2']
            over_current_2=queryres['over_current_2']
            target_power_fator_2=queryres['target_power_fator_2']
            upper_voltage_2=queryres['upper_voltage_2']
            capacity_2=queryres['capacity_2']
            bus_PT_2=queryres['bus_PT_2']
            lower_voltage_2=queryres['lower_voltage_2']
            time_delay_2=queryres['time_delay_2']
            bus_CT_2=queryres['bus_CT_2']
            under_voltage_2=queryres['under_voltage_2']
            stable_time_2=queryres['stable_time_2']
            mcr_PT_2=queryres['mcr_PT_2']
            switch_on_threshold_2=queryres['switch_on_threshold_2']
            max_operating_angle_2=queryres['max_operating_angle_2']
            mcr_CT_2=queryres['mcr_CT_2']
            unbalanced_threshold_2=queryres['unbalanced_threshold_2']
            resultarray = []
            resultarray.append(over_voltage_1)          
            resultarray.append(over_current_1)          
            resultarray.append(target_power_fator_1)    
            resultarray.append(upper_voltage_1)         
            resultarray.append(capacity_1)              
            resultarray.append(bus_PT_1)               
            resultarray.append(lower_voltage_1)         
            resultarray.append(time_delay_1)            
            resultarray.append(bus_CT_1)               
            resultarray.append(under_voltage_1)         
            resultarray.append(stable_time_1)           
            resultarray.append(mcr_PT_1)               
            resultarray.append(switch_on_threshold_1)   
            resultarray.append(max_operating_angle_1)   
            resultarray.append(mcr_CT_1)               
            resultarray.append(unbalanced_threshold_1)  
            resultarray.append(upper_power_factor_1)    
            resultarray.append(time_delay_power_fator_1)
            resultarray.append(over_voltage_2)          
            resultarray.append(over_current_2)          
            resultarray.append(target_power_fator_2)    
            resultarray.append(upper_voltage_2)         
            resultarray.append(capacity_2)              
            resultarray.append(bus_PT_2)               
            resultarray.append(lower_voltage_2)         
            resultarray.append(time_delay_2)            
            resultarray.append(bus_CT_2)               
            resultarray.append(under_voltage_2)         
            resultarray.append(stable_time_2)           
            resultarray.append(mcr_PT_2)               
            resultarray.append(switch_on_threshold_2)   
            resultarray.append(max_operating_angle_2)   
            resultarray.append(mcr_CT_2)               
            resultarray.append(unbalanced_threshold_2)  
            resultarray.append(1)
            return render1.page4(resultarray,dtuid)

        if(int(type)==2):
            outCmd = "0106002300033801"
            insert_cmds(dtuid, outCmd)
            return render1.page4(resultarray,dtuid)
        if(int(type)==3):
            outCmd = "010600230005B803"
            insert_cmds(dtuid, outCmd)
            return render1.page4(resultarray,dtuid)
        if(int(type)==4):
            outCmd = "010600230009B806"
            insert_cmds(dtuid, outCmd)
            return render1.page4(resultarray,dtuid)
        if(int(type)==5):
            outCmd = "010600230011B80C"
            insert_cmds(dtuid, outCmd)
            return render1.page4(resultarray,dtuid)
        if(int(type)==6):
            outCmd = "0106002400010801"
            insert_cmds(dtuid, outCmd)
            return render1.page4(resultarray,dtuid)
        if(int(type)==7):
            outCmd = "01060025000159C1"
            insert_cmds(dtuid, outCmd)
            return render1.page4(resultarray,dtuid)
        if(int(type)==8):
            outCmd = "0106003000014805"
            insert_cmds(dtuid, outCmd)
            return render1.page4(resultarray,dtuid)

class dtu1001_pageX:
    def GET(self):
        dtuid = dtuid1
        resultarray = []
        for i in range(0,35):
            resultarray.append(-1)
        return render1.pageX(resultarray ,dtuid)
    def POST(self):
        #i = web.input()
        dtuid = dtuid1
        type = web.input().type
        resultarray = []
        if(len(resultarray)==0):
            resultarray = [-1 for i in range(0,35)]

        if(int(type)==7):
            outCmd = "01060025000159C1"
            insert_cmds(dtuid, outCmd)
            return render1.pageX(resultarray,dtuid)
        if(int(type)==8):
            outCmd = "0106003000014805"
            insert_cmds(dtuid, outCmd)
            return render1.pageX(resultarray,dtuid)

class dtu1002_pageX:
    def GET(self):
        dtuid = dtuid1
        resultarray = []
        for i in range(0,35):
            resultarray.append(-1)
        return render2.pageX(resultarray ,dtuid)
	#return "hello"
    def POST(self):
        #i = web.input()
        dtuid = dtuid1
        type = web.input().type
        resultarray = []
        if(len(resultarray)==0):
            resultarray = [-1 for i in range(0,35)]

        if(int(type)==7):
            outCmd = "01060025000159C1"
            insert_cmds(dtuid, outCmd)
            return render2.pageX(resultarray,dtuid)
        if(int(type)==8):
            outCmd = "0106003000014805"
            insert_cmds(dtuid, outCmd)
            return render2.pageX(resultarray,dtuid)
class runoob_websocket:
    def GET(self):        

	return render21.runoob_websocket()
	#return render21.example.console()

    def POST(self):
	return "hello"
        #return render2.pageX(resultarray ,dtuid)
        #raise web.seeother('/home/yh/pywebsocket/mod_pywebsocket/runoob_websocket.html')
#class js:
    #def GET(self):
       # return render3.index("JS")
    #def POST(self):
         #return render3.index()



#********************************************************DTU003 START************************************************************************
class dtu1003_page1:
    def GET(self):
        dtuid = dtuid3
        input = web.input(reset1=0, reset2=0, mcr_angle_set_1=-1, mcr_angle_set_2=-1, mcr_auto_flag_set_1=-1, mcr_auto_flag_set_2=-1)
        reset1 = input.reset1
        reset2 = input.reset2
        mcr_angle_set_1 = input.mcr_angle_set_1
        mcr_angle_set_2 = input.mcr_angle_set_2
        mcr_auto_flag_set_1 = input.mcr_auto_flag_set_1
        mcr_auto_flag_set_2 = input.mcr_auto_flag_set_2

        if int(reset1) == 1:
            data=[("reset_mcr1",1)]
            outCmd = makeCmd.make_cmds(dtuid, data)
            insert_cmds(dtuid, outCmd)
        if int(reset2) == 1:
            data=[("reset_mcr2",1)]
            outCmd = makeCmd.make_cmds(dtuid, data)
            insert_cmds(dtuid, outCmd)

        if ((int(mcr_auto_flag_set_1)!=-1) and (int(mcr_auto_flag_set_2)!=-1)):
            data=[("mcr_auto_flag_set_1", int(mcr_auto_flag_set_1)),
                  ("mcr_auto_flag_set_2", int(mcr_auto_flag_set_2)),
                  ("mcr_auto_flag_change",1),
                  ("mcr_auto_flag_store",0)]
            if mcr_angle_set_1 != "":
                if int(mcr_angle_set_1)!=-1:
                    data.append(("mcr_angle_set_1",int(mcr_angle_set_1)))
            if mcr_angle_set_2 != "":
                if int(mcr_angle_set_2)!=-1:
                    data.append(("mcr_angle_set_2",int(mcr_angle_set_2)))
            #change the automode.....
            outCmd = makeCmd.make_cmds(dtuid, data)
            insert_cmds(dtuid, outCmd)
			
        dtuinfo = config.DB.query('select * from dtu_table1v2 where dtu_name=$dtuid order by updatetime desc limit 1',vars={'dtuid':dtuid})
        resultarray = []

        if(len(dtuinfo)==0):
            resultarray = [-1 for i in range(0,44)]
        else:
            queryres = dtuinfo[0]
            flag_voltage_1=(int(queryres['flag_voltage_over_1']) + int(queryres['flag_voltage_under_1']) + int(queryres['flag_threshold_over_1']))
            flag_current_1=(int(queryres['flag_current_over_1']) + int(queryres['flag_current_unblance_1']))
            flag_sampling_1=(int(queryres['flag_sampling_error_1']) + int(queryres['flag_sampling_warning_1']))
            flag_prediction_1=queryres['flag_prediction_1']
            flag_high_temperature_1=queryres['flag_high_temperature_1']
            flag_manul_auto_1=queryres['mcr_auto_flag_set_1']
            flag_manul_auto_2=queryres['mcr_auto_flag_set_2']
            flag_voltage_2=(int(queryres['flag_voltage_over_2']) + int(queryres['flag_voltage_under_2']) + int(queryres['flag_threshold_over_2']))
            flag_current_2=(int(queryres['flag_current_over_2']) + int(queryres['flag_current_unblance_2']))
            flag_sampling_2=(int(queryres['flag_sampling_error_2']) + int(queryres['flag_sampling_warning_2']))
            flag_prediction_2=queryres['flag_prediction_2']
            flag_high_temperature_2=queryres['flag_high_temperature_2']

            voltage_1=queryres['voltage_1']
            current_1=queryres['current_1']
            active_power_1=get_real_value(float_dtu(queryres['active_power_hign_1'])*65536+float_dtu(queryres['active_power_low_1']), 10)
            reactive_power_1=get_real_value(float_dtu(queryres['reactive_power_high_1'])*65536+float_dtu(queryres['reactive_power_low_1']), 10)
            power_factor_1=get_real_value_h(queryres['power_factor_1'], 100)

            voltage_2=queryres['voltage_2']
            current_2=queryres['current_2']
            active_power_2=get_real_value(float_dtu(queryres['active_power_hign_2'])*65536+float_dtu(queryres['active_power_low_2']), 10)
            reactive_power_2=get_real_value(float_dtu(queryres['reactive_power_high_2'])*65536+float_dtu(queryres['reactive_power_low_2']), 10)
            power_factor_2=get_real_value_h(queryres['power_factor_2'], 100)

            voltage_3=queryres['voltage_3']
            current_3=queryres['current_3']
            active_power_3=get_real_value(float_dtu(queryres['active_power_hign_3'])*65536+float_dtu(queryres['active_power_low_3']), 10)
            reactive_power_3=get_real_value(float_dtu(queryres['reactive_power_high_3'])*65536+float_dtu(queryres['reactive_power_low_3']), 10)
            power_factor_3=get_real_value_h(queryres['power_factor_3'], 100)
			
            mcr_voltage_1=queryres['mcr_voltage_A_1']
            mcr_current_A_1=queryres['mcr_current_A_1']
            mcr_current_B_1=queryres['mcr_current_B_1']
            mcr_current_C_1=queryres['mcr_current_C_1']
            mcr_operating_angle_1=queryres['mcr_operating_angle_1']
            mcr_voltage_2=queryres['mcr_voltage_A_2']
            mcr_current_A_2=queryres['mcr_current_A_2']
            mcr_current_B_2=queryres['mcr_current_B_2']
            mcr_current_C_2=queryres['mcr_current_C_2']
            mcr_operating_angle_2=queryres['mcr_operating_angle_2']
            flag_switch_entry_1=queryres['flag_switch_entry_1']
            flag_switch_gas_1=queryres['flag_switch_gas_1']
            flag_switch_entry_2=queryres['flag_switch_entry_2']
            flag_switch_mcr_1=queryres['flag_switch_mcr_1']
            flag_switch_mcr_2=queryres['flag_switch_mcr_2']
            flag_switch_main=queryres['flag_switch_main']
            flag_switch_gas_2=queryres['flag_switch_gas_2']

            updatetime=queryres['updatetime']
            a=time.mktime(updatetime.timetuple()) 
            b=time.time()
            delttime = b-a
            if(delttime>30):
                resultarray = [0 for i in range(0,44)]
            else: 
                resultarray.append(flag_voltage_1)  #0
                resultarray.append(flag_current_1)
                resultarray.append(flag_sampling_1)
                resultarray.append(flag_prediction_1)
                resultarray.append(flag_high_temperature_1)
                resultarray.append(flag_manul_auto_1) #5
                resultarray.append(flag_manul_auto_2)
                resultarray.append(flag_voltage_2)
                resultarray.append(flag_current_2)
                resultarray.append(flag_sampling_2)
                resultarray.append(flag_prediction_2) #10
                resultarray.append(flag_high_temperature_2)
                resultarray.append(voltage_1)
                resultarray.append(current_1)
                resultarray.append(active_power_1)
                resultarray.append(reactive_power_1) #15
                resultarray.append(power_factor_1)
                resultarray.append(voltage_2)
                resultarray.append(current_2)
                resultarray.append(active_power_2)
                resultarray.append(reactive_power_2) #20
                resultarray.append(power_factor_2)
                resultarray.append(voltage_3)
                resultarray.append(current_3)
                resultarray.append(active_power_3)
                resultarray.append(reactive_power_3) #25
                resultarray.append(power_factor_3)
                resultarray.append(mcr_voltage_1)
                resultarray.append(mcr_current_A_1)
                resultarray.append(mcr_current_B_1)
                resultarray.append(mcr_current_C_1)  #30
                resultarray.append(mcr_operating_angle_1)
                resultarray.append(mcr_voltage_2)
                resultarray.append(mcr_current_A_2)
                resultarray.append(mcr_current_B_2)
                resultarray.append(mcr_current_C_2) #35
                resultarray.append(mcr_operating_angle_2)
                resultarray.append(flag_switch_entry_1)
                resultarray.append(flag_switch_gas_1)
                resultarray.append(flag_switch_entry_2)
                resultarray.append(flag_switch_mcr_1) #40
                resultarray.append(flag_switch_mcr_2)
                resultarray.append(flag_switch_main)
                resultarray.append(flag_switch_gas_2)
        
        dtuinfo2 = config.DB.query('select project_name,product_model,product_code from dtu_basic_infov2 where dtu_name=$dtuid',vars={'dtuid':dtuid})
        if(len(dtuinfo2)==0):
            resultarray.append("No Project")
            resultarray.append("*********")
            resultarray.append("*********")
            curtime=get_cur_time()
            resultarray.append(curtime)
        else:
            queryres2 = dtuinfo2[0]
            project_name=queryres2['project_name']
            product_model=queryres2['product_model']
            product_code=queryres2['product_code']
            resultarray.append(project_name)
            resultarray.append(product_model)
            resultarray.append(product_code)
            curtime=get_cur_time()
            resultarray.append(curtime)
        return render3.page1(resultarray, dtuid)

class dtu1003_page2:
    def GET(self):
        dtuid = dtuid3
        
        eventhistory = config.DB.query('select * from dtu_event where dtu_name=$dtuid order by time desc;', vars={'dtuid':dtuid})
        dtuinfo = config.DB.query('select * from dtu_event where dtu_name=$dtuid order by time desc limit 1',vars={'dtuid':dtuid})
		
        if(len(dtuinfo)==0):
            resultarray = dtuinfo
        else:
            item = dtuinfo[0]
            print item
            eventTime = item['time']
            resultarray = config.DB.query('select * from dtu_event where dtu_name=$dtuid and time=$etime;', vars={'dtuid':dtuid, 'etime':eventTime})

        return render3.page2(resultarray,eventhistory,dtuid)

class dtu1003_page3:
    def GET(self):
        dtuid = dtuid3

        paremarray = web.input()
        starttime=paremarray.starttime
        endtime=paremarray.endtime

        if(starttime=='-1' or starttime==None or endtime=='-1' or endtime==None):
            historyinfo = config.DB.query("select power_factor_1,power_factor_2,power_factor_3,voltage_1,voltage_2,voltage_3,current_1,current_2,current_3, mcr_voltage_A_1, mcr_voltage_B_1, mcr_voltage_C_1, mcr_voltage_A_2, mcr_voltage_B_2, mcr_voltage_C_2, mcr_current_A_1,mcr_current_B_1,mcr_current_C_1,mcr_current_A_2,mcr_current_B_2,mcr_current_C_2,updatetime from dtu_table1v2 order by updatetime desc limit 50")
        else:
            starttime = web.input().starttime
            endtime = web.input().endtime
            historyinfo = config.DB.query("select power_factor_1,power_factor_2,power_factor_3,voltage_1,voltage_2,voltage_3,current_1,current_2,current_3, mcr_voltage_A_1, mcr_voltage_B_1, mcr_voltage_C_1, mcr_voltage_A_2, mcr_voltage_B_2, mcr_voltage_C_2, mcr_current_A_1,mcr_current_B_1,mcr_current_C_1,mcr_current_A_2,mcr_current_B_2,mcr_current_C_2,updatetime from dtu_table1v2 where updatetime>='"+starttime+"' and updatetime<='"+endtime+"'")

        result = historyinfo
        power_factor_1_array = []
        power_factor_2_array=[]
        power_factor_3_array=[]
        voltage_1_array=[]
        voltage_2_array=[]
        voltage_3_array=[]
        current_1_array=[]
        current_2_array=[]
        current_3_array=[]
        mcr_voltage_A_1_array=[]
        mcr_voltage_B_1_array=[]
        mcr_voltage_C_1_array=[]
        mcr_voltage_A_2_array=[]
        mcr_voltage_B_2_array=[]
        mcr_voltage_C_2_array=[]
        mcr_current_A_1_array=[]
        mcr_current_B_1_array=[]
        mcr_current_C_1_array=[]
        mcr_current_A_2_array=[]
        mcr_current_B_2_array=[]
        mcr_current_C_2_array=[]
        updatetime_array=[]
        for item in result:
            power_factor_1_array.append(get_real_value_h(float_dtu(item['power_factor_1']), 100))
            power_factor_2_array.append(get_real_value_h(float_dtu(item['power_factor_2']), 100))
            power_factor_3_array.append(get_real_value_h(float_dtu(item['power_factor_3']), 100))
            voltage_1_array.append(float_dtu(item['voltage_1']))
            voltage_2_array.append(float_dtu(item['voltage_2']))
            voltage_3_array.append(float_dtu(item['voltage_3']))
            current_1_array.append(float_dtu(item['current_1']))
            current_2_array.append(float_dtu(item['current_2']))
            current_3_array.append(float_dtu(item['current_3']))
            mcr_voltage_A_1_array.append(float_dtu(item['mcr_voltage_A_1']))
            mcr_voltage_B_1_array.append(float_dtu(item['mcr_voltage_B_1']))
            mcr_voltage_C_1_array.append(float_dtu(item['mcr_voltage_C_1']))
            mcr_voltage_A_2_array.append(float_dtu(item['mcr_voltage_A_2']))
            mcr_voltage_B_2_array.append(float_dtu(item['mcr_voltage_B_2']))
            mcr_voltage_C_2_array.append(float_dtu(item['mcr_voltage_C_2']))
            mcr_current_A_1_array.append(float_dtu(item['mcr_current_A_1']))
            mcr_current_B_1_array.append(float_dtu(item['mcr_current_B_1']))
            mcr_current_C_1_array.append(float_dtu(item['mcr_current_C_1']))
            mcr_current_A_2_array.append(float_dtu(item['mcr_current_A_2']))
            mcr_current_B_2_array.append(float_dtu(item['mcr_current_B_2']))
            mcr_current_C_2_array.append(float_dtu(item['mcr_current_C_2']))
            updatetime_array.append(str(item['updatetime']))

        return render3.page3(power_factor_1_array,power_factor_2_array,power_factor_3_array,voltage_1_array,voltage_2_array,voltage_3_array,current_1_array,current_2_array,current_3_array,mcr_voltage_A_1_array,mcr_voltage_B_1_array,mcr_voltage_C_1_array,mcr_voltage_A_2_array,mcr_voltage_B_2_array,mcr_voltage_C_2_array,mcr_current_A_1_array,mcr_current_B_1_array,mcr_current_C_1_array,mcr_current_A_2_array,mcr_current_B_2_array,mcr_current_C_2_array,updatetime_array, dtuid)

class dtu1003_page33:
    def GET(self):
        dtuid = dtuid3
        paremarray = web.input()
        starttime=paremarray.starttime
        endtime=paremarray.endtime

        if(starttime=='-1' or starttime==None or endtime=='-1' or endtime==None):
            historyinfo = config.DB.query("select power_factor_1,power_factor_2,power_factor_3,voltage_1,voltage_2,voltage_3,current_1,current_2,current_3, mcr_voltage_A_1, mcr_voltage_B_1, mcr_voltage_C_1, mcr_voltage_A_2, mcr_voltage_B_2, mcr_voltage_C_2, mcr_current_A_1,mcr_current_B_1,mcr_current_C_1,mcr_current_A_2,mcr_current_B_2,mcr_current_C_2,updatetime from dtu_table1v2 order by updatetime desc limit 50")
            print historyinfo
        else:
            starttime = web.input().starttime
            endtime = web.input().endtime
            historyinfo = config.DB.query("select power_factor_1,power_factor_2,power_factor_3,voltage_1,voltage_2,voltage_3,current_1,current_2,current_3, mcr_voltage_A_1, mcr_voltage_B_1, mcr_voltage_C_1, mcr_voltage_A_2, mcr_voltage_B_2, mcr_voltage_C_2, mcr_current_A_1,mcr_current_B_1,mcr_current_C_1,mcr_current_A_2,mcr_current_B_2,mcr_current_C_2,updatetime from dtu_table1v2 where updatetime>='"+starttime+"' and updatetime<='"+endtime+"'")
            print historyinfo

        result = historyinfo
        power_factor_1_array = []
        power_factor_2_array=[]
        power_factor_3_array=[]
        voltage_1_array=[]
        voltage_2_array=[]
        voltage_3_array=[]
        current_1_array=[]
        current_2_array=[]
        current_3_array=[]
        mcr_voltage_A_1_array=[]
        mcr_voltage_B_1_array=[]
        mcr_voltage_C_1_array=[]
        mcr_voltage_A_2_array=[]
        mcr_voltage_B_2_array=[]
        mcr_voltage_C_2_array=[]
        mcr_current_A_1_array=[]
        mcr_current_B_1_array=[]
        mcr_current_C_1_array=[]
        mcr_current_A_2_array=[]
        mcr_current_B_2_array=[]
        mcr_current_C_2_array=[]
        updatetime_array=[]
		
        for item in result:
            power_factor_1_array.append(get_real_value_h(float_dtu(item['power_factor_1']), 100))
            power_factor_2_array.append(get_real_value_h(float_dtu(item['power_factor_2']), 100))
            power_factor_3_array.append(get_real_value_h(float_dtu(item['power_factor_3']), 100))
            voltage_1_array.append(float_dtu(item['voltage_1']))
            voltage_2_array.append(float_dtu(item['voltage_2']))
            voltage_3_array.append(float_dtu(item['voltage_3']))
            current_1_array.append(float_dtu(item['current_1']))
            current_2_array.append(float_dtu(item['current_2']))
            current_3_array.append(float_dtu(item['current_3']))
            mcr_voltage_A_1_array.append(float_dtu(item['mcr_voltage_A_1']))
            mcr_voltage_B_1_array.append(float_dtu(item['mcr_voltage_B_1']))
            mcr_voltage_C_1_array.append(float_dtu(item['mcr_voltage_C_1']))
            mcr_voltage_A_2_array.append(float_dtu(item['mcr_voltage_A_2']))
            mcr_voltage_B_2_array.append(float_dtu(item['mcr_voltage_B_2']))
            mcr_voltage_C_2_array.append(float_dtu(item['mcr_voltage_C_2']))
            mcr_current_A_1_array.append(float_dtu(item['mcr_current_A_1']))
            mcr_current_B_1_array.append(float_dtu(item['mcr_current_B_1']))
            mcr_current_C_1_array.append(float_dtu(item['mcr_current_C_1']))
            mcr_current_A_2_array.append(float_dtu(item['mcr_current_A_2']))
            mcr_current_B_2_array.append(float_dtu(item['mcr_current_B_2']))
            mcr_current_C_2_array.append(float_dtu(item['mcr_current_C_2']))
            updatetime_array.append(str(item['updatetime']))
			
        resultReturn={
            'power_factor_1_array':power_factor_1_array,
            'power_factor_2_array':power_factor_2_array,
            'power_factor_3_array':power_factor_3_array,
            'voltage_1_array':voltage_1_array,
            'voltage_2_array':voltage_2_array,
            'voltage_3_array':voltage_3_array,
            'current_1_array':current_1_array,
            'current_2_array':current_2_array,
            'current_3_array':current_3_array,
            'mcr_voltage_A_1_array':mcr_voltage_A_1_array,
            'mcr_voltage_B_1_array':mcr_voltage_B_1_array,
            'mcr_voltage_C_1_array':mcr_voltage_C_1_array,
            'mcr_voltage_A_2_array':mcr_voltage_A_2_array,
            'mcr_voltage_B_2_array':mcr_voltage_B_2_array,
            'mcr_voltage_C_2_array':mcr_voltage_C_2_array,
            'mcr_current_A_1_array':mcr_current_A_1_array,
            'mcr_current_B_1_array':mcr_current_B_1_array,
            'mcr_current_C_1_array':mcr_current_C_1_array,
            'mcr_current_A_2_array':mcr_current_A_2_array,
            'mcr_current_B_2_array':mcr_current_B_2_array,
            'mcr_current_C_2_array':mcr_current_C_2_array,
            'updatetime_array':updatetime_array
        }
        resultReturn = json.dumps(resultReturn)
        return resultReturn

            
class dtu1003_page4:
    def GET(self):
        dtuid = dtuid3
        outCmd = "010300320022641C"
        #delete config table:dtu_config_tablev2
        config.DB.delete('dtu_config_tablev2', where='dtu_name=$dtuid',vars={'dtuid':dtuid})
        cmdinfo = config.DB.query('select * from dtu_config where dtu_name=$dtuid and status=1 and cmd=$readcmd;',vars={'dtuid':dtuid, 'readcmd':outCmd});
        if (len(cmdinfo)==0):
            insert_cmds(dtuid, outCmd)
        resultarray = []
        for i in range(0,35):
            resultarray.append(-1)
        return render3.page4(resultarray ,dtuid)
    def POST(self):
        dtuid = dtuid3
        input = web.input(type=-1)
        type = input.type
        resultarray = [-1 for i in range(0,35)]
        if(int(type)==-1):
            return render3.page4(resultarray,dtuid)

        if(int(type)==1):
            #config start，compose the cmd, insert into dtu_config , and status=1
            data=[("store_config",1),('over_voltage_1',web.input().over_voltage_1),
               ('over_current_1',web.input().over_current_1),
               ('target_power_fator_1',web.input().target_power_fator_1),
               ('upper_voltage_1',web.input().upper_voltage_1),
               ('capacity_1',web.input().capacity_1),
               ('bus_PT_1',web.input().bus_PT_1),
               ('lower_voltage_1',web.input().lower_voltage_1),
               ('time_delay_1',web.input().time_delay_1),
               ('bus_CT_1',web.input().bus_CT_1),
               ('under_voltage_1',web.input().under_voltage_1),
               ('stable_time_1',web.input().stable_time_1),
               ('mcr_PT_1',web.input().mcr_PT_1),
               ('switch_on_threshold_1',web.input().switch_on_threshold_1),
               ('max_operating_angle_1',web.input().max_operating_angle_1),
               ('mcr_CT_1',web.input().mcr_CT_1),
               ('unbalanced_threshold_1',web.input().unbalanced_threshold_1),
               ('upper_power_factor_1',web.input().upper_power_factor_1),
               ('time_delay_power_fator_1',web.input().time_delay_power_fator_1),
               ('over_voltage_2',web.input().over_voltage_2),
               ('over_current_2',web.input().over_current_2),
               ('target_power_fator_2',web.input().target_power_fator_2),
               ('upper_voltage_2',web.input().upper_voltage_2),
               ('capacity_2',web.input().capacity_2),
               ('bus_PT_2',web.input().bus_PT_2),
               ('lower_voltage_2',web.input().lower_voltage_2),
               ('time_delay_2',web.input().time_delay_2),
               ('bus_CT_2',web.input().bus_CT_2),
               ('under_voltage_2',web.input().under_voltage_2),
               ('stable_time_2',web.input().stable_time_2),
               ('mcr_PT_2',web.input().mcr_PT_2),
               ('switch_on_threshold_2',web.input().switch_on_threshold_2),
               ('max_operating_angle_2',web.input().max_operating_angle_2),
               ('mcr_CT_2',web.input().mcr_CT_2),
               ('unbalanced_threshold_2',web.input().unbalanced_threshold_2)]
            outCmd = makeCmd.make_cmds(dtuid, data)
            outCmd=outCmd + ',010300320022641C'
            insert_cmds(dtuid, outCmd)
            #delete config table:dtu_config_tablev2
            config.DB.delete('dtu_config_tablev2', where='dtu_name=$dtuid',vars={'dtuid':dtuid})
            return render1.page4(resultarray,dtuid)
        if(int(type)==9):
            outCmd = "010300320022641C"
            #delete config table:dtu_config_tablev2
            config.DB.delete('dtu_config_tablev2', where='dtu_name=$dtuid',vars={'dtuid':dtuid})
            cmdinfo = config.DB.query('select * from dtu_config where dtu_name=$dtuid and status=1 and cmd=$readcmd;',vars={'dtuid':dtuid, 'readcmd':outCmd});
            if (len(cmdinfo)==0):
                insert_cmds(dtuid, outCmd)
            return render3.page4(resultarray,dtuid)
        if(int(type)==0):
            #read configs
            #outCmd = "010300320022641C"
            #config.DB.insert('dtu_config',dtu_name=dtuid,cmd=outCmd,status=1,time=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
            dtuinfo = config.DB.query('select * from dtu_config_tablev2 where dtu_name=$dtuid order by updatetime desc limit 1;',vars={'dtuid':dtuid});
            if(len(dtuinfo)==0):
                outCmd = "010300320022641C"
                cmdinfo = config.DB.query('select * from dtu_config where dtu_name=$dtuid and status=1 and cmd=$readcmd;',vars={'dtuid':dtuid, 'readcmd':outCmd});
                if (len(cmdinfo)==0):
                    insert_cmds(dtuid, outCmd)
                return render1.page4(resultarray,dtuid)
            queryres = dtuinfo[0]
            over_voltage_1=queryres['over_voltage_1']
            over_current_1=queryres['over_current_1']
            target_power_fator_1=queryres['target_power_fator_1']
            upper_voltage_1=queryres['upper_voltage_1']
            capacity_1=queryres['capacity_1']
            bus_PT_1=queryres['bus_PT_1']
            lower_voltage_1=queryres['lower_voltage_1']
            time_delay_1=queryres['time_delay_1']
            bus_CT_1=queryres['bus_CT_1']
            under_voltage_1=queryres['under_voltage_1']
            stable_time_1=queryres['stable_time_1']
            mcr_PT_1=queryres['mcr_PT_1']
            switch_on_threshold_1=queryres['switch_on_threshold_1']
            max_operating_angle_1=queryres['max_operating_angle_1']
            mcr_CT_1=queryres['mcr_CT_1']
            unbalanced_threshold_1=queryres['unbalanced_threshold_1']
            upper_power_factor_1=queryres['upper_power_factor_1']
            time_delay_power_fator_1=queryres['time_delay_power_fator_1']
            over_voltage_2=queryres['over_voltage_2']
            over_current_2=queryres['over_current_2']
            target_power_fator_2=queryres['target_power_fator_2']
            upper_voltage_2=queryres['upper_voltage_2']
            capacity_2=queryres['capacity_2']
            bus_PT_2=queryres['bus_PT_2']
            lower_voltage_2=queryres['lower_voltage_2']
            time_delay_2=queryres['time_delay_2']
            bus_CT_2=queryres['bus_CT_2']
            under_voltage_2=queryres['under_voltage_2']
            stable_time_2=queryres['stable_time_2']
            mcr_PT_2=queryres['mcr_PT_2']
            switch_on_threshold_2=queryres['switch_on_threshold_2']
            max_operating_angle_2=queryres['max_operating_angle_2']
            mcr_CT_2=queryres['mcr_CT_2']
            unbalanced_threshold_2=queryres['unbalanced_threshold_2']
            resultarray = []
            resultarray.append(over_voltage_1)          
            resultarray.append(over_current_1)          
            resultarray.append(target_power_fator_1)    
            resultarray.append(upper_voltage_1)         
            resultarray.append(capacity_1)              
            resultarray.append(bus_PT_1)               
            resultarray.append(lower_voltage_1)         
            resultarray.append(time_delay_1)            
            resultarray.append(bus_CT_1)               
            resultarray.append(under_voltage_1)         
            resultarray.append(stable_time_1)           
            resultarray.append(mcr_PT_1)               
            resultarray.append(switch_on_threshold_1)   
            resultarray.append(max_operating_angle_1)   
            resultarray.append(mcr_CT_1)               
            resultarray.append(unbalanced_threshold_1)  
            resultarray.append(upper_power_factor_1)    
            resultarray.append(time_delay_power_fator_1)
            resultarray.append(over_voltage_2)          
            resultarray.append(over_current_2)          
            resultarray.append(target_power_fator_2)    
            resultarray.append(upper_voltage_2)         
            resultarray.append(capacity_2)              
            resultarray.append(bus_PT_2)               
            resultarray.append(lower_voltage_2)         
            resultarray.append(time_delay_2)            
            resultarray.append(bus_CT_2)               
            resultarray.append(under_voltage_2)         
            resultarray.append(stable_time_2)           
            resultarray.append(mcr_PT_2)               
            resultarray.append(switch_on_threshold_2)   
            resultarray.append(max_operating_angle_2)   
            resultarray.append(mcr_CT_2)               
            resultarray.append(unbalanced_threshold_2)  
            resultarray.append(1)
            return render1.page4(resultarray,dtuid)

        if(int(type)==2):
            outCmd = "0106002300033801"
            insert_cmds(dtuid, outCmd)
            return render3.page4(resultarray,dtuid)
        if(int(type)==3):
            outCmd = "010600230005B803"
            insert_cmds(dtuid, outCmd)
            return render3.page4(resultarray,dtuid)
        if(int(type)==4):
            outCmd = "010600230009B806"
            insert_cmds(dtuid, outCmd)
            return render3.page4(resultarray,dtuid)
        if(int(type)==5):
            outCmd = "010600230011B80C"
            insert_cmds(dtuid, outCmd)
            return render3.page4(resultarray,dtuid)
        if(int(type)==6):
            outCmd = "0106002400010801"
            insert_cmds(dtuid, outCmd)
            return render3.page4(resultarray,dtuid)
        if(int(type)==7):
            outCmd = "01060025000159C1"
            insert_cmds(dtuid, outCmd)
            return render3.page4(resultarray,dtuid)
        if(int(type)==8):
            outCmd = "0106003000014805"
            insert_cmds(dtuid, outCmd)
            return render3.page4(resultarray,dtuid)

class dtu1003_pageX:
    def GET(self):
        dtuid = dtuid3
        resultarray = []
        for i in range(0,35):
            resultarray.append(-1)
        return render3.pageX(resultarray ,dtuid)
    def POST(self):
        #i = web.input()
        dtuid = dtuid3
        type = web.input().type
        resultarray = []
        if(len(resultarray)==0):
            resultarray = [-1 for i in range(0,35)]

        if(int(type)==7):
            outCmd = "01060025000159C1"
            insert_cmds(dtuid, outCmd)
            return render3.pageX(resultarray,dtuid)
        if(int(type)==8):
            outCmd = "0106003000014805"
            insert_cmds(dtuid, outCmd)
            return render3.pageX(resultarray,dtuid)
#********************************************************DTU003 END************************************************************************
















if __name__ == "__main__":
    #threading.Thread(target = demaonThread, args = (), name = 'demonthread').start()
    LOG.info("Web server start")
    #print("In mem %s" % config.mc.get(str(144) + config._LEFTCOUNT))
    #alipay.alipayDeamon().start()
    app = web.application(urls, globals())
    app.run()
    app.run()

