from wtpy import WtBtEngine,EngineType
from wtpy.apps import WtBtAnalyst

import sys
sys.path.append('../Strategies')
from T1 import StraT1

if __name__ == "__main__":
    #创建一个运行环境，并加入策略
    engine = WtBtEngine(EngineType.ET_CTA)
    engine.init('../common/', "configbt.yaml")
    engine.configBacktest(201907310900,202008131500)
    engine.configBTStorage(mode="csv", path="../storage/")
    engine.commitBTConfig()

    straInfo = StraT1(name='t1_rb_i', code1="SHFE.rb.HOT", code2="DCE.i.HOT", bar_cnt=400, period="m5", N=360, threshold=0.9)
    engine.set_cta_strategy(straInfo)

    engine.run_backtest()

    analyst = WtBtAnalyst()
    analyst.add_strategy("t1_rb_i", folder="./outputs_bt/", init_capital=350000, rf=0.02, annual_trading_days=240)
    analyst.run_new()

    kw = input('press any key to exit\n')
    engine.release_backtest()