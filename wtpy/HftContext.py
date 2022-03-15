from pandas import DataFrame as df
import pandas as pd
import os
import json

from wtpy.SessionMgr import SessionInfo
from wtpy.wrapper import WtWrapper
from wtpy.WtDataDefs import WtBarRecords, WtTickRecords, WtOrdDtlRecords, WtOrdQueRecords, WtTransRecords

class HftContext:
    '''
    Context是策略可以直接访问的唯一对象
    策略所有的接口都通过Context对象调用
    Context类包括以下几类接口：
    1、时间接口（日期、时间等）,接口格式如：stra_xxx
    2、数据接口（K线、财务等）,接口格式如：stra_xxx
    3、下单接口（设置目标仓位、直接下单等）,接口格式如：stra_xxx
    '''

    def __init__(self, id:int, stra, wrapper: WtWrapper, engine):
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

    def on_getticks(self, stdCode:str, newTicks:list):
        key = stdCode

        ticks = self.__tick_cache__[key]
        for newTick in newTicks:
            ticks.append(newTick)

    def on_getbars(self, stdCode:str, period:str, newBars:list, isLast:bool):
        key = "%s#%s" % (stdCode, period)

        bars = self.__bar_cache__[key]
        for newBar in newBars:
            bars.append(newBar)

    def on_tick(self, stdCode:str, newTick:tuple):
        '''
        tick回调事件响应
        '''

        # By Wesley @ 2021.12.24
        # 因为新的数据结构传进来是一个tuple
        # 所以必须通过缓存中抓一下，才能当成dict传给策略
        # 如果合约的tick没有缓存，则预先分配一个长度为4的tick容器
        # 如果调用stra_get_ticks，再重新分配容器
        if stdCode not in self.__tick_cache__:
            self.__tick_cache__[stdCode] = WtTickRecords(size = 4)

        self.__tick_cache__[stdCode].append(newTick)
        self.__stra_info__.on_tick(self, stdCode, self.__tick_cache__[stdCode][-1])

    def on_order_queue(self, stdCode:str, newOrdQue:tuple):
        # By Wesley @ 2021.12.24
        # 因为新的数据结构传进来是一个tuple
        # 所以必须通过缓存中抓一下，才能当成dict传给策略
        if stdCode not in self.__ordque_cache__:
            return

        self.__ordque_cache__[stdCode].append(newOrdQue)
        self.__stra_info__.on_order_queue(self, stdCode, self.__ordque_cache__[stdCode][-1])

    def on_get_order_queue(self, stdCode:str, newOdrQues:list):
        key = stdCode
        items = self.__ordque_cache__[key]
        for newItem in newOdrQues:
            items.append(newItem)

    def on_order_detail(self, stdCode:str, newOrdDtl:tuple):
        # By Wesley @ 2021.12.24
        # 因为新的数据结构传进来是一个tuple
        # 所以必须通过缓存中抓一下，才能当成dict传给策略
        if stdCode not in self.__orddtl_cache__:
            return

        self.__orddtl_cache__[stdCode].append(newOrdDtl)
        self.__stra_info__.on_order_detail(self, stdCode, self.__orddtl_cache__[stdCode][-1])

    def on_get_order_detail(self, stdCode:str, newOrdDtls:list):
        key = stdCode
        items = self.__orddtl_cache__[key]
        for newItem in newOrdDtls:
            items.append(newItem)

    def on_transaction(self, stdCode:str, newTrans:tuple):
        # By Wesley @ 2021.12.24
        # 因为新的数据结构传进来是一个tuple
        # 所以必须通过缓存中抓一下，才能当成dict传给策略
        if stdCode not in self.__trans_cache__:
            return

        self.__trans_cache__[stdCode].append(newTrans)
        self.__stra_info__.on_transaction(self, stdCode, self.__trans_cache__[stdCode][-1])

    def on_get_transaction(self, stdCode:str, newTranses:list):
        key = stdCode
        items = self.__trans_cache__[key]
        for newItem in newTranses:
            items.append(newItem)

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

    def on_bar(self, stdCode:str, period:str, newBar:tuple):
        '''
        K线闭合事件响应
        @stdCode   品种代码
        @period K线基础周期
        @times  周期倍数
        @newBar 最新K线
        '''        
        key = "%s#%s" % (stdCode, period)

        if key not in self.__bar_cache__:
            return

        try:
            self.__bar_cache__[key].append(newBar)

            # By Wesley @ 2021.12.24
            # 因为基础数据结构改变了，传进来的newBar是一个tuple，一定要通过缓存中转一下，才能当成dict传给策略
            self.__stra_info__.on_bar(self, stdCode, period, self.__bar_cache__[key][-1])
        except ValueError as ve:
            print(ve)
        else:
            return

    def stra_log_text(self, message:str):
        '''
        输出日志
        @message    消息内容
        '''
        self.__wrapper__.hft_log_text(self.__id__, message)
        
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

    def stra_get_bars(self, stdCode:str, period:str, count:int) -> WtBarRecords:
        '''
        获取历史K线
        @stdCode   合约代码
        @period K线周期,如m3/d7
        @count  要拉取的K线条数
        @isMain 是否是主K线
        '''
        key = "%s#%s" % (stdCode, period)

        if key in self.__bar_cache__:
            #这里做一个数据长度处理
            return self.__bar_cache__[key]

        self.__bar_cache__[key] = WtBarRecords(size=count)
        cnt =  self.__wrapper__.hft_get_bars(self.__id__, stdCode, period, count)
        if cnt == 0:
            return None

        df_bars = self.__bar_cache__[key]

        return df_bars

    def stra_get_ticks(self, stdCode:str, count:int) -> WtTickRecords:
        '''
        获取tick数据
        @stdCode   合约代码
        @count  要拉取的tick数量
        '''
        # By Wesley @ 2021.12.24
        # 之前在stra_get_bars的时候生成了一个size为4的临时tick缓存
        # 所以这里要加一个判断，如果没有缓存，或者缓存的长度为4，则重新分配新的缓存
        if stdCode in self.__tick_cache__ and self.__tick_cache__[stdCode].size > 4:
            #这里做一个数据长度处理
            return self.__tick_cache__[stdCode]

        self.__tick_cache__[stdCode] = WtTickRecords(size=count)
        cnt = self.__wrapper__.hft_get_ticks(self.__id__, stdCode, count)
        if cnt == 0:
            return None
        
        hftData = self.__tick_cache__[stdCode]
        return hftData

    def stra_get_order_queue(self, stdCode:str, count:int) -> WtOrdQueRecords:
        '''
        获取委托队列数据
        @stdCode   合约代码
        @count  要拉取的tick数量
        '''
        if stdCode in self.__ordque_cache__:
            #这里做一个数据长度处理
            return self.__ordque_cache__[stdCode]

        self.__ordque_cache__[stdCode] = WtOrdQueRecords(size=count)
        cnt = self.__wrapper__.hft_get_ordque(self.__id__, stdCode, count)
        if cnt == 0:
            return None
        
        hftData = self.__ordque_cache__[stdCode]
        return hftData

    def stra_get_order_detail(self, stdCode:str, count:int) -> WtOrdDtlRecords:
        '''
        获取逐笔委托数据
        @stdCode   合约代码
        @count  要拉取的tick数量
        '''
        if stdCode in self.__orddtl_cache__:
            #这里做一个数据长度处理
            return self.__orddtl_cache__[stdCode]

        self.__orddtl_cache__[stdCode] = WtOrdDtlRecords(size=count)
        cnt = self.__wrapper__.hft_get_orddtl(self.__id__, stdCode, count)
        if cnt == 0:
            return None
        
        hftData = self.__orddtl_cache__[stdCode]
        return hftData

    def stra_get_transaction(self, stdCode:str, count:int) -> WtTransRecords:
        '''
        获取逐笔成交数据
        @stdCode   合约代码
        @count  要拉取的tick数量
        '''
        if stdCode in self.__trans_cache__:
            #这里做一个数据长度处理
            return self.__trans_cache__[stdCode]

        self.__trans_cache__[stdCode] = WtTransRecords(size=count)
        cnt = self.__wrapper__.hft_get_trans(self.__id__, stdCode, count)
        if cnt == 0:
            return None
        
        hftData = self.__trans_cache__[stdCode]
        return hftData

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

    def stra_buy(self, stdCode:str, price:float, qty:float, userTag:str, flag:int = 0):
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

    def stra_sell(self, stdCode:str, price:float, qty:float, userTag:str, flag:int = 0):
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
