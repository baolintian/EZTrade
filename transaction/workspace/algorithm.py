

PARAMS = {
    # "start_time": "2014-01-01 00:00:00",
    # "end_time": "2016-10-01 00:00:00",
    "slippage": 0.00001,
    "account_initial": {"huobi_cny_cash": 34375.16,
                        "huobi_cny_btc": 1},
    "threshold": 0.05,
    "minimum": 0.001,

}

def onTick(acc, stock):
    diffAsset = (acc["money"] - (acc["coin"] * stock["sell"])) / 2
    ratio = diffAsset / acc["money"]
    threshold = PARAMS['threshold']
    minimum = PARAMS['minimum']
    if abs(ratio) < threshold :
        return
    if (ratio > 0):

        buyAmount = diffAsset / stock["sell"]
        if (buyAmount < PARAMS["minimum"]):
            return
        PARAMS['account_initial']['huobi_cny_cash'] -= diffAsset
        PARAMS['account_initial']['huobi_cny_btc'] += buyAmount

    else:

        sellAmount = -diffAsset / stock["sell"]
        if (sellAmount < minimum):
            return
        PARAMS['account_initial']['huobi_cny_cash'] += (-diffAsset)
        PARAMS['account_initial']['huobi_cny_btc'] -= sellAmount



