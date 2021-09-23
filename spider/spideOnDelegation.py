import requests
import json
import time
import datetime

def get_token():
    url = "http://i-2o0wkhxv.cloud.nelbds.org.cn:8180/api/app//dwf/v1/app/login?password=31c15919&userName=admin"

    payload = {}
    headers = {
        'accept': '*/*',
        'Authorization': 'eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTYyNTY3NTgyNH0.LkYBQnKfeDoEYJAMs4HOZae_Gq9nyu8kqOVP3T_qkkdmHb9pgRJbw4dlbxjEO69tFh7NQ3-vT-EHLTYo6b8Nyw'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    return json.loads(response.text)["data"]


def get_delegation_info():
    url = "http://i-2o0wkhxv.cloud.nelbds.org.cn:8180/api/app//dwf/v1/omf/entities/DelegateInfo/objects"
    payload = json.dumps({
        "condition": "and 1=1",
        "pageSize": 10,
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
    return response

def get_coin_info(class_name, condition):
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
    return response

def delete_delegation_by_oid(class_name, oid):
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

    requests.request("POST", url, headers=headers, data=payload)

def create_transaction(class_name, message):
    import requests
    import json

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

def get_instance_by_oid(class_name, oid):
    import requests
    import json

    url = "http://i-2o0wkhxv.cloud.nelbds.org.cn:8180/api/app//dwf/v1/omf/entities/"+class_name+"/objects/oids"

    payload = json.dumps([
        oid
    ])
    token = get_token()
    headers = {
        'accept': '*/*',
        'Authorization': token,
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return json.loads(response.text)


def edit_VirtualAccount_by_oid(class_name, obj):
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

    print(response.text)

def get_single_coin_info(class_name, condition):

    url = "http://i-2o0wkhxv.cloud.nelbds.org.cn:8180/api/app//dwf/v1/omf/entities/"+class_name+"/objects"

    payload = json.dumps({
        "condition": condition,
        "pageSize": 100
    })
    token = get_token()
    headers = {
        'accept': '*/*',
        'Authorization': token,
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return json.loads(response.text)

def edit_single_coin_hold(class_name, obj):
    url = "http://i-2o0wkhxv.cloud.nelbds.org.cn:8180/api/app//dwf/v1/omf/entities/" + class_name + "/objects-update?forceUpdate=false"

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


while(True):
    delegation_info = get_delegation_info()
    # print(delegation_info)
    # print(len(delegation_info["data"]))
    delegation_info = delegation_info["data"]
    # 获取各个币种的价格信息
    coin_info = get_coin_info("CoinInfo", "and 1=1")
    coin_info = coin_info["data"]
    # print(coin_info)
    coin_dict = {}

    for i in range(len(coin_info)):
        coin_name = coin_info[i]["coinName"]
        coin_price = coin_info[i]["coinPrice"]
        coin_dict[coin_name] = coin_price

    # 对所有的委托进行处理
    for i in range(len(delegation_info)):
        print(delegation_info[i])
        delegate_coin_name = delegation_info[i]["delegateCoinName"]
        delegate_price = delegation_info[i]["delegatePrice"]
        delegate_action = delegation_info[i]["delegateAction"]
        delegate_number = delegation_info[i]["delegateAmount"]
        delegate_oid = delegation_info[i]["oid"]
        delegator_oid = delegation_info[i]["delegatorOID"]
        # delegate_type = delegation_info[i]["delegateType"]

        # 异常处理
        if delegate_action != "BUY" and delegate_action != "SELL":
            delete_delegation_by_oid("DelegateInfo", delegate_oid)

        if delegate_coin_name in coin_dict.keys():
            if delegate_action == "BUY" and delegate_price < coin_dict[delegate_coin_name]:
                continue

            if delegate_action == "SELL" and delegate_price > coin_dict[delegate_coin_name]:
                continue

            if delegate_action == "BUY":
                transaction_message = {
                    "transactionCoinName": delegate_coin_name,
                    "transactionAmount": delegate_number,
                    "transactionPrice": delegate_price,
                    "transactionPersonOID": delegator_oid,
                    "transactionAction": delegate_action,
                    "transactionTime": str(int(time.mktime(datetime.datetime.now().timetuple()))*1000)
                }
                print("BUY")
                print(transaction_message)
                result = create_transaction("TransactionHistory", transaction_message)
                if result:
                    # 增加或者修改持仓信息
                    user = get_instance_by_oid("VirtualAccount", delegator_oid)["data"][0]
                    user_oid = user["oid"]
                    user_tot = user["asset"]

                    user_coin_asset = user["coinAsset"]
                    user_cash = user["cash"]

                    user_frozenAsset = user["frozenAsset"]
                    user_usableAsset = user["usableAsset"]

                    user_frozenAsset = user_frozenAsset - delegate_number*delegate_price*(1+0.001)
                    user_coin_asset = user_coin_asset + delegate_number*coin_dict[delegate_coin_name]

                    user_cash = user_frozenAsset+user_usableAsset

                    user_tot = user_cash+user_coin_asset

                    # TODO: 更新收益率

                    obj = {
                        "oid": user_oid,
                        "asset": user_tot,
                        "coinAsset": user_coin_asset,
                        "cash": user_cash,
                        "frozenAsset": user_frozenAsset,
                        "usableAsset": user_usableAsset
                        # "delegatorOID": delegator_oid
                    }

                    edit_VirtualAccount_by_oid("VirtualAccount", obj)


                    # 增加或者修改持仓信息
                    hold_info = get_single_coin_info(r"SingleCoinInfo", "and obj.coinHolderOID = '"+str(user_oid)+r"'")

                    hold_info = hold_info["data"]
                    hold_coin_dict = {}

                    flag = False

                    for j in range(len(hold_info)):
                        if hold_info[j]["coinName"] == delegate_coin_name:
                            print("real update")
                            flag = True
                            coin_number = hold_info[j]["coinAmount"]
                            hold_price = hold_info[j]["coinHoldPrice"]
                            avg_price = hold_info[j]["coinAveragePrice"]
                            transaction_time = hold_info[j]["coinTime"]
                            usable_amount = hold_info[j]["coinUsableAmount"]

                            hold_price = (hold_price * coin_number + delegate_number * delegate_price) / (
                                        coin_number + delegate_number)
                            avg_price = (hold_price*transaction_time+delegate_price)/(1+transaction_time)
                            transaction_time = transaction_time+1
                            coin_number = coin_number+delegate_number
                            usable_amount = usable_amount+delegate_number
                            obj = {
                                "oid": hold_info[j]["oid"],
                                "coinAmount": coin_number,
                                "coinHoldPrice": hold_price,
                                "coinAveragePrice": avg_price,
                                "coinTime": transaction_time,
                                "coinUsableAmount": usable_amount
                            }
                            edit_single_coin_hold("SingleCoinInfo", obj)

                            break
                    if flag == False:
                        obj = {
                            "coinAmount": delegate_number,
                            "coinHoldPrice": delegate_price,
                            "coinAveragePrice": delegate_price,
                            "coinTime": 1,
                            "coinName": delegate_coin_name,
                            "coinHolderOID": delegator_oid,
                            "coinUsableAmount": delegate_number
                        }
                        create_transaction("SingleCoinInfo", obj)

                    # 删除委托信息
                    delete_delegation_by_oid("DelegateInfo", delegate_oid)


            if delegate_action == "SELL":
                # 更改用户的资金
                # 更改/删除用户持仓信息
                # 创建交易记录
                # 删除委托信息
                transaction_message = {
                    # 包含SELL 和 AUTO SELL
                    "transactionAction": delegate_action,
                    "transactionCoinName": delegate_coin_name,
                    "transactionAmount": delegate_number,
                    "transactionPrice": delegate_price,
                    "transactionPersonOID": delegator_oid,
                    "transactionTime": str(int(time.mktime(datetime.datetime.now().timetuple())) * 1000)
                }
                print("SELL")
                print(transaction_message)
                result = create_transaction("TransactionHistory", transaction_message)
                if result:
                    # 增加或者修改持仓信息
                    user = get_instance_by_oid("VirtualAccount", delegator_oid)["data"][0]
                    user_oid = user["oid"]
                    user_tot = user["asset"]

                    user_coin_asset = user["coinAsset"]
                    user_cash = user["cash"]

                    user_frozenAsset = user["frozenAsset"]
                    user_usableAsset = user["usableAsset"]


                    user_coin_asset = user_coin_asset - delegate_number * coin_dict[delegate_coin_name]
                    user_usableAsset = user_usableAsset+delegate_number * delegate_price*(1-0.001)
                    user_cash = user_frozenAsset + user_usableAsset

                    user_tot = user_cash + user_coin_asset

                    # TODO: 更新收益率

                    obj = {
                        "oid": user_oid,
                        "asset": user_tot,
                        "coinAsset": user_coin_asset,
                        "cash": user_cash,
                        "frozenAsset": user_frozenAsset,
                        "usableAsset": user_usableAsset
                    }
                    edit_VirtualAccount_by_oid("VirtualAccount", obj)

                    # 增加或者修改持仓信息
                    hold_info = get_single_coin_info(r"SingleCoinInfo",
                                                     "and obj.coinHolderOID = '" + str(user_oid) + r"'")

                    hold_info = hold_info["data"]
                    hold_coin_dict = {}

                    for j in range(len(hold_info)):
                        if hold_info[j]["coinName"] == delegate_coin_name:
                            print("real update")
                            # flag = True
                            coin_number = hold_info[j]["coinAmount"]
                            hold_price = hold_info[j]["coinHoldPrice"]
                            avg_price = hold_info[j]["coinAveragePrice"]
                            transaction_time = hold_info[j]["coinTime"]
                            usable_amount = hold_info[j]["coinUsableAmount"]

                            if(coin_number - delegate_number != 0):
                                hold_price = (hold_price * coin_number - delegate_number * delegate_price) / (
                                        coin_number - delegate_number)
                            else:
                                hold_price = 0
                            avg_price = (hold_price * transaction_time + delegate_price) / (1 + transaction_time)
                            transaction_time = transaction_time+1
                            coin_number = coin_number - delegate_number
                            print("剩余币种")
                            print(coin_number)
                            if(coin_number <= 0.0001):
                                # 直接删除持仓记录
                                delete_delegation_by_oid("SingleCoinInfo", hold_info[j]["oid"])
                            else:

                                usable_amount = usable_amount
                                obj = {
                                    "oid": hold_info[j]["oid"],
                                    "coinAmount": coin_number,
                                    "coinHoldPrice": hold_price,
                                    "coinAveragePrice": avg_price,
                                    "coinTime": transaction_time,
                                    "coinUsableAmount": usable_amount
                                }
                                edit_single_coin_hold("SingleCoinInfo", obj)

                            break
                    # 删除委托信息
                    delete_delegation_by_oid("DelegateInfo", delegate_oid)


    time.sleep(2)