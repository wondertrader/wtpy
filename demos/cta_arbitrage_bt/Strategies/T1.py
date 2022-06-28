from wtpy import BaseCtaStrategy
from wtpy import CtaContext
import numpy as np
import statsmodels.tsa.stattools as ts

# 我们首先创建一个函数用来协整检验
def cointegration_check(series01, series02):
    urt_1 = ts.adfuller(np.array(series01), 1)[1]
    urt_2 = ts.adfuller(np.array(series02), 1)[1]

    # 同时平稳或不平稳则差分再次检验
    if (urt_1 > 0.1 and urt_2 > 0.1) or (urt_1 < 0.1 and urt_2 < 0.1):
        urt_diff_1 = ts.adfuller(np.diff(np.array(series01)), 1)[1]
        urt_diff_2 = ts.adfuller(np.diff(np.array(series02), 1))[1]

        # 同时差分平稳进行OLS回归的残差平稳检验
        if urt_diff_1 < 0.1 and urt_diff_2 < 0.1:
            matrix = np.vstack([series02, np.ones(len(series02))]).T
            beta, c = np.linalg.lstsq(matrix, series01, rcond=None)[0]
            resid = series01 - beta * series02 - c
            if ts.adfuller(np.array(resid), 1)[1] > 0.1:
                result = False
            else:
                result = True
            return beta, c, resid, result
        else:
            result = False
            return 0.0, 0.0, 0.0, result

    else:
        result = False
        return 0.0, 0.0, 0.0, result

class StraT1(BaseCtaStrategy):
    
    def __init__(self, name:str, code1:str, code2:str, bar_cnt:int, period:str, N:int, threshold:float=1):
        BaseCtaStrategy.__init__(self, name)

        self.__n__ = N
        self.__threshold__ = threshold

        self.__period__ = period
        self.__bar_cnt__ = bar_cnt
        self.__code_1__ = code1
        self.__code_2__ = code2

        self.__tradable__ = True

    def on_init(self, context:CtaContext):
        context.stra_get_bars(self.__code_1__, self.__period__, self.__bar_cnt__, isMain = True)
        context.stra_get_bars(self.__code_2__, self.__period__, self.__bar_cnt__, isMain = False)
        context.stra_log_text("T1 inited")

    
    def on_calculate(self, context:CtaContext):
        #读取当前仓位
        curPos1 = context.stra_get_position(self.__code_1__)
        curPos2 = context.stra_get_position(self.__code_2__)

        df_bars_1 = context.stra_get_bars(self.__code_1__, self.__period__, self.__bar_cnt__, isMain = True)
        df_bars_2 = context.stra_get_bars(self.__code_2__, self.__period__, self.__bar_cnt__, isMain = False)

        #把策略参数读进来，作为临时变量，方便引用
        days = self.__n__
        threshold = self.__threshold__

        close_ay1 = df_bars_1.closes
        close_ay2 = df_bars_2.closes

        maxlen = min(len(close_ay1), len(close_ay2))

        curDate = context.stra_get_date()
        curTime = context.stra_get_time()

        if curTime == 905:
            self.beta, self.c, resid, result = cointegration_check(close_ay1[-days-1:-1], close_ay2[-days-1:-1])
            self.__tradable__ = result
            if not result:
                if curPos1 != 0:
                    context.stra_log_text("[%d.%04d]协整检验不通过，清掉头寸" % (curDate, curTime))
                    context.stra_set_position(self.__code_1__, 0, 'CutA')
                    context.stra_set_position(self.__code_2__, 0, 'CutB')
                return
            # 计算残差的标准差上下轨
            mean = np.mean(resid)
            std = np.std(resid)
            self.up = mean + self.__threshold__ * std
            self.down = mean - self.__threshold__ * std

        if not self.__tradable__:
            return
        
        # 计算新残差
        resid_new = close_ay1[-1] - self.beta * close_ay2[-1] - self.c

        if resid_new > self.up and curPos1 != -1:
            # 做多价差，买入A，卖出B
            context.stra_log_text("[%d.%04d]残差正向扩大，做空价差" % (curDate, curTime))
            context.stra_enter_short(self.__code_1__, 1, 'OpenSA')
            context.stra_enter_long(self.__code_2__, 1, 'OpenLB')

        elif resid_new < self.down and curPos1 != 1:
            # 做空价差，卖出A，买入B
            context.stra_log_text("[%d.%04d]残差反向扩大，做多价差" % (curDate, curTime))
            context.stra_enter_long(self.__code_1__, 1, 'OpenLA')
            context.stra_enter_short(self.__code_2__, 1, 'OpenSB')

        elif curPos1 != 0 and self.down  <= resid_new and resid_new <= self.up:
            # 做多价差，买入A，卖出B
            context.stra_log_text("[%d.%04d]残差回归，清掉头寸" % (curDate, curTime))
            context.stra_set_position(self.__code_1__, 0, 'ExitA')
            context.stra_set_position(self.__code_2__, 0, 'ExitB')

    def on_tick(self, context:CtaContext, stdCode:str, newTick:dict):
        #context.stra_log_text ("on tick fired")
        return