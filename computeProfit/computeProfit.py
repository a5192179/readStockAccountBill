import xlrd
import pandas as pd
import datetime
from getDayTradeData import getDayTradeData


class Asset:
    def __init__(self):
        self.date = datetime.datetime(2014, 8, 6)
        self.hold = pd.DataFrame(columns = ['currentPrice', 'costPrice', 'amount', 'buyDate', 'fee'])#code 是 行名
        self.cash = 0 # 现金
        self.cashFund = 0 # 货币基金
        self.stockAsset = 0 # 证券资产总额
        self.netAsset = 0 # 净资产
        self.todayIn = 0 # 今天转入，今天转入的直接加入当天的结算
        self.net = 1 #净值 当天总结算的时候更新
        self.returnRate = 0
        self.position = 0 #仓位 当天总结算的时候更新

    def copy(self):
        newAsset = Asset()
        newAsset.date = self.date
        newAsset.hold = self.hold.copy(deep=True)
        newAsset.cash = self.cash
        newAsset.cashFund = self.cashFund
        newAsset.stockAsset = self.stockAsset
        newAsset.netAsset = self.netAsset
        newAsset.todayIn = self.todayIn
        newAsset.net = self.net
        newAsset.returnRate = self.returnRate
        newAsset.position = self.position
        return newAsset

    def updateStockAsset(self):
        self.stockAsset = 0
        for stockCode in self.hold.index:
            self.stockAsset += self.hold.loc[stockCode, 'currentPrice'] * self.hold.loc[stockCode, 'amount']

    def updateNetAsset(self):
        self.netAsset = self.cash + self.cashFund + self.stockAsset

    def updateHoldPrice(self):
        dateStr = self.date.strftime("%Y%m%d")
        for rowName in self.hold.index:
            stockCode = rowName
            if int(stockCode) > 131800 and int(stockCode) < 131899:
                continue
            # TODO 处理国债逆回购
            tradeData = getDayTradeData(stockCode, dateStr)
            if not tradeData.empty:
                self.hold.loc[stockCode, 'currentPrice'] = tradeData['close'][0]

def getMoneyFromBank(asset, operateRecord):
    # TODO 考虑失败
    # 1、银行转存
    money = operateRecord.loc[operateRecord.index.values[0], '收付金额'] # .loc[:, '日期']得到的是个单元素的array 还要取第一个元素
    asset.cash += money
    asset.todayIn += money

def withdrawMoneyToBank(asset, operateRecord):
    # TODO 考虑失败
    # 银行转取
    money = -operateRecord.loc[operateRecord.index.values[0], '收付金额']
    asset.cash -= money
    asset.todayIn -= money
    
def confirmSubscription(asset, operateRecord):
    #申购确认 股市资金减，货币基金资金增。申购货币基金，资金转到货币基金。收付金额记录为负，没有数量，以收付金额为准
    # !!好像2014年12月31日-2015年8月11日之间的收付金额是正的
    dateThisDay = asset.date
    thresholdDayBegin = datetime.datetime.strptime('20141231', "%Y%m%d")
    thresholdDayEnd = datetime.datetime.strptime('20150811', "%Y%m%d")
    if (dateThisDay - thresholdDayBegin).days > 0 and (dateThisDay - thresholdDayEnd).days < 0:
        # 2014年12月31日之后的收付金额试正的
        money = operateRecord.loc[operateRecord.index.values[0], '收付金额']
    else:
        money = -operateRecord.loc[operateRecord.index.values[0], '收付金额']
    asset.cash -= money
    asset.cashFund += money

def confirmRedemption(asset, operateRecord):
    #赎回确认 股市资金增，货币基金资金减。赎回货币基金，资金转到现金。收付金额记录为正，没有数量，以收付金额为准
    money = operateRecord.loc[operateRecord.index.values[0], '收付金额']
    asset.cash += money
    asset.cashFund -= money

