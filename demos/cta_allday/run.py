from wtpy import WtEngine,EngineType
from wtpy import BaseExtExecuter

import sys
import time

sys.path.append('../Strategies')
from DualThrust import StraDualThrust

class MyExecuter(BaseExtExecuter):
    def __init__(self, id: str, scale: float):
        super().__init__(id, scale)

    def init(self):
        print("inited")

    def set_position(self, stdCode: str, targetPos: float):
        print("position confirmed: %s -> %f " % (stdCode, targetPos))


if __name__ == "__main__":
    #创建一个运行环境，并加入策略
    env = WtEngine(EngineType.ET_CTA)
    env.init('./common/', "config.yaml", 
        contractfile="okex_tickers.json",
        sessionfile="btc_sessions.json",
        commfile=None,holidayfile=None,hotfile=None,secondfile=None)
    
    straInfo = StraDualThrust(name='pydt_okex', code="OKEX.BTC-USDT", barCnt=50, period="m1", days=30, k1=0.2, k2=0.2, isForStk=False)
    env.add_cta_strategy(straInfo)

    # 注册外部执行器
    myExecuter = MyExecuter('exec', 1)
    env.add_exetended_executer(myExecuter)

    env.run()

    print('press ctrl-c to exit')
    try:
    	while True:
            time.sleep(1)
    except KeyboardInterrupt as e:
    	exit(0)