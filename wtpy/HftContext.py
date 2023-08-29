from ctypes import POINTER
from wtpy.SessionMgr import SessionInfo
from wtpy.WtCoreDefs import WTSBarStruct, WTSOrdDtlStruct, WTSOrdQueStruct, WTSTickStruct, WTSTransStruct
from wtpy.WtDataDefs import WtNpKline, WtNpOrdDetails, WtNpOrdQueues, WtNpTicks, WtNpTransactions

class HftContext:
    '''
    Context是策略可以直接访问的唯一对象
    策略所有的接口都通过Context对象调用
    Context类包括以下几类接口：
    1、时间接口（日期、时间等）,接口格式如：stra_xxx
    2、数据接口（K线、财务等）,接口格式如：stra_xxx
    3、下单接口（设置目标仓位、直接下单等）,接口格式如：stra_xxx
    '''

    def __init__(self, id:int, stra, wrapper, engine):
        self.__stra_info__ = stra       #策略对象,对象基类BaseStrategy.py
        self.__wrapper__ = wrapper      #底层接口转换器
        self.__id__ = id                #策略ID
        self.__bar_cache__ = dict()     #K线缓存
        self.__tick_cache__ = dict()    #Tick缓存
        self.__ordque_cache__ = dict()  #委托队列缓存
        self.__orddtl_cache__ = dict()  #逐笔委托缓存
        self.__trans_cache__ = dict()   #逐笔成交缓存
        self.__sname__ = stra.name()    
        self.__engine__ = engine          #交易环境

        self.is_backtest = self.__engine__.is_backtest

    @property
    def id(self):
        return self.__id__

    def on_init(self):
        '''
        初始化,一般用于系统启动的时候
        '''
        self.__stra_info__.on_init(self)

    def on_session_begin(self, curTDate:int):
        '''
        交易日开始事件

        @curTDate   交易日，格式为20210220
        '''
        self.__stra_info__.on_session_begin(self, curTDate)

    def on_session_end(self, curTDate:int):
        '''
        交易日结束事件

        @curTDate   交易日，格式为20210220
        '''
        self.__stra_info__.on_session_end(self, curTDate)

    def on_backtest_end(self):
        '''
        回测结束事件
        '''
        self.__stra_info__.on_backtest_end(self)

    def on_getticks(self, stdCode:str, newTicks:WtNpTicks):
        self.__tick_cache__[stdCode] = newTicks

    def on_getbars(self, stdCode:str, period:str, npBars:WtNpKline):
        key = "%s#%s" % (stdCode, period)
        self.__bar_cache__[key] = npBars

    def on_tick(self, stdCode:str, newTick:POINTER(WTSTickStruct)):
        '''
        tick回调事件响应
        '''
        self.__stra_info__.on_tick(self, stdCode, newTick.contents.to_dict)

    def on_order_queue(self, stdCode:str, newOrdQue:POINTER(WTSOrdQueStruct)):
        self.__stra_info__.on_order_queue(self, stdCode, newOrdQue.contents.to_tuple())

    def on_get_order_queue(self, stdCode:str, newOdrQues:WtNpOrdQueues):
        self.__ordque_cache__[stdCode] = newOdrQues

    def on_order_detail(self, stdCode:str, newOrdDtl:POINTER(WTSOrdDtlStruct)):
        self.__stra_info__.on_order_detail(self, stdCode, newOrdDtl.contents.to_tuple())

    def on_get_order_detail(self, stdCode:str, newOrdDtls:WtNpOrdDetails):
        self.__orddtl_cache__[stdCode] = newOrdDtls

    def on_transaction(self, stdCode:str, newTrans:POINTER(WTSTransStruct)):
        self.__stra_info__.on_transaction(self, stdCode, newTrans.contents.to_tuple())

    def on_get_transaction(self, stdCode:str, newTranses:WtNpTransactions):
        key = stdCode
        self.__trans_cache__[key] = newTranses

    def on_channel_ready(self):
        self.__stra_info__.on_channel_ready(self)

    def on_channel_lost(self):
        self.__stra_info__.on_channel_lost(self)

    def on_entrust(self, localid:int, stdCode:str, bSucc:bool, msg:str, userTag:str):
        self.__stra_info__.on_entrust(self, localid, stdCode, bSucc, msg, userTag)

    def on_position(self, stdCode:str, isLong:bool, prevol:float, preavail:float, newvol:float, newavail:float):
        self.__stra_info__.on_position(self, stdCode, isLong, prevol, preavail, newvol, newavail)

    def on_order(self, localid:int, stdCode:str, isBuy:bool, totalQty:float, leftQty:float, price:float, isCanceled:bool, userTag:str):
        self.__stra_info__.on_order(self, localid, stdCode, isBuy, totalQty, leftQty, price, isCanceled, userTag)

    def on_trade(self, localid:int, stdCode:str, isBuy:bool, qty:float, price:float, userTag:str):
        self.__stra_info__.on_trade(self, localid, stdCode, isBuy, qty, price, userTag)
        
    def on_bar(self, stdCode:str, period:str, newBar:POINTER(WTSBarStruct)):
        '''
        K线闭合事件响应
        @stdCode   品种代码
        @period     K线基础周期
        @times      周期倍数
        @newBar     最新K线
        '''        
        key = "%s#%s" % (stdCode, period)

        if key not in self.__bar_cache__:
            return
        
        try:
            self.__stra_info__.on_bar(self, stdCode, period, newBar.contents.to_dict)
        except ValueError as ve:
            print(ve)
        else:
            return

    def stra_log_text(self, message:str, level:int = 1):
        '''
        输出日志
        @level      日志级别，0-debug，1-info，2-warn，3-error
        @message    消息内容，最大242字符
        '''
        self.__wrapper__.hft_log_text(self.__id__, level, message[:242])
        
    def stra_get_date(self):
        '''
        获取当前日期
        @return int,格式如20180513
        '''
        return self.__wrapper__.hft_get_date()

    def stra_get_time(self):
        '''
        获取当前时间,24小时制,精确到分
        @return int,格式如1231
        '''
        return self.__wrapper__.hft_get_time()

    def stra_get_secs(self):
        '''
        获取当前秒数,精确到毫秒
        @return int,格式如1231
        '''
        return self.__wrapper__.hft_get_secs()

    def stra_get_price(self, stdCode):
        '''
        获取最新价格,一般在获取了K线以后再获取该价格
        @return 最新价格
        '''
        return self.__wrapper__.hft_get_price(stdCode)
    
    def stra_prepare_bars(self, stdCode:str, period:str, count:int):
        '''
        准备历史K线
        一般在on_init调用
        @stdCode   合约代码
        @period K线周期, 如m3/d7
        @count  要拉取的K线条数
        @isMain 是否是主K线
        '''

        self.__wrapper__.hft_get_bars(self.__id__, stdCode, period, count)

    def stra_get_bars(self, stdCode:str, period:str, count:int) -> WtNpKline:
        '''
        获取历史K线
        @stdCode   合约代码
        @period K线周期,如m3/d7
        @count  要拉取的K线条数
        @isMain 是否是主K线
        '''
        key = "%s#%s" % (stdCode, period)

        cnt =  self.__wrapper__.hft_get_bars(self.__id__, stdCode, period, count)
        if cnt == 0:
            return None

        return self.__bar_cache__[key]

    def stra_get_ticks(self, stdCode:str, count:int) -> WtNpTicks:
        '''
        获取tick数据
        @stdCode   合约代码
        @count  要拉取的tick数量
        '''
        cnt = self.__wrapper__.hft_get_ticks(self.__id__, stdCode, count)
        if cnt == 0:
            return None
        
        return self.__tick_cache__[stdCode]

    def stra_get_order_queue(self, stdCode:str, count:int) -> WtNpOrdQueues:
        '''
        获取委托队列数据
        @stdCode   合约代码
        @count  要拉取的tick数量
        '''
        cnt = self.__wrapper__.hft_get_ordque(self.__id__, stdCode, count)
        if cnt == 0:
            return None
        
        return  self.__ordque_cache__[stdCode]

    def stra_get_order_detail(self, stdCode:str, count:int) -> WtNpOrdDetails:
        '''
        获取逐笔委托数据
        @stdCode   合约代码
        @count  要拉取的tick数量
        '''
        if stdCode in self.__orddtl_cache__:
            #这里做一个数据长度处理
            return self.__orddtl_cache__[stdCode]

        cnt = self.__wrapper__.hft_get_orddtl(self.__id__, stdCode, count)
        if cnt == 0:
            return None
        
        return self.__orddtl_cache__[stdCode]

    def stra_get_transaction(self, stdCode:str, count:int) -> WtNpTransactions:
        '''
        获取逐笔成交数据
        @stdCode   合约代码
        @count  要拉取的tick数量
        '''
        cnt = self.__wrapper__.hft_get_trans(self.__id__, stdCode, count)
        if cnt == 0:
            return None
        
        return self.__trans_cache__[stdCode]

    def stra_get_position(self, stdCode:str, bonlyvalid:bool = False):
        '''
        读取当前仓位
        @stdCode    合约/股票代码
        @return     正为多仓,负为空仓
        '''
        return self.__wrapper__.hft_get_position(self.__id__, stdCode, bonlyvalid)

    def stra_get_position_profit(self, stdCode:str = ""):
        '''
        读取指定持仓的浮动盈亏
        @stdCode    合约/股票代码
        @return     指定持仓的浮动盈亏
        '''
        return self.__wrapper__.hft_get_position_profit(self.__id__, stdCode)

    def stra_get_position_avgpx(self, stdCode:str = ""):
        '''
        读取指定持仓的持仓均价
        @stdCode    合约/股票代码
        @return     指定持仓的浮动盈亏
        '''
        return self.__wrapper__.hft_get_position_avgpx(self.__id__, stdCode)

    def stra_get_undone(self, stdCode:str):
        return self.__wrapper__.hft_get_undone(self.__id__, stdCode)


    def user_save_data(self, key:str, val):
        '''
        保存用户数据
        @key    数据id
        @val    数据值,可以直接转换成str的数据均可
        '''
        self.__wrapper__.hft_save_user_data(self.__id__, key, str(val))

    def user_load_data(self, key:str, defVal = None, vType = float):
        '''
        读取用户数据
        @key    数据id
        @defVal 默认数据,如果找不到则返回改数据,默认为None
        @return 返回值,默认处理为float数据
        '''
        ret = self.__wrapper__.hft_load_user_data(self.__id__, key, "")
        if ret == "":
            return defVal

        return vType(ret)

    def stra_get_rawcode(self, stdCode:str):
        '''
        获取分月合约代码
        @stdCode   连续合约代码如SHFE.ag.HOT
        @return 品种信息,结构请参考ProductMgr中的ProductInfo
        '''
        if self.__engine__ is None:
            return ""
        return self.__engine__.getRawStdCode(stdCode)

    def stra_get_comminfo(self, stdCode:str):
        '''
        获取品种详情
        @stdCode   合约代码如SHFE.ag.HOT,或者品种代码如SHFE.ag
        @return 品种信息,结构请参考ProductMgr中的ProductInfo
        '''
        if self.__engine__ is None:
            return None
        return self.__engine__.getProductInfo(stdCode)
        
    def stra_get_sessinfo(self, stdCode:str) -> SessionInfo:
        '''
        获取交易时段详情
        @stdCode   合约代码如SHFE.ag.HOT，或者品种代码如SHFE.ag
        @return 品种信息，结构请参考SessionMgr中的SessionInfo
        '''
        if self.__engine__ is None:
            return None
        return self.__engine__.getSessionByCode(stdCode)

    def stra_sub_ticks(self, stdCode:str):
        '''
        订阅实时行情数据
        获取K线和tick数据的时候会自动订阅，这里只需要订阅额外要检测的品种即可
        @stdCode   品种代码
        '''
        self.__wrapper__.hft_sub_ticks(self.__id__, stdCode)

    def stra_cancel(self, localid:int):
        '''
        撤销指定订单
        @id         策略ID
        @localid    下单时返回的本地订单号
        '''
        return self.__wrapper__.hft_cancel(self.__id__, localid)

    def stra_cancel_all(self, stdCode:str, isBuy:bool):
        '''
        撤销指定品种的全部买入订单or卖出订单
        @id         策略ID
        @stdCode    品种代码
        @isBuy      买入or卖出
        '''
        idstr = self.__wrapper__.hft_cancel_all(self.__id__, stdCode, isBuy)
        if len(idstr) == 0:
            return list()

        ids = idstr.split(",")
        localids = list()
        for localid in ids:
            localids.append(int(localid))
        return localids

    def stra_buy(self, stdCode:str, price:float, qty:float, userTag:str = "", flag:int = 0):
        '''
        买入指令
        @id         策略ID
        @stdCode    品种代码
        @price      买入价格, 0为市价
        @qty        买入数量
        @flag       下单标志, 0-normal, 1-fak, 2-fok
        '''
        idstr = self.__wrapper__.hft_buy(self.__id__, stdCode, price, qty, userTag, flag)
        if len(idstr) == 0:
            return list()
            
        ids = idstr.split(",")
        localids = list()
        for localid in ids:
            localids.append(int(localid))
        return localids

    def stra_sell(self, stdCode:str, price:float, qty:float, userTag:str = "", flag:int = 0):
        '''
        卖出指令
        @id         策略ID
        @stdCode    品种代码
        @price      卖出价格, 0为市价
        @qty        卖出数量
        @flag       下单标志, 0-normal, 1-fak, 2-fok
        '''
        idstr = self.__wrapper__.hft_sell(self.__id__, stdCode, price, qty, userTag, flag)
        if len(idstr) == 0:
            return list()
            
        ids = idstr.split(",")
        localids = list()
        for localid in ids:
            localids.append(int(localid))
        return localids
    
    def stra_get_all_codes(self) -> list:
        '''
        获取全部合约代码列表
        '''
        if self.__engine__ is None:
            return []
        return self.__engine__.getAllCodes()
    
    def stra_get_codes_by_product(self, stdPID:str) -> list:
        '''
        根据品种代码读取合约列表
        @stdPID 品种代码，格式如SHFE.rb
        '''
        if self.__engine__ is None:
            return []
        return self.__engine__.getCodesByProduct(stdPID)
    
    def stra_get_codes_by_underlying(self, underlying:str) -> list:
        '''
        根据underlying读取合约列表
        @underlying 格式如CFFEX.IM2304
        '''
        if self.__engine__ is None:
            return []
        return self.__engine__.getCodesByUnderlying(underlying)
