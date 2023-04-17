from wtpy import WtBtEngine,EngineType
from wtpy.apps import WtBtAnalyst

import sys
sys.path.append('../Strategies')
from DualThrust_Sel import StraDualThrustSel

# from Strategies.XIM import XIM

if __name__ == "__main__":
    #创建一个运行环境，并加入策略
    engine = WtBtEngine(EngineType.ET_SEL)
    engine.init('../common/', "configbt.yaml")
    engine.configBacktest(201909100900,202008071500)
    engine.configBTStorage(mode="csv", path="../storage/")
    engine.commitBTConfig()

    straInfo = StraDualThrustSel(name='DT_COMM_SEL', codes=["SHFE.rb.HOT","DCE.i.HOT"], barCnt=50, period="m5", days=30, k1=0.1, k2=0.1)
    engine.set_sel_strategy(straInfo, time=5, period="min")

    engine.run_backtest()

    analyst = WtBtAnalyst()
    #将回测的输出数据目录传递给绩效分析模块
    analyst.add_strategy("DT_COMM_SEL", folder="./outputs_bt/", init_capital=500000, rf=0.02, annual_trading_days=240)
    #运行绩效模块
    analyst.run_new()

    kw = input('press any key to exit\n')
    engine.release_backtest()