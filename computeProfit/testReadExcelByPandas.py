import pandas as pd
comment = pd.read_excel('/Users/test/OneDrive/Project/Stock/Datum/40047552对账单/All.xlsx') #读入评论内容
data=comment[comment.iloc[:,0]==20140818]
print(data)
a=1