def stockBuy(asset, operateRecord):
    #证券买入 股市资金减，股票增。数量、均价、佣金、其他费。收付金额记录为负
    #买入资金来源可能为货币资金或者货币基金，如果买入前现金够，则用现金，如果先卖了再买，则先用卖了得到的现金
    #如果现金不够，交割单的现金余额会显示为负，晚上结算会使用货币基金，在买入后当天会有赎回记录
    money     = -operateRecord.loc[operateRecord.index.values[0], '收付金额']
    stockCode = operateRecord.loc[operateRecord.index.values[0], '证券代码']
    price     = operateRecord.loc[operateRecord.index.values[0], '成交均价']
    amount    = operateRecord.loc[operateRecord.index.values[0], '发生数量']
    fee       = operateRecord.loc[operateRecord.index.values[0], '佣金'] + operateRecord.loc[operateRecord.index.values[0], '印花税'] + operateRecord.loc[operateRecord.index.values[0], '其他费']
    buyDate   = operateRecord.loc[operateRecord.index.values[0], '日期']
    asset.cash -= money
    if stockCode in asset.hold.index:
        # 已经有持仓了，计算平均成本
        #code price amount buydate fee
        asset.hold.loc[stockCode, 'fee'] += fee
        allMoney = asset.hold.loc[stockCode, 'amount'] * asset.hold.loc[stockCode, 'costPrice'] + amount * price + fee
        allAmount = asset.hold.loc[stockCode, 'amount'] + amount
        asset.hold.loc[stockCode, 'amount'] = allAmount
        asset.hold.loc[stockCode, 'costPrice'] = round(allMoney / allAmount, 3)
    else:
        # 没有持仓，新建一行
        if stockCode == '072807':
            stockCode = '128034'
        temp = pd.Series([price, price, amount, buyDate, fee], index=asset.hold.columns, name = stockCode)
        asset.hold = asset.hold.append(temp)

def stockSell(asset, operateRecord):
    #证券卖出 股市资金增，股票减。数量、均价、佣金、印花税、其他费
    #数量是负的
    money     = operateRecord.loc[operateRecord.index.values[0], '收付金额']
    stockCode = operateRecord.loc[operateRecord.index.values[0], '证券代码']
    price     = operateRecord.loc[operateRecord.index.values[0], '成交均价']
    amount    = -operateRecord.loc[operateRecord.index.values[0], '发生数量']
    fee       = operateRecord.loc[operateRecord.index.values[0], '佣金'] + operateRecord.loc[operateRecord.index.values[0], '印花税'] + operateRecord.loc[operateRecord.index.values[0], '其他费']
    sellDate   = operateRecord.loc[operateRecord.index.values[0], '日期']
    asset.cash += money
    if amount < asset.hold.loc[stockCode, 'amount']:
        # 没卖完，数量减，重新计算成本
        asset.hold.loc[stockCode, 'fee'] += fee
        allMoney = asset.hold.loc[stockCode, 'amount'] * asset.hold.loc[stockCode, 'costPrice'] - amount * price + fee
        allAmount = asset.hold.loc[stockCode, 'amount'] - amount
        asset.hold.loc[stockCode, 'amount'] = allAmount
        asset.hold.loc[stockCode, 'costPrice'] = round(allMoney / allAmount, 3)
    else:
        stockName = operateRecord.loc[operateRecord.index.values[0], '证券名称']
        if stockName[0:2] != 'DR':
            # 卖完了，不是待分红的股，直接清掉
            asset.hold.drop([stockCode], inplace=True)
        else:
            # 沪市可能在除权日已经把登记的股份卖光了，不能直接删除，还有除权股要来
            asset.hold.loc[stockCode, 'fee'] += fee
            allMoney = asset.hold.loc[stockCode, 'amount'] * asset.hold.loc[stockCode, 'costPrice'] - amount * price + fee
            allAmount = 0
            asset.hold.loc[stockCode, 'amount'] = allAmount
            asset.hold.loc[stockCode, 'costPrice'] = allMoney # 卖完了，成本价就记录所有的支出。

