from wtpy import CtaContext, SelContext, HftContext

class BaseCtaStrategy:
    '''
    CTA策略基础类，所有的策略都从该类派生\n
    包含了策略的基本开发框架
    '''
    def __init__(self, name):
        self.__name__ = name
        
    
    def name(self):
        return self.__name__


    def on_init(self, context:CtaContext):
        '''
        策略初始化，启动的时候调用\n
        用于加载自定义数据\n
        @context    策略运行上下文
        '''
        return

    
    def on_calculate(self, context:CtaContext):
        '''
        K线闭合时调用，一般作为策略的核心计算模块\n
        @context    策略运行上下文
        '''
        return


    def on_tick(self, context:CtaContext, stdCode:str, newTick:dict):
        '''
        逐笔数据进来时调用\n
        生产环境中，每笔行情进来就直接调用\n
        回测环境中，是模拟的逐笔数据\n
        @context    策略运行上下文\n
        @stdCode    合约代码
        @newTick    最新逐笔
        '''
        return

    def on_bar(self, context:CtaContext, stdCode:str, period:str, newBar:dict):
        '''
        K线闭合时回调
        @context    策略上下文\n
        @stdCode    合约代码
        @period     K线周期
        @newBar     最新闭合的K线
        '''
        return

class BaseHftStrategy:
    '''
    HFT策略基础类，所有的策略都从该类派生\n
    包含了策略的基本开发框架
    '''
    def __init__(self, name):
        self.__name__ = name
        
    
    def name(self):
        return self.__name__


    def on_init(self, context:HftContext):
        '''
        策略初始化，启动的时候调用\n
        用于加载自定义数据\n
        @context    策略运行上下文
        '''
        return



    def on_tick(self, context:HftContext, stdCode:str, newTick:dict):
        '''
        逐笔数据进来时调用\n
        生产环境中，每笔行情进来就直接调用\n
        回测环境中，是模拟的逐笔数据\n
        @context    策略运行上下文\n
        @stdCode    合约代码\n
        @newTick    最新逐笔
        '''
        return

    def on_bar(self, context:HftContext, stdCode:str, period:str, newBar:dict):
        '''
        K线闭合时回调
        @context    策略上下文\n
        @stdCode    合约代码
        @period     K线周期
        @newBar     最新闭合的K线
        '''
        return

    def on_channel_ready(self, context:HftContext):
        '''
        交易通道就绪通知\n
        @context    策略上下文\n
        '''
        return

    def on_channel_lost(self, context:HftContext):
        '''
        交易通道丢失通知\n
        @context    策略上下文\n
        '''
        return

    def on_entrust(self, context:HftContext, localid:int, stdCode:str, bSucc:bool, msg:str):
        '''
        下单结果回报
        @context    策略上下文\n
        @localid    本地订单id\n
        @stdCode    合约代码\n
        @bSucc      下单结果\n
        @mes        下单结果描述
        '''
        return

    def on_order(self, context:HftContext, localid:int, stdCode:str, isBuy:bool, totalQty:float, leftQty:float, price:float, isCanceled:bool):
        '''
        订单回报
        @context    策略上下文\n
        @localid    本地订单id\n
        @stdCode    合约代码\n
        @isBuy      是否买入\n
        @totalQty   下单数量\n
        @leftQty    剩余数量\n
        @price      下单价格\n
        @isCanceled 是否已撤单
        '''
        return

    def on_trade(self, context:HftContext, stdCode:str, isBuy:bool, qty:float, price:float):
        '''
        成交回报
        @context    策略上下文\n
        @stdCode    合约代码\n
        @isBuy      是否买入\n
        @qty        成交数量\n
        @price      成交价格
        '''
        return

class BaseSelStrategy:
    '''
    选股策略基础类，所有的多因子策略都从该类派生\n
    包含了策略的基本开发框架
    '''
    def __init__(self, name):
        self.__name__ = name
        
    
    def name(self):
        return self.__name__


    def on_init(self, context:SelContext):
        '''
        策略初始化，启动的时候调用\n
        用于加载自定义数据\n
        @context    策略运行上下文
        '''
        return

    
    def on_calculate(self, context:SelContext):
        '''
        K线闭合时调用，一般作为策略的核心计算模块\n
        @context    策略运行上下文
        '''
        return


    def on_tick(self, context:SelContext, stdCode:str, newTick:dict):
        '''
        逐笔数据进来时调用\n
        生产环境中，每笔行情进来就直接调用\n
        回测环境中，是模拟的逐笔数据\n
        @context    策略运行上下文\n
        @stdCode    合约代码\n
        @newTick    最新逐笔
        '''
        return

    def on_bar(self, context:SelContext, stdCode:str, period:str, newBar:dict):
        '''
        K线闭合时回调
        @context    策略上下文\n
        @stdCode    合约代码\n
        @period     K线周期\n
        @newBar     最新闭合的K线
        '''
        return