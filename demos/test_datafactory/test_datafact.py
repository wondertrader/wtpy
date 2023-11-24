from ctypes import POINTER
import datetime
import os
from wtpy.WtCoreDefs import WTSBarStruct
from wtpy.apps.datahelper import DHFactory as DHF

hlper = DHF.createHelper("baostock")
hlper.auth()

# tushare
# hlper = DHF.createHelper("tushare")
# hlper.auth(**{"token":"xxxxxxxxxxx", "use_pro":True})

# rqdata
# hlper = DHF.createHelper("rqdata")
# hlper.auth(**{"username":"00000000", "password":"0000000"})

# 落地股票列表
# hlper.dmpCodeListToFile("stocks.json")

# 下载K线数据
# hlper.dmpBarsToFile(folder='./', codes=["CFFEX.IF.HOT","CFFEX.IC.HOT"], period='min1')
# hlper.dmpBarsToFile(folder='./', codes=["CFFEX.IF.HOT","CFFEX.IC.HOT"], period='min5')
hlper.dmpBarsToFile(folder='./', codes=["SZSE.399005","SZSE.399006","SZSE.399303"], period='day')

# 下载复权因子
# hlper.dmpAdjFactorsToFile(codes=["SSE.600000",'SZSE.000001'], filename="./adjfactors.json")

# 初始化数据库
# dbHelper = MysqlHelper("127.0.0.1","root","","test", 5306)
# dbHelper.initDB()

# 将数据下载到数据库
# hlper.dmpBarsToDB(dbHelper, codes=["CFFEX.IF.2103"], period="day")
# hlper.dmpAdjFactorsToDB(dbHelper, codes=["SSE.600000",'SSE.600001'])

# 将数据直接落地成dsb
def on_bars_block(exchg:str, stdCode:str, firstBar:POINTER(WTSBarStruct), count:int, period:str):
    from wtpy.wrapper import WtDataHelper
    dtHelper = WtDataHelper()
    if stdCode[-4:] == '.HOT':
        stdCode = stdCode[:-4] + "_HOT"
    else:
        ay = stdCode.split(".")
        if exchg == 'CZCE':
            stdCode = ay[1] + ay[2][1:]
        else:
            stdCode = ay[1] + ay[2]

    filename = f"../storage/his/{period}/{exchg}/"
    if not os.path.exists(filename):
        os.makedirs(filename)
    filename += f"{stdCode}.dsb"
    if period == "day":
        period = "d"
    elif period == "min1":
        period = "m1"
    else:
        period = "m5"
    dtHelper.store_bars(filename, firstBar, count, period)
    pass

# hlper.dmpBars(codes=["CFFEX.IF.2103"], cb=on_bars_block, start_date=datetime.datetime(2020,12,1), end_date=datetime.datetime(2021,3,16), period="min5")