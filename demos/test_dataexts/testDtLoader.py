import time
from wtpy.ExtModuleDefs import BaseExtDataLoader
from ctypes import POINTER
from wtpy.WtCoreDefs import WTSBarStruct, WTSTickStruct

import pandas as pd

import random

from wtpy import WtEngine,WtBtEngine,EngineType
from wtpy.apps import WtBtAnalyst
from Strategies.DualThrust import StraDualThrust

class MyDataLoader(BaseExtDataLoader):
    
    def load_final_his_bars(self, stdCode:str, period:str, feeder) -> bool:
        '''
        加载历史K线（回测、实盘）
        @stdCode    合约代码，格式如CFFEX.IF.2106
        @period     周期，m1/m5/d1
        @feeder     回调函数，feed_raw_bars(bars:POINTER(WTSBarStruct), count:int, factor:double)
        '''
        print("loading %s bars of %s from extended loader" % (period, stdCode))

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

        feeder(buffer, len(df))
        return True

    def load_his_ticks(self, stdCode:str, uDate:int, feeder) -> bool:
        '''
        加载历史K线（只在回测有效，实盘只提供当日落地的）
        @stdCode    合约代码，格式如CFFEX.IF.2106
        @uDate      日期，格式如yyyymmdd
        @feeder     回调函数，feed_raw_ticks(ticks:POINTER(WTSTickStruct), count:int)
        '''
        print("loading ticks on %d of %s from extended loader" % (uDate, stdCode))

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
                curTick.bid_prices[x] = float(df[i]["申买价"+tags[x]])
                curTick.bid_qty[x] = float(df[i]["申买量"+tags[x]])
                curTick.ask_prices[x] = float(df[i]["申卖价"+tags[x]])
                curTick.ask_qty[x] = float(df[i]["申卖量"+tags[x]])

        feeder(buffer, len(df))

def test_in_bt():
    engine = WtBtEngine(EngineType.ET_CTA)

    # 初始化之前，向回测框架注册加载器
    engine.set_extended_data_loader(loader=MyDataLoader(), bAutoTrans=False)

    engine.init('../common/', "configbt.yaml")

    engine.configBacktest(201909100930,201912011500)
    engine.configBTStorage(mode="csv", path="../storage/")
    engine.commitBTConfig()

    straInfo = StraDualThrust(name='pydt_IF', code="CFFEX.IF.HOT", barCnt=50, period="m5", days=30, k1=0.1, k2=0.1, isForStk=False)
    engine.set_cta_strategy(straInfo)

    engine.run_backtest()

    analyst = WtBtAnalyst()
    analyst.add_strategy("pydt_IF", folder="./outputs_bt/pydt_IF/", init_capital=500000, rf=0.02, annual_trading_days=240)
    analyst.run()

    kw = input('press any key to exit\n')
    engine.release_backtest()

def test_in_rt():
    engine = WtEngine(EngineType.ET_CTA)

    # 初始化之前，向实盘框架注册加载器
    engine.set_extended_data_loader(MyDataLoader())

    engine.init('../common/', "config.yaml")
    
    straInfo = StraDualThrust(name='pydt_au', code="SHFE.au.HOT", barCnt=50, period="m5", days=30, k1=0.2, k2=0.2, isForStk=False)
    engine.add_cta_strategy(straInfo)

    engine.run()

    print('press ctrl-c to exit')
    try:
    	while True:
            time.sleep(1)
    except KeyboardInterrupt as e:
    	exit(0)

test_in_bt()