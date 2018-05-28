# -*- coding: UTF-8 -*-
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time
from Queue import Queue
import db, model, config
import threading, sys
import aliparser
import MySQLdb, config
import LOG
from Queue import Empty
import traceback
import config, memcache
#import chardet

'''
存储交易信息的队列
里面的结构就是Model.Trade
'''
queue = Queue()

mc = memcache.Client([config.memServer], debug=0)

class alipayDeamon(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def updateDB(self, userid, added):
        print("-------------")
        print("update DB")
        print("-------------")
        try:
            conn=MySQLdb.connect(host=config.host,user=config.user,passwd=config.passwd,db=config.db,port=config.port)
            cur=conn.cursor()
            cur.execute('update userinfo set leftCount=leftCount + %d where ID = %s' % (added, userid))
            if int(cur.rowcount) == 0:
                result="1001"
            else:
                result="ok"
            cur.close()
            conn.commit()
            conn.close()
            #add for memcached
            config.mc.incr(str(userid)+ config._LEFTCOUNT,delta=added)
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
        login(driver)
        time.sleep(10) #wait 10s for user input username and password
        refreshPage = "https://consumeprod.alipay.com/record/advanced.htm"
        while(True):
            #每次循环都刷新页面
            try:
                trade = queue.get(True, 60)
                if isLogout(driver):
                    login(driver)
                    continue
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
		if isLogout(driver):
                    login(driver)
                    continue
		pass
            except:
                driver.get(refreshPage)
		traceback.print_exc()
                print "Error occured:", sys.exc_info()
            
def test():
    #ali = alipayDeamon()
    #trade = model.record(14,"20140726000040011100420044226154",30,0, False, None)
    content = aliparser.readFile()
    ret = aliparser.myParser(content)
    print(ret)
    #ali.checkAndInsert(trade, content)

def updateDB2(userN, added):
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
    return result

def isLogout(driver):
    url = driver.current_url
    print("url :" + url)
    if url.find("record/advanced.htm") == -1:
        return True
    return False

def login(driver):
    #driver = webdriver.Firefox()
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
    #这里还需要再检测一下验证码
    #不过感觉如果登陆频率不高的话应该不用输入
    driver.find_element_by_id("J_SubmitStatic").click()
if __name__ == "__main__":
    login()
