import pandas as pd
import numpy as np
# comment = pd.read_excel('/Users/test/OneDrive/Project/Stock/Datum/40047552对账单/All.xlsx') #读入评论内容
data = {'state': ['Ohio', 'Ohio', 'Ohio', 'Nevada', 'Nevada', 'Nevada'],
        'year' : [2000, 2001, 2002, 2001, 2001, 2003],
        'pop'  : [1.5, 1.7,  3.6, 2.4, 2.9, 3.2]}
frame2 = pd.DataFrame(data, columns=['year', 'state', 'pop', 'debt'],
                            index=['one', 'two', 'three', 'four', 'five', 'six'])
s = pd.Series(['Ohio7', 2017, 1.8, 1], index=frame2.columns, name='seven')
frame2 = frame2.append(s, ignore_index=True)

data=pd.DataFrame(np.arange(16).reshape(4,4),index=list("ABCD"),columns=list("wxyz"))
print(data)

print(data[data.w>5])

a=1