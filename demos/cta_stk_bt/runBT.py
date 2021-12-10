from wtpy import WtBtEngine,EngineType
from Strategies.DualThrust import StraDualThrustStk
from wtpy.apps import WtBtAnalyst

if __name__ == "__main__":
    #创建一个运行环境，并加入策略
    engine = WtBtEngine(EngineType.ET_CTA)
    engine.init(folder='../common/', cfgfile="configbt.json", commfile="stk_comms.json", contractfile="stocks.json")
    engine.configBacktest(201901010930,201912151500)
    engine.configBTStorage(mode="csv", path="../storage/")
    engine.commitBTConfig()
    
    straInfo = StraDualThrustStk(name='pydt_SH510300', code="SSE.510300", barCnt=50, period="m1", days=30, k1=0.1, k2=0.1)
    engine.set_cta_strategy(straInfo)

    engine.run_backtest()

    #绩效分析
    analyst = WtBtAnalyst()
    analyst.add_strategy("pydt_SH510300", folder="./outputs_bt/pydt_SH510300/", init_capital=5000, rf=0.02, annual_trading_days=240)
    analyst.run()

    kw = input('press any key to exit\n')
    engine.release_backtest()