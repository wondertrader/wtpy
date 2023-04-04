from wtpy import WtBtEngine,EngineType
from wtpy.apps import WtBtAnalyst

import sys
sys.path.append('../Strategies')
from DualThrust import StraDualThrust

if __name__ == "__main__":
    #创建一个运行环境，并加入策略
    engine = WtBtEngine(EngineType.ET_CTA)
    engine.init(folder='../common/', cfgfile="configbt.yaml", commfile="stk_comms.json", contractfile="stocks.json")
    engine.configBacktest(201901010930,201912151500)
    engine.configBTStorage(mode="csv", path="../storage/")
    engine.commitBTConfig()
    
    straInfo = StraDualThrust(name='pydt_SH510300', code="SSE.ETF.510300", barCnt=50, period="m5", days=30, k1=0.1, k2=0.1)
    engine.set_cta_strategy(straInfo)

    engine.run_backtest()

    #绩效分析
    analyst = WtBtAnalyst()
    analyst.add_strategy("pydt_SH510300", folder="./outputs_bt/", init_capital=5000, rf=0.0, annual_trading_days=240)
    analyst.run()

    kw = input('press any key to exit\n')
    engine.release_backtest()