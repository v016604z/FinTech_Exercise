import sys
import numpy as np
import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed
from numba import njit

@njit
def ema_optimized(pastPriceVec, windowSize):
    alpha = 2 / (windowSize + 1)
    ema_values = np.zeros(len(pastPriceVec))
    ema_values[0] = np.mean(pastPriceVec[:windowSize])  # 初始值使用前windowSize的平均

    for i in range(1, len(pastPriceVec)):
        ema_values[i] = alpha * pastPriceVec[i] + (1 - alpha) * ema_values[i - 1]
    
    return ema_values[-1]

@njit
def myStrategy(pastPriceVec, shortWindow, longWindow, signalWindow):
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
    if dataLen >= longWindow + signalWindow:
        MACDEma = ema_optimized(DIF, signalWindow)
    else:
        MACDEma = DIF

    # 根據MACD和DIF來決定操作
    if MACDEma - DIF >= 0:
        action = 1
    elif MACDEma - DIF < 0:
        action = -1

    return action

@njit
def computeReturnRate(priceVec, shortWindow, longWindow, signalWindow):
    capital = 1000.0  # 初始資金
    capitalOrig = capital  # 原始資金
    dataCount = len(priceVec)  # 資料天數
    suggestedAction = np.zeros(dataCount)  # 建議的操作向量
    stockHolding = np.zeros(dataCount)  # 股票持有量向量
    total = np.zeros(dataCount)  # 總資產向量
    realAction = np.zeros(dataCount)  # 實際操作向量
    
    # 每天進行迭代
    for ic in range(dataCount):
        currentPrice = priceVec[ic]  # 當前價格
        suggestedAction[ic] = myStrategy(priceVec[:ic + 1], shortWindow, longWindow, signalWindow)  # 獲取建議的操作
        
        # 根據建議的操作執行實際操作
        if ic > 0:
            stockHolding[ic] = stockHolding[ic - 1]  # 前一天的股票持有量
        
        if suggestedAction[ic] == 1:  # 建議操作是 "買入"
            if stockHolding[ic] == 0:  # 只有在沒有持有股票時才進行 "買入"
                stockHolding[ic] = capital / currentPrice  # 用現金買入股票
                capital = 0  # 清空現金
                realAction[ic] = 1
        elif suggestedAction[ic] == -1:  # 建議操作是 "賣出"
            if stockHolding[ic] > 0:  # 只有在持有股票時才進行 "賣出"
                capital = stockHolding[ic] * currentPrice  # 賣出股票換取現金
                stockHolding[ic] = 0  # 清空股票持有量
                realAction[ic] = -1
        else:  # 沒有操作
            realAction[ic] = 0
        
        total[ic] = capital + stockHolding[ic] * currentPrice  # 總資產，包括股票持有量和現金

    returnRate = (total[-1] - capitalOrig) / capitalOrig  # 這次運行的回報率
    return returnRate
    
# Parallel processing for return rate calculation
def computeReturnRateParallel(adjClose, shortWindow, longWindow, signalWindow):
    return shortWindow, longWindow, signalWindow, computeReturnRate(adjClose, shortWindow, longWindow, signalWindow)

if __name__ == '__main__':
    returnRateBest = -1.00  # Initial best return rate
    df = pd.read_csv(sys.argv[1])  # Read stock file
    adjClose = df["Adj Close"].values  # Get adj close as the price vector

    # Range of windowSize to explore
    alphaMin, alphaMax = 12, 50  # Range of shortWindow (alpha)
    betaMin, betaMax = 26, 50  # Range of longWindow (beta)
    gammaMin, gammaMax = 9 , 50  # Range of signalWindow (gamma)

    futures = []

    with ProcessPoolExecutor(max_workers=6) as executor:
        for shortWindow in range(alphaMin, alphaMax + 1):
            for longWindow in range(betaMin, betaMax + 1):
                for signalWindow in range(gammaMin, gammaMax + 1):
                    futures.append(executor.submit(computeReturnRateParallel, adjClose, shortWindow, longWindow, signalWindow))

        for future in as_completed(futures):
            shortWindow, longWindow, signalWindow, returnRate = future.result()
            print(f"shortWindow={shortWindow}, longWindow={longWindow}, signalWindow={signalWindow} ==> returnRate={returnRate:.6f}")

            if returnRate > returnRateBest:
                shortWindowBest = shortWindow
                longWindowBest = longWindow
                signalWindowBest = signalWindow
                returnRateBest = returnRate

    print(f"Best settings: shortWindow={shortWindowBest}, longWindow={longWindowBest}, signalWindow={signalWindowBest} ==> returnRate={returnRateBest:.6f}")
