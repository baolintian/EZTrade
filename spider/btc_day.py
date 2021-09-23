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


url_day = "https://api.huobi.pro/market/history/kline?period=1day&size=2000&symbol=btcusdt"

oid_day = 'C3E350DCE0CB314EA1564AE02CAC0089'

payload={}
headers = {}


response1 = requests.request("GET", url_day, headers=headers, data=payload)
res1 = json.loads(response1.text)
market_json = res1["data"]

print(market_json)

market = []

for i in range(len(market_json)):
    unix_t = market_json[i]["id"]
    unix_t = local_time(unix_t)
    open = market_json[i]["open"]
    close = market_json[i]["close"]
    low = market_json[i]["low"]
    high = market_json[i]["high"]
    amount = market_json[i]["amount"]
    now = []
    now.append(unix_t)
    now.append(open)
    now.append(close)
    now.append(low)
    now.append(high)
    now.append(amount)
    market.append(now)

market.reverse()
obj = {
    "oid": oid_day,
    "coinMarket": json.dumps(market)
}
edit_obj("CoinInfo", obj)
