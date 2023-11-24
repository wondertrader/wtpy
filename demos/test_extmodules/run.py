import sys
from wtpy import BaseExtParser, BaseExtExecuter
from wtpy import WTSTickStruct
from ctypes import byref
import threading
import time

from wtpy import WtEngine,EngineType
sys.path.append('../Strategies')
from DualThrust import StraDualThrust


class MyExecuter(BaseExtExecuter):
    def __init__(self, id: str, scale: float):
        super().__init__(id, scale)

    def init(self):
        print("inited")

    def set_position(self, stdCode: str, targetPos: float):
        print("position confirmed: %s -> %f " % (stdCode, targetPos))

class MyParser(BaseExtParser):
    def __init__(self, id: str):
        super().__init__(id)
        self.__worker__ = None

    def init(self, engine:WtEngine):
        '''
        初始化
        '''
        super().init(engine)

    def random_sim(self):
        while True:
            curTick = WTSTickStruct()
            curTick.code = bytes("IF2106", encoding="UTF8")
            curTick.exchg = bytes("CFFEX", encoding="UTF8")

            self.__engine__.push_quote_from_extended_parser(self.__id__, byref(curTick), True)
            time.sleep(1)


    def connect(self):
        '''
        开始连接
        '''
        print("connect")
        if self.__worker__ is None:
            self.__worker__ = threading.Thread(target=self.random_sim, daemon=True)
            self.__worker__.start()
        return

    def disconnect(self):
        '''
        断开连接
        '''
        print("disconnect")
        return

    def release(self):
        '''
        释放，一般是进程退出时调用
        '''
        print("release")
        return

    def subscribe(self, fullCode:str):
        '''
        订阅实时行情\n
        @fullCode   合约代码，格式如CFFEX.IF2106
        '''
        # print("subscribe: " + fullCode)
        return

    def unsubscribe(self, fullCode:str):
        '''
        退订实时行情\n
        @fullCode   合约代码，格式如CFFEX.IF2106
        '''
        # print("unsubscribe: " + fullCode)
        return

if __name__ == "__main__":
    #创建一个运行环境，并加入策略
    engine = WtEngine(EngineType.ET_CTA)
    engine.init('../common/', "config.yaml")
    
    straInfo = StraDualThrust(name='pydt_au', code="SHFE.au.HOT", barCnt=50, period="m5", days=30, k1=0.2, k2=0.2, isForStk=False)
    engine.add_cta_strategy(straInfo)
    
    myParser = MyParser("test")
    myParser.init(engine)
    myExecuter = MyExecuter('exec', 1)
    engine.commitConfig()
    engine.add_exetended_parser(myParser)
    engine.add_exetended_executer(myExecuter)

    engine.run()

    print('press ctrl-c to exit')
    try:
    	while True:
            time.sleep(1)
    except KeyboardInterrupt as e:
    	exit(0)