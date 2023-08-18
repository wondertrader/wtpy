from wtpy import BaseSelStrategy
from wtpy import SelContext
import numpy as np


class StraDualThrustSel(BaseSelStrategy):
    def __init__(self, name, codes:list, barCnt:int, period:str, days:int, k1:float, k2:float, isForStk:bool = False):
        BaseSelStrategy.__init__(self, name)

        self.__days__ = days
        self.__k1__ = k1
        self.__k2__ = k2

        self.__period__ = period
        self.__bar_cnt__ = barCnt
        self.__codes__ = codes

        self.__is_stk__ = isForStk
    

    def on_init(self, context:SelContext):
        return

    
    def on_calculate(self, context:SelContext):
        curTime = context.stra_get_time()
        trdUnit = 1
        if self.__is_stk__:
            trdUnit = 100

        for code in self.__codes__:
            sInfo = context.stra_get_sessioninfo(code)
            if not sInfo.isInTradingTime(curTime):
                continue

             #读取最近50条1分钟线(dataframe对象)
            theCode = code
            if self.__is_stk__:
                theCode = theCode + "Q"
            df_bars = context.stra_get_bars(theCode, self.__period__, self.__bar_cnt__)

            #把策略参数读进来，作为临时变量，方便引用
            days = self.__days__
            k1 = self.__k1__
            k2 = self.__k2__

            #平仓价序列、最高价序列、最低价序列
            closes = df_bars.closes
            highs = df_bars.highs
            lows = df_bars.lows

            #读取days天之前到上一个交易日位置的数据
            hh = np.amax(highs[-days:-1])
            hc = np.amax(closes[-days:-1])
            ll = np.amin(lows[-days:-1])
            lc = np.amin(closes[-days:-1])

            #读取今天的开盘价、最高价和最低价
            # lastBar = df_bars.get_last_bar()
            openpx = df_bars.opens[-1]
            highpx = df_bars.highs[-1]
            lowpx = df_bars.lows[-1]

            '''
            !!!!!这里是重点
            1、首先根据最后一条K线的时间，计算当前的日期
            2、根据当前的日期，对日线进行切片,并截取所需条数
            3、最后在最终切片内计算所需数据
            '''

            #确定上轨和下轨
            upper_bound = openpx + k1* max(hh-lc,hc-ll)
            lower_bound = openpx - k2* max(hh-lc,hc-ll)

            #读取当前仓位
            curPos = context.stra_get_position(code)/trdUnit

            if curPos == 0:
                if highpx >= upper_bound:
                    context.stra_set_position(code, 1*trdUnit, 'enterlong')
                    context.stra_log_text("{} 向上突破{}>={}，多仓进场".format(code, highpx, upper_bound))
                    continue

                if lowpx <= lower_bound and not self.__is_stk__:
                    context.stra_set_position(code, -1*trdUnit, 'entershort')
                    context.stra_log_text("{} 向下突破{}<={}，空仓进场".format(code, lowpx, lower_bound))
                    continue
            elif curPos > 0:
                if lowpx <= lower_bound:
                    context.stra_set_position(code, 0, 'exitlong')
                    context.stra_log_text("{} 向下突破{}<={}，多仓出场".format(code, lowpx, lower_bound))
                    #raise Exception("except on purpose")
                    continue
            else:
                if highpx >= upper_bound and not self.__is_stk__:
                    context.stra_set_position(code, 0, 'exitshort')
                    context.stra_log_text("{} 向上突破{}>={}，空仓出场".format(code, highpx, upper_bound))
                    continue


    def on_tick(self, context:SelContext, code:str, newTick:dict):
        return

    def on_bar(self, context:SelContext, code:str, period:str, newBar:dict):
        return