def bonusDistribution(asset, operateRecord):
    # 最后一笔红利发放到2015年8月7日
    # 红利发放 货币基金资金增。货币基金分红 直接计入总资产 没有收付金额
    # 老版本才有
    money = operateRecord.loc[operateRecord.index.values[0], '发生数量']
    asset.cashFund += money

def bulkInterestReturn(asset, operateRecord):
    # 批量利息归本 股市资金增。收付金额
    # 利息归本也是这个，早期记录为批量利息归本，后来记录为利息归本
    money = operateRecord.loc[operateRecord.index.values[0], '收付金额']
    asset.cash += money

def newStockSubscription(asset, operateRecord):
    # 新股申购 股市资金减。数量、均价、收付金额
    # 为了方便计算净资产，申购后放入持仓，申购返款消除持仓
    money     = -operateRecord.loc[operateRecord.index.values[0], '收付金额']
    stockCode = operateRecord.loc[operateRecord.index.values[0], '证券代码']
    price     = operateRecord.loc[operateRecord.index.values[0], '成交均价']
    amount    = operateRecord.loc[operateRecord.index.values[0], '发生数量']
    fee       = operateRecord.loc[operateRecord.index.values[0], '佣金'] + operateRecord.loc[operateRecord.index.values[0], '印花税'] + operateRecord.loc[operateRecord.index.values[0], '其他费']
    buyDate   = operateRecord.loc[operateRecord.index.values[0], '日期']
    asset.cash -= money
    temp = pd.Series([price, price, amount, buyDate, fee], index=asset.hold.columns, name = stockCode)
    asset.hold = asset.hold.append(temp)

def newStockSubscriptionRefund(asset, operateRecord):
    # 申购返款 股市资金增。数量、均价、收付金额
    # 为了方便计算净资产，申购后放入持仓，申购返款消除持仓
    money     = operateRecord.loc[operateRecord.index.values[0], '收付金额']
    stockCode = operateRecord.loc[operateRecord.index.values[0], '证券代码']
    price     = operateRecord.loc[operateRecord.index.values[0], '成交均价']
    amount    = -operateRecord.loc[operateRecord.index.values[0], '发生数量']
    fee       = operateRecord.loc[operateRecord.index.values[0], '佣金'] + operateRecord.loc[operateRecord.index.values[0], '印花税'] + operateRecord.loc[operateRecord.index.values[0], '其他费']
    sellDate   = operateRecord.loc[operateRecord.index.values[0], '日期']
    asset.cash += money
    asset.hold.drop([stockCode], inplace=True)

def dividendAccounting(asset, operateRecord):
    # 股息入账 股市资金增。数据来源为“收付金额”
    # 要除权 , 盘后到账，以到账当日的收盘价为基准，每股股息发了多少，第二天开盘基准价就要减多少
    money = operateRecord.loc[operateRecord.index.values[0], '收付金额']
    stockCode = operateRecord.loc[operateRecord.index.values[0], '证券代码']
    asset.cash += money
    # 'currentPrice', 'costPrice', 'amount', 'buyDate', 'fee'
    asset.hold.loc[stockCode, 'currentPrice'] -= round(money / asset.hold.loc[stockCode, 'amount'], 3)
    asset.hold.loc[stockCode, 'costPrice'] -= round(money / asset.hold.loc[stockCode, 'amount'], 3)

def dividendBonusTaxRepayment(asset, operateRecord):
    # 股息红利税补缴 股市资金减，净资产减。收付金额
    # 备注信息里面有 证券账户: A460607489, 证券代码：601028, 初始
    money = -operateRecord.loc[operateRecord.index.values[0], '收付金额']
    asset.cash -= money

# % SZ 主板   000xxx                           ->101
# % SZ 中小板 002xxx,003xxx,004xxx             ->102
# % SZ 创业板 300xxx                           ->103
# % SH 主板   600xxx,601xxx,603xxx             ->201
# % SH 科创板 688xxx                           ->202
def identificationCode(stockCode):
    if 0 <= stockCode and stockCode <= 999:
        classID = 101
    elif 2000 <= stockCode and stockCode <= 4999:
        classID = 102
    elif 300000 <= stockCode and stockCode <= 300999:
        classID = 103
    elif 600000 <= stockCode and stockCode <= 601999:
        classID = 201
    elif 603000 <= stockCode and stockCode <= 603999:
        classID = 201
    elif 688000 <= stockCode and stockCode <= 688999:
        classID = 202
    else:
        classID = 0
    return classID

