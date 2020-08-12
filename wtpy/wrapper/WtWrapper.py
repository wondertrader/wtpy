from ctypes import cdll, c_int, c_char_p, c_longlong, c_bool, c_void_p, c_ulong, c_uint, c_uint64, c_double, POINTER
from wtpy.WtCoreDefs import CB_STRATEGY_INIT, CB_STRATEGY_TICK, CB_STRATEGY_CALC, CB_STRATEGY_BAR, CB_STRATEGY_GET_BAR, CB_STRATEGY_GET_TICK, CB_ENGINE_EVENT
from wtpy.WtCoreDefs import CB_HFTSTRA_CHNL_EVT, CB_HFTSTRA_ENTRUST, CB_HFTSTRA_ORD, CB_HFTSTRA_TRD
from wtpy.WtCoreDefs import CHNL_EVENT_READY, CHNL_EVENT_LOST
from wtpy.WtCoreDefs import WTSTickStruct,WTSBarStruct
import platform
import os
import sys

EVENT_ENGINE_INIT	= 1	    #框架初始化
EVENT_SESSION_BEGIN = 2	    #交易日开始
EVENT_SESSION_END	= 3	    #交易日结束
EVENT_ENGINE_SCHDL	= 4	    #框架调度

theEngine = None

def isPythonX64():
    ret = platform.architecture()
    return (ret[0] == "64bit")

def isWindows():
    if "windows" in platform.system().lower():
        return True

    return False

def on_engine_event(evtid, evtDate, evtTime):
    engine = theEngine
    if evtid == EVENT_ENGINE_INIT:
        engine.on_init()
    elif evtid == EVENT_ENGINE_SCHDL:
        engine.on_schedule(evtDate, evtTime)
    elif evtid == EVENT_SESSION_BEGIN:
        engine.on_session_begin(evtDate)
    elif evtid == EVENT_SESSION_END:
        engine.on_session_end(evtDate)
    return

#回调函数
def on_stra_init(id):
    engine = theEngine
    ctx = engine.get_context(id)
    if ctx is not None:
        ctx.on_init()
    return

def on_stra_tick(id, stdCode, newTick:POINTER(WTSTickStruct)):
    engine = theEngine
    ctx = engine.get_context(id)

    realTick = newTick.contents
    tick = dict()
    tick["time"] = realTick.action_date * 1000000000 + realTick.action_time
    tick["open"] = realTick.open
    tick["high"] = realTick.high
    tick["low"] = realTick.low
    tick["price"] = realTick.price
    tick["bidprice"] = list()
    tick["bidqty"] = list()
    tick["askprice"] = list()
    tick["askqty"] = list()

    for i in range(10):
        if realTick.bid_qty[i] != 0:
            tick["bidprice"].append(realTick.bid_prices[i])
            tick["bidqty"].append(realTick.bid_qty[i])

        if realTick.ask_qty[i] != 0:
            tick["askprice"].append(realTick.ask_prices[i])
            tick["askqty"].append(realTick.ask_qty[i])

    if ctx is not None:
        ctx.on_tick(bytes.decode(stdCode), tick)
    return

def on_stra_calc(id):
    engine = theEngine
    ctx = engine.get_context(id)
    if ctx is not None:
        ctx.on_calculate()
    return

def on_stra_bar(id, stdCode, period, newBar:POINTER(WTSBarStruct)):
    period = bytes.decode(period)
    engine = theEngine
    ctx = engine.get_context(id)
    newBar = newBar.contents
    curBar = dict()
    if period[0] == 'd':
        curBar["time"] = newBar.date
    else:
        curBar["time"] = 1990*100000000 + newBar.time
    curBar["bartime"] = curBar["time"]
    curBar["open"] = newBar.open
    curBar["high"] = newBar.high
    curBar["low"] = newBar.low
    curBar["close"] = newBar.close
    curBar["volumn"] = newBar.vol
    if ctx is not None:
        ctx.on_bar(bytes.decode(stdCode), period, curBar)
    return


