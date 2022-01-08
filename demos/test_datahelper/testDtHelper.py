from wtpy.wrapper import WtDataHelper
from wtpy.WtCoreDefs import WTSBarStruct, WTSTickStruct
from ctypes import POINTER
from wtpy.SessionMgr import SessionMgr
import pandas as pd

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

class PickleReader:
    pd: pd.DataFrame

    def __len__(self) -> int:
        return len(self.pd)

    def load_ticks(self, filename:str) -> bool:
        self.pd = pd.read_pickle(filename)
        return True

    def get_tick(self, curTick:POINTER(WTSTickStruct), idx:int) -> bool:
        row = self.pd.iloc[idx]


        # open 	float 	开盘价
        # high 	float 	最高价
        # low 	float 	最低价
        # price 	float 	最新价
        # cum_volume 	float 	成交总量/最新成交量,累计值
        # cum_amount 	float 	成交总金额/最新成交额,累计值
        # trade_type 	int 	交易类型 1: ‘双开’, 2: ‘双平’, 3: ‘多开’, 4: ‘空开’, 5: ‘空平’, 6: ‘多平’, 7: ‘多换’, 8: ‘空换’
        # last_volume 	int 	瞬时成交额
        # cum_position 	int 	合约持仓量(期),累计值
        # last_amount 	float 	瞬时成交额
        # created_at 	datetime.datetime 	创建时间
        # quotes 	list[quote] 	期货提供买卖一档数据; 跌停时无买方报价，涨停时无卖方报价

        exchg,code = row.symbol.split('.', 1)
        curTick.contents.exchg = bytes(exchg, 'utf-8')
        curTick.contents.code = bytes(code.upper() if exchg=='CFFEX' or exchg=='CZCE' else code.lower(),'utf-8')

        curTick.contents.open = row.open
        curTick.contents.high = row.high
        curTick.contents.low = row.low
        curTick.contents.price = row.price

        curTick.contents.action_date = int(row.created_at.strftime("%Y%m%d"))
        curTick.contents.trading_date = int(row.created_at.strftime("%Y%m%d"))
        curTick.contents.action_time = int(row.created_at.strftime("%H%M%S"))*1000

        curTick.contents.total_volume = row.cum_volume
        curTick.contents.total_turnover = row.cum_amount
        curTick.contents.volume = row.last_volume
        curTick.contents.open_interest = row.cum_position

        curTick.contents.bid_prices[0] = row.quotes[0]['bid_p']
        curTick.contents.bid_qty[0] = row.quotes[0]['bid_v']

        curTick.contents.ask_prices[0] = row.quotes[0]['ask_p']
        curTick.contents.ask_qty[0] = row.quotes[0]['ask_v']

        print(curTick.contents)

        
        return True



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
# reader = CsvReader("../storage/csv/CFFEX.IC.HOT_m1.csv", isMin=True)
# dtHelper.trans_bars(barFile="./test_m1.dsb", getter=reader.get_bar, count=len(reader.lines), period="m1")

# 转储日线
# reader = CsvReader("../storage/csv/CFFEX.IC.HOT_d.csv", isMin=False)
# dtHelper.trans_bars(barFile="./test_d.dsb", getter=reader.get_bar, count=len(reader.lines), period="d")

# 转储tick
reader = PickleReader()
reader.load_ticks('./CZCE.ZC.2021-04-27.pkl')
dtHelper.trans_ticks(tickFile="./CZCE.ZC.2021-04-27.dsb", getter=reader.get_tick, count=10000)#len(reader)


# 测试重采样
# sessMgr = SessionMgr()
# sessMgr.load("sessions.json")
# sInfo = sessMgr.getSession("SD0930")
# ret = dtHelper.resample_bars("IC2009.dsb",'m1',5,202001010931,202009181500,sInfo)
# print(ret)