def bonusAccount(asset, operateRecord):
    # 红股入账 股票增，改价格
    # 沪市的交割单日期是K线除权日，交割单日期当日价格就是除权后价格。交割单上的价格是除权后的价格
    # 深市的交割单日期是股权登记日，股权数量是交割单当日的数量+交割单上分红得到的股票，价格是交割单当日价格进行除权后的价格。交割单上的价格是除权前的价格
    money     = operateRecord.loc[operateRecord.index.values[0], '收付金额']
    stockCode = operateRecord.loc[operateRecord.index.values[0], '证券代码']
    price     = operateRecord.loc[operateRecord.index.values[0], '成交均价']
    amount    = operateRecord.loc[operateRecord.index.values[0], '发生数量']
    marketCode = identificationCode(int(stockCode))
    if marketCode == 101 or marketCode == 102 or marketCode == 103:
        # 深市，要计算除权价格，更改数量
        registerAmount = asset.hold.loc[stockCode, 'amount']
        afterBonusAmount = registerAmount + amount
        asset.hold.loc[stockCode, 'currentPrice'] = round(asset.hold.loc[stockCode, 'currentPrice'] * registerAmount / afterBonusAmount, 3)
        asset.hold.loc[stockCode, 'costPrice'] = round(asset.hold.loc[stockCode, 'costPrice'] * registerAmount / afterBonusAmount, 3)
        asset.hold.loc[stockCode, 'amount'] = afterBonusAmount
    else:
        # 沪市，不用计算价格，只用计算数量
        beforeBonusAmount = asset.hold.loc[stockCode, 'amount']
        afterBonusAmount = beforeBonusAmount + amount
        asset.hold.loc[stockCode, 'amount'] = afterBonusAmount
        if beforeBonusAmount == 0:
            # 沪市可能在除权日已经把登记的股份卖光了
            allMoney = asset.hold.loc[stockCode, 'costPrice']
            allAmount = afterBonusAmount
            asset.hold.loc[stockCode, 'costPrice'] = round(allMoney / allAmount, 3)
            asset.hold.loc[stockCode, 'amount'] = afterBonusAmount

def pledgeRepoSell(asset, operateRecord):
    #质押回购拆出 股市资金减，股票增。数量、均价、佣金、其他费。收付金额记录为负。这个相当于把钱借出去
    #买入资金来源可能为货币资金或者货币基金，如果买入前现金够，则用现金，如果先卖了再买，则先用卖了得到的现金
    #如果现金不够，则使用货币基金，在买入后当天会有赎回记录
    #交割单里面的成交价格是年化利率，价格要用(收付金额-佣金)/数量 计算
    #其他按照买入股票计算
    money     = -operateRecord.loc[operateRecord.index.values[0], '收付金额']
    stockCode = operateRecord.loc[operateRecord.index.values[0], '证券代码']
    amount    = operateRecord.loc[operateRecord.index.values[0], '发生数量']
    fee       = operateRecord.loc[operateRecord.index.values[0], '佣金'] + operateRecord.loc[operateRecord.index.values[0], '印花税'] + operateRecord.loc[operateRecord.index.values[0], '其他费']
    price     = round((money - fee) / amount, 3)
    costPrice = round(money / amount, 3)
    buyDate   = operateRecord.loc[operateRecord.index.values[0], '日期']
    asset.cash -= money
    if stockCode in asset.hold.index:
        # 已经有持仓了，计算平均成本
        #code price amount buydate fee
        asset.hold.loc[stockCode, 'fee'] += fee
        allMoney = asset.hold.loc[stockCode, 'amount'] * asset.hold.loc[stockCode, 'costPrice'] + amount * price + fee
        allAmount = asset.hold.loc[stockCode, 'amount'] + amount
        asset.hold.loc[stockCode, 'amount'] = allAmount
        asset.hold.loc[stockCode, 'costPrice'] = round(allMoney / allAmount, 3)
    else:
        # 没有持仓，新建一行
        temp = pd.Series([price, costPrice, amount, buyDate, fee], index=asset.hold.columns, name = stockCode)
        asset.hold = asset.hold.append(temp)

