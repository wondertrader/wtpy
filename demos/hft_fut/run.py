import time
from wtpy import WtEngine, EngineType

import sys
sys.path.append('../Strategies')
from HftStraDemo import HftStraDemo

if __name__ == "__main__":
    #创建一个运行环境，并加入策略
    engine = WtEngine(EngineType.ET_HFT)

    #初始化执行环境，传入
    engine.init(folder = '../common/', cfgfile = "config.yaml")

    #设置数据存储目录
    # engine.configStorage(module="", path="D:\\WTP_Data\\")

    # 调用C++开发的HFT策略
    # engine.regHftStraFactories(factFolder = "../Strategies/")    
    # params = {
    #     "name":"WtHftStraFact.SimpleHft",
    #     "active": True,
    #     "params":{ 
    #         "code": "CFFEX.IF.HOT",
    #         "count": 50,
    #         "offset": 1,
    #         "second": 10,
    #         "stock": False
    #     },
    #     "trader": "simnow"
    # }
    # engine.addExternalHftStrategy(id = "hft_demo", params = params)

    engine.commitConfig()
    
    #添加Python版本的策略
    straInfo = HftStraDemo(name='pyhft_IF', code="CFFEX.IF.HOT", expsecs=15, offset=0, freq=30)
    engine.add_hft_strategy(straInfo, trader="simnow")
    
    #开始运行
    engine.run()

    print('press ctrl-c to exit')
    try:
    	while True:
            time.sleep(1)
    except KeyboardInterrupt as e:
    	exit(0)