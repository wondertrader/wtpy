from wtpy import BaseCtaStrategy
import MyStrategy

from wtpy import WtBtEngine,EngineType
from wtpy.apps import WtBtAnalyst

def getStrategy():
    attrs = dir(MyStrategy)
    for symbol in attrs:
        tp = getattr(MyStrategy, symbol)
        if issubclass(tp, BaseCtaStrategy) and tp is not BaseCtaStrategy:
            return tp

    return None

def run_bt(fromTime:int, endTime:int, straid:str, init_capital:int=500000, slippage:int=0):
    StrategyType = getStrategy()
    if StrategyType is None:
        raise Exception("Module has no subtype of BaseCtaStrategy")
        return

    #创建一个运行环境，并加入策略
    engine = WtBtEngine(EngineType.ET_CTA)
    engine.init('../common/', "configbt.yaml")
    engine.configBacktest(fromTime, endTime)
    engine.configBTStorage(mode="csv", path="../storage")
    engine.commitBTConfig()

    straInfo = StrategyType(name=straid)
    engine.set_cta_strategy(straInfo, slippage)

    engine.run_backtest()

    analyst = WtBtAnalyst()
    analyst.add_strategy(straid, folder="./outputs_bt/%s/" % (straid), init_capital=init_capital, rf=0.02, annual_trading_days=240)
    analyst.run_new()
    analyst.run_simple()

    engine.release_backtest()

if __name__ == "__main__":
    run_bt($FROMTIME$, $ENDTIME$, "$STRAID$", $CAPITAL$, $SLIPPAGE$)