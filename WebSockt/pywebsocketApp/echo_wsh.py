# -*- coding: utf-8 -*-
# Copyright 2011, Google Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#     * Neither the name of Google Inc. nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


_GOODBYE_MESSAGE = u'Goodbye'


import web
#import datetime
#import hashlib
#import model
#import db
import threading, sys
#import LOG
#import random
from cStringIO import StringIO
#from os import path
#import uuid
import time
#import makeCmd
#import json
import struct
from mod_pywebsocket import common
#from mod_pywebsocket import stream

global DB

_LEFTCOUNT="_LEFTCOUNT"
_CALLEDCOUNT="_CALLEDCOUNT"
_SUCCESSCOUNT="_SUCCESSCOUNT"




def get_real_value(value, factor):
    v = int(float(value) * factor)
    (real,) = struct.unpack('>l',struct.pack('>L', v))
    return real/float(factor)

def get_real_value_h(value, factor):
    v = int(float(value) * factor)
    (real,) = struct.unpack('>h',struct.pack('>H', v))
    return real/float(factor)

def float_dtu(string):
    try:
        v = float(string)
    except:
        v = 0
    return v

def web_socket_do_extra_handshake(request):
    # This example handler accepts any request. See origin_check_wsh.py for how
    # to reject access from untrusted scripts based on origin value.
    global DB
    DB = web.database(host='localhost', dbn='mysql', user='root', pw='rootroot', db='mysql')

    pass  # Always accept.


def web_socket_transfer_data(request):  
    global DB  
    
    while True:
        line = request.ws_stream.receive_message()       

        if line is None:
            return
        if isinstance(line, unicode):
            if (cmp(line,"dtu1001")) == 0:
                dtuid = line
                #DB = web.database(host='localhost', dbn='mysql', user='root', pw='rootroot', db='mysql')
                dtuinfo = DB.query('select * from dtu_table1v2 where dtu_name=$dtuid order by updatetime desc limit 1',vars={'dtuid':dtuid})
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
                
                dtuinfo2 = DB.query('select project_name,product_model,product_code from dtu_basic_infov2 where dtu_name=$dtuid',vars={'dtuid':dtuid})
                sendData = []
                lengthlist = len(resultarray)
                for i in range(0, lengthlist-1):
                    temp1 = resultarray[i]
                    #print ("resultarray[%d] type is %s value = %s" % (i, type(temp1),  resultarray[i]))
                    if isinstance(temp1, unicode):
                        temp  = temp1.encode("utf-8")
                    else:
                        temp = str(temp1)                    
                    #print "\033[1;31m newdata type is  ("%s value = %s" % (type(temp),  temp))\033[0m"  

                    sendData.append(temp)
            
                mystr = ' '.join(sendData) #变为字符串
                #newlist = mystr.split()#再次变为数组
                print "\033[1;31m <************************************ \033[0m"
                print mystr              
                print "\033[1;35m ************************************> \033[0m" 
                #print newlist   
                #print "\033[1;31m ************************************> \033[0m"
                    
                request.ws_stream.send_message(mystr, binary=False)
            else:
                request.ws_stream.send_message(line, binary=True)


def web_socket_passive_closing_handshake(request):
    # Simply echo a close status code
    code, reason = request.ws_close_code, request.ws_close_reason

    # pywebsocket sets pseudo code for receiving an empty body close frame.
    if code == common.STATUS_NO_STATUS_RECEIVED:
        code = None
        reason = ' '
    elif code == 1001:
        reason = 'closed by browser'
        
    #temp  = reason.encode("utf-8")
 
    print ("webSocket is closed, code is %d, reason is %s " % (code, reason))
    return code, reason


# vi:sts=4 sw=4 et
