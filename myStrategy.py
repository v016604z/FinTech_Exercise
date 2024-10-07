def ema_optimized(pastPriceVec, windowSize):
    import numpy as np

    alpha = 2 / (windowSize + 1)
    ema_values = np.zeros(len(pastPriceVec))
    ema_values[0] = np.mean(pastPriceVec[:windowSize])  # 初始值使用前windowSize的平均

    for i in range(1, len(pastPriceVec)):
        ema_values[i] = alpha * pastPriceVec[i] + (1 - alpha) * ema_values[i - 1]
    
    return ema_values[-1]

def myStrategy(pastPriceVec, currentPrice):
    # 我的方法說明：
	# 1. 使用的技術指標：移動平均收斂/發散指標 (MACD)
	# 2. 如果 MACD > signal ==> 買入
	#    如果 MACD < signal ==> 賣出
	# 3. 可調整的參數：短期 EMA、長期 EMA 和 signal 線的視窗大小
	# 4. 使用固定參數值來進行交易動作判斷

    import numpy as np

    shortWindow = 177
    longWindow = 59
    MACDWindow = 45
    action = 0  
    dataLen = len(pastPriceVec)  

    if dataLen < longWindow:
        return action  

    # 計算短期 EMA
    shortEma = ema_optimized(pastPriceVec, shortWindow)
    
    # 計算長期 EMA
    longEma = ema_optimized(pastPriceVec, longWindow)

    # 計算 DIF (短期 EMA - 長期 EMA)
    DIF = shortEma - longEma

    # 計算 MACD EMA
    if dataLen >= longWindow + MACDWindow:
        MACDEma = ema_optimized(np.array([shortEma - longEma for _ in range(MACDWindow)]), MACDWindow)
    else:
        MACDEma = DIF

    # 根據MACD和DIF來決定操作
    if MACDEma - DIF >= 0:
        action = 1
    elif MACDEma - DIF < 0:
        action = -1

    return action