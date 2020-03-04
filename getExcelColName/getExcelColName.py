import xlrd
import pandas as pd

excelPath = '/Users/test/OneDrive/Project/Stock/Datum/40047552对账单/All.xlsx'
outputPath = '/Users/test/OneDrive/Project/Stock/Datum/40047552对账单/operateName.txt'
book = xlrd.open_workbook(excelPath)
sheetName = 'Sheet1'
sheet = book.sheet_by_name(sheetName)
rows = sheet.nrows #获取行数
col = 5
colValues = []
for row in range(rows):
    value = sheet.cell(row, col).value
    bRecordBefore = False
    # if value == '红利发放':
    #     a=1
    for name in colValues:
        if value == name:
            bRecordBefore = True
            break
    if bRecordBefore:
        continue
    colValues.append(value)

colValuesPd = pd.Series(colValues)
colValuesPd.to_csv(outputPath, header = False, index = False) #保存txt,

