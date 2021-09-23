
import requests
import json
import time
import xmltodict
import os

import sys
import argparse
import signal
import datetime
from collections import deque


def get_token():
    url = "http://i-2o0wkhxv.cloud.nelbds.org.cn:8180/api/app//dwf/v1/app/login?password=31c15919&userName=admin"

    payload = {}
    headers = {
        'accept': '*/*',
        'Authorization': 'eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTYyNTY3NTgyNH0.LkYBQnKfeDoEYJAMs4HOZae_Gq9nyu8kqOVP3T_qkkdmHb9pgRJbw4dlbxjEO69tFh7NQ3-vT-EHLTYo6b8Nyw'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    return json.loads(response.text)["data"]

def get_info(class_name, condition):
    url = "http://i-2o0wkhxv.cloud.nelbds.org.cn:8180/api/app//dwf/v1/omf/entities/"+class_name+"/objects"
    payload = json.dumps({
        "condition": condition,
        "pageSize": 100,
        "startIndex": 0
    })
    token = get_token()
    headers = {
        'accept': '*/*',
        'Authorization': token,
        'Content-Type': 'application/json',
        'Cookie': 'JSESSIONID=8BC976CB994C3656F9AE0E913A2521C9'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    response = json.loads(response.text)
    return response["data"]


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

def create_obj(class_name, message):
    url = "http://i-2o0wkhxv.cloud.nelbds.org.cn:8180/api/app//dwf/v1/omf/entities/"+class_name+"/objects-create"

    payload = json.dumps([
        message
    ])
    token = get_token()
    headers = {
        'accept': '*/*',
        'Authorization': token,
        'Content-Type': 'application/json',
        'Cookie': 'JSESSIONID=8BC976CB994C3656F9AE0E913A2521C9'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        return True
    else:
        return False

def delete_by_oid(class_name, oid):
    url = "http://i-2o0wkhxv.cloud.nelbds.org.cn:8180/api/app//dwf/v1/omf/entities/"+class_name+"/objects-delete"

    payload = json.dumps([
        oid
    ])
    token = get_token()
    headers = {
        'accept': '*/*',
        'Authorization': token,
        'Content-Type': 'application/json',
        'Cookie': 'JSESSIONID=8BC976CB994C3656F9AE0E913A2521C9'
    }

    response = requests.request("POST", url, headers=headers, data=payload)


def load_json(xml_path):
    xml_file = open(xml_path, "r")
    xml_str = xml_file.read()
    json = xmltodict.parse(xml_str)
    return json

def log(message):
    log_message["message"].append(message)
    obj = {
        "oid": taskOid,
        "virFirmLog": json.dumps(log_message)
    }
    edit_obj("VirFirmApp", obj)


def lock_account():
    obj = {
        "oid": userOid,
        "isTransaction": "是"
    }
    edit_obj("VirtualAccount", obj)


def unlock_account():
    obj = {
        "oid": userOid,
        "isTransaction": "否"
    }
    edit_obj("VirtualAccount", obj)


def buy(coin_name, price, amount):
    user_info = get_info("VirtualAccount", "and obj.oid=" + "'" + userOid + "'")[0]
    if(price*amount*(1+0.001)>user_info["usableAsset"] or user_info["usableAsset"] <= 0):
        log("委托【买】可用资金不足， "+coin_name+"价格： "+str(price)+", "+"数量： "+str(amount))

    # 检测账户是否上锁，从而进行交易
    if(("isTransaction" in user_info.keys()) and user_info["isTransaction"] == "是"):
        log("委托【买】无法进行，账户正在进行委托交易")

    # 上锁交易
    lock_account()
    user_info = get_info("VirtualAccount", "and obj.oid=" + "'" + userOid + "'")[0]
    usableAsset = user_info["usableAsset"]
    frozenAsset = user_info["frozenAsset"]
    usableAsset -= price*amount*(1+0.001)
    frozenAsset += price*amount*(1+0.001)

    obj = {
        "oid": userOid,
        "usableAsset": usableAsset,
        "frozenAsset": frozenAsset
    }
    edit_obj("VirtualAccount", obj)
    obj = {
        "delegatorOID": userOid,
        "delegateCoinName": coin_type,
        "delegatePrice": price,
        "delegateAmount": amount,
        "delegateAction": "BUY",
        "delegateType": "AUTO BUY",
        "delegateAppOID": taskOid
    }
    create_obj("DelegateInfo", obj)
    unlock_account()


def sell(coin_name, price, amount):
    hold_info = get_info("SingleCoinInfo", "and obj.coinHolderOID="+"'"+userOid+"'"+" and obj.coinName="+"'"+coin_type+"'")
    if(len(hold_info) == 0):
        log("委托【卖】"+coin_name+"无持仓")
        return
    if(len(hold_info)):
        hold_info = hold_info[0]

    if (amount > hold_info["coinUsableAmount"]):
        log("委托【卖】可用数量不足， " + coin_name + "价格： " + str(price) + ", " + "数量： " + str(amount))

    # 检测账户是否上锁，从而进行交易
    user_info = get_info("VirtualAccount", "and obj.oid=" + "'" + userOid + "'")[0]
    if (("isTransaction" in user_info.keys()) and user_info["isTransaction"] == "是"):
        log("委托【卖】无法进行，账户正在进行委托交易")

    # 上锁交易
    lock_account()

    hold_info = get_info("SingleCoinInfo",
                         "and obj.coinHolderOID=" + "'" + userOid + "'" + " and obj.coinName=" + "'" + coin_type + "'")[0]
    coinUsableAmount = hold_info["coinUsableAmount"]-amount
    print(coinUsableAmount)
    coinUsableAmount = ('%.8f' % coinUsableAmount)
    hold_info_oid = hold_info["oid"]
    print(hold_info_oid)

    obj = {
        "oid": hold_info_oid,
        "coinUsableAmount": coinUsableAmount
    }
    edit_obj("SingleCoinInfo", obj)
    obj = {
        "delegatorOID": userOid,
        "delegateCoinName": coin_type,
        "delegatePrice": price,
        "delegateAmount": amount,
        "delegateAction": "SELL",
        "delegateType": "AUTO SELL",
        "delegateAppOID": taskOid
    }
    create_obj("DelegateInfo", obj)
    unlock_account()


def retreate():
    delegate_info = get_info("DelegateInfo",
                         "and obj.delegatorOID=" + "'" + userOid + "'" + " and obj.delegateAppOID=" + "'" + taskOid + "'")
    if(len(delegate_info)<=0):
        return
    lock_account()

    for single_delegate in delegate_info:
        if single_delegate["delegateAction"] == "BUY":
            price = single_delegate["delegatePrice"]
            amount = single_delegate["delegateAmount"]

            user_info = get_info("VirtualAccount", "and obj.oid=" + "'" + userOid + "'")[0]
            usableAsset = user_info["usableAsset"]
            frozenAsset = user_info["frozenAsset"]
            usableAsset += price * amount * (1 + 0.001)
            frozenAsset -= price * amount * (1 + 0.001)
            obj = {
                "oid": userOid,
                "usableAsset": usableAsset,
                "frozenAsset": frozenAsset
            }
            edit_obj("VirtualAccount", obj)

            obj = {
                "transactionPersonOID": userOid,
                "transactionCoinName": coin_type,
                "transactionAmount": amount,
                "transactionAction": "AUTO RETREATE BUY",
                "transactionPrice": price
            }
            create_obj("TransactionHistory", obj)

            delete_by_oid("DelegateInfo", single_delegate["oid"])
            log("撤销【买】"+coin_type+", 价格"+str(price)+", 数量"+str(amount))

        elif single_delegate["delegateAction"] == "SELL":

            price = single_delegate["delegatePrice"]
            amount = single_delegate["delegateAmount"]
            hold_info = get_info("SingleCoinInfo",
                                 "and obj.coinHolderOID=" + "'" + userOid + "'" + " and obj.coinName=" + "'" + coin_type + "'")[
                0]
            coinUsableAmount = hold_info["coinUsableAmount"] + amount
            hold_info_oid = hold_info["oid"]
            obj = {
                "oid": hold_info_oid,
                "coinUsableAmount": coinUsableAmount
            }
            edit_obj("SingleCoinInfo", obj)
            obj = {
                "transactionPersonOID": userOid,
                "transactionCoinName": coin_name,
                "transactionAmount": amount,
                "transactionAction": "AUTO RETREATE SELL",
                "transactionPrice": price
            }
            create_obj("TransactionHistory", obj)

            delete_by_oid("DelegateInfo", single_delegate["oid"])
            log("撤销【卖】" + coin_type + ", 价格" + str(price) + ", 数量" + str(amount))


    unlock_account()


# def onTick(coin_info, user_info, hold_info):
#     retreate()
#     pass

phase = 0
def onTick(coin_info, user_info, hold_info):
    global phase
    coin_name = list(coin_info.keys())[0]
    price = coin_info[coin_name]
    if phase == 0:
        buy(coin_name, price+0.2, 0.01)
        phase = phase+1
    elif phase == 1:
        buy(coin_name, price-20, 0.01)
        phase = phase+1
    elif phase == 2:
        retreate()
        phase = phase+1
    elif phase == 3:
        sell(coin_name, price+20, 0.01)
        phase = phase+1
    elif phase == 4:
        retreate()
        phase = phase + 1
    else:
        buy(coin_name, price+1, 0.01)

def sigintHandler(signum, frame):
    print("中断发生。")
    global taskOid
    obj = {
        "oid": str(taskOid),
        "virRunEndTime": str(int(time.mktime(datetime.datetime.now().timetuple()))*1000),
        "virFirmStatus": "手动结束"
    }
    edit_obj("VirFirmApp", obj)
    print("执行最后的清理工作。")
    exit()



taskOid = 0
if __name__ == "__main__":


    parser = argparse.ArgumentParser(description='Test process.')
    if len(sys.argv) > 1:
        defaultPath = sys.argv[1]
    parser.add_argument('-i', '--in', metavar='param_file', dest='param_file', help='Parameter file',
                            default=defaultPath)

    args = parser.parse_args()
    xml_path = args.param_file


    json_content = load_json(xml_path)
    taskOid = json_content["parameters"]["param"][0]["#text"]
    userOid = json_content["parameters"]["param"][1]["#text"]
    coin_type = json_content["parameters"]["param"][2]["#text"]
    signal.signal(signal.SIGINT, sigintHandler)  # 由Interrupt Key产生，通常是CTRL+C或者DELETE产生的中断
    signal.signal(signal.SIGHUP, sigintHandler)  # 发送给具有Terminal的Controlling Process，当terminal 被disconnect时候发送
    signal.signal(signal.SIGTERM, sigintHandler)  # 请求中止进程，kill命令缺省发送 不要强制杀死


    log_message = {}
    log_message["message"] = []

    pid = os.getpid()
    print(pid)
    obj = {
        "oid": str(taskOid),
        "virFirmPid": str(pid),
        "virFirmStatus": "开始工作",
        "virRunStartTime": str(int(int(time.mktime(datetime.datetime.now().timetuple()))*1000))
    }
    edit_obj("VirFirmApp", obj)

    raw_asset = -1
    time_series = []
    price = []
    ratio = []
    tot_asset = []
    # 保存三个月的数据
    max_length = 24*60*31*3
    update_interval = 60


    prev = datetime.datetime.now()

    max_retreate = 0
    mx = -1
    after_max_min = 1e9

    while True:
        # TODO 消去所有上次未成交的订单

        # 获取想要的币种信息
        print("in loop")
        coin_info = get_info("CoinInfo", "and obj.coinName="+"'"+coin_type+"'")
        coin_dict = {}

        for i in range(len(coin_info)):
            coin_name = coin_info[i]["coinName"]
            coin_price = coin_info[i]["coinPrice"]
            coin_dict[coin_name] = coin_price

        print(coin_dict)
        user_info = get_info("VirtualAccount", "and obj.oid="+"'"+userOid+"'")[0]
        if raw_asset < 0:
            raw_asset = user_info["asset"]

        hold_info = get_info("SingleCoinInfo", "and obj.coinHolderOID="+"'"+userOid+"'"+" and obj.coinName="+"'"+coin_type+"'")
        if(len(hold_info)>0):
            hold_info = hold_info[0]

        print(user_info)
        print(hold_info)
        account_info = {
            "usableAsset": user_info["usableAsset"]
        }
        if(len(hold_info)):
            hold_info = {
                "coinUsableAmount": hold_info["coinUsableAmount"]
            }
        else:
            hold_info = {
                "coinUsableAmount": 0
            }


        # 当前价格，收益率，
        # 总资产
        # 目前收益


        onTick(coin_dict, account_info, hold_info)
        now = datetime.datetime.now()
        # 分钟级别的更新
        if int(time.mktime(now.timetuple())) - int(time.mktime(prev.timetuple())) >= 60:
            prev = now




            if len(time_series) > max_length:
                time_series.pop(0)
                tot_asset.pop(0)
                price.pop(0)
                ratio.pop(0)


            time_string = str(datetime.datetime.now().year)+"/"+str(datetime.datetime.now().month)+"/"+str(datetime.datetime.now().day)+" "+str(datetime.datetime.now().hour)+":"+str(datetime.datetime.now().minute)
            time_series.append(time_string)
            tot_asset.append(user_info["asset"])
            price.append(coin_price)
            ratio.append((user_info["asset"]-raw_asset)/raw_asset*100)
            if mx < -1:
                mx = user_info["asset"]
                after_max_min = user_info["asset"]
            if mx <= user_info["asset"]:
                mx = user_info["asset"]
                after_max_min = 1e9
            else:
                after_max_min = min(after_max_min, user_info["asset"])
                max_retreate = max(max_retreate, (mx-after_max_min)/mx*100)
            # 待增加【买】，【卖】操作数量的统计
            res = {
                "time_stamp": time_series,
                "price": price,
                "tot_asset": tot_asset,
                "ratio": ratio,
                "now_gain": ((user_info["asset"]-raw_asset)/raw_asset*100),
                "retreate": max_retreate
            }
            obj = {
                "oid": str(taskOid),
                "virFirmResultString": json.dumps(res)
            }
            edit_obj("VirFirmApp", obj)

        time.sleep(10)
