from scipy.optimize import fsolve

def irrFind(cashFlowVec, cashFlowPeriod, compoundPeriod):

    # n = 總共幾次現金流
    n = len(cashFlowVec) 
    
    # 定義函數
    def func(irr):
        return sum([cashFlowVec[i] / (1 + irr / (cashFlowPeriod / compoundPeriod)) ** (i * cashFlowPeriod / compoundPeriod) for i in range(n)])

    # 利用 fsolve 求 IRR
    irr = fsolve(func, 0)[0]
    
    # 將 IRR 轉換成年化利率
    if cashFlowPeriod != 12:
        return irr * (12 / cashFlowPeriod)
    
    return irr

