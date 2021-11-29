from wtpy.ExtModuleDefs import BaseExtDataLoader
from ctypes import POINTER
from wtpy.WtCoreDefs import WTSBarStruct, WTSTickStruct

import random

from wtpy import WtEngine,WtBtEngine,EngineType
from wtpy.apps import WtBtAnalyst
from Strategies.DualThrust import StraDualThrust

class MyDataLoader(BaseExtDataLoader):
    
    def load_his_bars(self, stdCode:str, period:str, feeder) -> bool:
        '''
        加载历史K线（回测、实盘）
        @stdCode    合约代码，格式如CFFEX.IF.2106
        @period     周期，m1/m5/d1
        @feeder     回调函数，feed_raw_bars(bars:POINTER(WTSBarStruct), count:int, factor:double)
        '''
        print("loading %s bars of %s from extended loader" % (period, stdCode))
        BarArray = WTSBarStruct*100
        ayBars = BarArray()
        for i in range(100):
            curBar:WTSBarStruct = ayBars[i]
            curBar.open = i*4
            curBar.high = i*4 + 1
            curBar.low = i*4 + 2
            curBar.close = i*4 + 3

        feeder(ayBars, 100, 1.0)
        return True

    def load_his_tick(self, stdCode:str, uDate:int, feeder) -> bool:
        '''
        加载历史K线（只在回测有效，实盘只提供当日落地的）
        @stdCode    合约代码，格式如CFFEX.IF.2106
        @uDate      日期，格式如yyyymmdd
        @feeder     回调函数，feed_raw_bars(bars:POINTER(WTSTickStruct), count:int)
        '''
        print("loading ticks on %d of %s from extended loader" % (uDate, stdCode))
        TickArray = WTSTickStruct*10
        ticks = TickArray()
        for i in range(10):
            ticks[i].exchg = bytes("CFFEX%d" % i, encoding="utf8")
            ticks[i].code = bytes("IF%04d" % i, encoding="utf8")
            ticks[i].price = random.random()

        feeder(ticks, 10)

def test_in_bt():
    engine = WtBtEngine(EngineType.ET_CTA)

    # 初始化之前，向回测框架注册加载器
    engine.set_extended_data_loader(MyDataLoader())

    engine.init('./common/', "configbt.json")

    engine.configBacktest(201909100930,201912011500)
    engine.configBTStorage(mode="csv", path="./storage/")
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

    engine.init('./common/', "config.json")
    
    straInfo = StraDualThrust(name='pydt_au', code="SHFE.au.HOT", barCnt=50, period="m5", days=30, k1=0.2, k2=0.2, isForStk=False)
    engine.add_cta_strategy(straInfo)

    engine.run()

    kw = input('press any key to exit\n')