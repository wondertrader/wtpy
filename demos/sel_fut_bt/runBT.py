from wtpy import WtBtEngine,EngineType

from Strategies.DualThrust_Sel import StraDualThrustSel

# from Strategies.XIM import XIM

if __name__ == "__main__":
    #创建一个运行环境，并加入策略
    engine = WtBtEngine(EngineType.ET_SEL)
    engine.init('.\\Common\\', "configbt.json")
    engine.configBacktest(201909100900,202008071500)
    engine.configBTStorage(mode="csv", path=".\\storage\\")
    engine.commitBTConfig()

    straInfo = StraDualThrustSel(name='DT_COMM_SEL', codes=["CFFEX.IF.HOT","SHFE.rb.HOT","DCE.i.HOT"], barCnt=50, period="m5", days=30, k1=0.1, k2=0.1)
    engine.set_sel_strategy(straInfo, time=5, period="min")

    engine.run_backtest()

    kw = input('press any key to exit\n')
    engine.release_backtest()