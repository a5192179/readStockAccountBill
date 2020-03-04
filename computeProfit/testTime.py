import datetime
dateBegin = datetime.datetime(1970, 1, 1, 0, 0, 0, 0)#719529
timestr='20200101 0:0:0' #737791
dateThisDay = datetime.datetime.strptime(timestr, "%Y%m%d %H:%M:%S")
# dateThisDay = datetime.datetime(0, 0, 0, 0, 0, 0, 0)
diff = (dateThisDay - dateBegin).days
num = 719529 + diff
print(dateThisDay.strftime("%Y%m%d"))
a=1