from wtpy.wrapper import WtDataHelper
from wtpy.WtCoreDefs import WTSBarStruct, WTSTickStruct
from ctypes import POINTER
from wtpy.SessionMgr import SessionMgr
import pandas as pd

dtHelper = WtDataHelper()

def test_store_bars():
    df = pd.read_csv('../storage/csv/CFFEX.IF.HOT_m5.csv')
    df = df.rename(columns={
        '<Date>':'date',
        ' <Time>':'time',
        ' <Open>':'open',
        ' <High>':'high',
        ' <Low>':'low',
        ' <Close>':'close',
        ' <Volume>':'vol',
        })
    df['date'] = df['date'].astype('datetime64').dt.strftime('%Y%m%d').astype('int64')
    df['time'] = (df['date']-19900000)*10000 + df['time'].str.replace(':', '').str[:-2].astype('int')

    BUFFER = WTSBarStruct*len(df)
    buffer = BUFFER()

    def assign(procession, buffer):
        tuple(map(lambda x: setattr(buffer[x[0]], procession.name, x[1]), enumerate(procession)))


    df.apply(assign, buffer=buffer)
    print(df)
    print(buffer[0].to_dict)
    print(buffer[-1].to_dict)

    dtHelper.store_bars(barFile="./CFFEX.IF.HOT_m5.bin", firstBar=buffer, count=len(df), period="m5")
    
def test_store_ticks():

    df = pd.read_csv('../storage/csv/rb主力连续_20201030.csv')
    BUFFER = WTSTickStruct*len(df)
    buffer = BUFFER()

    tags = ["一","二","三","四","五"]

    for i in range(len(df)):
        curTick = buffer[i]

        curTick.exchg = b"SHFE"
        curTick.code = b"SHFE.rb.HOT"

        curTick.price = float(df[i]["最新价"])
        curTick.open = float(df[i]["今开盘"])
        curTick.high = float(df[i]["最高价"])
        curTick.low = float(df[i]["最低价"])
        curTick.settle = float(df[i]["本次结算价"])
        
        curTick.total_volume = float(df[i]["数量"])
        curTick.total_turnover = float(df[i]["成交额"])
        curTick.open_interest = float(df[i]["持仓量"])

        curTick.trading_date = int(df[i]["交易日"])
        curTick.action_date = int(df[i]["业务日期"])
        curTick.action_time = int(df[i]["最后修改时间"].replace(":",""))*1000 + int(df[i]["最后修改毫秒"])

        curTick.pre_close = float(df[i]["昨收盘"])
        curTick.pre_settle = float(df[i]["上次结算价"])
        curTick.pre_interest = float(df[i]["昨持仓量"])

        for x in range(5):
            setattr(curTick, f"bid_price_{x}", float(df[i]["申买价"+tags[x]]))
            setattr(curTick, f"bid_qty_{x}", float(df[i]["申买量"+tags[x]]))
            setattr(curTick, f"ask_price_{x}", float(df[i]["申卖价"+tags[x]]))
            setattr(curTick, f"ask_qty_{x}", float(df[i]["申卖量"+tags[x]]))

    dtHelper.store_ticks(tickFile="./SHFE.rb.HOT_ticks.dsb", firstTick=buffer, count=len(df))

def test_resample():
    # 测试重采样
    sessMgr = SessionMgr()
    sessMgr.load("../common/sessions.json")
    sInfo = sessMgr.getSession("SD0930")
    ret = dtHelper.resample_bars("IC2212_m5.dsb",'m5',5,202201010931,202212311500,sInfo, True).to_df().to_csv("IC2212_m5.csv")
    print(ret)

import datetime
def compare_read_dsb_bars(times:int = 100):
    t2 = datetime.datetime.now()
    num_bars = 0
    for i in range(times):
        ret = dtHelper.read_dsb_bars("../storage/his/min5/CFFEX/CFFEX.IF_HOT.dsb")
        num_bars = len(ret)
    t3 = datetime.datetime.now()
    elapse = (t3-t2).total_seconds()*1000.0
    print(f"read_dsb_bars {num_bars} bars for {times} times: {elapse:.2f}ms totally, {elapse/times:.2f}ms per reading")

def compare_read_dsb_ticks(times:int = 100):
    t2 = datetime.datetime.now()
    for i in range(times):
        ret = dtHelper.read_dsb_ticks("../storage/bin/ticks/CFFEX.IF.HOT_tick_20210104.dsb")
        num_ticks = len(ret)
    t3 = datetime.datetime.now()
    elapse = (t3-t2).total_seconds()*1000.0
    print(f"read_dsb_ticks {num_ticks} ticks for {times} times: {elapse:.2f}ms totally, {elapse/times:.2f}ms per reading")

compare_read_dsb_bars()
compare_read_dsb_ticks()
