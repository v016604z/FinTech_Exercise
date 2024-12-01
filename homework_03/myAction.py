import numpy as np

# A simple greedy approach
def myActionSimple(priceMat, transFeeRate):
    # Explanation of my approach:
	# 1. Technical indicator used: Watch next day price
	# 2. if next day price > today price + transFee ==> buy
    #       * buy the best stock
	#    if next day price < today price + transFee ==> sell
    #       * sell if you are holding stock
    # 3. You should sell before buy to get cash each day
    # default
    cash = 1000
    hold = 0
    # user definition
    nextDay = 1
    dataLen, stockCount = priceMat.shape  # day size & stock count   
    stockHolding = np.zeros((dataLen,stockCount))  # Mat of stock holdings
    actionMat = []  # An k-by-4 action matrix which holds k transaction records.
    
    for day in range( 0, dataLen-nextDay ) :
        dayPrices = priceMat[day]  # Today price of each stock
        nextDayPrices = priceMat[ day + nextDay ]  # Next day price of each stock
        
        if day > 0:
            stockHolding[day] = stockHolding[day-1]  # The stock holding from the previous action day
        
        buyStock = -1  # which stock should buy. No action when is -1
        buyPrice = 0  # use how much cash to buy
        sellStock = []  # which stock should sell. No action when is null
        sellPrice = []  # get how much cash from sell
        bestPriceDiff = 0  # difference in today price & next day price of "buy" stock
        stockCurrentPrice = 0  # The current price of "buy" stock
        
        # Check next day price to "sell"
        for stock in range(stockCount) :
            todayPrice = dayPrices[stock]  # Today price
            nextDayPrice = nextDayPrices[stock]  # Next day price
            holding = stockHolding[day][stock]  # how much stock you are holding
            
            if holding > 0 :  # "sell" only when you have stock holding
                if nextDayPrice < todayPrice*(1+transFeeRate) :  # next day price < today price, should "sell"
                    sellStock.append(stock)
                    # "Sell"
                    sellPrice.append(holding * todayPrice)
                    cash = holding * todayPrice*(1-transFeeRate) # Sell stock to have cash
                    stockHolding[day][sellStock] = 0
        
        # Check next day price to "buy"
        if cash > 0 :  # "buy" only when you have cash
            for stock in range(stockCount) :
                todayPrice = dayPrices[stock]  # Today price
                nextDayPrice = nextDayPrices[stock]  # Next day price
                
                if nextDayPrice > todayPrice*(1+transFeeRate) :  # next day price > today price, should "buy"
                    diff = nextDayPrice - todayPrice*(1+transFeeRate)
                    if diff > bestPriceDiff :  # this stock is better
                        bestPriceDiff = diff
                        buyStock = stock
                        stockCurrentPrice = todayPrice
            # "Buy" the best stock
            if buyStock >= 0 :
                buyPrice = cash
                stockHolding[day][buyStock] = cash*(1-transFeeRate) / stockCurrentPrice # Buy stock using cash
                cash = 0
                
        # Save your action this day
        if buyStock >= 0 or len(sellStock) > 0 :
            action = []
            if len(sellStock) > 0 :
                for i in range( len(sellStock) ) :
                    action = [day, sellStock[i], -1, sellPrice[i]]
                    actionMat.append( action )
            if buyStock >= 0 :
                action = [day, -1, buyStock, buyPrice]
                actionMat.append( action )
    return actionMat

