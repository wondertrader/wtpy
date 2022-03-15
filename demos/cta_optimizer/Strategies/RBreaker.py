from wtpy import BaseCtaStrategy
from wtpy import CtaContext

class StraRBreaker(BaseCtaStrategy):

    def __init__(self, name:str, code:str, barCnt:int, period:str, N:int, a:float, b:float, c:float, d:float, cleartimes:list):
        BaseCtaStrategy.__init__(self, name)

        self.__N__ = N
        self.__a__ = a
        self.__b__ = b
        self.__c__ = c
        self.__d__ = d

        self.__period__ = period
        self.__bar_cnt__ = barCnt
        self.__code__ = code
        self.__cleartimes__ = cleartimes    # 尾盘清仓需要多个时间区间，因为夜盘和白盘都要清仓，格式如[[1455,1515],[2255,2300]]

    def on_init(self, context:CtaContext):
        code = self.__code__
        context.stra_get_bars(code, self.__period__, self.__bar_cnt__, isMain = True)
        context.stra_log_text("R-Breaker inited")

    
    def on_calculate(self, context:CtaContext):
        code = self.__code__    #品种代码

        #读取当前仓位
        curPos = context.stra_get_position(code)
        curTime = context.stra_get_time()

        bCleared = False
        for tmPair in self.__cleartimes__:
            if curTime >= tmPair[0] and curTime <= tmPair[1]:
                if curPos != 0: # 如果持仓不为0，则要检查尾盘清仓
                    context.stra_set_position(code, 0, "clear") # 清仓直接设置仓位为0
                    context.stra_log_text("尾盘清仓")
                bCleared = True
                break

        if bCleared:
            return

        df_bars = context.stra_get_bars(code, self.__period__, self.__bar_cnt__, isMain = True)
        N = self.__N__
        a = self.__a__
        b = self.__b__
        c = self.__c__
        d = self.__d__

        #平仓价序列、最高价序列、最低价序列
        closes = df_bars["close"]
        highs = df_bars["high"]
        lows = df_bars["low"]

        #读取days天之前到上一个交易日位置的数据
        hh = highs[-N:].max()   #N条最高价
        ll = lows[-N:].min()    #N条最低价
        lc = closes.iloc[-1]    #最后收盘价

        Ssetup = hh + a * (lc - ll)
        Bsetup = ll - a * (hh - lc)
        Senter = b / 2 * (hh + ll) - c * ll
        Benter = b / 2 * (hh + ll) - c * hh
        Sbreak = Ssetup - d * (Ssetup - Bsetup)
        Bbreak = Bsetup + d * (Ssetup - Bsetup)

        curPx = lc  #最新价就是最后一个收盘价

        if curPos == 0:
            if curPx >= Bbreak:
                context.stra_enter_long(code, 1, 'rb-bbreak')
                context.stra_log_text("向上突破%.2f>=%.2f，多仓进场" % (curPx, Bbreak))
            elif curPx <= Sbreak:
                context.stra_enter_short(code, 1, 'rb-sbreak')
                context.stra_log_text("向下突破%.2f<=%.2f，空仓进场" % (curPx, Bbreak))
        elif curPos > 0:
            if curPx <= Senter:
                context.stra_enter_short(code, 1, 'rb-senter')
                context.stra_log_text("向下反转%.2f<=%.2f，多反空" % (curPx, Senter))
        elif curPos < 0:
            if curPx >= Benter:
                context.stra_enter_long(code, 1, 'rb-benter')
                context.stra_log_text("向上反转%.2f>=%.2f，空反多" % (curPx, Benter))


    def on_tick(self, context:CtaContext, code:str, newTick:dict):
        return

    def on_bar(self, context:CtaContext, code:str, period:str, newBar:dict):
        return

    
