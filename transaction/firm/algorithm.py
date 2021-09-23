

phase = 0
def onTick(coin_info, user_info, hold_info):
    global phase
    if phase == 0:
        buy("BTC", 34000, 0.01)
        phase = phase+1
    elif phase == 1:
        buy("BTC", 33999, 0.01)
        phase = phase+1
    elif phase == 2:
        retreate()
        phase = phase+1
    elif phase == 3:
        sell("BTC", 34001, 0.01)
        phase = phase+1
    elif phase == 4:
        retreate()
        phase = phase + 1