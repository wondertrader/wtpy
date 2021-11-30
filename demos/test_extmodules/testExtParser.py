from wtpy import BaseExtParser, BaseExtExecuter
from wtpy import WTSTickStruct
from ctypes import byref
import threading
import time

from wtpy import WtEngine,EngineType



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
    myParser = MyParser("test")
    myExecuter = MyExecuter('exec', 1)
    #创建一个运行环境，并加入策略
    env = WtEngine(EngineType.ET_CTA)
    env.init('../common/', "config.json")
    env.commitConfig()
    env.add_exetended_parser(myParser)
    env.add_exetended_executer(myExecuter)
    
    env.run()

    kw = input('press any key to exit\n')