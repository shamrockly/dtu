# -*- coding: utf-8 -*-

TRADESTR = "https://shenghuo.alipay.com/send/queryTransferDetail.htm?tradeNo="
MONEYSTR = "amount-pay-in"
TRADETYPE = "tradeNo ft-gray"
import codecs
def readFile():
    mystring = ""
    #f = open("context.html",'r', 'utf-8')
    f = codecs.open("context.html",'r', 'utf-8')
    ret = ""
    line = f.readline()
    while line:
        #print line,
        ret += line
        line = f.readline()
            #mylist = list(mystring)
            #mystring = "".join(line)

    f.close()
    #print ret
    return ret

'''
ugly parser here
因为只能取直接从支付宝转账的，所以很多交易要去掉的
去的金额后判断这里，如果只有交易号，则合法，如果还有订单号，那此金额不算
<td class="tradeNo ft-gray">
<p>订单号:1407809926834351457</p>
<p>交易号:2014081200001000750037588806</p>
</td>
'''
def myParser(content):
    begin = 0
    ret = []
    while(True):
        typeBegin = content.find(TRADETYPE, begin)
        #print("typeBegin:" + str(typeBegin))
        if typeBegin == -1:
            print(ret)
            return ret
        typeEnd = content.find("</td>", typeBegin)
        typeContent = content[typeBegin : typeEnd]
        #print(typeContent)
        if typeContent.find(u"订单号") != -1:
            #包含订单号，该项被过滤
            print(u"订单号")
            begin = typeBegin + typeContent.find(u"订单号") + 10
            typeContent = content[begin : typeEnd]
        #不包含订单号，这个是正确的
        #print("One Correct")
        #newC = typeContent.encode('gb18030')
        newC = typeContent
        numberBegin = newC.find(u":")
        numberEnd = newC.find("</p>", numberBegin)
        #numberEnd = numberBegin + 20
        
        number = newC[numberBegin + len(u":"): numberEnd]
        #print("number:" + str(number))
        #开始寻找money
        #重新赋值正确的number begin and end
        numberBegin = typeBegin
        numberEnd = typeBegin + len(typeContent)
        moneyBegin = content.find(MONEYSTR, numberBegin)
        moneyEnd = content.find("</span>", moneyBegin)
        
        #print("money:" + str(money))
        #距离太长就表明找到下一个订单的number去了，舍弃
        #print("numberEnd:" + str(numberEnd))
        #print("moneyEnd:" + str(moneyEnd))
        if (moneyEnd - numberEnd) > 800:
            begin = numberEnd + 10
            continue
        moneyContent = content[moneyBegin : moneyEnd]
        #newM = moneyContent.encode('gb18030')
        newM = moneyContent
        newB = newM.find(MONEYSTR)
        newE = newM.find("</span>", newB)
        money = newM[newB + len(MONEYSTR) + 3: newE]
        ret.append((number, money))
        begin = moneyEnd

def myParserNoDingDanHao(content):
    begin = 0
    ret = []
    while(True):
        typeBegin = content.find(TRADETYPE, begin)
        #print("typeBegin:" + str(typeBegin))
        if typeBegin == -1:
            print(ret)
            return ret
        typeEnd = content.find("</td>", typeBegin)
        typeContent = content[typeBegin : typeEnd]
        #print(typeContent)
        if typeContent.find(u"订单号") != -1:
            #包含订单号，该项被过滤
            begin = typeBegin + len(TRADETYPE)
            continue
        #不包含订单号，这个是正确的
        #print("One Correct")
        #newC = typeContent.encode('gb18030')
        newC = typeContent
        numberBegin = newC.find(u":")
        numberEnd = newC.find("</p>", numberBegin)
        #numberEnd = numberBegin + 20
        
        number = newC[numberBegin + len(u":"): numberEnd]
        #print("number:" + str(number))
        #开始寻找money
        #重新赋值正确的number begin and end
        numberBegin = typeBegin
        numberEnd = typeBegin + len(typeContent)
        moneyBegin = content.find(MONEYSTR, numberBegin)
        moneyEnd = content.find("</span>", moneyBegin)
        
        #print("money:" + str(money))
        #距离太长就表明找到下一个订单的number去了，舍弃
        #print("numberEnd:" + str(numberEnd))
        #print("moneyEnd:" + str(moneyEnd))
        if (moneyEnd - numberEnd) > 800:
            begin = numberEnd + 10
            continue
        moneyContent = content[moneyBegin : moneyEnd]
        #newM = moneyContent.encode('gb18030')
        newM = moneyContent
        newB = newM.find(MONEYSTR)
        newE = newM.find("</span>", newB)
        money = newM[newB + len(MONEYSTR) + 3: newE]
        ret.append((number, money))
        begin = moneyEnd

'''
获取下一页的link，如果有，返回字符串，如果没有，返回None
'''
def getNextPageLink(content):
    print(type(content))
    #content = content.encode('gb18030')
    nextExist = content.find(u"下一页")
    if nextExist == -1:
        return None
    nextBegin = content.rfind("href=\"", 0, nextExist)
    nextEnd = content.find("\">", nextBegin)
    #print(nextBegin)
    #print(nextEnd)
    link = content[nextBegin + len("href=\"") : nextEnd]
    print("Next Page : " + link)
    return link
    

#old parser
def myParser2(content):
    begin = 0
    ret = []
    while(True):
        begin2 = content.find(MONEYSTR, begin)
        
        end2 = content.find("</span>", begin2)
        money = content[begin2 + len(MONEYSTR) + 2 : end2]
        
        begin1 = content.find(TRADESTR, end2)
        #print("begin1:" + str(begin1))
        if begin1 == -1:
            #can not find any trade now
            return ret
        print(str(begin1) + "-" + str(end2))
        if (begin1 - end2) > 400:
            begin = end2 + 10
            continue
        end1 = content.find('"', begin1 + 10)
        #print("end1:" + str(end1))
        number = content[begin1 + len(TRADESTR):end1]
        #print("number:" + str(number))
        
        ret.append((number, money))
        begin = end2

s = u"中文"
print(s)
print(myParser(readFile()))
