from wtpy import BaseCtaStrategy
from wtpy import CtaContext
import numpy as np

class StraDualThrust(BaseCtaStrategy):
    
    def __init__(self, name:str, code:str, barCnt:int, period:str, days:int, k1:float, k2:float, isForStk:bool = False):
        BaseCtaStrategy.__init__(self, name)

        self.__days__ = days
        self.__k1__ = k1
        self.__k2__ = k2

        self.__period__ = period
        self.__bar_cnt__ = barCnt
        self.__code__ = code

        self.__is_stk__ = isForStk

    def on_init(self, context:CtaContext):
        code = self.__code__    #品种代码
        if self.__is_stk__:
            code = code + "Q"




        context.stra_get_bars(code, self.__period__, self.__bar_cnt__, isMain = True)
        context.stra_log_text("DualThrust inited")

        #读取存储的数据
        self.xxx = context.user_load_data('xxx',1)

    
    def on_calculate(self, context:CtaContext):
        code = self.__code__    #品种代码

        trdUnit = 1
        if self.__is_stk__:
            trdUnit = 100

        #读取最近50条1分钟线(dataframe对象)
        theCode = code
        if self.__is_stk__:
            theCode = theCode + "Q"
        df_bars = context.stra_get_bars(theCode, self.__period__, self.__bar_cnt__, isMain = True)

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

        # 向外输出指标
        lastBar = df_bars.get_bar(-1)
        timePx = lastBar["bartime"]
        now = context.stra_get_date()*10000 + timePx%10000
        context.write_indicator(tag=self.__period__, time=int(now), data={
            "highpx": highpx,
            "lowpx": lowpx,
            "upper_bound": upper_bound,
            "lower_bound": lower_bound,
            "current_position": curPos
        })
        # 测试各个接口
        #这里演示了品种信息获取的接口
        pInfo = context.stra_get_comminfo(code)
        print(pInfo)
        # 交易时段详情接口测试
        sinfo = context.stra_get_sessinfo(code)
        print(sinfo)
        test_tdate = context.stra_get_tdate()
        context.stra_log_text('当前交易日:{}'.format(test_tdate))
        test_ndate = context.stra_get_date()
        context.stra_log_text('当前日期:{}'.format(test_ndate))
        test_time = context.stra_get_time()
        context.stra_log_text('当前时间:{}'.format(test_time))
        context.stra_log_text('输出日志测试:123456')
        tbars = context.stra_get_bars(code, self.__period__, self.__bar_cnt__, True)
        context.stra_log_text('K线数据,最高价:{}'.format(tbars.highs))
        test_ticks = context.stra_get_ticks(code, 10)
        context.stra_log_text('tick数据:{}'.format(test_ticks))
        test_sticks = context.stra_sub_ticks(code)
        context.stra_log_text('实时行情:{}'.format(test_sticks))
        test_price = context.stra_get_price(code)
        context.stra_log_text('最新价格:{}'.format(test_price))
        test_position = context.stra_get_position(code)
        context.stra_log_text('持仓部位:{}'.format(test_position))
        test_position_avg = context.stra_get_position_avgpx()
        context.stra_log_text('持仓均价:{}'.format(test_position_avg))
        test_position_profit = context.stra_get_position_profit(code)
        context.stra_log_text('持仓盈亏:{}'.format(test_position_profit))
        test_all_position = context.stra_get_all_position()
        context.stra_log_text('全部持仓：{}'.format(test_all_position))
        test_fund_data = context.stra_get_fund_data(0)
        context.stra_log_text('资金数据：{}'.format(test_fund_data))
        test_last_entry = context.stra_get_last_entrytime(code)
        context.stra_log_text('最后入场时间:{}'.format(test_last_entry))
        test_last_exit = context.stra_get_last_exittime(code)
        context.stra_log_text('最后出场时间：{}'.format(test_last_exit))
        test_first_entry = context.stra_get_first_entrytime(code)
        context.stra_log_text('当前持仓第一次进场时间:{}'.format(test_first_entry))
        test_detail_cost = context.stra_get_detail_cost(code, usertag='enterlong')
        context.stra_log_text('指定信号的进场价格：{}'.format(test_detail_cost))
        test_detail_enter = context.stra_get_detail_entertime(code, usertag='enterlong')
        context.stra_log_text('指定信号进场时间:{}'.format(test_detail_enter))
        test_detail_profit = context.stra_get_detail_profit(code, usertag='enterlong')
        context.stra_log_text('指定信号的持仓盈亏:{}'.format(test_detail_profit))

        if curPos == 0:
            if highpx >= upper_bound:
                context.stra_enter_long(code, 1*trdUnit, 'enterlong')
                # context.stra_log_text("向上突破%.2f>=%.2f，多仓进场" % (highpx, upper_bound))
                #修改并保存
                self.xxx = 1
                context.user_save_data('xxx', self.xxx)
                return

            if lowpx <= lower_bound and not self.__is_stk__:
                context.stra_enter_short(code, 1*trdUnit, 'entershort')
                context.stra_log_text("向下突破%.2f<=%.2f，空仓进场" % (lowpx, lower_bound))
                return
        elif curPos > 0:
            if lowpx <= lower_bound:
                context.stra_exit_long(code, 1*trdUnit, 'exitlong')
                # context.stra_log_text("向下突破%.2f<=%.2f，多仓出场" % (lowpx, lower_bound))
                #raise Exception("except on purpose")
                return
        else:
            if highpx >= upper_bound and not self.__is_stk__:
                context.stra_exit_short(code, 1*trdUnit, 'exitshort')
                context.stra_log_text("向上突破%.2f>=%.2f，空仓出场" % (highpx, upper_bound))
                return



    def on_tick(self, context:CtaContext, stdCode:str, newTick:dict):
        #context.stra_log_text ("on tick fired")
        return