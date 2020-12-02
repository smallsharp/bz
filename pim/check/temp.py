from openpyxl import load_workbook
import time

start = time.time()

wb = load_workbook('./files/TM_CommonToRoss.xlsx')
ws = wb['0 运动-运动鞋-羽毛球鞋']

# for row in ws.iter_rows():
#     print(row)
from openpyxl.cell.cell import Cell
from openpyxl.cell.cell import MergedCell
from openpyxl.worksheet import worksheet

for row in ws.iter_rows(min_row=2, values_only=True):
    print(row)
    # for cell in row:
    #     # print(cell.value)
    #     print(cell)
    # pass

# for row in ws.values:
#     print(row)

end = time.time()

print(end - start)
# items = [1, 2, 3, 4, 5]
#
# for item in items[:3]:
#     print(item)
