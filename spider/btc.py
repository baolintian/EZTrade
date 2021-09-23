import requests

import datetime
import time
import json

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

def local_time(timestamp):
    # 转换成localtime
    time_local = time.localtime(timestamp)
    # 转换成新的时间格式(2016-05-05 20:28:54)
    dt = time.strftime("%Y-%m-%d", time_local)
    return dt



url = "https://api.huobi.pro/market/trade?symbol=btcusdt"

url_day = "https://api.huobi.pro/market/history/kline?period=1day&size=2000&symbol=btcusdt"

url_1min = "https://api.huobi.pro/market/history/kline?period=1min&size=1&symbol=btcusdt"
url_1day = "https://api.huobi.pro/market/history/kline?period=1day&size=1&symbol=btcusdt"


oid = '7E56328CE0012540B21DD363616131B7'

oid_day = 'C3E350DCE0CB314EA1564AE02CAC0089'

oid_10s = 'C3E350DCE0CB314EA1564AE02CAC0089'

payload={}
headers = {}

prev_second = datetime.datetime.now()
prev_10s = datetime.datetime.now()

monitor = datetime.datetime.now()

flag_day = -1
day = datetime.datetime.now()

time_stamp = []
price = []
amount = []
window_size = 60*60


while True:


    now = datetime.datetime.now()
    if int(time.mktime(now.timetuple())) - int(time.mktime(prev_second.timetuple())) >= 1:
        prev_second = now
        response = requests.request("GET", url, headers=headers, data=payload)

        json_content = json.loads(response.text)
        price_now = json_content["tick"]["data"][0]["price"]
        amount_now = json_content["tick"]["data"][0]["amount"]
        if len(time_stamp) > 3600:
            time_stamp.pop(0)
            price.pop(0)
            amount.pop(0)

        time_string = "{:0>2d}".format(int(datetime.datetime.now().hour)) + ":" + "{:0>2d}".format(int(datetime.datetime.now().minute))+":"+"{:0>2d}".format(int(datetime.datetime.now().second))
        time_stamp.append(time_string)
        price.append(price_now)
        amount.append(amount_now)
        res = {
            "time": time_stamp,
            "price": price,
            "amount": amount
        }
        obj = {
            "oid": oid,
            "attribution": json.dumps(res)
        }
        edit_obj("MarketInfo", obj)

    # 更新检测日志
    if int(time.mktime(now.timetuple())) - int(time.mktime(monitor.timetuple())) >= 60:
        monitor = now
        print(now)

    # 更新日线
    if int(time.mktime(now.timetuple())) - int(time.mktime(day.timetuple())) >= 60*60*24 or flag_day < 0:
        day = now
        flag_day = 1
        response1 = requests.request("GET", url_day, headers=headers, data=payload)
        res1 = json.loads(response1.text)
        market_json = res1["data"]
        market = []

        for i in range(len(market_json)):
            unix_t = market_json[i]["id"]
            unix_t = local_time(unix_t)
            open1 = market_json[i]["open"]
            close1 = market_json[i]["close"]
            low1 = market_json[i]["low"]
            high1 = market_json[i]["high"]
            amount1 = market_json[i]["amount"]
            now1 = []
            now1.append(unix_t)
            now1.append(open1)
            now1.append(close1)
            now1.append(low1)
            now1.append(high1)
            now1.append(amount1)
            market.append(now1)

        market.reverse()
        obj = {
            "oid": oid_day,
            "coinMarket": json.dumps(market)
        }
        edit_obj("CoinInfo", obj)

    # 更新表格行情
    if int(time.mktime(now.timetuple())) - int(time.mktime(prev_10s.timetuple())) >= 10:
        prev_10s = now
        response1 = requests.request("GET", url_1min, headers=headers, data=payload)
        response2 = requests.request("GET", url_1day, headers=headers, data=payload)
        res1 = json.loads(response1.text)
        res1 = (res1["data"][0]["low"]+res1["data"][0]["high"])/2
        res2 = json.loads(response2.text)["data"][0]["open"]
        ratio = (res1-res2)/res2*100
        obj = {
            "oid": oid_10s,
            "coinPrice": '%.2f' % res1,
            "ratio": '%.2f' % ratio
        }
        print(obj)
        edit_obj("CoinInfo", obj)

    time.sleep(0.2)




