import pandas as pd
import datetime
def dateStr2DateNum(dateStr):
    dateBegin = datetime.datetime(1970, 1, 1, 0, 0, 0, 0)#719529
    timestr = dateStr + ' 0:0:0' #737791
    dateThisDay = datetime.datetime.strptime(timestr, "%Y%m%d %H:%M:%S")
    diff = (dateThisDay - dateBegin).days
    dateNum = 719529 + diff
    return dateNum

def getAllDayTradeData(stockCode):
    dataFolder = '/Users/test/Documents/Project/StockV20190119/StockMatlab/TidyGTADataBase'
    filePath = dataFolder + '/' + stockCode + '.txt'
    allTradeData = pd.read_table(filePath, header=0, sep=' ')
    # 1个股资料：整型 stockCode 2内部日期 Date,3Open,4High,5Close,6Low,7Volume,8Amount流通市值9CirculatingValue  总市值10Value 流通股本 11CirculatingEquity 总股本12Equity （万股）
    # allTradeData.rename(columns={0:'stockCode', 1:'date', 2:'open', 3:'high', 4:'close', 5:'low', 6:'volume', 7:'amount', 8:'circulatingValue', 9:'value', 10:'circulatingEquity', 11:'Equity'}, inplace = True)
    if allTradeData.shape[1] == 12:
        allTradeData.columns = ['stockCode', 'date', 'open', 'high', 'close', 'low', 'volume', 'amount', 'circulatingValue', 'value', 'circulatingEquity', 'Equity']
    else:
        allTradeData.columns = ['stockCode', 'date', 'open', 'high', 'close', 'low', 'volume', 'amount']
    return allTradeData

def getSectionTradeData(stockCode, beginDateStr, endDateStr):
    allTradeData = getAllDayTradeData(stockCode)
    tempSectionTradeData = allTradeData[allTradeData.iloc[:, 1] >= dateStr2DateNum(beginDateStr)]
    sectionTradeData = tempSectionTradeData[tempSectionTradeData.iloc[:, 1] <= dateStr2DateNum(endDateStr)]
    return sectionTradeData

def getDayTradeData(stockCode, dateStr, allTradeData = pd.DataFrame()):
    if allTradeData.empty:
        allTradeData = getAllDayTradeData(stockCode)
    dateMatlabNum = dateStr2DateNum(dateStr)
    tradeData = allTradeData[allTradeData.iloc[:, 1] == dateMatlabNum]
    if tradeData.shape[0] > 1:
        print(stockCode + ' ' + str(dateMatlabNum) + ' is more than one trade data')
        tradeData = tradeData.iloc[0, :]
        if tradeData.ndim == 1:
            tradeData = tradeData.to_frame().T
    if not tradeData.empty:
        tradeData.index = ['0']
    return tradeData

if __name__ == "__main__":
    stockCode = '399006'
    dateStr = '20151225'
    a=getDayTradeData(stockCode, dateStr)
    print(a)
    b=getSectionTradeData(stockCode, '20200106', '20200106')
    print(b)
#       stockCode    date   open   high  close    low     volume        amount  circulatingValue         value  circulatingEquity   Equity
# 6853          1  737793  16.94  17.31  17.18  16.92  111619400  1.917621e+09      9.895680e+09  9.895680e+09            57600.0  57600.0
    
    