def on_stra_get_bar(id, stdCode, period, curBar, isLast):
    '''
    获取K线回调，该回调函数因为是python主动发起的，需要同步执行，所以不走事件推送\n
    @id     策略id\n
    @stdCode   合约代码\n
    @period K线周期\n
    @curBar 最新一条K线\n
    @isLast 是否是最后一条
    '''
    engine = theEngine
    ctx = engine.get_context(id)
    realBar = None
    if curBar:
        realBar = curBar.contents

    period = bytes.decode(period)
    stdCode = bytes.decode(stdCode)

    bar = None
    if realBar is not None:
        bar = dict()
        if period[0] == 'd':
            bar["time"] = realBar.date
        else:
            bar["time"] = 1990*100000000 + realBar.time
        bar["bartime"] = bar["time"]
        bar["open"] = realBar.open
        bar["high"] = realBar.high
        bar["low"] = realBar.low
        bar["close"] = realBar.close
        bar["volumn"] = realBar.vol

    if ctx is not None:
        ctx.on_getbars(stdCode, period, bar, isLast)
    return

def on_stra_get_tick(id, stdCode, curTick, isLast):
    '''
    获取Tick回调，该回调函数因为是python主动发起的，需要同步执行，所以不走事件推送\n
    @id         策略id\n
    @stdCode       合约代码\n
    @curTick    最新一笔Tick\n
    @isLast     是否是最后一条
    '''

    engine = theEngine
    ctx = engine.get_context(id)
    realTick = None
    if curTick:
        realTick = curTick.contents

    tick = None
    if realTick is not None:
        tick = dict()
        tick["time"] = realTick.action_date * 1000000000 + realTick.action_time
        tick["open"] = realTick.open
        tick["high"] = realTick.high
        tick["low"] = realTick.low
        tick["price"] = realTick.price

    if ctx is not None:
        ctx.on_getticks(bytes.decode(stdCode), tick, isLast)
    return

def on_hftstra_channel_evt(id, trader, evtid):
    engine = theEngine
    ctx = engine.get_context(id)
    
    if evtid == CHNL_EVENT_READY:
        ctx.on_channel_ready()
    elif evtid == CHNL_EVENT_LOST:
        ctx.on_channel_lost()

def on_hftstra_order(id, localid, stdCode, isBuy, totalQty, leftQty, price, isCanceled):
    stdCode = bytes.decode(stdCode)
    engine = theEngine
    ctx = engine.get_context(id)
    ctx.on_order(localid, stdCode, isBuy, totalQty, leftQty, price, isCanceled)

def on_hftstra_trade(id, localid, stdCode, isBuy, qty, price):
    stdCode = bytes.decode(stdCode)
    engine = theEngine
    ctx = engine.get_context(id)
    ctx.on_trade(stdCode, isBuy, qty, price)

def on_hftstra_entrust(id, localid, stdCode, bSucc, message):
    stdCode = bytes.decode(stdCode)
    message = bytes.decode(message)
    engine = theEngine
    ctx = engine.get_context(id)
    ctx.on_entrust(localid, stdCode, bSucc, message)

'''
将回调函数转换成C接口识别的函数类型
''' 
cb_engine_event = CB_ENGINE_EVENT(on_engine_event)

cb_stra_init = CB_STRATEGY_INIT(on_stra_init)
cb_stra_tick = CB_STRATEGY_TICK(on_stra_tick)
cb_stra_calc = CB_STRATEGY_CALC(on_stra_calc)
cb_stra_bar = CB_STRATEGY_BAR(on_stra_bar)
cb_stra_get_bar = CB_STRATEGY_GET_BAR(on_stra_get_bar)
cb_stra_get_tick = CB_STRATEGY_GET_TICK(on_stra_get_tick)

