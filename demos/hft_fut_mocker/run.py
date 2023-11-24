import time
from wtpy import WtEngine,EngineType

import sys
sys.path.append('../Strategies')
from HftStraDemo import HftStraDemo

if __name__ == "__main__":
    #创建一个运行环境，并加入策略
    engine = WtEngine(EngineType.ET_HFT)
    engine.init('../common/', "config.yaml")
    engine.commitConfig()

    straInfo = HftStraDemo(name="hft_IF", code="CFFEX.IF.2304", expsecs=5, offset=100, freq=0)
    engine.add_hft_strategy(straInfo, 'mocker')
    
    engine.run()

    print('press ctrl-c to exit')
    try:
    	while True:
            time.sleep(1)
    except KeyboardInterrupt as e:
    	exit(0)