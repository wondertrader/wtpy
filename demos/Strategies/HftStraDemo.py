from wtpy import BaseHftStrategy
from wtpy import HftContext

from datetime import datetime

def makeTime(date:int, time:int, secs:int):
    '''
    将系统时间转成datetime\n
    @date   日期，格式如20200723\n
    @time   时间，精确到分，格式如0935\n
    @secs   秒数，精确到毫秒，格式如37500
    '''
    return datetime(year=int(date/10000), month=int(date%10000/100), day=date%100, 
        hour=int(time/100), minute=time%100, second=int(secs/1000), microsecond=secs%1000*1000)

class HftStraDemo(BaseHftStrategy):

    def __init__(self, name:str, code:str, expsecs:int, offset:int, freq:int=30):
        BaseHftStrategy.__init__(self, name)

        '''交易参数'''
        self.__code__ = code            #交易合约
        self.__expsecs__ = expsecs      #订单超时秒数
        self.__offset__ = offset        #指令价格偏移
        self.__freq__ = freq            #交易频率控制，指定时间内限制信号数，单位秒

        '''内部数据'''
        self.__last_tick__ = None       #上一笔行情
        self.__orders__ = dict()        #策略相关的订单
        self.__last_entry_time__ = None #上次入场时间
        self.__cancel_cnt__ = 0         #正在撤销的订单数
        self.__channel_ready__ = False  #通道是否就绪
        

    def on_init(self, context:HftContext):
        '''
        策略初始化，启动的时候调用\n
        用于加载自定义数据\n
        @context    策略运行上下文
        '''

        #先订阅实时数据
        context.stra_sub_ticks(self.__code__)

        self.__ctx__ = context

    def check_orders(self):
        #如果未完成订单不为空
        if len(self.__orders__.keys()) > 0 and self.__last_entry_time__ is not None:
            #当前时间，一定要从api获取，不然回测会有问题
            now = makeTime(self.__ctx__.stra_get_date(), self.__ctx__.stra_get_time(), self.__ctx__.stra_get_secs())
            span = now - self.__last_entry_time__
            if span.total_seconds() > self.__expsecs__: #如果订单超时，则需要撤单
                for localid in self.__orders__:
                    self.__ctx__.stra_cancel(localid)
                    self.__cancel_cnt__ += 1
                    self.__ctx__.stra_log_text("cancelcount -> %d" % (self.__cancel_cnt__))

    def on_tick(self, context:HftContext, stdCode:str, newTick:dict):
        if self.__code__ != stdCode:
            return

        #如果有未完成订单，则进入订单管理逻辑
        if len(self.__orders__.keys()) != 0:
            self.check_orders()
            return

        if not self.__channel_ready__:
            return

        self.__last_tick__ = newTick

        #如果已经入场，则做频率检查
        if self.__last_entry_time__ is not None:
            #当前时间，一定要从api获取，不然回测会有问题
            now = makeTime(self.__ctx__.stra_get_date(), self.__ctx__.stra_get_time(), self.__ctx__.stra_get_secs())
            span = now - self.__last_entry_time__
            if span.total_seconds() <= 30:
                return

        #信号标志
        signal = 0
        #最新价作为基准价格
        price = newTick["price"]
        #计算理论价格
        pxInThry = (newTick["bid_price_0"]*newTick["ask_qty_0"] + newTick["ask_price_0"]*newTick["bid_qty_0"]) / (newTick["ask_qty_0"] + newTick["bid_qty_0"])

        context.stra_log_text("理论价格%f，最新价：%f" % (pxInThry, price))

        if pxInThry > price:    #理论价格大于最新价，正向信号
            signal = 1
            context.stra_log_text("出现正向信号")
        elif pxInThry < price:  #理论价格小于最新价，反向信号
            signal = -1
            context.stra_log_text("出现反向信号")

        if signal != 0:
            #读取当前持仓
            curPos = context.stra_get_position(self.__code__)
            #读取品种属性，主要用于价格修正
            commInfo = context.stra_get_comminfo(self.__code__)
            #当前时间，一定要从api获取，不然回测会有问题
            now = makeTime(self.__ctx__.stra_get_date(), self.__ctx__.stra_get_time(), self.__ctx__.stra_get_secs())

            #如果出现正向信号且当前仓位小于等于0，则买入
            if signal > 0 and curPos <= 0:
                #买入目标价格=基准价格+偏移跳数*报价单位
                targetPx = price + commInfo.pricetick * self.__offset__

                #执行买入指令，返回所有订单的本地单号
                ids = context.stra_buy(self.__code__, targetPx, 1, "buy")

                #将订单号加入到管理中
                for localid in ids:
                    self.__orders__[localid] = localid
                
                #更新入场时间
                self.__last_entry_time__ = now

            #如果出现反向信号且当前持仓大于等于0，则卖出
            elif signal < 0 and curPos >= 0:
                #买入目标价格=基准价格-偏移跳数*报价单位
                targetPx = price - commInfo.pricetick * self.__offset__

                #执行卖出指令，返回所有订单的本地单号
                ids = context.stra_sell(self.__code__, targetPx, 1, "sell")

                #将订单号加入到管理中
                for localid in ids:
                    self.__orders__[localid] = localid
                
                #更新入场时间
                self.__last_entry_time__ = now


    def on_bar(self, context:HftContext, stdCode:str, period:str, newBar:dict):
        return

    def on_channel_ready(self, context:HftContext):
        undone = context.stra_get_undone(self.__code__)
        if undone != 0 and len(self.__orders__.keys()) == 0:
            context.stra_log_text("%s存在不在管理中的未完成单%f手，全部撤销" % (self.__code__, undone))
            isBuy = (undone > 0)
            ids = context.stra_cancel_all(self.__code__, isBuy)
            for localid in ids:
                self.__orders__[localid] = localid
            self.__cancel_cnt__ += len(ids)
            context.stra_log_text("cancelcnt -> %d" % (self.__cancel_cnt__))
        self.__channel_ready__ = True

    def on_channel_lost(self, context:HftContext):
        context.stra_log_text("交易通道连接丢失")
        self.__channel_ready__ = False

    def on_entrust(self, context:HftContext, localid:int, stdCode:str, bSucc:bool, msg:str, userTag:str):
        if bSucc:
            context.stra_log_text("%s下单成功，本地单号：%d" % (stdCode, localid))
        else:
            context.stra_log_text("%s下单失败，本地单号：%d，错误信息：%s" % (stdCode, localid, msg))

    def on_order(self, context:HftContext, localid:int, stdCode:str, isBuy:bool, totalQty:float, leftQty:float, price:float, isCanceled:bool, userTag:str):
        if localid not in self.__orders__:
            return

        if isCanceled or leftQty == 0:
            self.__orders__.pop(localid)
            if self.__cancel_cnt__ > 0:
                self.__cancel_cnt__ -= 1
                self.__ctx__.stra_log_text("cancelcount -> %d" % (self.__cancel_cnt__))
        return

    def on_trade(self, context:HftContext, localid:int, stdCode:str, isBuy:bool, qty:float, price:float, userTag:str):
        return
