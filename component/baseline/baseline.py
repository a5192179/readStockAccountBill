import pandas as pd
import sys
sys.path.append(r'./computeProfit')
import getDayTradeData
sys.path.append(r'./component/time')
import timeAndDate
# 第一天是用来初始化的，第一天净值为1，初始价格为第一天的价格
class Baseline:
    def __init__(self, stockCode, beginDateStr):
        self.stockCode = stockCode
        self.beginDateStr = beginDateStr
        self.baseDateStr = beginDateStr
        self.baseNet = pd.Series([1], index = [beginDateStr]) # 行是日期，列是净值
        self.baseYearRaise = pd.Series() # 行是年，每年最后第一个自然日的日期，列是年内涨幅
        self.allDayTradeData = getDayTradeData.getAllDayTradeData(stockCode)
        self.basePrice = self.getOneDayClose(beginDateStr)

    def getOneDayClose(self, dateStr):
        # 如果有一天没有数据，则向前取直到取到数据
        tradeData = getDayTradeData.getDayTradeData(self.stockCode, dateStr, self.allDayTradeData)
        # stockCode date open high close low volume amount circulatingValue value circulatingEquity Equity
        if tradeData.empty:
            yesterdayStr = dateStr
            for i in range(1000):
                if i % 1 == 0:
                    print('i=' + str(i) + ', yesterday:' + yesterdayStr + ' has no trade data')
                yesterdayStr = timeAndDate.getYesteray(yesterdayStr)
                tradeData = getDayTradeData.getDayTradeData(self.stockCode, yesterdayStr, self.allDayTradeData)
                if not tradeData.empty:
                    break
        return tradeData.loc['0', 'close']

    def updateNet(self, newDateStr):
        newPrice = self.getOneDayClose(newDateStr)
        newNet = pd.Series(self.baseNet[-1] * (1 + (newPrice - self.basePrice) / self.basePrice), index = [newDateStr])
        self.basePrice = newPrice
        self.baseNet = self.baseNet.append(newNet)
        self.baseDateStr = newDateStr

    def updateYearRaise(self, newDateStr):
        # 每年最后一天统计当年去年12月31日至今年12月31日的收益，没有去年12月31日的按今年的算
        if not timeAndDate.isLastDayofThisYear(newDateStr):
            return
        lastYear = timeAndDate.getLastYear(newDateStr)
        lastDayofLastYear = lastYear + '1231'
        if self.beginDateStr[0:4] == newDateStr[0:4]:
            yearBaseDay = self.beginDateStr
        else:
            yearBaseDay = lastDayofLastYear
        baseDayNet = self.baseNet[yearBaseDay]
        todayNet = self.baseNet[newDateStr]
        yearRaise = (todayNet - baseDayNet) / baseDayNet
        yearRaiseSeries = pd.Series(yearRaise, index = [newDateStr])
        self.baseYearRaise = self.baseYearRaise.append(yearRaiseSeries)
        print('base, year:' + newDateStr[0:4] + ', raise:' + str(yearRaise))
        
if __name__ == "__main__":
    beginDateStr = '20171130'
    baseline = Baseline('399006', beginDateStr)
    todayStr = beginDateStr
    for i in range(1200):
        todayStr = timeAndDate.getTomorrow(todayStr)
        baseline.updateNet(todayStr)
        if int(todayStr) > 20200110:
            break
    # baseline.updateNet('20200108')
    # baseline.getOneDayClose('20191005')
    # testData = baseline.getOneDayTradeData('20200107')
    # print(testData)
    baseline.updateYearRaise('20171231') #base, year:2017, raise:-0.009970061571485389
    baseline.updateYearRaise('20181231') #base, year:2018, raise:-0.28649188371893947
    baseline.updateYearRaise('20191231') #base, year:2019, raise:0.4378863361934528
    a=1