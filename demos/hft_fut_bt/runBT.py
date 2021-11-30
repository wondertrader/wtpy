from wtpy import WtBtEngine, EngineType
from strategies.HftStraDemo import HftStraDemo

if __name__ == "__main__":
    # 创建一个运行环境，并加入策略
    engine = WtBtEngine(EngineType.ET_HFT)
    engine.init('../common/', "configbt.json")
    engine.configBacktest(202101040900,202101181500)
    engine.configBTStorage(mode="csv", path="../storage/")
    engine.commitBTConfig()

    straInfo = HftStraDemo(name='hft_IF',
                         code="CFFEX.IF.HOT",
                         expsecs=5,
                         offset=0,
                         freq=10)

    engine.set_hft_strategy(straInfo)

    engine.run_backtest()

    kw = input('press any key to exit\n')
    engine.release_backtest()
