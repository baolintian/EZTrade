
import pandas as pd
import matplotlib.pyplot as plt
from math import *
import xmltodict
import os
import json
import requests
import datetime
import time
import sys
import argparse
import signal


from algorithm import *
# url = i-2o0wkhxv.cloud.nelbds.org.cn

def get_token():
    url = "http://i-2o0wkhxv.cloud.nelbds.org.cn:8180/api/app//dwf/v1/app/login?password=31c15919&userName=admin"

    payload = {}
    headers = {
        'accept': '*/*',
        'Authorization': 'eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTYyNTY3NTgyNH0.LkYBQnKfeDoEYJAMs4HOZae_Gq9nyu8kqOVP3T_qkkdmHb9pgRJbw4dlbxjEO69tFh7NQ3-vT-EHLTYo6b8Nyw'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    return json.loads(response.text)["data"]

def edit_obj(class_name, obj):
    url = "http://i-2o0wkhxv.cloud.nelbds.org.cn:8180/api/app//dwf/v1/omf/entities/"+class_name+"/objects-update?forceUpdate=false"

    payload = json.dumps([
        obj
    ])
    token = get_token()
    headers = {
        'accept': '*/*',
        'Authorization': token,
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return response.text

def load_json(xml_path):
    xml_file = open(xml_path, "r")
    xml_str = xml_file.read()
    json = xmltodict.parse(xml_str)
    return json

def sigintHandler(signum, frame):
    print("中断发生。")
    obj = {
        "oid": str(oid),
        "backtestRunEndTime": str(int(time.mktime(datetime.datetime.now().timetuple()))*1000),
        "backtestStatus": "手动结束"
    }
    edit_obj("BacktestApp", obj)
    print("执行最后的清理工作。")
    exit()



# csv=pd.read_csv('/workspace/Bitstamp_BTCUSD_2021_minute.csv', sep=',')




signal.signal(signal.SIGINT, sigintHandler)  # 由Interrupt Key产生，通常是CTRL+C或者DELETE产生的中断
signal.signal(signal.SIGHUP, sigintHandler)  # 发送给具有Terminal的Controlling Process，当terminal 被disconnect时候发送
signal.signal(signal.SIGTERM, sigintHandler)  # 请求中止进程，kill命令缺省发送 不要强制杀死


parser = argparse.ArgumentParser(description='Test process.')
if len(sys.argv) > 1:
    defaultPath = sys.argv[1]
parser.add_argument('-i', '--in', metavar='param_file', dest='param_file', help='Parameter file',
                        default=defaultPath)

args = parser.parse_args()
xml_path = args.param_file
json_content = load_json(xml_path)
oid = json_content["parameters"]["param"][0]["#text"]

segment_start = json_content["parameters"]["param"][1]["#text"]
temp = datetime.datetime.fromtimestamp(eval(segment_start)/1000)

if temp.month < 10:
    month = '0'+str(temp.month)
else:
    month = str(temp.month)
if temp.day < 10:
    day = '0'+str(temp.day)
else:
    day = str(temp.day)

start = str(temp.year)+"-"+\
        month+"-"+\
        day
segment_end = json_content["parameters"]["param"][2]["#text"]

# 更新进程号
pid = os.getpid()
print("进程号：", pid)

obj = {
    "oid": str(oid),
    "backtestPid": str(pid),
    "backtestStatus": "回测开始"
}
res = edit_obj("BacktestApp", obj)

# filename = '/test_text.txt'
# with open(filename, 'w') as file_object:
#     file_object.write(res)


# kill test
# time.sleep(10000)

temp = datetime.datetime.fromtimestamp(eval(segment_end)/1000)
if temp.month < 10:
    month = '0'+str(temp.month)
else:
    month = str(temp.month)
if temp.day < 10:
    day = '0'+str(temp.day)
else:
    day = str(temp.day)

end = str(temp.year)+"-"+\
        month+"-"+\
        day

print(start)
print(end)


from iotdb.Session import Session
ip = "127.0.0.1"
port_ = "6667"
username_ = "root"
password_ = "root"
session = Session(ip, port_, username_, password_, fetch_size=1024, zone_id="UTC+8")
session.open(False)



iotdb_path = "root.btc"
print("select * from "+iotdb_path+" where Time >= "+start+" and Time <= "+end+";")
result = session.execute_query_statement(
            "select * from "+iotdb_path+" where Time >= "+start+" and Time <= "+end+";")
df = result.todf()
session.close()
temp = df.loc[:, [iotdb_path+".open"]].values
temp1 = df.loc[:, ["Time"]].values
data = []
time_stamp = []
for i in range(len(temp)):
    data.append(temp[i][0])
    dd = datetime.datetime.fromtimestamp(temp1[i][0]/1000)
    time_stamp.append(str(dd.year)+"/"+"{:0>2d}".format(dd.month)+"/"+"{:0>2d}".format(dd.day)+" "+"{:0>2d}".format(dd.hour)+":"+"{:0>2d}".format(dd.minute))

price = []
result = {}
raw_asset = -1
ratio = []
print(time_stamp[0])
for i in range(len(data)):

    acc = {
        "money": PARAMS['account_initial']['huobi_cny_cash'],
        "coin": PARAMS['account_initial']['huobi_cny_btc'],
    }
    stock = {
        "sell": data[i],
    }

    onTick(acc, stock)
    price.append(PARAMS['account_initial']['huobi_cny_cash']+PARAMS['account_initial']['huobi_cny_btc']*data[i])
    if raw_asset < 0:
        raw_asset = price[0]
    ratio.append((price[len(price)-1]-raw_asset)/raw_asset*100)
    obj = {
        "oid": oid,
        "backtestProcess": (i+1)/len(data)*100
    }
    edit_obj("BacktestApp", obj)

data_point_number = 200

max_retreate = 0
mx = -1
after_mx_min = 1e9

for i in range(len(price)):
    if(mx < 0):
        mx = price[i]
        after_mx_min = price[i]
    if mx < price[i]:
        mx = price[i]
        after_mx_min = 1e9
    else:
        after_mx_min = min(after_mx_min, price[i])
        max_retreate = max(max_retreate, (mx-after_mx_min)/mx*100)




if(len(time_stamp)>data_point_number):
    interval = len(time_stamp)//data_point_number
    time_stamp1 = []
    data1 = []
    price1 = []
    ratio1 = []
    for i in range(0, len(time_stamp), interval):
        time_stamp1.append(time_stamp[i])
        data1.append(data[i])
        price1.append(price[i])
        ratio1.append(ratio[i])

    if len(time_stamp1)%data_point_number != data_point_number-1:
        time_stamp1.append(time_stamp[len(time_stamp)-1])
        data1.append(data[len(data) - 1])
        price1.append(price[len(price) - 1])
        ratio1.append(ratio[len(ratio) - 1])

result = {
    "time_stamp": time_stamp1,
    "price": data1,
    "tot_asset": price1,
    "ratio": ratio1,
    "now_gain": ((price1[len(price1)-1]-raw_asset)/raw_asset*100),
    "retreate": max_retreate
}
obj = {
    "oid": str(oid),
    "backtestResultString": json.dumps(result),
    "backtestRunEndTime": str(int(int(time.mktime(datetime.datetime.now().timetuple()))*1000)),
    "backtestStatus": "回测完成"
}
edit_obj("BacktestApp", obj)

