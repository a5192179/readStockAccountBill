import datetime

def getYesteray(dateStr):
    # dateStr example:'20141231'
    thisDay = datetime.datetime.strptime(dateStr, "%Y%m%d")
    yesterday = thisDay + datetime.timedelta(days = -1)
    yesterdayStr = yesterday.strftime("%Y%m%d")
    return yesterdayStr

def getTomorrow(dateStr):
    # dateStr example:'20141231'
    thisDay = datetime.datetime.strptime(dateStr, "%Y%m%d")
    tomorrow = thisDay + datetime.timedelta(days = 1)
    tomorrowStr = tomorrow.strftime("%Y%m%d")
    return tomorrowStr

def getLastYear(dateStr):
    thisDay = datetime.datetime.strptime(dateStr, "%Y%m%d")
    if int(dateStr[0:4]) % 4 == 0: 
        #闰年
        thisDayOfLastYear = thisDay + datetime.timedelta(days = -366)
    else:
        thisDayOfLastYear = thisDay + datetime.timedelta(days = -365)
    thisDayOfLastYearStr = thisDayOfLastYear.strftime("%Y%m%d")
    lastYear = thisDayOfLastYearStr[0:4]
    return lastYear

def isLastDayofThisYear(dateStr):
    thisDay = datetime.datetime.strptime(dateStr, "%Y%m%d")
    if thisDay.month == 12 and thisDay.day == 31:
        return True
    else:
        return False

if __name__ == '__main__':
    yesterday = getYesteray('20200315')
    # a=lastDayofThisYear('20201231')
    a=getLastYear('20191231')
    print(a)
    print(yesterday)

