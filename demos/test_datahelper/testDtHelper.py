from wtpy.wrapper import WtDataHelper
from wtpy.WtCoreDefs import WTSBarStruct, WTSTickStruct
from ctypes import POINTER

def strToDate(strDate:str) -> int:
    items = strDate.split("/")
    if len(items) == 1:
        items = strDate.split("-")

    if len(items) > 1:
        return int(items[0])*10000 + int(items[1])*100 + int(items[2])
    else:
        return int(strDate)

def strToTime(strTime:str) -> int:
    items = strTime.split(":")
    if len(items) > 1:
        return int(items[0])*100 + int(items[1])
    else:
        return int(strTime)

class CsvReader:
    def __init__(self, filename:str, isMin:bool = False):
        f = open(filename, 'r')
        content = f.read()
        lines = content.split("\n")
        self.lines = lines[1:]
        if len(self.lines[-1]) == 0:
            self.lines = self.lines[:-1]
        self.isMin = isMin

    def get_bar(self, curBar:POINTER(WTSBarStruct), idx:int) -> bool:
        if idx < 0 or idx >= len(self.lines):
            return False

        line = self.lines[idx]
        items = line.split(",")
        if not self.isMin:
            curBar.contents.date = strToDate(items[0])
            curBar.contents.open = float(items[1])
            curBar.contents.high = float(items[2])
            curBar.contents.low = float(items[3])
            curBar.contents.close = float(items[4])
            curBar.contents.vol = int(float(items[5]))
            curBar.contents.money = float(items[6])
        else:
            curBar.contents.date = strToDate(items[0])
            curBar.contents.time = (curBar.contents.date-19900000)*10000 + strToTime(items[1])
            curBar.contents.open = float(items[2])
            curBar.contents.high = float(items[3])
            curBar.contents.low = float(items[4])
            curBar.contents.close = float(items[5])
            curBar.contents.vol = int(float(items[6]))
            curBar.contents.money = float(items[7])

        return True

dtHelper = WtDataHelper()
# 转储分钟线
reader = CsvReader("./CFFEX.IC.HOT_m1.csv", isMin=True)
dtHelper.trans_bars(barFile="./test_m1.dsb", getter=reader.get_bar, count=len(reader.lines), period="m1")

# 转储日线
# reader = CsvReader("./CFFEX.IC.HOT_d.csv", isMin=False)
# dtHelper.trans_bars(barFile="./test_d.dsb", getter=reader.get_bar, count=len(reader.lines), period="d")
    