# A DP-based approach to obtain the optimal return
def myAction01(priceMat, transFeeRate):
    cash = 1000  # Initial cash
    dataLen, stockCount = priceMat.shape  # m: number of days, n: number of stocks
    stockHolding = np.zeros((dataLen, stockCount))  # Stock holdings matrix
    actionMat = []  # The action matrix for storing the transaction records
    
    for day in range(0, dataLen-1):
        dayPrices = priceMat[day]  # Prices of each stock on the current day
        nextDayPrices = priceMat[day + 1]  # Prices of each stock on the next day
        
        # Carry over stock holdings from previous day
        if day > 0:
            stockHolding[day] = stockHolding[day - 1]

        # Variables for buy/sell decision
        buyStock = -1  # Stock to buy (-1 means no action)
        buyPrice = 0  # Cash to spend on buying the stock
        sellStocks = []  # List of stocks to sell
        sellPrices = []  # List of how much cash to get from selling
        bestPriceDiff = 0  # Best difference for buying a stock
        stockCurrentPrice = 0  # Price of the stock being considered to buy

        # Check which stocks to sell
        for stock in range(stockCount):
            todayPrice = dayPrices[stock]
            nextDayPrice = nextDayPrices[stock]
            holding = stockHolding[day][stock]

            if holding > 0 and nextDayPrice < todayPrice * (1 + transFeeRate):  # Sell condition
                sellStocks.append(stock)
                sellPrices.append(holding * todayPrice * (1 - transFeeRate))
                cash += holding * todayPrice * (1 - transFeeRate)  # Update cash after selling
                stockHolding[day][stock] = 0  # Clear stock holdings after selling

        # Check which stock to buy
        if cash > 0:  # Only buy if there's cash
            for stock in range(stockCount):
                todayPrice = dayPrices[stock]
                nextDayPrice = nextDayPrices[stock]

                # Check if next day price is higher than current price (considering transaction fee)
                if nextDayPrice > todayPrice * (1 + transFeeRate):
                    priceDiff = nextDayPrice - todayPrice * (1 + transFeeRate)
                    if priceDiff > bestPriceDiff:  # Choose the stock with the largest price increase
                        bestPriceDiff = priceDiff
                        buyStock = stock
                        stockCurrentPrice = todayPrice

            # Buy the best stock
            if buyStock >= 0:
                buyPrice = cash * (1 - transFeeRate)  # Calculate the amount to buy
                stockHolding[day][buyStock] = buyPrice / stockCurrentPrice  # Update stock holdings
                cash = 0  # Use up all cash for buying stock

        # Record the transactions (buy or sell)
        if buyStock >= 0 or len(sellStocks) > 0:
            for i in range(len(sellStocks)):
                actionMat.append([day, sellStocks[i], -1, sellPrices[i]])

            if buyStock >= 0:
                actionMat.append([day, -1, buyStock, buyPrice])

    return actionMat

import numpy as np

def myAction02(priceMat, transFeeRate, K):
    cash = 1000  # Initial cash
    dataLen, stockCount = priceMat.shape  # m: number of days, n: number of stocks
    stockHolding = np.zeros((dataLen, stockCount))  # Stock holdings matrix
    actionMat = []  # The action matrix for storing the transaction records
    cashHoldingDays = np.zeros(dataLen)  # Track how many days cash has been held consecutively
    
    for day in range(0, dataLen - 1):
        dayPrices = priceMat[day]  # Prices of each stock on the current day
        nextDayPrices = priceMat[day + 1]  # Prices of each stock on the next day
        
        # Carry over stock holdings from previous day
        if day > 0:
            stockHolding[day] = stockHolding[day - 1]

        # Variables for buy/sell decision
        buyStock = -1  # Stock to buy (-1 means no action)
        buyPrice = 0  # Cash to spend on buying the stock
        sellStocks = []  # List of stocks to sell
        sellPrices = []  # List of how much cash to get from selling
        bestPriceDiff = 0  # Best difference for buying a stock
        stockCurrentPrice = 0  # Price of the stock being considered to buy

        # Check which stocks to sell
        for stock in range(stockCount):
            todayPrice = dayPrices[stock]
            nextDayPrice = nextDayPrices[stock]
            holding = stockHolding[day][stock]

            if holding > 0 and nextDayPrice < todayPrice * (1 + transFeeRate):  # Sell condition
                sellStocks.append(stock)
                sellPrices.append(holding * todayPrice * (1 - transFeeRate))
                cash += holding * todayPrice * (1 - transFeeRate)  # Update cash after selling
                stockHolding[day][stock] = 0  # Clear stock holdings after selling

        # Track how many consecutive days have we held cash
        if cash > 0:
            cashHoldingDays[day] = cashHoldingDays[day - 1] + 1 if day > 0 else 1
        else:
            cashHoldingDays[day] = 0
        
        # Check which stock to buy only if cash has been held for at least K days
        if cash > 0 and cashHoldingDays[day] >= K:  # Only buy after holding cash for K days
            for stock in range(stockCount):
                todayPrice = dayPrices[stock]
                nextDayPrice = nextDayPrices[stock]

                # Check if next day price is higher than current price (considering transaction fee)
                if nextDayPrice > todayPrice * (1 + transFeeRate):
                    priceDiff = nextDayPrice - todayPrice * (1 + transFeeRate)
                    if priceDiff > bestPriceDiff:  # Choose the stock with the largest price increase
                        bestPriceDiff = priceDiff
                        buyStock = stock
                        stockCurrentPrice = todayPrice

            # Buy the best stock if a valid stock is found
            if buyStock >= 0:
                buyPrice = cash * (1 - transFeeRate)  # Calculate the amount to buy
                stockHolding[day][buyStock] = buyPrice / stockCurrentPrice  # Update stock holdings
                cash = 0  # Use up all cash for buying stock

        # Record the transactions (buy or sell)
        if buyStock >= 0 or len(sellStocks) > 0:
            for i in range(len(sellStocks)):
                actionMat.append([day, sellStocks[i], -1, sellPrices[i]])

            if buyStock >= 0:
                actionMat.append([day, -1, buyStock, buyPrice])

    return actionMat

