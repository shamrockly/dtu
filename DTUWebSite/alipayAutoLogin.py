# -*- coding: UTF-8 -*-
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time
from Queue import Queue
import threading, sys
import LOG
from Queue import Empty
import traceback
#import chardet

'''
存储交易信息的队列
里面的结构就是Model.Trade
'''
queue = Queue()

class alipayDeamon(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def updateDB(self, userN, added):
        print("-------------")
        print("update DB")
        print("-------------")
        try:
            conn=MySQLdb.connect(host=config.host,user=config.user,passwd=config.passwd,db=config.db,port=config.port)
            cur=conn.cursor()
            cur.execute('update userinfo set leftCount=leftCount + %d where ID = %s' % (added, userN))
            if int(cur.rowcount) == 0:
                result="1001"
            else:
                result="ok"
            cur.close()
            conn.commit()
            conn.close()
        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
            result="1003"
            
    def checkAndInsert(self, trade, pageSource):
        #trades = parser.myParser(driver.page_source)
        trades = aliparser.myParser(pageSource)
        print(trades)
        result = True
        comment = ""
        #1.检查数据库中（成功的记录里）有没有该订单号
        myvar = dict(tradeNumber=trade.tradeNumber, result=True)
        results = config.DB.select('record', myvar, where="tradeNumber = $tradeNumber and result = $result")
        if(len(results) > 0):
            print("select did not pass.")
            trade.result = False
            trade.comment = u"请不要提交重复的订单号"
            db.addRecord(trade)
        else:
            print("select pass.")
            find = False
            #2.数据库中没有，可以在支付宝页面中查询了
            #这里要查询金额是否一样。之后相应的插入结果
            for t in trades:
                print("%s - %s" % (t[0], trade.tradeNumber))
                if t[0] == trade.tradeNumber:
                    print("%d - %d" % (int(float(t[1])), int(trade.money)))
                    find = True
                    if int(float(t[1])) == int(trade.money):
                        trade.result = True
                        intMoney = int(trade.money)
                        if intMoney == 1:
                            trade.count = 100
                        elif intMoney == 30:
                            trade.count = 10000
                        elif intMoney == 100:
                            trade.count = 40000
                        elif intMoney == 200:
                            trade.count = 90000
                        elif intMoney == 500:
                            trade.count = 240000
                        elif intMoney == 1000:
                            trade.count = 500000
                        elif intMoney == 2000:
                            trade.count = 2000000
                        else:
                            trade.result = False
                            trade.comment = u"充值金额填写错误"
                        
                        #trade.count = int(trade.money) * 1000
                    else:
                        trade.result = False
                        trade.comment = u"交易金额填写错误"
                    break
            if find == False:
                trade.result = False
                trade.comment = u"订单号不存在"
            if trade.result == True:
                trade.comment = u"提交正确！"
            db.addRecord(trade)
            #如果该订单号正确，需要更新userinfo表，增加相应的调用次数
            if trade.result == True:
                added = trade.count
                self.updateDB(str(trade.userid), added)
                #n = config.DB.update('userinfo', where="ID = " + str(trade.userid), LEFTCOUNT=added)
    def run(self):
        driver = webdriver.Firefox() # Get local session of firefox
        driver.get("https://www.alipay.com") # Load page
        time.sleep(60) #wait 10s for user input username and password
        elem = driver.find_element_by_name("J-input-user")
        elem.clear()
        elem.send_keys("er6e@qq.com")
        getCaptchaResult()
        driver.save_screenshot('screenshot.png')
        refreshPage = "https://consumeprod.alipay.com/record/advanced.htm"
        '''while(True):
            #每次循环都刷新页面
            try:
                trade = queue.get(True, 30)
                driver.get(refreshPage)
                source = driver.page_source
                nextPage = aliparser.getNextPageLink(source)
                if(nextPage != None):
                    driver.get(nextPage)
                    s2 = driver.page_source
                    nextPage = aliparser.getNextPageLink(s2)
                    source += s2
                if(nextPage != None):
                    driver.get(nextPage)
                    s3 = driver.page_source
                    source += s3
                #encoding = chardet.detect(source)
                print(type(source))
                self.checkAndInsert(trade, source)
            except Empty:
		driver.get(refreshPage)
		pass
            except:
                driver.get(refreshPage)
		traceback.print_exc()
                print "Error occured:", sys.exc_info()'''
            

def inputPwdIE(pwd):
    import win32gui, time, win32con
    ieHandle = win32gui.FindWindowEx(None, 0, "IEFrame", None)
    print(ieHandle)
    frameHandle = win32gui.FindWindowEx(ieHandle, 0, "Frame Tab", None)
    print(frameHandle)
    tabHandle = win32gui.FindWindowEx(frameHandle, 0, "TabWindowClass", None)
    shellHandle  = win32gui.FindWindowEx(tabHandle, 0, "Shell DocObject View", None)
    serverHandle  = win32gui.FindWindowEx(shellHandle, 0, "Internet Explorer_Server", None)
    atlHandle  = win32gui.FindWindowEx(serverHandle, 0, None, "")
    editHandle  = win32gui.FindWindowEx(atlHandle, 0, "ATL:Edit", None)
    print(editHandle)
    win32gui.SetForegroundWindow(editHandle)
    #pwd = "test"
    for i in range(len(pwd)):
        win32gui.SendMessage(editHandle, 0x102, ord(pwd[i]), 0)
        time.sleep(1)

def inputPwdFirefox(pwd):
    import win32gui, time, win32con
    ieHandle = win32gui.FindWindowEx(None, 0, None, u'支付宝 知托付！ - Mozilla Firefox: IBM Edition')
    print(ieHandle)
    c1Handle = win32gui.FindWindowEx(ieHandle, 0, "MozillaWindowClass", None)
    print(c1Handle)
    c2Handle = win32gui.FindWindowEx(ieHandle, c1Handle, "MozillaWindowClass", None)
    print(c2Handle)
    c3Handle = win32gui.FindWindowEx(ieHandle, c2Handle, "MozillaWindowClass", None)
    print(c3Handle)
    frameHandle = win32gui.FindWindowEx(ieHandle, c1Handle, "MozillaWindowClass", None)
    print(frameHandle)
    tabHandle = win32gui.FindWindowEx(frameHandle, 0, "GeckoPluginWindow", None)
    print(tabHandle)
    editHandle  = win32gui.FindWindowEx(tabHandle, 0, None, 'Alipay Security Edit control')
    print(editHandle)
    win32gui.SetForegroundWindow(editHandle)
    #pwd = "test"
    for i in range(len(pwd)):
        win32gui.SendMessage(editHandle, 0x102, ord(pwd[i]), 0)
        time.sleep(1)

def getCaptchaResult():
    from ctypes import *
    import sys
    import os
    import hashlib
    import httplib
    import urllib
    import string
    import zlib
    import binascii
    import range
    UUDLL=os.path.join(os.path.dirname(__file__), 'UUWiseHelper_x64.dll')                   #当前目录下的优优API接口文件
    #此处指的当前脚本同目录中test_pics文件夹下面的test.jpg
    #可以修改成你想要的文件路径

    # 加载动态链接库, 需要放在System 的path里，或者当前目录下
    UU = windll.LoadLibrary(UUDLL)

    # 初始化函数调用
    setSoftInfo = UU.uu_setSoftInfoW
    login = UU.uu_loginW
    recognizeByCodeTypeAndPath = UU.uu_recognizeByCodeTypeAndPathW
    getResult = UU.uu_getResultW
    uploadFile = UU.uu_UploadFileW
    getScore = UU.uu_getScoreW
    checkAPi=UU.uu_CheckApiSignW	#api文件校验函数，调用后返回：MD5（软件ID+大写DLL校验KEY+大写随机值参数+优优API文件的MD5值+大写的优优API文件的CRC32值）

    setSoftInfo(c_int(100422), c_wchar_p("55aecfb860a64354b4957f97ea81df83"))

    user = c_wchar_p("zhangda733")  # 授权用户名
    passwd = c_wchar_p("Uutest123")  # 授权密码

    ret = login(user, passwd)		                #用户登录，仅需要调用一次即可，不需要每次上传图片都调用一次，特殊情况除外，比如当成脚本执行的话

    if ret > 0:
        print('login ok, user_id:%d' % ret)                 #登录成功返回用户ID
    else:
        print('login error,errorCode:%d' %ret )
        sys.exit(0)

    ret = getScore(user, passwd)                            #获取用户当前剩余积分
    print('The Score of User : %s  is :%d' % (user.value, ret))

    '''result=c_wchar_p("                                              ")	#分配内存空间，避免内存泄露
    code_id = recognizeByCodeTypeAndPath(c_wchar_p("1.jpg"),c_int(2002),result)
    if code_id <= 0:
        print('get result error ,ErrorCode: %d' % code_id)
    else:
        checkedRes=checkResult(result.value, s_id, softVerifyKey, code_id);
        print("the resultID is :%d result is %s" % (code_id,checkedRes[1]))  #识别结果为宽字符类型 c_wchar_p,运用的时候注意转换一下
        return checkedRes[1]
    '''
def login():
    driver = webdriver.Firefox()
    driver.get("https://login.taobao.com/member/login.jhtml?style=alipay&goto=https%3A%2F%2Flab.alipay.com%3A443%2Fuser%2Fnavigate.htm%3Fsign_from%3D3000")
    username = driver.find_element_by_id("TPL_username_1")
    username.clear()
    username.send_keys(u"吴富清")
    try:
        if driver.find_element_by_id("J_SafeLoginCheck").is_selected():
            driver.find_element_by_id("J_SafeLoginCheck").click()
    except:
        #如果没找到安全控件的复选框，那就pass
        pass
    pwd = driver.find_element_by_id("TPL_password_1")
    pwd.clear()
    pwd.send_keys("zy666566")
    driver.find_element_by_id("J_SubmitStatic").click()
    
if __name__ == "__main__":
    login()
    '''#inputPwdFirefox('test1')
    import os
    #iedriver = "C:\Program Files\Internet Explorer\IEDriverServer.exe"
    #os.environ["webdriver.ie.driver"] = iedriver
    #driver = webdriver.Ie(iedriver)
    driver = webdriver.Firefox()
    driver.get("https://www.alipay.com/")
    print(driver.page_source)
    #print(driver.window_handles)
    #driver.switch_to_window(driver.window_handles[0])
    #time.sleep(30)
    
    inputs = driver.find_elements_by_tag_name('input')
    print(inputs)
    inputs = driver.find_elements_by_tag_name('div')
    print(inputs)
    elem = driver.find_element_by_id("TPL_username_1")
    elem.clear()
    elem.send_keys("er6e@qq.com")
    #inputPwdIE('zhangyang')
    #getCaptchaResult()
    driver.save_screenshot('screenshot.png')'''
