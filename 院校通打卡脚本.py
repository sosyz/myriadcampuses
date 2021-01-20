import requests
import configparser
import json
import time

#以下三个自己填
phone = '' #手机号
password = ''#密码
lifeInfo = ["内蒙古", "呼和浩特市", "玉泉区"]#所在地点



#SCKEY从http://sc.ftqq.com/ 获取
#只是用来微信通知执行情况 非必须
SCKEY = ''

#open('log.txt', 'a')
logFile = ''
def log(context):
    global logFile
    data = "[" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "] ==> " + str(context)
    print(data)
    logFile += data + "<br>"

def getPlaceId(check, name, pid):
    if check == 0:
        url = 'http://ci.scwqsm.com/areaData/getProvinces'
    elif check > 0:
        url = 'http://ci.scwqsm.com/areaData/getAreaByPID?id=' + str(pid)
    re = json.loads(requests.get(url).text)['data']
    for info in range(len(re)):
        if name == re[info]['areaName']:
            return (re[info]['areaId'], info)
    log("error, can't find " + name + " in " + str(re))
    return 0

def login(user, pw):
    url = 'http://ci.wq.com/login'
    postData = '{"mobile":"'+ user + '","pwd":"' + pw + '","type":"4"}'
    datalen = len(postData)
    headers = {
        'x-registration-id': '1507bfd3f766300e63b',
        'x-client-systemVersion': '30',
        'x-client-system': 'Android',
        'x-client-appVersion': '44',
        'x-device-code': '3eded90e9ebaf750',
        'x-client-appName': '2.2.8',
        'x-user-token': '',
        'user_type': '4',
        'Content-Type': 'application/json; charset=UTF-8',
        'Content-Length': str(datalen),
        'Host': 'ci.wq.com',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
        'User-Agent': 'okhttp/4.7.2'
    }
    r = requests.post(url, data=postData, headers=headers)
    token = json.loads(r.text)
    return token

def getUserInfo(token):
    url = 'http://ci.scwqsm.com/yqHealthData/initYqHealthAllData'
    headers = {
        'x-user-token': token,
        'content-type': 'application/json',
        'Accept-Charset': 'UTF-8',
        'referer': 'http://ci.scwqsm.com/1234567891234567/0.0.14.0/yqHealthData/initYqHealthAllData',
        'Content-Length': '0',
        'Connection': 'Keep-Alive',
        'User-Agent': 'Mozilla/5.0 (Linux; U; Android 11; zh-CN; BRQ-AN00 Build/RKQ1.200826.002) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/69.0.3497.100 UWS/3.21.0.174 Mobile Safari/537.36 UCBS/3.21.0.174_200825145737 ChannelId(1) NebulaSDK/1.8.100112 Nebula AlipayDefined(nt:WIFI,ws:393|0|2.75,ac:sp)  useStatusBar/true isConcaveScreen/false mPaaSClient'
    }
    r = requests.post(url, data='', headers=headers)
    return r.text

def sendHealthData(token):
    info = json.loads(getUserInfo(token))['data']['yqHealthData']
    global lifeInfo

    cid = [0, 0, 0]
    sid = ['', '', '']
    tid = 0
    for i in range(len(lifeInfo)):
        idInfo = getPlaceId(i, lifeInfo[i], tid)
        tid = idInfo[0]
        cid[i] = idInfo[0]
        sid[i] = str(idInfo[1])

    sid[0] = str(int(sid[0]) + 1)
    data = {
        "provinceId": cid[0], #
        "cityId": cid[1],#
        "areaId": cid[2],#
        "isCase": "0",#
        "isContact": "0",#是否接触
        "name": info['name'],
        "mobile": info['mobile'],
        "idCard": info['idCard'],
        "symptomDetail": '',#症状详细信息
        "temperature": "36.5",
        "isCheck": 1,#应该是是否负责
        "isClock": "0",
        "memberId": info['memberId'],
        "userId": info['userId'],
        "userType": info['userType'],
        "officeId": info['officeId'],
        "provinceName": lifeInfo[0],#省
        "cityName": lifeInfo[1],#市
        "areaName": lifeInfo[2],#区
        "symptom": "0",#症状
        "address": ",".join(sid),#选择位置的索引
        "currentSataus": 3#现在状况
    }
    url = 'http://ci.scwqsm.com/yqHealthData/saveYqHealthAllData'
    headers = {
        'x-user-token': token,
        'content-type': 'application/json',
        'Accept-Charset': 'UTF-8',
        'referer': 'http://ci.scwqsm.com/1234567891234567/0.0.14.0/yqHealthData/saveYqHealthAllData',
        'Content-Length': str(len(data)),
        'Connection': 'Keep-Alive',
        'User-Agent': 'Mozilla/5.0 (Linux; U; Android 11; zh-CN; BRQ-AN00 Build/RKQ1.200826.002) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/69.0.3497.100 UWS/3.21.0.174 Mobile Safari/537.36 UCBS/3.21.0.174_200825145737 ChannelId(1) NebulaSDK/1.8.100112 Nebula AlipayDefined(nt:WIFI,ws:393|0|2.75,ac:sp)  useStatusBar/true isConcaveScreen/false mPaaSClient'
    }
    log("postData: " + json.dumps(data))
    return requests.post(url, data=json.dumps(data), headers=headers).text

def getTokenState(token):
    state = json.loads(getUserInfo(token))['code']
    if state == '000002':
        log("token can't login")
        return False
    elif state == '000000':
        log("token can login")
        return True
    elif state == '000012':
        log("token is expired")
        return False
    log("unknow error: " + getUserInfo(token))
    return False
def sendWechatMsg(title, context):
    global SCKEY
    if SCKEY != '':
        url = 'https://sc.ftqq.com/' + SCKEY + '.send'
        datas = {
            'text': title,
            'desp': context
        }
        requests.packages.urllib3.disable_warnings()
        requests.post(url, data=datas, headers='', verify=False)

try:
    #read config
    conf = configparser.ConfigParser()
    conf.read('conf.ini')
    if (conf.sections() == []):
        conf.add_section("data")
        conf['data']['token'] = ""
        with open('conf.ini', 'w+') as f:
            conf.write(f)
            f.close()

    token = conf['data']['token']

    #get token state
    if token == "" or getTokenState(token) == False:
        log("try login")
        token = login(phone, password)
        print(token)
        if token['data']['token'] == "":
            log("error, reponseText: " + r)
        token = token['data']['token']
        conf['data']['token'] = token
        with open('conf.ini', 'w') as f:
            conf.write(f)
            f.close()

    #send data
    log("Send Health Data")
    log("Response Data: " + sendHealthData(token))
    sendWechatMsg('Save healthData Result', logFile)
    fo = open(time.strftime("%Y-%m-%d %H_%M_%S", time.localtime()) + ".log", "w+")
    fo.write(logFile.replace("<br>", "\n"))
    fo.close()
except Exception as e:
    sendWechatMsg('Run Error', e)