import numpy as np

def myAction03(priceMat, transFeeRate, K):
    cash = 1000  # Initial cash
    dataLen, stockCount = priceMat.shape  # m: number of days, n: number of stocks
    stockHolding = np.zeros((dataLen, stockCount))  # Stock holdings matrix
    actionMat = []  # The action matrix for storing the transaction records
    cashHoldingDays = np.zeros(dataLen)  # Track how many days cash has been held consecutively
    stockHoldingDays = np.zeros(dataLen)  # Track how many days stocks have been held consecutively
    
    for day in range(0, dataLen - 1):
        dayPrices = priceMat[day]  # Prices of each stock on the current day
        nextDayPrices = priceMat[day + 1]  # Prices of each stock on the next day
        
        # Carry over stock holdings from previous day
        if day > 0:
            stockHolding[day] = stockHolding[day - 1]
            stockHoldingDays[day] = stockHoldingDays[day - 1]

        # Variables for buy/sell decision
        buyStock = -1  # Stock to buy (-1 means no action)
        buyPrice = 0  # Cash to spend on buying the stock
        sellStocks = []  # List of stocks to sell
        sellPrices = []  # List of how much cash to get from selling
        bestPriceDiff = 0  # Best difference for buying a stock
        stockCurrentPrice = 0  # Price of the stock being considered to buy

        # Check which stocks to sell
        for stock in range(stockCount):
            todayPrice = dayPrices[stock]
            nextDayPrice = nextDayPrices[stock]
            holding = stockHolding[day][stock]

            if holding > 0 and nextDayPrice < todayPrice * (1 + transFeeRate):  # Sell condition
                sellStocks.append(stock)
                sellPrices.append(holding * todayPrice * (1 - transFeeRate))
                cash += holding * todayPrice * (1 - transFeeRate)  # Update cash after selling
                stockHolding[day][stock] = 0  # Clear stock holdings after selling
                stockHoldingDays[day] = 0  # Reset stock holding days after selling

        # Update cashHoldingDays only if no stocks are held
        if np.sum(stockHolding[day]) == 0:  # No stocks are held, increment cash holding days
            cashHoldingDays[day] = cashHoldingDays[day - 1] + 1 if day > 0 else 1
        else:  # If holding stocks, reset cash holding days
            cashHoldingDays[day] = 0
            stockHoldingDays[day] = stockHoldingDays[day - 1] + 1 if day > 0 else 1

        # Check which stock to buy only if cash has been held for at least K days
        if cash > 0 and cashHoldingDays[day] >= K:  # Only buy after holding cash for K days
            for stock in range(stockCount):
                todayPrice = dayPrices[stock]
                nextDayPrice = nextDayPrices[stock]

                # Check if next day price is higher than current price (considering transaction fee)
                if nextDayPrice > todayPrice * (1 + transFeeRate):
                    priceDiff = nextDayPrice - todayPrice * (1 + transFeeRate)
                    if priceDiff > bestPriceDiff:  # Choose the stock with the largest price increase
                        bestPriceDiff = priceDiff
                        buyStock = stock
                        stockCurrentPrice = todayPrice

            # Buy the best stock if a valid stock is found
            if buyStock >= 0:
                buyPrice = cash * (1 - transFeeRate)  # Calculate the amount to buy
                stockHolding[day][buyStock] = buyPrice / stockCurrentPrice  # Update stock holdings
                cash = 0  # Use up all cash for buying stock
                cashHoldingDays[day] = 0  # Reset cash holding days after buying stock
                stockHoldingDays[day] = 1  # Start counting the holding days for the purchased stock

        # Record the transactions (buy or sell)
        if buyStock >= 0 or len(sellStocks) > 0:
            for i in range(len(sellStocks)):
                actionMat.append([day, sellStocks[i], -1, sellPrices[i]])

            if buyStock >= 0:
                actionMat.append([day, -1, buyStock, buyPrice])

    return actionMat

