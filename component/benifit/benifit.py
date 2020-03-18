import pandas as pd
import sys
sys.path.append(r'./computeProfit')
import getDayTradeData
sys.path.append(r'./component/time')
import timeAndDate
# 第一天是用来初始化的，第一天净值为1，初始价格为第一天的价格
class BenifitStatistic:
    def __init__(self, beginDateStr, ):
        self.net = pd.Series([1], index = [beginDateStr]) # 行是日期，列是净值
        self.BenifitStatistic pd.DataFrame(columns = ['currentPrice', 'costPrice', 'amount', 'buyDate', 'fee'])#code 是 行名
        self.hold = pd.Series([0], index = [beginDateStr]) # 行是日期，列是仓位
        self.hold = pd.Series([0], index = [beginDateStr]) # 行是日期，列是仓位
        self.yearRaise = pd.Series() # 行是年，每年最后第一个自然日的日期，列是年内涨幅