def pledgeRepoBuy(asset, operateRecord):
    #拆出质押购回 股市资金增。数量、均价、收付金额
    #数量是负的
    money     = operateRecord.loc[operateRecord.index.values[0], '收付金额']
    stockCode = operateRecord.loc[operateRecord.index.values[0], '证券代码']
    price     = operateRecord.loc[operateRecord.index.values[0], '成交均价']
    amount    = -operateRecord.loc[operateRecord.index.values[0], '发生数量']
    fee       = operateRecord.loc[operateRecord.index.values[0], '佣金'] + operateRecord.loc[operateRecord.index.values[0], '印花税'] + operateRecord.loc[operateRecord.index.values[0], '其他费']
    sellDate   = operateRecord.loc[operateRecord.index.values[0], '日期']
    asset.cash += money
    if amount < asset.hold.loc[stockCode, 'amount']:
        # 没卖完，数量减，重新计算成本
        # asset.hold.loc[stockCode, 'fee'] += fee
        allMoney = asset.hold.loc[stockCode, 'amount'] * asset.hold.loc[stockCode, 'costPrice'] - money + fee
        allAmount = asset.hold.loc[stockCode, 'amount'] - amount
        asset.hold.loc[stockCode, 'amount'] = allAmount
        asset.hold.loc[stockCode, 'costPrice'] = round(allMoney / allAmount, 3)
    else:
        # 卖完了
        asset.hold.drop([stockCode], inplace=True)

def payForIPOSubscriptionConfirmation(asset, operateRecord):
    # 新股申购确认缴款 股市资金减，总资金减，股票增。数量、均价、收付金额
    stockBuy(asset, operateRecord)
 
    
def updateNetAndReturnRate(allAsset):
    # net
    if allAsset[-2].netAsset != 0:
        changeRate = (allAsset[-1].netAsset - allAsset[-1].todayIn - allAsset[-2].netAsset) / allAsset[-2].netAsset
    else:
        changeRate = 0
    allAsset[-1].net = (1 + changeRate) * allAsset[-2].net
    if allAsset[-1].netAsset != 0:
        allAsset[-1].position = allAsset[-1].stockAsset / allAsset[-1].netAsset #仓位 当天总结算的时候更新
    else:
        allAsset[-1].position = 0
    

def endToday(allAsset):
    allAsset[-1].updateStockAsset()
    allAsset[-1].updateNetAsset()
    updateNetAndReturnRate(allAsset)

def newDay(allAsset):
    oldAsset = allAsset[-1]
    newAsset = oldAsset.copy()
    newAsset.date = newAsset.date + datetime.timedelta(days=1)
    newAsset.todayIn = 0
    allAsset.append(newAsset)