cb_hftstra_chnl_evt = CB_HFTSTRA_CHNL_EVT(on_hftstra_channel_evt)
cb_hftstra_order = CB_HFTSTRA_ORD(on_hftstra_order)
cb_hftstra_trade = CB_HFTSTRA_TRD(on_hftstra_trade)
cb_hftstra_entrust = CB_HFTSTRA_ENTRUST(on_hftstra_entrust)

# Python对接C接口的库
class WtWrapper:
    '''
    Wt平台C接口底层对接模块
    '''

    # api可以作为公共变量
    api = None
    ver = "Unknown"
    
    # 构造函数，传入动态库名
    def __init__(self):
        paths = os.path.split(__file__)
        if isWindows(): #windows平台
            if isPythonX64():
                dllname = "x64/WtPorter.dll"
                a = (paths[:-1] + (dllname,))
                _path = os.path.join(*a)
                self.api = cdll.LoadLibrary(_path)
            else:
                dllname = "x86/WtPorter.dll"
                a = (paths[:-1] + (dllname,))
                _path = os.path.join(*a)
                self.api = cdll.LoadLibrary(_path)
        else:#Linux平台
            dllname = "linux/libWtPorter.so"
            a = (paths[:-1] + (dllname,))
            _path = os.path.join(*a)
            self.api = cdll.LoadLibrary(_path)
        self.api.get_version.restype = c_char_p
        self.api.cta_get_last_entertime.restype = c_uint64
        self.api.cta_get_first_entertime.restype = c_uint64
        self.api.cta_get_detail_entertime.restype = c_uint64
        self.api.cta_enter_long.argtypes = [c_ulong, c_char_p, c_double, c_char_p, c_double, c_double]
        self.api.cta_enter_short.argtypes = [c_ulong, c_char_p, c_double, c_char_p, c_double, c_double]
        self.api.cta_exit_long.argtypes = [c_ulong, c_char_p, c_double, c_char_p, c_double, c_double]
        self.api.cta_exit_short.argtypes = [c_ulong, c_char_p, c_double, c_char_p, c_double, c_double]
        self.api.cta_set_position.argtypes = [c_ulong, c_char_p, c_double, c_char_p, c_double, c_double]
        self.ver = bytes.decode(self.api.get_version())

        self.api.cta_save_userdata.argtypes = [c_ulong, c_char_p, c_char_p]
        self.api.cta_load_userdata.argtypes = [c_ulong, c_char_p, c_char_p]
        self.api.cta_load_userdata.restype = c_char_p

        self.api.cta_get_position.restype = c_double
        self.api.cta_get_position_profit.restype = c_double
        self.api.cta_get_position_avgpx.restype = c_double
        self.api.cta_get_detail_cost.restype = c_double
        self.api.cta_get_detail_profit.restype = c_double

        self.api.sel_save_userdata.argtypes = [c_ulong, c_char_p, c_char_p]
        self.api.sel_load_userdata.argtypes = [c_ulong, c_char_p, c_char_p]
        self.api.sel_load_userdata.restype = c_char_p
        self.api.sel_get_position.restype = c_double
        self.api.sel_set_position.argtypes = [c_ulong, c_char_p, c_double, c_char_p]

        self.api.hft_save_userdata.argtypes = [c_ulong, c_char_p, c_char_p]
        self.api.hft_load_userdata.argtypes = [c_ulong, c_char_p, c_char_p]
        self.api.hft_load_userdata.restype = c_char_p
        self.api.hft_get_position.restype = c_double
        self.api.hft_get_undone.restype = c_double

        self.api.hft_buy.restype = c_char_p
        self.api.hft_buy.argtypes = [c_ulong, c_char_p, c_double, c_double]
        self.api.hft_sell.restype = c_char_p
        self.api.hft_sell.argtypes = [c_ulong, c_char_p, c_double, c_double]
        self.api.hft_cancel_all.restype = c_char_p

    def run(self):
        self.api.run_porter(True)

    def release(self):
        self.api.release_porter()

    def write_log(self, level, message:str, catName:str = ""):
        self.api.write_log(level, bytes(message, encoding = "utf8").decode('utf-8').encode('gbk'), bytes(catName, encoding = "utf8"))

    def config(self, cfgfile:str = 'config.json'):
        self.api.config_porter(bytes(cfgfile, encoding = "utf8"))

    def initialize_cta(self, engine, logProfile:str = "logcfg.json"):
        '''
        C接口初始化
        '''
        global theEngine
        theEngine = engine
        try:
            self.api.register_evt_callback(cb_engine_event)
            self.api.register_cta_callbacks(cb_stra_init, cb_stra_tick, cb_stra_calc, cb_stra_bar)
            self.api.init_porter(bytes(logProfile, encoding = "utf8"))
        except OSError as oe:
            print(oe)

        self.write_log(102, "Wt交易框架已初始化完成，框架版本号：%s" % (self.ver))

    def initialize_hft(self, engine, logProfile:str = "logcfg.json"):
        '''
        C接口初始化
        '''
        global theEngine
        theEngine = engine
        try:
            self.api.register_evt_callback(cb_engine_event)
            self.api.register_hft_callbacks(cb_stra_init, cb_stra_tick, cb_stra_bar, cb_hftstra_chnl_evt, cb_hftstra_order, cb_hftstra_trade, cb_hftstra_entrust)
            self.api.init_porter(bytes(logProfile, encoding = "utf8"))
        except OSError as oe:
            print(oe)

        self.write_log(102, "Wt交易框架已初始化完成，框架版本号：%s" % (self.ver))

    def initialize_sel(self, engine, logProfile:str = "logcfg.json"):
        '''
        C接口初始化
        '''
        global theEngine
        theEngine = engine
        try:
            self.api.register_evt_callback(cb_engine_event)
            self.api.register_sel_callbacks(cb_stra_init, cb_stra_tick, cb_stra_calc, cb_stra_bar)
            self.api.init_porter(bytes(logProfile, encoding = "utf8"))
        except OSError as oe:
            print(oe)

        self.write_log(102, "Wt交易框架已初始化完成，框架版本号：%s" % (self.ver))

    def create_cta_context(self, name:str):
        '''
        创建策略环境\n
        @name      策略名称
        @return    系统内策略ID 
        '''
        return self.api.create_cta_context(bytes(name, encoding = "utf8") )

    def create_hft_context(self, name:str, trader:str):
        '''
        创建策略环境\n
        @name      策略名称
        @return    系统内策略ID 
        '''
        return self.api.create_hft_context(bytes(name, encoding = "utf8"), bytes(trader, encoding = "utf8") )

    def create_sel_context(self, name:str, date:int, time:int, period:str, trdtpl:str = 'CHINA', session:str = "TRADING"):
        '''
        创建策略环境\n
        @name      策略名称
        @return    系统内策略ID 
        '''
        return self.api.create_sel_context(bytes(name, encoding = "utf8"), date, time, 
            bytes(period, encoding = "utf8"), bytes(trdtpl, encoding = "utf8"), bytes(session, encoding = "utf8"))

    def reg_cta_factories(self, factFolder:str):
        return self.api.reg_cta_factories(bytes(factFolder, encoding = "utf8") )

    def reg_hft_factories(self, factFolder:str):
        return self.api.reg_hft_factories(bytes(factFolder, encoding = "utf8") )

    def reg_sel_factories(self, factFolder:str):
        return self.api.reg_sel_factories(bytes(factFolder, encoding = "utf8") )

    def reg_exe_factories(self, factFolder:str):
        return self.api.reg_exe_factories(bytes(factFolder, encoding = "utf8") )

    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    '''CTA接口'''
    def cta_enter_long(self, id:int, stdCode:str, qty:float, usertag:str, limitprice:float = 0.0, stopprice:float = 0.0):
        '''
        开多\n
        @id     策略id\n
        @stdCode   合约代码\n
        @qty    手数，大于等于0\n
        '''
        self.api.cta_enter_long(id, bytes(stdCode, encoding = "utf8"), qty, bytes(usertag, encoding = "utf8"), limitprice, stopprice)

    def cta_exit_long(self, id:int, stdCode:str, qty:float, usertag:str, limitprice:float = 0.0, stopprice:float = 0.0):
        '''
        平多\n
        @id     策略id\n
        @stdCode   合约代码\n
        @qty    手数，大于等于0\n
        '''
        self.api.cta_exit_long(id, bytes(stdCode, encoding = "utf8"), qty, bytes(usertag, encoding = "utf8"), limitprice, stopprice)

    def cta_enter_short(self, id:int, stdCode:str, qty:float, usertag:str, limitprice:float = 0.0, stopprice:float = 0.0):
        '''
        开空\n
        @id     策略id\n
        @stdCode   合约代码\n
        @qty    手数，大于等于0\n
        '''
        self.api.cta_enter_short(id, bytes(stdCode, encoding = "utf8"), qty, bytes(usertag, encoding = "utf8"), limitprice, stopprice)

    def cta_exit_short(self, id:int, stdCode:str, qty:float, usertag:str, limitprice:float = 0.0, stopprice:float = 0.0):
        '''
        平空\n
        @id     策略id\n
        @stdCode   合约代码\n
        @qty    手数，大于等于0\n
        '''
        self.api.cta_exit_short(id, bytes(stdCode, encoding = "utf8"), qty, bytes(usertag, encoding = "utf8"), limitprice, stopprice)

    def cta_get_bars(self, id:int, stdCode:str, period:str, count:int, isMain:bool):
        '''
        读取K线\n
        @id     策略id\n
        @stdCode   合约代码\n
        @period 周期，如m1/m3/d1等\n
        @count  条数\n
        @isMain 是否主K线
        '''
        return self.api.cta_get_bars(id, bytes(stdCode, encoding = "utf8"), bytes(period, encoding = "utf8"), count, isMain, cb_stra_get_bar)

    def cta_get_ticks(self, id:int, stdCode:str, count:int):
        '''
        读取Tick\n
        @id     策略id\n
        @stdCode   合约代码\n
        @count  条数\n
        '''
        return self.api.cta_get_ticks(id, bytes(stdCode, encoding = "utf8"), count, cb_stra_get_tick)

    def cta_get_position_profit(self, id:int, stdCode:str):
        '''
        获取浮动盈亏\n
        @id     策略id\n
        @stdCode   合约代码\n
        @return 指定合约的浮动盈亏
        '''
        return self.api.cta_get_position_profit(id, bytes(stdCode, encoding = "utf8"))

    def cta_get_position_avgpx(self, id:int, stdCode:str):
        '''
        获取持仓均价\n
        @id     策略id\n
        @stdCode   合约代码\n
        @return 指定合约的持仓均价
        '''
        return self.api.cta_get_position_avgpx(id, bytes(stdCode, encoding = "utf8"))
    
    def cta_get_position(self, id:int, stdCode:str, usertag:str = ""):
        '''
        获取持仓\n
        @id     策略id\n
        @stdCode   合约代码\n
        @usertag    进场标记，如果为空则获取该合约全部持仓\n
        @return 指定合约的持仓手数，正为多，负为空
        '''
        return self.api.cta_get_position(id, bytes(stdCode, encoding = "utf8"), bytes(usertag, encoding = "utf8"))

    def cta_get_price(self, stdCode:str):
        '''
        @stdCode   合约代码\n
        @return 指定合约的最新价格 
        '''
        return self.api.cta_get_price(bytes(stdCode, encoding = "utf8"))

    def cta_set_position(self, id:int, stdCode:str, qty:float, usertag:str = "", limitprice:float = 0.0, stopprice:float = 0.0):
        '''
        设置目标仓位\n
        @id     策略id
        @stdCode   合约代码\n
        @qty    目标仓位，正为多，负为空
        '''
        self.api.cta_set_position(id, bytes(stdCode, encoding = "utf8"), qty, bytes(usertag, encoding = "utf8"), limitprice, stopprice)

    def cta_get_date(self):
        '''
        获取当前日期\n
        @return    当前日期 
        '''
        return self.api.cta_get_date()

    def cta_get_time(self):
        '''
        获取当前时间\n
        @return    当前时间 
        '''
        return self.api.cta_get_time()

    def cta_get_first_entertime(self, id:int, stdCode:str):
        '''
        获取当前持仓的首次进场时间\n
        @stdCode       合约代码\n
        @return     进场时间，格式如201907260932 
        '''
        return self.api.cta_get_first_entertime(id, bytes(stdCode, encoding = "utf8"))

    def cta_get_last_entertime(self, id:int, stdCode:str):
        '''
        获取当前持仓的最后进场时间\n
        @stdCode       合约代码\n
        @return     进场时间，格式如201907260932 
        '''
        return self.api.cta_get_last_entertime(id, bytes(stdCode, encoding = "utf8"))

    def cta_log_text(self, id:int, message:str):
        '''
        日志输出\n
        @id         策略ID\n
        @message    日志内容
        '''
        self.api.cta_log_text(id, bytes(message, encoding = "utf8").decode('utf-8').encode('gbk'))

    def cta_get_detail_entertime(self, id:int, stdCode:str, usertag:str):
        '''
        获取指定标记的持仓的进场时间\n
        @id         策略id\n
        @stdCode       合约代码\n
        @usertag    进场标记\n
        @return     进场时间，格式如201907260932 
        '''
        return self.api.cta_get_detail_entertime(id, bytes(stdCode, encoding = "utf8"), bytes(usertag, encoding = "utf8")) 

    def cta_get_detail_cost(self, id:int, stdCode:str, usertag:str):
        '''
        获取指定标记的持仓的开仓价\n
        @id         策略id\n
        @stdCode       合约代码\n
        @usertag    进场标记\n
        @return     开仓价 
        '''
        return self.api.cta_get_detail_cost(id, bytes(stdCode, encoding = "utf8"), bytes(usertag, encoding = "utf8")) 

    def cta_get_detail_profit(self, id:int, stdCode:str, usertag:str, flag:int):
        '''
        获取指定标记的持仓的盈亏\n
        @id         策略id\n
        @stdCode       合约代码\n
        @usertag    进场标记\n
        @flag       盈亏记号，0-浮动盈亏，1-最大浮盈，2-最大亏损（负数）\n
        @return     盈亏 
        '''
        return self.api.cta_get_detail_profit(id, bytes(stdCode, encoding = "utf8"), bytes(usertag, encoding = "utf8"), flag) 

    def cta_save_user_data(self, id:int, key:str, val:str):
        '''
        保存用户数据\n
        @id         策略id\n
        @key        数据名\n
        @val        数据值
        '''
        self.api.cta_save_userdata(id, bytes(key, encoding = "utf8"), bytes(val, encoding = "utf8"))

    def cta_load_user_data(self, id:int, key:str, defVal:str  = ""):
        '''
        加载用户数据\n
        @id         策略id\n
        @key        数据名\n
        @defVal     默认值
        '''
        ret = self.api.cta_load_userdata(id, bytes(key, encoding = "utf8"), bytes(defVal, encoding = "utf8"))
        return bytes.decode(ret)

    def cta_sub_ticks(self, id:int, stdCode:str):
        '''
        订阅行情
        @id         策略id\n
        @stdCode    品种代码
        '''
        self.api.cta_sub_ticks(id, bytes(stdCode, encoding = "utf8"))
  
    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    '''SEL接口'''
    def sel_get_bars(self, id:int, stdCode:str, period:str, count:int):
        '''
        读取K线\n
        @id     策略id\n
        @stdCode   合约代码\n
        @period 周期，如m1/m3/d1等\n
        @count  条数
        '''
        return self.api.sel_get_bars(id, bytes(stdCode, encoding = "utf8"), bytes(period, encoding = "utf8"), count, cb_stra_get_bar)

    def sel_get_ticks(self, id:int, stdCode:str, count:int):
        '''
        读取Tick\n
        @id     策略id\n
        @stdCode   合约代码\n
        @count  条数\n
        '''
        return self.api.sel_get_ticks(id, bytes(stdCode, encoding = "utf8"), count, cb_stra_get_tick)

    def sel_save_user_data(self, id:int, key:str, val:str):
        '''
        保存用户数据\n
        @id         策略id\n
        @key        数据名\n
        @val        数据值
        '''
        self.api.sel_save_userdata(id, bytes(key, encoding = "utf8"), bytes(val, encoding = "utf8"))

    def sel_load_user_data(self, id:int, key:str, defVal:str  = ""):
        '''
        加载用户数据\n
        @id         策略id\n
        @key        数据名\n
        @defVal     默认值
        '''
        ret = self.api.sel_load_userdata(id, bytes(key, encoding = "utf8"), bytes(defVal, encoding = "utf8"))
        return bytes.decode(ret)

    def sel_get_position(self, id:int, stdCode:str, usertag:str = ""):
        '''
        获取持仓\n
        @id     策略id\n
        @stdCode   合约代码\n
        @usertag    进场标记，如果为空则获取该合约全部持仓\n
        @return 指定合约的持仓手数，正为多，负为空
        '''
        return self.api.sel_get_position(id, bytes(stdCode, encoding = "utf8"), bytes(usertag, encoding = "utf8"))

    def sel_get_price(self, stdCode:str):
        '''
        @stdCode   合约代码\n
        @return 指定合约的最新价格 
        '''
        return self.api.sel_get_price(bytes(stdCode, encoding = "utf8"))

    def sel_set_position(self, id:int, stdCode:str, qty:float, usertag:str = ""):
        '''
        设置目标仓位\n
        @id     策略id
        @stdCode   合约代码\n
        @qty    目标仓位，正为多，负为空
        '''
        self.api.sel_set_position(id, bytes(stdCode, encoding = "utf8"), qty, bytes(usertag, encoding = "utf8"))

    def sel_get_date(self):
        '''
        获取当前日期\n
        @return    当前日期 
        '''
        return self.api.sel_get_date()

    def sel_get_time(self):
        '''
        获取当前时间\n
        @return    当前时间 
        '''
        return self.api.sel_get_time()

    def sel_log_text(self, id:int, message:str):
        '''
        日志输出\n
        @id         策略ID\n
        @message    日志内容
        '''
        self.api.sel_log_text(id, bytes(message, encoding = "utf8").decode('utf-8').encode('gbk'))

    def sel_sub_ticks(self, id:int, stdCode:str):
        '''
        订阅行情
        @id         策略id\n
        @stdCode    品种代码
        '''
        self.api.sel_sub_ticks(id, bytes(stdCode, encoding = "utf8"))

    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    '''HFT接口'''
    def hft_get_bars(self, id:int, stdCode:str, period:str, count:int):
        '''
        读取K线\n
        @id     策略id\n
        @stdCode   合约代码\n
        @period 周期，如m1/m3/d1等\n
        @count  条数
        '''
        return self.api.hft_get_bars(id, bytes(stdCode, encoding = "utf8"), bytes(period, encoding = "utf8"), count, cb_stra_get_bar)

    def hft_get_ticks(self, id:int, stdCode:str, count:int):
        '''
        读取Tick\n
        @id     策略id\n
        @stdCode   合约代码\n
        @count  条数\n
        '''
        return self.api.hft_get_ticks(id, bytes(stdCode, encoding = "utf8"), count, cb_stra_get_tick)

    def hft_save_user_data(self, id:int, key:str, val:str):
        '''
        保存用户数据\n
        @id         策略id\n
        @key        数据名\n
        @val        数据值
        '''
        self.api.hft_save_userdata(id, bytes(key, encoding = "utf8"), bytes(val, encoding = "utf8"))

    def hft_load_user_data(self, id:int, key:str, defVal:str  = ""):
        '''
        加载用户数据\n
        @id         策略id\n
        @key        数据名\n
        @defVal     默认值
        '''
        ret = self.api.hft_load_userdata(id, bytes(key, encoding = "utf8"), bytes(defVal, encoding = "utf8"))
        return bytes.decode(ret)

    def hft_get_position(self, id:int, stdCode:str):
        '''
        获取持仓\n
        @id     策略id\n
        @stdCode   合约代码\n
        @return 指定合约的持仓手数，正为多，负为空
        '''
        return self.api.hft_get_position(id, bytes(stdCode, encoding = "utf8"))

    def hft_get_undone(self, id:int, stdCode:str):
        '''
        获取持仓\n
        @id     策略id\n
        @stdCode   合约代码\n
        @return 指定合约的持仓手数，正为多，负为空
        '''
        return self.api.hft_get_undone(id, bytes(stdCode, encoding = "utf8"))

    def hft_get_price(self, stdCode:str):
        '''
        @stdCode   合约代码\n
        @return 指定合约的最新价格 
        '''
        return self.api.hft_get_price(bytes(stdCode, encoding = "utf8"))

    def hft_get_date(self):
        '''
        获取当前日期\n
        @return    当前日期 
        '''
        return self.api.hft_get_date()

    def hft_get_time(self):
        '''
        获取当前时间\n
        @return    当前时间 
        '''
        return self.api.hft_get_time()

    def hft_get_secs(self):
        '''
        获取当前时间\n
        @return    当前时间 
        '''
        return self.api.hft_get_secs()

    def hft_log_text(self, id:int, message:str):
        '''
        日志输出\n
        @id         策略ID\n
        @message    日志内容
        '''
        self.api.hft_log_text(id, bytes(message, encoding = "utf8").decode('utf-8').encode('gbk'))

    def hft_sub_ticks(self, id:int, stdCode:str):
        '''
        订阅实时行情数据\n
        @id         策略ID\n
        @stdCode    品种代码
        '''
        self.api.hft_sub_ticks(id, bytes(stdCode, encoding = "utf8"))

    def hft_cancel(self, id:int, localid:int):
        '''
        撤销指定订单\n
        @id         策略ID\n
        @localid    下单时返回的本地订单号
        '''
        return self.api.hft_cancel(id, localid)

    def hft_cancel_all(self, id:int, stdCode:str, isBuy:bool):
        '''
        撤销指定品种的全部买入订单or卖出订单\n
        @id         策略ID\n
        @stdCode    品种代码\n
        @isBuy      买入or卖出
        '''
        ret = self.api.hft_cancel_all(id, bytes(stdCode, encoding = "utf8"), isBuy)
        return bytes.decode(ret)

    def hft_buy(self, id:int, stdCode:str, price:float, qty:float):
        '''
        买入指令\n
        @id         策略ID\n
        @stdCode    品种代码\n
        @price      买入价格, 0为市价\n
        @qty        买入数量
        '''
        ret = self.api.hft_buy(id, bytes(stdCode, encoding = "utf8"), price, qty)
        return bytes.decode(ret)

    def hft_sell(self, id:int, stdCode:str, price:float, qty:float):
        '''
        卖出指令\n
        @id         策略ID\n
        @stdCode    品种代码\n
        @price      卖出价格, 0为市价\n
        @qty        卖出数量
        '''
        ret = self.api.hft_sell(id, bytes(stdCode, encoding = "utf8"), price, qty)
        return bytes.decode(ret)