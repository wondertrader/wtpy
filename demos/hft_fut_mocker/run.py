from wtpy import WtEngine,EngineType
from strategies.HftStraDemo import HftStraDemo

if __name__ == "__main__":
    #创建一个运行环境，并加入策略
    engine = WtEngine(EngineType.ET_HFT)
    engine.init('../common/', "config.json")
    engine.commitConfig()

    straInfo = HftStraDemo(name="hft_IF", code="CFFEX.IF.2104", expsecs=5, offset=100, freq=0)
    engine.add_hft_strategy(straInfo, 'mocker')
    
    engine.run()

    kw = input('press any key to exit\n')