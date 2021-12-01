

class BaseExtParser:
    '''
    扩展行情接入模块基类
    '''
    def __init__(self, id:str):
        '''
        构造函数
        @id     解析器ID
        '''
        self.__id__ = id
        return

    def id(self) -> str:
        return self.__id__

    def init(self, engine):
        '''
        初始化
        '''
        self.__engine__ = engine
        return

    def connect(self):
        '''
        开始连接
        '''
        return

    def disconnect(self):
        '''
        断开连接
        '''
        return

    def release(self):
        '''
        释放，一般是进程退出时调用
        '''
        return

    def subscribe(self, fullCode:str):
        '''
        订阅实时行情
        @fullCode   合约代码，格式如CFFEX.IF2106
        '''
        return

    def unsubscribe(self, fullCode:str):
        '''
        退订实时行情
        @fullCode   合约代码，格式如CFFEX.IF2106
        '''
        return


class BaseExtExecuter:
    '''
    扩展执行器基类
    '''

    def __init__(self, id:str, scale:float):
        '''
        构造函数
        @id     执行器ID
        @scale  数量放大倍数
        '''
        self.__id__ = id
        self.__scale__ = scale
        self.__targets__ = dict()
        return

    def id(self):
        return self.__id__
    
    def init(self):
        return

    def set_position(self, stdCode:str, targetPos:float):
        '''
        设置目标部位
        @stdCode    合约代码，期货格式为CFFEX.IF.2106
        @targetPos  目标仓位，浮点数
        '''

        # 确定原来的目标仓位
        oldPos = 0
        if stdCode in self.__targets__:
            oldPos = self.__targets__[stdCode]

        # 修改最新的目标仓位
        self.__targets__[stdCode] = targetPos
        return

class BaseExtDataLoader:

    def __init__(self):
        pass

    def load_his_bars(self, stdCode:str, period:str, feeder) -> bool:
        '''
        加载历史K线（回测、实盘）
        @stdCode    合约代码，格式如CFFEX.IF.2106
        @period     周期，m1/m5/d1
        @feeder     回调函数，feed_raw_bars(bars:POINTER(WTSBarStruct), count:int, factor:double)
        '''
        return True

    def load_his_tick(self, stdCode:str, uDate:int, feeder) -> bool:
        '''
        加载历史K线（只在回测有效，实盘只提供当日落地的）
        @stdCode    合约代码，格式如CFFEX.IF.2106
        @uDate      日期，格式如yyyymmdd
        @feeder     回调函数，feed_raw_bars(bars:POINTER(WTSTickStruct), count:int)
        '''
        return True

class BaseExtDataDumper:

    def __init__(self, id:str):
        self.__id__ = id

    def id(self):
        return self.__id__

    def dump_his_bars(self, stdCode:str, period:str, bars, count:int) -> bool:
        '''
        加载历史K线（回测、实盘）
        @stdCode    合约代码，格式如CFFEX.IF.2106
        @period     周期，m1/m5/d1
        @bars       回调函数，WTSBarStruct的指针
        @count      数据条数
        '''
        return True

    def dump_his_ticks(self, stdCode:str, uDate:int, ticks, count:int) -> bool:
        '''
        加载历史K线（只在回测有效，实盘只提供当日落地的）
        @stdCode    合约代码，格式如CFFEX.IF.2106
        @uDate      日期，格式如yyyymmdd
        @ticks      回调函数，WTSTickStruct的指针
        @count      数据条数
        '''
        return True