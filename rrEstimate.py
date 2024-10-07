# 如何執行這個程式:
#    python rrEstimate.py SPY.csv
import sys
import numpy as np
import pandas as pd
from myStrategy import myStrategy

# 估算給定價格向量的回報率
def rrEstimate(priceVec):
    capital=1000    # 初始資金
    capitalOrig=capital     # 原始資金
    dataCount=len(priceVec)   # 資料天數
    suggestedAction=np.zeros((dataCount,1))   # 建議的操作向量
    stockHolding=np.zeros((dataCount,1))      # 股票持有量向量
    total=np.zeros((dataCount,1))             # 總資產向量
    realAction=np.zeros((dataCount,1))        # 實際操作，可能與建議操作不同。例如，當建議操作是 1 (買入) 但你沒有資金時，實際操作為 0 (持有或不操作)
    
    # 每天進行迭代
    for ic in range(dataCount):
        currentPrice=priceVec[ic]   # 當前價格
        suggestedAction[ic]=myStrategy(priceVec[0:ic], currentPrice)   # 獲取建議的操作
        # 根據建議的操作執行實際操作
        if ic > 0:
            stockHolding[ic] = stockHolding[ic-1]   # 前一天的股票持有量
        if suggestedAction[ic] == 1:   # 建議操作是 "買入"
            if stockHolding[ic] == 0:   # 只有在沒有持有股票時才進行 "買入"
                stockHolding[ic] = capital / currentPrice   # 用現金買入股票
                capital = 0   # 清空現金
                realAction[ic] = 1
        elif suggestedAction[ic] == -1:   # 建議操作是 "賣出"
            if stockHolding[ic] > 0:   # 只有在持有股票時才進行 "賣出"
                capital = stockHolding[ic] * currentPrice   # 賣出股票換取現金
                stockHolding[ic] = 0   # 清空股票持有量
                realAction[ic] = -1
        elif suggestedAction[ic] == 0:   # 沒有操作
            realAction[ic] = 0
        else:
            assert False   # 確保操作的正確性
        total[ic] = capital + stockHolding[ic] * currentPrice   # 總資產，包括股票持有量和現金
    
    returnRate = (total[-1].item() - capitalOrig) / capitalOrig   # 這次運行的回報率
    return returnRate

if __name__ == '__main__':
    file = sys.argv[1]   # 輸入的檔案
    df = pd.read_csv(file)
    priceVec = df["Adj Close"].values   # 獲取調整後的收盤價作為價格向量
    rr = rrEstimate(priceVec)   # 計算回報率
    print("rr=%f%%" % (rr * 100))   # 輸出回報率