if __name__ == "__main__":
    # 读取数据
    tradeList = pd.read_excel('/Users/test/OneDrive/Project/Stock/Datum/40047552对账单/All.xlsx')
    # 生成一个初始asset list
    allAsset = []
    asset = Asset()
    allAsset.append(asset)
    # 新的一天开始
    print(tradeList.shape[0] - 1)
    for dayNum in range(tradeList.shape[0] - 1):
        newDay(allAsset)
        today = allAsset[-1].date
        todayDateNum = int(today.strftime("%Y%m%d")) # 这里从对账单里面读出来的是int类型的，不是字符串，所以要转换一下
        if todayDateNum == 20170102:
            a=1
        if todayDateNum == 20191206:
            break
        todayTradeOperateRecord = tradeList[tradeList.iloc[:, 0] == todayDateNum]
        # 处理盘中交易
        if not todayTradeOperateRecord.empty:
            for tradeIndex in todayTradeOperateRecord.index:
                operateRecord = todayTradeOperateRecord.loc[tradeIndex, :]
                if operateRecord.ndim == 1:
                    operateRecord = operateRecord.to_frame().T
                if operateRecord.loc[tradeIndex, '业务标志'] == '银行转存':
                    getMoneyFromBank(allAsset[-1], operateRecord)
                elif operateRecord.loc[tradeIndex, '业务标志'] == '银行转取':
                    withdrawMoneyToBank(allAsset[-1], operateRecord)
                elif operateRecord.loc[tradeIndex, '业务标志'] == '证券买入':
                    stockBuy(allAsset[-1], operateRecord)
                elif operateRecord.loc[tradeIndex, '业务标志'] == '证券卖出':
                    stockSell(allAsset[-1], operateRecord)
                elif operateRecord.loc[tradeIndex, '业务标志'] == '质押回购拆出':
                    pledgeRepoSell(allAsset[-1], operateRecord)
                elif operateRecord.loc[tradeIndex, '业务标志'] == '拆出质押购回':
                    pledgeRepoBuy(allAsset[-1], operateRecord)
                elif operateRecord.loc[tradeIndex, '业务标志'] == '新股申购':
                    newStockSubscription(allAsset[-1], operateRecord)
        # 更新当日持仓价格
        allAsset[-1].updateHoldPrice()
        # 处理盘后交易
        if not todayTradeOperateRecord.empty:
            for tradeIndex in todayTradeOperateRecord.index:
                operateRecord = todayTradeOperateRecord.loc[tradeIndex, :]
                if operateRecord.ndim == 1:
                    operateRecord = operateRecord.to_frame().T
                if operateRecord.loc[tradeIndex, '业务标志'] == '申购确认':
                    confirmSubscription(allAsset[-1], operateRecord)
                elif operateRecord.loc[tradeIndex, '业务标志'] == '赎回确认':
                    confirmRedemption(allAsset[-1], operateRecord)
                elif operateRecord.loc[tradeIndex, '业务标志'] == '红利发放':
                    bonusDistribution(allAsset[-1], operateRecord)
                elif operateRecord.loc[tradeIndex, '业务标志'] == '批量利息归本' or operateRecord.loc[tradeIndex, '业务标志'] == '利息归本':
                    bulkInterestReturn(allAsset[-1], operateRecord)
                elif operateRecord.loc[tradeIndex, '业务标志'] == '申购返款':
                    newStockSubscriptionRefund(allAsset[-1], operateRecord)
                elif operateRecord.loc[tradeIndex, '业务标志'] == '股息入账':
                    dividendAccounting(allAsset[-1], operateRecord)
                elif operateRecord.loc[tradeIndex, '业务标志'] == '股息红利税补缴':
                    dividendBonusTaxRepayment(allAsset[-1], operateRecord)
                elif operateRecord.loc[tradeIndex, '业务标志'] == '红股入账':
                    bonusAccount(allAsset[-1], operateRecord)
                elif operateRecord.loc[tradeIndex, '业务标志'] == '新股申购确认缴款':
                    payForIPOSubscriptionConfirmation(allAsset[-1], operateRecord)
        # 统计
        endToday(allAsset)
        # print(allAsset[-1].date.strftime("%Y-%m-%d") + ' cash:' + str(allAsset[-1].cash))
        print(str(dayNum) + ' ' + allAsset[-1].date.strftime("%Y-%m-%d") + \
            ' net:' + str(round(allAsset[-1].net, 2)) + \
            ' posi:' + str(round(allAsset[-1].position, 2)) + \
            ' netAsset:' + str(round(allAsset[-1].netAsset, 2)) + \
            ' stockAsset:' + str(round(allAsset[-1].stockAsset, 2)) + \
            ' todayIn:' + str(round(allAsset[-1].todayIn, 2)) + \
            ' cash:' + str(round(allAsset[-1].cash, 2)) + \
            ' cashFund:' + str(round(allAsset[-1].cashFund, 2)))
        a=1
    # 画图