from pandas import DataFrame as df
import pandas as pd
import numpy as np
from dateutil.parser import parse
from collections import Counter
from datetime import datetime
import math
import os
import json
from xlsxwriter import Workbook


class Calculate():
    '''
    绩效比率计算
    '''
    def __init__(self, ret, mar, rf, period, trade,capital,ret_day=[],trade_day=0,profit=0):
        """
        :param ret: 收益率序列(单笔)
        :param mar: 最低可接受回报
        :param rf: 无风险利率
        :param period: 年交易日（用来年化）240
        :param capital: 初始本金
        :param ret_day: 收益率序列（每日）
        :param trade_day: 交易天数
        :param profit: 每笔利润
        """
        self.ret = ret
        self.mar = mar
        self.rf = rf
        self.trade = math.ceil(trade)
        self.period = period
        self.daily_rf = (self.rf + 1) ** (1 / self.period) - 1
        self.capital = capital
        self.ret_day = ret_day
        self.trade_day = trade_day
        self.profit = profit

    # 潜在上行比率
    def calculate_upside_ratio(self):
        upside = self.ret_day - self.daily_rf
        acess_return = upside[upside > 0].sum() / self.trade_day
        downside_std = math.sqrt((upside[upside < 0] ** 2).sum()/self.trade_day)
        if len(upside[upside < 0]) ==0:
            return 9999
        upside_ratio = acess_return / downside_std
        return upside_ratio

    # 夏普率
    def sharp_ratio(self):
        expect_return = self.ret_day.mean()
        std = self.ret_day.std()
        sharp_ratio = (expect_return - self.daily_rf) / std * np.sqrt(self.period)
        return sharp_ratio

    # 索提诺比率
    def sortion_ratio(self):
        expect_return = self.ret_day.mean()
        downside = self.ret_day-self.daily_rf
        downside_std = downside[downside < 0].std()
        # downside_std = self.ret[self.ret.apply(lambda x: x < 0)].std()
        sortion_ratio = (expect_return - self.daily_rf) / downside_std * np.sqrt(self.period)
        return sortion_ratio

    # 最大回撤值
    def maxDrawdown(self):
        ret = (self.ret + 1).cumprod()
        i = np.argmax((np.maximum.accumulate(ret) - ret) / np.maximum.accumulate(ret))
        if i == 0:
            return 0
        j = np.argmax(ret[:i])
        # return (ret[j] - ret[i]) / ret[j]
        return self.capital * ret[j] * (ret[j] - ret[i]) / ret[j]

    # 最大回撤比例
    def maxDrawdown_ratio(self):
        ret = (self.ret + 1).cumprod()
        i = np.argmax((np.maximum.accumulate(ret) - ret) / np.maximum.accumulate(ret))
        if i == 0:
            return 0
        j = np.argmax(ret[:i])
        return (ret[j] - ret[i]) / ret[j]

    def maxDrawdown_time(self):
        ret = (self.ret + 1).cumprod()
        i = np.argmax((np.maximum.accumulate(ret) - ret) / np.maximum.accumulate(ret))
        if i == 0:
            return 0
        j = np.argmax(ret[:i])
        return i, j

    # 卡尔马比率
    def calmar_ratio(self):
        maxdrawdown = Calculate.maxDrawdown_ratio(self)
        annual_return = Calculate.get_annual_return(self)
        calmar_ratio = annual_return / maxdrawdown
        return calmar_ratio

    # 斯特林比率
    def sterling_a_ratio(self):
        annual_return = Calculate.get_annual_return(self)
        sterling_a_ratio = annual_return / abs(Calculate.maxDrawdown_ratio(self)- 0.1)
        return sterling_a_ratio

    # 单笔最大回撤
    def single_largest_maxdrawdown(self):
        single_largest_mdd = self.ret[self.ret.apply(lambda x: x < 0)]
        if len(single_largest_mdd) == 0:
            single_largest_mxd = 0
            return single_largest_mxd
        single_largest_mxd = abs(single_largest_mdd.min())
        return single_largest_mxd

    # 单笔最大回撤值
    def single_largest_maxdrawdown_value(self):
        i = np.argmin(self.ret)
        single_largest_mxd = abs(self.profit[i])
        return single_largest_mxd

    # 单笔最大回撤索引
    def single_maxdrawdown_time(self):
        i = np.argmin(self.ret)
        return i

    # 年化收益率
    def get_annual_return(self):
        annual_return = 0 if self.trade_day==0 else (1+self.ret_day).cumprod()[len(self.ret_day)-1] ** (self.period / self.trade_day) - 1
        return annual_return

    # 月化收益率
    def monthly_return(self):
        ann = Calculate.get_annual_return(self)
        monthly_return = (ann + 1) ** (1/12) - 1
        return monthly_return

    # 月平均收益
    def monthly_average_return(self):
        monthly = self.ret_day.mean() * (self.period / 12)
        return monthly

    # 衰落时间
    def decay_time(self):
        netvalue = (self.ret+1).cumprod()

        ser = []
        temp = netvalue[0]
        ss = 0
        for x in netvalue:
            if x >= temp:
                ss = 0
                ser.append(ss)
                temp = x

            else:
                ss = ss + 1
                ser.append(ss)
        ss = max(pd.Series(ser))
        return ss

def fmtNAN(val, defVal = 0):
    if math.isnan(val):
        return defVal

    return val

def continue_trading_analysis(data, x_value) -> dict:
    '''
    连续交易分析
    '''
    mean = data['profit'].mean()
    std = data['profit'].std()
    z_score = (x_value - mean) / std
    times = 0
    win_time = 0
    ltimes = 0
    loss_time = 0
    con_win_profit = []
    con_lose_loss = []
    for i in range(len(data)-1):
        sss = data['profit'][i]
        if sss > 0:
            times += 1
            ltimes = 0
            rem = i
            if times > win_time:
                win_time = times
                # con_win_p_end = []
                # con_win_p_end.append(rem)
                con_win_profit.append((data['profit'].loc[rem - win_time + 1:rem]).sum())
            elif times == win_time:
                # con_win_p_end.append(rem)
                con_win_profit.append((data['profit'].loc[rem - win_time + 1:rem]).sum())
        else:
            times = 0
            ltimes += 1
            rem = i
            if ltimes > loss_time:
                loss_time = ltimes
                # con_loss_p_end = []
                # con_loss_p_end.append(rem)
                con_lose_loss.append((data['profit'].loc[rem - loss_time + 1:rem]).sum())
            elif ltimes == loss_time:
                # con_loss_p_end.append(rem)
                con_lose_loss.append((data['profit'].loc[rem - loss_time + 1:rem]).sum())
    capital = 500000

    # for rem in con_win_p_end:
    #     con_win_profit.append((data['profit'].loc[rem-win_time + 1:rem]).sum())
    con_win_profit = max(con_win_profit)

    # for rem in con_loss_p_end:
    #     con_lose_loss.append((data['profit'].loc[rem-loss_time + 1 :rem]).sum())
    con_lose_loss = min(con_lose_loss)
    # con_win_p_end, win_time 连续盈利结束位置，连续盈利最大次数
    # con_loss_p_end，loss_time 连续亏损结束位置，连续亏损最大次数

    cot_profit_ratio = con_win_profit / capital
    loss_profit_ratio = con_lose_loss / capital

    result = {'z值': z_score,
              '最大连续盈利交易次数': win_time,
              '最大连续亏损交易次数': loss_time,
              '最大连续盈利额': con_win_profit,
              '最大连续亏损额': con_lose_loss,
              '最大连续盈利（%）': cot_profit_ratio,
              '最大连续亏损（%）': loss_profit_ratio}

    return result

def nomalize_val(val):
    if math.isnan(val):
        return 0
    else:
        return val

def extreme_trading(data, time_of_std=1):
    '''
    极端交易分析
    '''
    std = data['profit'].std()
    df_wins = data[data["profit"] > 0]
    df_wins_std = df_wins['profit'].std()
    df_loses = data[data["profit"] <= 0]
    df_loses_std = df_loses['profit'].std()
    winamout = df_wins["profit"].sum()  # 毛盈利
    loseamount = df_loses["profit"].sum()  # 毛亏损
    trdnetprofit = winamout + loseamount  # 交易净盈亏
    totaltimes = len(data)  # 总交易次数
    avgprof = trdnetprofit / totaltimes if totaltimes > 0 else 0  # 单次平均盈亏
    avgprof_win = winamout / len(df_wins)
    avgprof_lose = loseamount / len(df_loses)
    # 单笔盈利 + 标准差
    sin_profit_plstd = avgprof + (std * time_of_std)
    sin_profit_plstd_win = avgprof_win + (df_wins_std * time_of_std)
    sin_profit_plstd_lose = avgprof_lose + (df_loses_std * time_of_std)
    # 单笔盈利 - 标准差
    sin_profit_mistd = avgprof - (std * time_of_std)
    sin_profit_mistd_win = avgprof_win - (df_wins_std * time_of_std)
    sin_profit_mistd_lose = avgprof_lose - (df_loses_std * time_of_std)
    # 极端交易数量
    extreme_result = data[data['profit'].apply(lambda x: x > sin_profit_plstd or x < sin_profit_mistd)]
    extreme_num = len(extreme_result)
    extreme_num_win = len(extreme_result[extreme_result['profit'] > 0])
    extreme_num_lose = len(extreme_result[extreme_result['profit'] < 0])
    # 极端交易盈亏 1 Std. Deviation of Avg. Trade
    extreme_profit = 0 if extreme_num==0 else extreme_result['profit'].sum()
    extreme_profit_win = 0 if extreme_num_win ==0 else extreme_result[extreme_result['profit'] > 0]['profit'].sum()
    extreme_profit_lose = 0 if extreme_num_lose == 0 else extreme_result[extreme_result['profit'] < 0]['profit'].sum()
    # 极端盈利交易计算

    result = {'总计':{
            '1 Std. Deviation of Avg. Trade': nomalize_val(std),
            '单笔净利 +1倍标准差': nomalize_val(sin_profit_plstd),
            '单笔净利 -1倍标准差': nomalize_val(sin_profit_mistd),
            '极端交易数量': extreme_num,
            '极端交易盈亏': extreme_profit
        },
        '极端盈利':{
            '1 Std. Deviation of Avg. Trade': nomalize_val(df_wins_std),
            '单笔净利 +1倍标准差': nomalize_val(sin_profit_plstd_win),
            '单笔净利 -1倍标准差': nomalize_val(sin_profit_mistd_win),
            '极端交易数量': extreme_num_win,
            '极端交易盈亏': extreme_profit_win
        },
        '极端亏损':{
            '1 Std. Deviation of Avg. Trade': nomalize_val(df_loses_std),
            '单笔净利 +1倍标准差': nomalize_val(sin_profit_plstd_lose),
            '单笔净利 -1倍标准差': nomalize_val(sin_profit_mistd_lose),
            '极端交易数量': extreme_num_lose,
            '极端交易盈亏': extreme_profit_lose
        }
    }

    result = pd.DataFrame(result)

    return result


def average_profit(data):
    '''
    连续交易分析之平均收益
    '''
    data = data['profit']
    win = 0
    li = []
    lose = 0
    li_2 = []
    dic= []
    dicc = []
    for i in range(1, len(data) - 1):
        if (data[i] > 0) == (data[i - 1] > 0):
            if data[i] > 0:
                c = 1
                win = win + c
            else:
                c = 1
                lose = lose + c
            if (data[i] > 0) == ((data[i + 1]) > 0):
                pass
            else:
                if data[i] > 0:
                    dis = {str(win): data[i-win:i+1].sum()}
                    dic.append(dis)
                    li.append(win)
                    win = 0

                else:
                    dis = {str(lose): data[i-lose:i+1].sum()}
                    dicc.append(dis)
                    li_2.append(lose)
                    lose = 0
        else:
            win = 0
            lose = 0
    number_win = Counter(li)
    number_lose = Counter(li_2)
    ss = pd.DataFrame()
    for x in dic:
        df = pd.DataFrame([x])
        ss = pd.concat([ss, df.T])
    win_ss = ss.reset_index()
    win_ss = win_ss.groupby('index').mean()

    ss2 = pd.DataFrame()
    for y in dicc:
        df = pd.DataFrame([y])
        ss2 = pd.concat([ss2, df.T])
    lose_ss = ss2.reset_index()
    lose_ss = lose_ss.groupby('index').mean()
    result = {'连续盈利次数': number_win,
              '连续亏损次数': number_lose,
              '每个序列平均收益': win_ss,
              '每个序列平均亏损': lose_ss}
    return result

def stat_closes_by_day(df_closes:df, capital) -> df:
    '''
    按天统计平仓数据
    '''
    df_closes['day'] = df_closes['opentime']
    df_closes['win'] = df_closes['profit'].apply(lambda x: 1 if x > 0 else 0)
    df_closes['times'] = 1
    df_closes['gross_profit'] = df_closes['profit'].apply(lambda x: x if x > 0 else 0)
    df_closes['gross_loss'] = df_closes['profit'].apply(lambda x: x if x < 0 else 0)
    profit = df_closes.groupby(df_closes['day'])[['win', 'times', 'profit', 'gross_profit', 'gross_loss']].sum()
    profit['win_rate'] = profit['win'] / profit['times']
    profit['profit_ratio'] = profit['profit']*100.0/capital
    res = profit[['profit', 'gross_profit', 'gross_loss', 'times', 'win_rate', 'profit_ratio']]
    return res.iloc[::-1]

def stat_closes_by_month(df_closes:df, capital) -> df:
    '''
    按月统计平仓数据
    '''
    df_closes['month'] = df_closes['opentime'].apply(lambda x: x.strftime("%Y/%m"))
    df_closes['win'] = df_closes['profit'].apply(lambda x: 1 if x > 0 else 0)
    df_closes['times'] = 1
    df_closes['gross_profit'] = df_closes['profit'].apply(lambda x: x if x > 0 else 0)
    df_closes['gross_loss'] = df_closes['profit'].apply(lambda x: x if x < 0 else 0)
    profit = df_closes.groupby(df_closes['month'])[['win', 'times', 'profit', 'gross_profit', 'gross_loss']].sum()
    profit['win_rate'] = profit['win'] / profit['times']
    profit['profit_ratio'] = profit['profit']*100.0/capital
    res = profit[['profit', 'gross_profit', 'gross_loss', 'times', 'win_rate', 'profit_ratio']]
    return res.iloc[::-1]

def stat_closes_by_year(df_closes:df, capital) -> df:
    '''
    按年统计平仓数据
    '''
    df_closes['year'] = df_closes['opentime'].apply(lambda x: x.strftime("%Y"))
    df_closes['win'] = df_closes['profit'].apply(lambda x: 1 if x > 0 else 0)
    df_closes['times'] = 1
    df_closes['gross_profit'] = df_closes['profit'].apply(lambda x: x if x > 0 else 0)
    df_closes['gross_loss'] = df_closes['profit'].apply(lambda x: x if x < 0 else 0)
    profit = df_closes.groupby(df_closes['year'])[['win', 'times', 'profit', 'gross_profit', 'gross_loss']].sum()
    profit['win_rate'] = profit['win'] / profit['times']
    profit['profit_ratio'] = profit['profit']*100.0/capital
    res = profit[['profit', 'gross_profit', 'gross_loss', 'times', 'win_rate', 'profit_ratio']]
    return res.iloc[::-1]

def time_analysis(df_closes:df,df_funds:df) -> dict:
    '''
    时间分析
    '''
    trading_time = df_closes['closebarno'][len(df_closes) - 1]

    # 策略运行时间
    str_time = (df_closes['closebarno'] - df_closes['openbarno']).sum()
    # 比率
    porition = str_time / trading_time * 100

    # 最大空仓时间
    empty_time = (df_closes['openbarno'].shift(-1) - df_closes['closebarno']).max()

    capital = 500000
    df_closes['principal'] = df_closes['totalprofit'] + capital
    df_closes['principal'] = df_closes['principal'].shift(1)
    input_data = df_closes.fillna(value=500000)
    ret = input_data['profit'] / input_data['principal']
    mar = 0
    rf = 0.02
    period = 240
    trade = input_data['closebarno'][len(input_data) - 1] / 47
    factors = Calculate(ret, mar, rf, period, trade,capital)

    single_drawdown_date = factors.single_maxdrawdown_time()
    signe_drawdown_date = parse(str(input_data['opentime'][single_drawdown_date]))

    # 最大回撤区间
    maxdrawdown_time = factors.maxDrawdown_time()

    # 回撤开始日期
    start_time = maxdrawdown_time[1]
    start_time = parse(str(input_data['opentime'][start_time]))

    # 回撤结束日期
    end_time = maxdrawdown_time[0]
    end_time = parse(str(input_data['opentime'][end_time]))

    # 最大损失日期
    loss_time_index = np.argmin(input_data['profit'])
    loss_time = parse(str(input_data['opentime'][loss_time_index]))

    result = {'交易周期': str(trading_time) + '根K线',
              '策略运行时间': str(str_time) + '根K线',
              '策略运行时间%': str(round(porition,2)) + '%',
              '最长空仓时间': str(empty_time) + '根K线',
              '策略最大回撤开始时间': start_time.strftime("%Y/%m/%d %H:%M"),
              '策略最大回撤结束时间': end_time.strftime("%Y/%m/%d %H:%M"),
              '单笔最大回撤时间': signe_drawdown_date.strftime("%Y/%m/%d %H:%M"),
              '平仓交易最大损失日期': loss_time.strftime("%Y/%m/%d %H:%M")}

    return result

def ratio_calculate(data, data2,after_merge, capital = 500000, rf = 0, period = 240) -> dict:
    data['principal'] = data['totalprofit'] + capital
    data['principal'] = data['principal'].shift(1)
    profit = data['profit']
    data2['principal'] = data2['dynbalance'] + capital
    data2['principal2'] = data2['principal'].shift(1)
    input_data = data.fillna(value=capital)
    input_data2 = data2.fillna(value=capital)
    ret = input_data['profit'] / input_data['principal']
    ret_day =input_data2['principal']/input_data2['principal2'] -1
    trade_day = data2.shape[0]
    mar = 0
    trade = input_data['closebarno'][len(input_data) - 1] / 47
    factors = Calculate(ret, mar, rf, period, trade,capital,ret_day,trade_day,profit)
    # 潜在上涨比率
    potential_upside_ratio = factors.calculate_upside_ratio()
    # 夏普比率
    sharpe_ratio = factors.sharp_ratio()
    # 索提诺比率
    sortino_ratio = factors.sortion_ratio()
    # 卡尔马比率(Calmar Ratio)
    calmar_ratio = factors.calmar_ratio()
    # 斯特林比率
    sterling_ratio = factors.sterling_a_ratio()
    result1 = performance_summary(data, after_merge,data2=data2)
    # 净利/单笔最大亏损
    net_s_loss = result1.get('净利') / result1.get('单笔最大亏损')
    # 净利/单笔最大回撤
    net_s_drawdown = result1.get('净利') / factors.single_largest_maxdrawdown_value()
    # 净利/ 策略最大回撤
    net_strategy_drawdown =  result1.get('净利') / factors.maxDrawdown()
    # 调整净利/单笔最大亏损
    adjust_s_loss = result1.get('调整净利') / result1.get('单笔最大亏损')
    # 调整净利/单笔最大回撤
    adjust_s_drawdown = result1.get('调整净利') / factors.single_largest_maxdrawdown_value()
    # 调整净利/ 策略最大回撤
    adjust_strategy_drawdown = result1.get('调整净利') / factors.maxDrawdown()

    result = {'潜在上涨比率':potential_upside_ratio,
              '夏普比率':sharpe_ratio,
              '索提诺比率':sortino_ratio,
              '卡尔马比率':calmar_ratio,
              '斯特林比率':sterling_ratio,
              '净利/单笔最大亏损':net_s_loss,
              '净利/单笔最大回撤':net_s_drawdown,
              '净利/ 策略最大回撤':net_strategy_drawdown,
              '调整净利/单笔最大亏损':adjust_s_loss,
              '调整净利/单笔最大回撤':adjust_s_drawdown,
              '调整净利/ 策略最大回撤':adjust_strategy_drawdown}

    return result

def performance_summary(input_data, input_data1, capital = 500000, rf = 0.00, period = 240,data2 = []):
    '''
    绩效统计
    '''
    # 指标计算准备
    input_data['principal'] = input_data['totalprofit'] + capital
    input_data['principal'] = input_data['principal'].shift(1)
    input_data = input_data.fillna(value=capital)
    ret = input_data['profit'] / input_data['principal']
    mar = 0
    trade = len(input_data)
    #trade = input_data['closebarno'][len(input_data)-1] / 47

    data2['principal'] = data2['dynbalance'] + capital
    data2['principal2'] = data2['principal'].shift(1)
    input_data2 = data2.fillna(value=capital)
    ret_day = input_data2['principal'] / input_data2['principal2'] - 1
    trade_day = data2.shape[0]
    # 指标class
    factors = Calculate(ret, mar, rf, period, trade,capital,ret_day,trade_day)
    # 毛利
    profit = input_data[input_data['profit'].apply(lambda x: x >= 0)]
    total_profit = 0 if len(profit)==0 else profit['profit'].sum()
    # 毛损
    loss = input_data[input_data['profit'].apply(lambda x: x < 0)]
    total_loss = 0 if len(loss)==0 else loss['profit'].sum()
    # 净利
    net_profit = total_profit + total_loss
    input_data1['adjust_profit'] = (input_data1['profit'] - input_data1['transaction_fee']) if len(input_data1)>0 else 0
    # 调整毛利
    adjust_profit = input_data1[input_data1['adjust_profit'].apply(lambda x: x >= 0)]
    total_adjust_profit = 0 if len(adjust_profit)==0 else adjust_profit['adjust_profit'].sum()
    # 调整毛损
    adjust_loss = input_data1[input_data1['adjust_profit'].apply((lambda x: x < 0))]
    total_adjust_loss = 0 if len(adjust_loss)==0 else adjust_loss['adjust_profit'].sum()
    # 调整净利
    adjust_net_profit = total_adjust_profit + total_adjust_loss
    # 盈利因子
    profit_factor = 0 if total_loss==0 else np.abs(total_profit / total_loss)
    # 调整盈利因子
    adjust_profit_factor = 0 if total_adjust_loss == 0 else np.abs(total_adjust_profit / total_adjust_loss)
    # 最大持有合约数量
    max_holding_number = 1
    # 已付手续费
    paid_trading_fee = input_data1['transaction_fee'].sum() if len(input_data1)>0 else 0
    # 单笔最大亏损
    single_loss = input_data[input_data['profit'].apply(lambda x: x < 0)]
    single_largest_loss = 0 if len(single_loss)==0 else abs(single_loss['profit'].min())
    # 平仓交易最大亏损
    trading_loss = single_largest_loss
    # 平仓交易最大亏损比
    trading_loss_rate = -trading_loss / capital
    # 年化收益率
    annual_ret = factors.get_annual_return()
    # 月化收益率
    monthly_return = factors.monthly_return()
    # 月平均收益
    monthly_average_return = factors.monthly_average_return()

    # 结果封装字典
    result = {'毛利': total_profit,
              '毛损': total_loss,
              '净利': net_profit,
              '调整毛利': total_adjust_profit,
              '调整毛损': total_adjust_loss,
              '调整净利': adjust_net_profit,
              '盈利因子': profit_factor,
              '调整盈利因子': adjust_profit_factor,
              '最大持有合约数量': max_holding_number,
              '已付手续费': paid_trading_fee,
              '单笔最大亏损': single_largest_loss,
              '平仓交易最大亏损': trading_loss,
              '平仓交易最大亏损比': trading_loss_rate,
              '年化收益率': annual_ret,
              '月化收益率': monthly_return,
              '月平均收益': monthly_average_return}
    return result

def do_trading_analyze(df_closes, df_funds):
    
    df_wins = df_closes[df_closes["profit"] > 0]
    df_loses = df_closes[df_closes["profit"] <= 0]

    ay_WinnerBarCnts = df_wins["closebarno"] - df_wins["openbarno"]
    ay_LoserBarCnts = df_loses["closebarno"] - df_loses["openbarno"]

    total_winbarcnts = ay_WinnerBarCnts.sum()
    total_losebarcnts = ay_LoserBarCnts.sum()

    total_fee = df_closes['fee'].sum()

    totaltimes = len(df_closes)  # 总交易次数
    wintimes = len(df_wins)  # 盈利次数
    losetimes = len(df_loses)  # 亏损次数
    winamout = df_wins["profit"].sum()  # 毛盈利
    loseamount = df_loses["profit"].sum()  # 毛亏损
    trdnetprofit = winamout + loseamount  # 交易净盈亏
    accnetprofit = trdnetprofit - total_fee  # 账户净盈亏
    winrate = (wintimes / totaltimes) if totaltimes > 0 else 0  # 胜率
    avgprof = (trdnetprofit / totaltimes) if totaltimes > 0 else 0  # 单次平均盈亏
    avgprof_win = (winamout / wintimes) if wintimes > 0 else 0  # 单次盈利均值
    avgprof_lose = (loseamount / losetimes) if losetimes > 0 else 0  # 单次亏损均值
    winloseratio = abs(avgprof_win / avgprof_lose) if avgprof_lose != 0 else "N/A"  # 单次盈亏均值比

    # 单笔最大盈利交易
    largest_profit = df_wins['profit'].max()
    # 单笔最大亏损交易
    largest_loss = df_loses['profit'].min()
    # 交易的平均持仓K线根数
    avgtrd_hold_bar = 0 if totaltimes==0 else ((df_closes['closebarno'] - df_closes['openbarno']).sum()) / totaltimes
    # 平均空仓K线根数
    avb = (df_closes['openbarno'] - df_closes['closebarno'].shift(1).fillna(value=0))
    avgemphold_bar = 0 if len(df_closes)==0 else avb.sum() / len(df_closes)

    # 两笔盈利交易之间的平均空仓K线根数
    win_holdbar_situ = (df_wins['openbarno'].shift(-1) - df_wins['closebarno']).dropna()
    winempty_avgholdbar = 0 if len(df_wins)== 0 or len(df_wins) == 1 else win_holdbar_situ.sum() / (len(df_wins)-1)
    # 两笔亏损交易之间的平均空仓K线根数
    loss_holdbar_situ = (df_loses['openbarno'].shift(-1) - df_loses['closebarno']).dropna()
    lossempty_avgholdbar = 0 if len(df_loses)== 0 or len(df_loses) == 1 else loss_holdbar_situ.sum() / (len(df_loses)-1)

    max_consecutive_wins = 0  # 最大连续盈利次数
    max_consecutive_loses = 0  # 最大连续亏损次数

    avg_bars_in_winner = total_winbarcnts / wintimes if wintimes > 0 else "N/A"
    avg_bars_in_loser = total_losebarcnts / losetimes if losetimes > 0 else "N/A"

    consecutive_wins = 0
    consecutive_loses = 0

    for idx, row in df_closes.iterrows():
        profit = row["profit"]
        if profit > 0:
            consecutive_wins += 1
            consecutive_loses = 0
        else:
            consecutive_wins = 0
            consecutive_loses += 1

        max_consecutive_wins = max(max_consecutive_wins, consecutive_wins)
        max_consecutive_loses = max(max_consecutive_loses, consecutive_loses)

    summary = dict()

    summary["交易总数量"] = totaltimes
    summary["盈利交易次数"] = wintimes
    summary["亏损交易次数"] = losetimes
    summary["毛盈利"] = float(winamout)
    summary["毛亏损"] = float(loseamount)
    summary["交易净盈亏"] = float(trdnetprofit)
    summary["% 胜率"] = winrate * 100
    summary["单次平均盈亏"] = avgprof
    summary["单次盈利均值"] = avgprof_win
    summary["单次亏损均值"] = avgprof_lose
    summary["% 单次盈亏均值比"] = winloseratio
    summary["最大连续盈利次数"] = max_consecutive_wins
    summary["最大连续亏损次数"] = max_consecutive_loses
    summary["盈利交易的平均持仓K线根数"] = avg_bars_in_winner
    summary["亏损交易的平均持仓K线根数"] = avg_bars_in_loser
    summary["账户净盈亏"] = 0 if totaltimes==0 else accnetprofit
    summary['单笔最大盈利交易'] = largest_profit
    summary['单笔最大亏损交易'] = largest_loss
    summary['交易的平均持仓K线根数'] = avgtrd_hold_bar
    summary['平均空仓K线根数'] = avgemphold_bar
    summary['两笔盈利交易之间的平均空仓K线根数'] = winempty_avgholdbar
    summary['两笔亏损交易之间的平均空仓K线根数'] = lossempty_avgholdbar
    summary = pd.DataFrame([summary]).T
    summary = summary.reset_index()
    return summary

def trading_analyze(workbook:Workbook, df_closes, df_funds, capital = 500000):
    '''
    交易分析
    '''
    res = average_profit(df_closes)
    rr = res.get('连续盈利次数')
    df = pd.DataFrame([rr]).T
    df.columns = ['连续次数']
    df = df.reset_index()

    every_series_profit = res.get('每个序列平均收益')
    every_series_profit = every_series_profit.reset_index()
    df['index'] = df['index'].apply(lambda x: int(x))
    every_series_profit['index'] = every_series_profit['index'].apply(lambda x: int(x))
    f_result = df.merge(every_series_profit)
    f_result = f_result.sort_values('index')
    f_result.columns = ['连续次数', '出现次数', '每个序列平均收益']
    f_result['连续次数'] = f_result['连续次数'] + 1

    rr_2 = res.get('连续亏损次数')
    df_2 = pd.DataFrame([rr_2]).T
    df_2.columns = ['连续次数']
    df_2 = df_2.reset_index()

    every_series_loss = res.get('每个序列平均亏损')
    every_series_loss = every_series_loss.reset_index()
    df_2['index'] = df_2['index'].apply(lambda x: int(x))
    every_series_loss['index'] = every_series_loss['index'].apply(lambda x: int(x))
    f_2_result = df_2.merge(every_series_loss)
    f_2_result = f_2_result.sort_values('index')
    f_2_result.columns = ['连续次数', '出现次数', '每个序列平均亏损']
    f_2_result['连续次数'] = f_2_result['连续次数'] + 1

    ssaa = df_funds['closeprofit'].iloc[-1]

    # 连续交易系列分析
    s = continue_trading_analysis(df_closes, ssaa)
    # 极端交易
    sss = extreme_trading(df_closes)

    title_format = workbook.add_format({
        'font_size':    16,
        'bold':         True,
        'align':        'left',  # 水平居中
        'valign':       'vcenter'  # 垂直居中
    })

    index_format = workbook.add_format({
        'font_size':    12,
        'bold':         True,
        'align':        'left',  # 水平居中
        'valign':       'vcenter'  # 垂直居中
    })

    value_format = workbook.add_format({
        'align':        'right',  # 水平居中
        'valign':       'vcenter'  # 垂直居中
    })

    date_format = workbook.add_format({
        'num_format':   'yyyy/mm/dd',
        'bold':         True,
        'align':        'left',  # 水平居中
        'valign':       'vcenter'  # 垂直居中
    })
    worksheet = workbook.add_worksheet('交易分析')

    df_closes['fee'] = df_closes['profit'] - df_closes['totalprofit'] + df_closes['totalprofit'].shift(1).fillna(value=0)
    trade_s = do_trading_analyze(df_closes, df_funds)
    data_1 = df_closes[df_closes['direct'].apply(lambda x: 'LONG' in x)]
    trade_s_long = do_trading_analyze(data_1, df_funds)
    data_2 = df_closes[df_closes['direct'].apply(lambda x: 'SHORT' in x)]
    trade_s_short = do_trading_analyze(data_2, df_funds)
    trade_s = trade_s.merge(trade_s_long, how='inner', on='index')
    trade_s = trade_s.merge(trade_s_short,how='inner', on='index')
    trade_s.columns =['类别', '所有交易', '多头', '空头']
    trade_s.fillna(value=0, inplace=True)

    worksheet.write_row('A1', ['总体交易分析'], title_format)
    worksheet.write_row('B3', ['所有交易','多头交易','空头交易'], index_format)
    worksheet.write_column('A4', trade_s['类别'], index_format)
    worksheet.write_column('B4', trade_s['所有交易'], value_format)
    worksheet.write_column('C4', trade_s['多头'], value_format)
    worksheet.write_column('D4', trade_s['空头'], value_format)

    worksheet.write_row('A28', ['极端交易'], title_format)
    worksheet.write_row('B30', ['总计','极端盈利','极端亏损'], index_format)
    worksheet.write_column('A31', sss.index, index_format)
    worksheet.write_column('B31', sss['总计'], value_format)
    worksheet.write_column('C31', sss['极端盈利'], value_format)
    worksheet.write_column('D31', sss['极端亏损'], value_format)

    worksheet.write_row('A38', ['连续交易系列分析'], title_format)
    worksheet.write_column('A40', s.keys(), index_format)
    worksheet.write_column('B40', s.values(), value_format)

    worksheet.write_row('A49', ['连续交易系列统计'], title_format)
    worksheet.write_row('A51', ['连续盈利次数','出现次数','每个序列的平均收益'], index_format)
    worksheet.write_column('A52', f_result['连续次数'], value_format)
    worksheet.write_column('B52', f_result['出现次数'], value_format)
    worksheet.write_column('C52', f_result['每个序列平均收益'], value_format)

    win_cnt = len(f_result)
    next_row = win_cnt+52
    worksheet.write_row('A%d'%next_row, ['连续亏损次数','出现次数','每个序列的平均亏损'], index_format)
    worksheet.write_column('A%d'%(next_row+1), f_2_result['连续次数'], value_format)
    worksheet.write_column('B%d'%(next_row+1), f_2_result['出现次数'], value_format)
    worksheet.write_column('C%d'%(next_row+1), f_2_result['每个序列平均亏损'], value_format)


    # 这里开始画图
    next_row += len(f_2_result) + 3
    worksheet.write_row('A%d'%next_row, ['全部交易'], title_format)
    chart_col = workbook.add_chart({'type': 'scatter'})
    length = len(df_closes)
    sheetName = '交易列表'
    chart_col.add_series(
        {
            'name': '收益分布',
            'categories': '=%s!$A$4:$A$%s' % (sheetName, length+3),
            'values':   '=%s!$J$4:$J$%s' % (sheetName, length+3),
            'marker': {
                'type':"circle", 
                'size':3
            }
        }
    )
    chart_col.set_title({'name': '收益分布'})
    chart_col.set_x_axis({'label_position': 'low'})
    worksheet.insert_chart('A%d' % (next_row+2), chart_col,{'x_scale': 1.8, 'y_scale': 1.8})

    next_row += 30
    worksheet.write_row('A%d'%next_row, ['潜在盈利'], title_format)
    chart_col = workbook.add_chart({'type': 'scatter'})
    length = len(df_closes)
    sheetName = '交易列表'
    chart_col.add_series(
        {
            'name': '潜在盈利',
            'categories': '=%s!$A$4:$A$%s' % (sheetName, length+3),
            'values':   '=%s!$N$4:$N$%s' % (sheetName, length+3),
            'marker': {
                'type':"diamond", 
                'size':3, 
                'border': {'color': 'red'},
                'fill':   {'color': 'red'}
            }
        }
    )
    chart_col.set_title({'name': '潜在盈利'})
    chart_col.set_x_axis({'label_position': 'low'})
    worksheet.insert_chart('A%d' % (next_row+2), chart_col,{'x_scale': 1.8, 'y_scale': 1.8})

    next_row += 30
    worksheet.write_row('A%d'%next_row, ['潜在亏损'], title_format)
    chart_col = workbook.add_chart({'type': 'scatter'})
    length = len(df_closes)
    sheetName = '交易列表'
    chart_col.add_series(
        {
            'name': '潜在亏损',
            'categories': '=%s!$A$4:$A$%s' % (sheetName, length+3),
            'values':   '=%s!$P$4:$P$%s' % (sheetName, length+3),
            'marker': {
                'type':"triangle", 
                'size':3, 
                'border': {'color': 'green'},
                'fill':   {'color': 'green'}
            }
        }
    )
    chart_col.set_title({'name': '潜在亏损'})
    chart_col.set_x_axis({'label_position': 'low'})
    worksheet.insert_chart('A%d' % (next_row+2), chart_col,{'x_scale': 1.8, 'y_scale': 1.8})

 
    # 周期分析
    worksheet = workbook.add_worksheet('周期分析')

    df_closes['opentime'] = df_closes['opentime'].apply(lambda x: parse(str(int(x / 10000))))
    res = stat_closes_by_day(df_closes.copy(), capital)    
    worksheet.write_row('A1', ['日度绩效分析'], title_format)
    worksheet.write_row('A3', ['期间','盈利(¤)','盈利(%)','毛利','毛损','交易次数','胜率(%)'], index_format)
    worksheet.write_column('A4', res.index, date_format)
    worksheet.write_column('B4', res["profit"], value_format)
    worksheet.write_column('C4', res["profit_ratio"], value_format)
    worksheet.write_column('D4', res["gross_profit"], value_format)
    worksheet.write_column('E4', res["gross_loss"], value_format)
    worksheet.write_column('F4', res["times"], value_format)
    worksheet.write_column('G4', res["win_rate"]*100, value_format)
  
    next_row = 5 + len(res)
    res = stat_closes_by_month(df_closes.copy(), capital)
    worksheet.write_row('A%d'%(next_row+1), ['月度绩效分析'], title_format)
    worksheet.write_row('A%d'%(next_row+3), ['期间','盈利(¤)','盈利(%)','毛利','毛损','交易次数','胜率(%)'], index_format)
    worksheet.write_column('A%d'%(next_row+4), res.index, index_format)
    worksheet.write_column('B%d'%(next_row+4), res["profit"], value_format)
    worksheet.write_column('C%d'%(next_row+4), res["profit_ratio"], value_format)
    worksheet.write_column('D%d'%(next_row+4), res["gross_profit"], value_format)
    worksheet.write_column('E%d'%(next_row+4), res["gross_loss"], value_format)
    worksheet.write_column('F%d'%(next_row+4), res["times"], value_format)
    worksheet.write_column('G%d'%(next_row+4), res["win_rate"]*100, value_format)

    next_row = next_row + 4 + len(res)
    res = stat_closes_by_year(df_closes.copy(), capital) 
    worksheet.write_row('A%d'%(next_row+1), ['年度绩效分析'], title_format)
    worksheet.write_row('A%d'%(next_row+3), ['期间','盈利(¤)','盈利(%)','毛利','毛损','交易次数','胜率(%)'], index_format)
    worksheet.write_column('A%d'%(next_row+4), res.index, index_format)
    worksheet.write_column('B%d'%(next_row+4), res["profit"], value_format)
    worksheet.write_column('C%d'%(next_row+4), res["profit_ratio"], value_format)
    worksheet.write_column('D%d'%(next_row+4), res["gross_profit"], value_format)
    worksheet.write_column('E%d'%(next_row+4), res["gross_loss"], value_format)
    worksheet.write_column('F%d'%(next_row+4), res["times"], value_format)
    worksheet.write_column('G%d'%(next_row+4), res["win_rate"]*100, value_format)

def strategy_analyze(workbook:Workbook, df_closes, df_trades,df_funds, capital, rf = 0.0, period = 240):
    '''
    策略分析
    '''

    # 截取开仓明细
    data1_open = df_trades[df_trades['action'].apply(lambda x: 'OPEN' in x)].reset_index()
    data1_open = data1_open.drop(columns=['index'])
    # 截取平仓明细
    data1_close = df_trades[df_trades['action'].apply(lambda x: 'CLOSE' in x)].reset_index()
    data1_close = data1_close.drop(columns=['index'])

    # 将平仓明细字段重命名，并跟开仓明细合并成一个大表
    data1_close = data1_close.rename(columns={'code': 'code_1', 'time': 'time_1', 'direct': 'direct_1',
                                              'action': 'action_1', 'price': 'price_1', 'qty': 'qty_1', 'tag': 'tag_1',
                                              'fee': 'fee_1'})

    new_data = pd.concat([data1_open, data1_close], axis=1)
    new_data = new_data.dropna()
    new_data = new_data.drop(columns=['code_1', 'qty_1'])

    # 计算开仓平仓手续费
    new_data['transaction_fee'] = new_data['fee'] + new_data['fee_1']
    clean_data = new_data[['time', 'transaction_fee']]
    clean_data = clean_data.rename(columns={'time': 'opentime'})

    # 合并数据
    after_merge = pd.merge(df_closes, clean_data, how='inner', on='opentime')

    data_long = df_closes[df_closes['direct'].apply(lambda x:'LONG' in x )].reset_index()
    after_merge_long = after_merge[after_merge['direct'].apply(lambda x: 'LONG' in x)].reset_index()
    data_short = df_closes[df_closes['direct'].apply(lambda x: 'SHORT' in x)].reset_index()
    after_merge_short = after_merge[after_merge['direct'].apply(lambda x: 'SHORT' in x)].reset_index()

    # 全部平仓明细进行绩效分析
    result1 = performance_summary(df_closes, after_merge, capital=capital, rf=rf, period=period,data2=df_funds)
    # 做多平仓明细进行绩效分析
    result1_2 = performance_summary(data_long, after_merge_long, capital=capital, rf=rf, period=period,data2= df_funds)
    # 做空平仓明细进行绩效分析
    result1_3 = performance_summary(data_short,after_merge_short, capital=capital, rf=rf, period=period,data2= df_funds)
    # 绩效比率计算
    result2 = ratio_calculate(df_closes,df_funds, after_merge, capital=capital, rf=rf, period=period)
    # 时间分析
    result3 = time_analysis(df_closes,df_funds)

    result1 = pd.DataFrame(pd.Series(result1), columns=['所有交易'])
    result1 = result1.reset_index().rename(columns={'index': '策略绩效概要'})

    result1_2 = pd.DataFrame(pd.Series(result1_2), columns=['多头交易'])
    result1_2 = result1_2.reset_index().rename(columns={'index': '策略绩效概要'})

    result1_3 = pd.DataFrame(pd.Series(result1_3), columns=['空头交易'])
    result1_3 = result1_3.reset_index().rename(columns={'index': '策略绩效概要'})

    result1 = result1.merge(result1_2,how='inner',on='策略绩效概要')
    result1 = result1.merge(result1_3,how='inner',on='策略绩效概要')

    sheetName = '策略分析'
    worksheet = workbook.add_worksheet(sheetName)

    title_format = workbook.add_format({
        'font_size':    16,
        'bold':         True,
        'align':        'left',  # 水平居中
        'valign':       'vcenter'  # 垂直居中
    })

    index_format = workbook.add_format({
        'font_size':    12,
        'bold':         True,
        'align':        'left',  # 水平居中
        'valign':       'vcenter'  # 垂直居中
    })

    value_format = workbook.add_format({
        'align':        'right',  # 水平居中
        'valign':       'vcenter'  # 垂直居中
    })
    result1.fillna(value=0, inplace=True)
    worksheet.write_row('A1', ['策略绩效概要'], title_format)    
    worksheet.write_row('B3', ['所有交易','多头交易','空头交易'], index_format)
    worksheet.write_column('A4', result1['策略绩效概要'], index_format)
    worksheet.write_column('B4', result1['所有交易'], value_format)
    worksheet.write_column('C4', result1['多头交易'], value_format)
    worksheet.write_column('D4', result1['空头交易'], value_format)

    worksheet.write_row('A22', ['绩效比率'], title_format)    
    worksheet.write_column('A24', result2.keys(), index_format)
    worksheet.write_column('B24', result2.values(), value_format)

    worksheet.write_row('A37', ['时间分析'], title_format)    
    worksheet.write_column('A39', result3.keys(), index_format)
    worksheet.write_column('B39', result3.values(), value_format)

    #修正：重算多头、空头交易的年化月化月平均收益率
    net_profit_long = result1_2.loc[5,'多头交易']
    net_profit_short = result1_3.loc[5,'空头交易']
    trade_day = df_funds.shape[0]
    long_annualp =  ((net_profit_long + capital) / capital) ** (period / trade_day) -1
    short_annualp = ((net_profit_short + capital) / capital) ** (period / trade_day) - 1
    long_monthlyp = (long_annualp + 1) ** (1/12) -1
    short_monthlyp = (short_annualp + 1 ) ** (1/12) -1
    long_month_average = ((net_profit_long + capital) / capital -1) / trade_day * period / 12
    short_month_average = ((net_profit_short + capital) / capital -1) / trade_day * period / 12
    worksheet.write('C17',long_annualp,value_format)
    worksheet.write('D17',short_annualp,value_format)
    worksheet.write('C18', long_monthlyp, value_format)
    worksheet.write('D18', short_monthlyp, value_format)
    worksheet.write('C19', long_month_average, value_format)
    worksheet.write('D19', short_month_average, value_format)


    # 这里开始画图

    worksheet.write_row('A49', ['详细权益曲线'], title_format)
    chart_col = workbook.add_chart({'type': 'line'})
    length = len(df_closes)
    sheetName = '交易列表'

    chart_col.add_series(
        {
            'name': '详细权益曲线',
            'categories': '=%s!$S$4:$S$%s' % (sheetName, length+3),
            'values':   '=%s!$R$4:$R$%s' % (sheetName, length+3),
            'line': {'color': 'red', 'width': 1}
        }
    )
    chart_col.set_title({'name': '详细权益曲线'})
    chart_col.set_x_axis({'name': '平仓K线编号'})
    worksheet.insert_chart('A51', chart_col, {'x_scale': 1.8, 'y_scale': 1.8})


    worksheet.write_row('A79', ['每笔收益'], title_format)
    chart_col = workbook.add_chart({'type': 'column'})
    chart_col.add_series(
        {
            'name': '每笔收益',
            'categories': '=%s!$A$4:$A$%s' % (sheetName, length+3),
            'values':   '=%s!$J$4:$J$%s' % (sheetName, length+3),
            'line': {'color': 'black', 'width': 1}
        }
    )
    chart_col.set_title({'name': '每笔收益'})
    chart_col.set_x_axis({'label_position': 'low', 'name': '交易编号'})
    worksheet.insert_chart('A81', chart_col, {'x_scale': 1.8, 'y_scale': 1.8})

    worksheet.write_row('A109', ['潜在盈利与潜在亏损'], title_format)
    chart_col = workbook.add_chart({'type': 'column'})
    chart_col.add_series(
        {
            'name': '潜在盈利',
            'categories': '=%s!$S$4:$S$%s' % (sheetName, length+3),
            'values':   '=%s!$N$4:$N$%s' % (sheetName, length+3),
            'line': {'color': 'red','width': 1}
        }
    )
    chart_col.add_series(
        {
            'name': '潜在亏损',
            'categories': '=%s!$S$4:$S$%s' % (sheetName, length+3),
            'values':   '=%s!$P$4:$P$%s' % (sheetName, length+3),
            'line': {'color': 'green','width': 1}
        }
    )
    chart_col.set_x_axis({'label_position': 'low', 'name': '平仓K线编号'})
    chart_col.set_title({'name': '潜在盈利与潜在亏损'})
    worksheet.insert_chart('A111', chart_col, {'x_scale': 1.8, 'y_scale': 1.8})

    # df_closes['entrytime'] = df_closes['opentime'].apply(lambda x: datetime.strptime(str(x), '%Y%m%d%H%M'))
    # df_closes['exittime'] = df_closes['closetime'].apply(lambda x: datetime.strptime(str(x), '%Y%m%d%H%M'))
    # df_closes['exittime'] = pd.to_datetime(df_closes['exittime'])


    # #用matplotlib画图
    # plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签

    # worksheet.write_row('A139', ['详细多头权益曲线'], title_format)
    df_closes['fee'] = df_closes['profit'] - df_closes['totalprofit'] + df_closes['totalprofit'].shift(1).fillna(value=0)
    df_temp = pd.DataFrame()
    df_temp['profit'] = df_closes[df_closes['direct'] == 'LONG']['profit'] - df_closes[df_closes['direct'] == 'LONG']['fee']
    df_temp['equity'] = df_temp['profit'].expanding().sum() + capital
    np_temp = np.arange(1, len(df_temp)+1, 1)
    df_temp['index'] = np_temp

    # plt.plot(df_temp['index'], df_temp['equity'])
    # imgdata = BytesIO()
    # plt.xlabel('多头交易编号')
    # plt.title('详细多头权益曲线')
    # plt.ylabel('权益')
    # plt.savefig(imgdata, format="png")
    # imgdata.seek(0)
    # worksheet.insert_image(141, 0, "", {'image_data': imgdata})

    # worksheet.write_row('A169', ['详细空头权益曲线'], title_format)
    # plt.clf()
    df_temp2 = pd.DataFrame()
    df_temp2['profit'] = df_closes[df_closes['direct'] == 'SHORT']['profit'] - df_closes[df_closes['direct'] == 'SHORT']['fee']
    df_temp2['equity'] = df_temp2['profit'].expanding().sum() + capital
    np_temp2 = np.arange(1, len(df_temp2) + 1, 1)
    df_temp2['index'] = np_temp2

    # plt.plot(df_temp2['index'], df_temp2['equity'])
    # imgdata = BytesIO()
    # plt.xlabel('空头交易编号')
    # plt.title('详细空头权益曲线')
    # plt.ylabel('权益')
    # plt.savefig(imgdata, format="png")
    # imgdata.seek(0)
    # worksheet.insert_image(
    #     171, 0, "",
    #     {'image_data': imgdata}
    # )
    worksheet = workbook.add_worksheet('交易列表')
    length0 = len(df_closes)
    worksheet.write_row('A'+str(length0+98), ['作图数据'], index_format)
    worksheet.write_column('A'+str(length0+100), df_temp['index'], value_format)
    worksheet.write_column('B'+str(length0+100), df_temp['equity'], value_format)
    worksheet.write_column('C'+str(length0+100), df_temp2['index'], value_format)
    worksheet.write_column('D'+str(length0+100), df_temp2['equity'], value_format)

    worksheet = workbook.get_worksheet_by_name('策略分析')
    worksheet.write_row('A139', ['详细多头权益曲线'], title_format)
    chart_col = workbook.add_chart({'type': 'line'})
    length = len(df_temp)
    sheetName = '交易列表'

    chart_col.add_series(
        {
            'name': '详细权益曲线',
            'categories': '=%s!$A$%s:$A$%s' % (sheetName, length0+100, length0+100+length),
            'values':   '=%s!$B$%s:$B$%s' % (sheetName, length0+100, length0+100+length),
            'line': {'color': 'red', 'width': 1}
        }
    )
    chart_col.set_title({'name': '详细多头权益曲线'})
    chart_col.set_x_axis({'name': '交易列表'})
    worksheet.insert_chart('A141', chart_col, {'x_scale': 1.8, 'y_scale': 1.8})

    worksheet.write_row('A169', ['详细空头权益曲线'], title_format)
    chart_col = workbook.add_chart({'type': 'line'})
    length = len(df_temp2)

    chart_col.add_series(
        {
            'name': '详细权益曲线',
            'categories': '=%s!$C$%s:$C$%s' % (sheetName, length0+100, length0+100+length),
            'values':   '=%s!$D$%s:$D$%s' % (sheetName, length0+100, length0+100+length),
            'line': {'color': 'red', 'width': 1}
        }
    )
    chart_col.set_title({'name': '详细空头权益曲线'})
    chart_col.set_x_axis({'name': '交易列表'})
    worksheet.insert_chart('A171', chart_col, {'x_scale': 1.8, 'y_scale': 1.8})

def output_closes(workbook:Workbook, df_closes:df, capital = 500000):
    worksheet = workbook.get_worksheet_by_name('交易列表')
    title_format = workbook.add_format({
        'font_size':    16,
        'bold':         True,
        'align':        'left',  # 水平居中
        'valign':       'vcenter'  # 垂直居中
    })

    index_format = workbook.add_format({
        'font_size':    12,
        'bold':         True,
        'align':        'left',  # 水平居中
        'valign':       'vcenter'  # 垂直居中
    })

    value_format = workbook.add_format({
        'align':        'right',  # 水平居中
        'valign':       'vcenter'  # 垂直居中
    })

    time_format = workbook.add_format({
        'num_format':   'yyyy/mm/dd HH:MM',
        'align':        'right',  # 水平居中
        'valign':       'vcenter'  # 垂直居中
    })
    

    df_closes['entrytime'] = df_closes['opentime'].apply(lambda x: datetime.strptime(str(x), '%Y%m%d%H%M'))
    df_closes['exittime'] = df_closes['closetime'].apply(lambda x: datetime.strptime(str(x), '%Y%m%d%H%M'))

    worksheet.write_row('A1', ['交易列表'], title_format)    
    worksheet.write_row('A3', ['编号', '代码','方向','进场时间','进场价格','进场标记','出场时间','出场价格','出场标记',
    '盈利¤','盈利%','累计盈利¤','累计盈利%','潜在盈利¤','潜在盈利%','潜在亏损¤','潜在亏损%','累计权益','平仓K线编号'], index_format)
    df_closes["profit_ratio"] = df_closes["profit"]*100/capital
    df_closes["total_profit_ratio"] = df_closes["totalprofit"]*100/capital
    df_closes["max_profit_ratio"] = df_closes["maxprofit"]*100/capital
    df_closes["max_loss_ratio"] = df_closes["maxloss"]*100/capital
    df_closes['direct'].replace('SHORT', '空', inplace=True)
    df_closes['direct'].replace('LONG', '多', inplace=True)

    worksheet.write_column('A4', df_closes.index+1, value_format)
    worksheet.write_column('B4', df_closes['code'], value_format)
    worksheet.write_column('C4', df_closes['direct'], value_format)
    worksheet.write_column('D4', df_closes['entrytime'], time_format)
    worksheet.write_column('E4', df_closes['openprice'], value_format)
    ay = df_closes['entertag'].apply(lambda x: x if type(x)==str else '' if math.isnan(x) else x)
    worksheet.write_column('F4', ay, value_format)
    worksheet.write_column('G4', df_closes['exittime'], time_format)
    worksheet.write_column('H4', df_closes['closeprice'], value_format)
    ay = df_closes['exittag'].apply(lambda x: x if type(x)==str else '' if math.isnan(x) else x)
    worksheet.write_column('I4', ay, value_format)

    worksheet.write_column('J4', df_closes['profit'], value_format)
    worksheet.write_column('K4', df_closes['profit_ratio'], value_format)
    worksheet.write_column('L4', df_closes['totalprofit'], value_format)
    worksheet.write_column('M4', df_closes['total_profit_ratio'], value_format)
    worksheet.write_column('N4', df_closes['maxprofit'], value_format)
    worksheet.write_column('O4', df_closes['max_profit_ratio'], value_format)
    worksheet.write_column('P4', df_closes['maxloss'], value_format)
    worksheet.write_column('Q4', df_closes['max_loss_ratio'], value_format)
    worksheet.write_column('R4', df_closes['totalprofit']+capital, value_format)
    worksheet.write_column('S4', df_closes['closebarno'], value_format)

def summary_analyze(df_funds:df, capital = 5000000, rf = 0, period = 240) -> dict:
    '''
    概要分析
    '''
    init_capital = capital
    annual_days = period
    days = len(df_funds)

    #先做资金统计吧
    # print("anayzing fund data……")
    df_funds["dynbalance"] += init_capital
    ayBal = df_funds["dynbalance"]              # 每日期末动态权益

    #生成每日期初动态权益
    ayPreBal = np.array(ayBal.tolist()[:-1])  
    ayPreBal = np.insert(ayPreBal, 0, init_capital)    #每日期初权益
    df_funds["prebalance"] = ayPreBal

    #统计期末权益大于期初权益的天数，即盈利天数
    windays = len(df_funds[df_funds["dynbalance"]>df_funds["prebalance"]])

    #每日净值
    ayNetVals = (ayBal/init_capital)
    
    if ayNetVals.iloc[-1] >= 0:
        ar = math.pow(ayNetVals.iloc[-1], annual_days/days) - 1       #年化收益率=总收益率^(年交易日天数/统计天数)
    else:
        ar = -9999
    ayDailyReturn = ayBal/ayPreBal-1 #每日收益率
    delta = fmtNAN(ayDailyReturn.std(axis=0)*math.pow(annual_days,0.5),0)       #年化标准差=每日收益率标准差*根号下(年交易日天数)
    down_delta = fmtNAN(ayDailyReturn[ayDailyReturn<0].std(axis=0)*math.pow(annual_days,0.5), 0)    #下行标准差=每日亏损收益率标准差*根号下(年交易日天数)

    #sharpe率
    if delta != 0.0:
        sr = (ar-rf)/delta
    else:
        sr = 9999.0

    #计算最大回撤和最大上涨
    maxub = ayNetVals[0]
    minub = maxub
    mdd = 0.0
    midd = 0.0
    mup = 0.0
    for idx in range(1,len(ayNetVals)):
        maxub = max(maxub, ayNetVals[idx])
        minub = min(minub, ayNetVals[idx])
        profit = (ayNetVals[idx] - ayNetVals[idx-1])/ayNetVals[idx-1]
        falldown = (ayNetVals[idx] - maxub)/maxub
        riseup = (ayNetVals[idx] - minub)/minub
        if profit <= 0:
            midd = max(midd, abs(profit))
            mdd = max(mdd, abs(falldown))
        else:
            mup = max(mup, abs(riseup))
    #索提诺比率
    if down_delta != 0.0:
        sortino = (ar-rf)/down_delta
    else:
        sortino = 0.0
    if mdd != 0.0:
        calmar = ar/mdd
    else:
        calmar = 999999.0


    # key_indicator = ['交易天数', '累积收益（%）', '年化收益率（%）', '胜率（%）', '最大回撤（%）', '最大上涨（%）', '标准差（%）',
    #         '下行波动率（%）', 'Sharpe比率', 'Sortino比率', 'Calmar比率']
    return {
        'capital': capital,
        "days": days,
        "total_return":(ayNetVals.iloc[-1]-1)*100, 
        "annual_return":ar*100, 
        "win_rate":(windays/days)*100, 
        "max_falldown":mdd*100, 
        "max_profratio":mup*100, 
        "std":delta*100, 
        "down_std":down_delta*100, 
        "sharpe_ratio":sr, 
        "sortino_ratio":sortino, 
        "calmar_ratio":calmar
    }

def funds_analyze(workbook:Workbook, df_funds:df, capital = 5000000, rf = 0, period = 240):
    '''
    逐日资金分析
    '''
    init_capital = capital
    annual_days = period
    days = len(df_funds)

    #先做资金统计吧
    print("anayzing fund data……")
    df_funds["dynbalance"] += init_capital
    ayBal = df_funds["dynbalance"]              # 每日期末动态权益

    #生成每日期初动态权益
    ayPreBal = np.array(ayBal.tolist()[:-1])  
    ayPreBal = np.insert(ayPreBal, 0, init_capital)    #每日期初权益
    df_funds["prebalance"] = ayPreBal

    #统计期末权益大于期初权益的天数，即盈利天数
    windays = len(df_funds[df_funds["dynbalance"]>df_funds["prebalance"]])

    #每日净值
    ayNetVals = (ayBal/init_capital)
    
    ar = math.pow(ayNetVals.iloc[-1], annual_days/days) - 1       #年化收益率=总收益率^(年交易日天数/统计天数)
    ayDailyReturn = ayBal/ayPreBal-1 #每日收益率
    delta = fmtNAN(ayDailyReturn.std(axis=0)*math.pow(annual_days,0.5),0)       #年化标准差=每日收益率标准差*根号下(年交易日天数)
    down_delta = fmtNAN(ayDailyReturn[ayDailyReturn<0].std(axis=0)*math.pow(annual_days,0.5), 0)    #下行标准差=每日亏损收益率标准差*根号下(年交易日天数)

    #sharpe率
    if delta != 0.0:
        sr = (ar-rf)/delta
    else:
        sr = 9999.0

    #计算最大回撤和最大上涨
    maxub = ayNetVals[0]
    minub = maxub
    mdd = 0.0
    midd = 0.0
    mup = 0.0
    for idx in range(1,len(ayNetVals)):
        maxub = max(maxub, ayNetVals[idx])
        minub = min(minub, ayNetVals[idx])
        profit = (ayNetVals[idx] - ayNetVals[idx-1])/ayNetVals[idx-1]
        falldown = (ayNetVals[idx] - maxub)/maxub
        riseup = (ayNetVals[idx] - minub)/minub
        if profit <= 0:
            midd = max(midd, abs(profit))
            mdd = max(mdd, abs(falldown))
        else:
            mup = max(mup, abs(riseup))
    #索提诺比率
    if down_delta != 0.0:
        sortino = (ar-rf)/down_delta
    else:
        sortino = 0.0
    if mdd != 0.0:
        calmar = ar/mdd
    else:
        calmar = 999999.0

    #输出到excel
    sheetName = '逐日绩效概览'
    worksheet = workbook.add_worksheet(sheetName)

    #   设置合并单元格及格式   #
    # ~~~~~~ 写入数据 ~~~~~~ #
    title_format = workbook.add_format({
        'bold':     True,
        'border':   1,
        'align':    'center',   # 水平居中
        'valign':   'vcenter',  # 垂直居中
        'fg_color': '#bcbcbc'
    })
    fund_data_format = workbook.add_format({
        'border': 1,
        'align':    'right',    # 右对齐
        'valign':   'vcenter',  # 垂直居中
    })
        
    fund_data_format_2 = workbook.add_format({
        'border': 1,
        'align':    'right',    # 右对齐
        'valign':   'vcenter',  # 垂直居中
        'num_format': '0.00'
    })

    fund_data_format_3 = workbook.add_format({
        'border': 1,
        'align':    'right',    # 右对齐
        'valign':   'vcenter',  # 垂直居中
        'num_format': '0.000'
    })

    fund_data_format_4 = workbook.add_format({
        'border': 1,
        'align':    'right',    # 右对齐
        'valign':   'vcenter',  # 垂直居中
        'num_format': '0.0000'
    })


    merge_format = workbook.add_format({
        'font_size': 16,
        'bold':     True,
        'align':    'center',   # 水平居中
        'valign':   'vcenter',  # 垂直居中
    })
    indicator_format = workbook.add_format({
        'font_size': 12,
        'bold':     True,
        'align':    'center',   # 水平居中
        'valign':   'vcenter',  # 垂直居中
    })
    worksheet.merge_range('A1:D1', '收益率统计指标', merge_format)
    worksheet.merge_range('E1:H1', '风险统计指标', merge_format)
    worksheet.merge_range('I1:K1', '综合指标', merge_format)

    key_indicator = ['交易天数', '累积收益（%）', '年化收益率（%）', '胜率（%）', '最大回撤（%）', '最大上涨（%）', '标准差（%）',
            '下行波动率（%）', 'Sharpe比率', 'Sortino比率', 'Calmar比率']
    key_data = [(ayNetVals.iloc[-1]-1)*100, ar*100, (windays/days)*100, mdd*100, mup*100, delta*100, down_delta*100, sr, sortino, calmar]
    worksheet.write_row('A2', key_indicator, indicator_format)
    worksheet.write_column('A3', [days], fund_data_format)
    worksheet.write_row('B3', key_data, fund_data_format_3)

    #   画图   #
    chart_col = workbook.add_chart({'type': 'line'})
    length = days
    chart_col.add_series(                                   # 给图表设置格式，填充内容
        {
            'name': '累计净值',
            'categories': '=逐日绩效分析!$A$3:$A$%d' % (length+2),
            'values':   '=逐日绩效分析!$G$3:$G$%d' % (length+2),
            'line': {'color': 'blue', 'width':1},
        }
    )
    chart_col.set_title({'name': '累计净值'})
    worksheet.insert_chart('A8', chart_col)

    #  准备第二张表格  #
    sheetName = '逐日绩效分析'
    worksheet = workbook.add_worksheet(sheetName)
    title_format2 = workbook.add_format({
        'border': 1,
        'align':    'center',   # 水平居中
        'valign':   'vcenter',  # 垂直居中
        'fg_color': '#D3D3D3',
        'text_wrap': 1
    })
    worksheet.merge_range('A1:A2', '日期', title_format2)
    worksheet.merge_range('B1:B2', '统计时间', title_format2)
    worksheet.merge_range('C1:C2', '初始资金', title_format2)
    worksheet.merge_range('D1:D2', '出入金', title_format2)
    worksheet.merge_range('E1:E2', '当前权益', title_format2)
    worksheet.merge_range('F1:F2', '累计盈亏', title_format2)
    worksheet.merge_range('G1:G2', '累计净值', title_format2)
    worksheet.merge_range('H1:I1', '当日盈亏', title_format2)
    indicator = ['数值', '比例']
    worksheet.write_row('H2', indicator, title_format2)
    worksheet.merge_range('J1:J2', '峰值', title_format2)
    worksheet.merge_range('K1:K2', '当日累计回撤', title_format2)
    worksheet.merge_range('L1:L2', '历史最大累计回撤', title_format2)
    worksheet.merge_range('M1:M2', '最大单日回撤', title_format2)
    worksheet.merge_range('N1:N2', '衰落时间', title_format2)
    # worksheet.merge_range('O1:O2', 'IF指数', title_format2)
    # worksheet.merge_range('P1:P2', 'IF净值', title_format2)

    #  写入内容  #
    profit_format = workbook.add_format({
        'border': 1,
        'align':    'right',    # 靠右
        'valign':   'vcenter',  # 垂直居中
        'fg_color': '#FAFAD2',
        'num_format': '0.00'
    })

    percent_format = workbook.add_format({
        'border': 1,
        'align':    'right',    # 右对齐
        'valign':   'vcenter',  # 垂直居中
        'num_format': '0.00%'
    })

    date_format = workbook.add_format({
        'num_format':   'yyyy/mm/dd',
        'border': 1,
        'align':    'right',    # 右对齐
        'valign':   'vcenter',  # 垂直居中
    })

    ayDates = df_funds['date'].apply(lambda x: str(x)[:4]+'/'+str(x)[4:6]+'/'+str(x)[6:8])
    worksheet.write_column('A3', ayDates, date_format)
    worksheet.write_column('B3', range(len(df_funds)), fund_data_format)
    initial = [init_capital]*len(df_funds)
    worksheet.write_column('C3', initial, fund_data_format)
    worksheet.write_column('D3', '/', fund_data_format)
    worksheet.write_column('E3', ayBal, fund_data_format)
    worksheet.write_column('F3', ayBal-init_capital, fund_data_format_2)
    worksheet.write_column('G3', ayNetVals, fund_data_format_4)
    worksheet.write_column('H3', ayBal-ayPreBal, profit_format)
    worksheet.write_column('I3', ayDailyReturn, percent_format)
    #  计算峰值
    upper = np.maximum.accumulate(ayNetVals)
    worksheet.write_column('J3', upper, fund_data_format_4)
    #  回撤指标
    temp = 1-(ayNetVals)/(np.maximum.accumulate(ayNetVals))
    worksheet.write_column('K3', temp, percent_format)
    worksheet.write_column('L3', np.maximum.accumulate(temp), percent_format)
    worksheet.write_column('M3', np.minimum.accumulate(ayDailyReturn), percent_format)
    #  计算衰落时间
    down_time = [0]
    for i in range(1, len(upper)):
        if upper[i] > upper[i-1]:
            down_time.append(0)
        else:
            l = down_time[i-1]
            down_time.append(l+1)
    worksheet.write_column('N3', down_time, fund_data_format)

def do_trading_analyze2(df_closes, df_funds):
    df_wins = df_closes[df_closes["profit"] > 0]
    df_loses = df_closes[df_closes["profit"] <= 0]

    ay_WinnerBarCnts = df_wins["closebarno"] - df_wins["openbarno"]
    ay_LoserBarCnts = df_loses["closebarno"] - df_loses["openbarno"]
    total_winbarcnts = ay_WinnerBarCnts.sum()
    total_losebarcnts = ay_LoserBarCnts.sum()

    total_fee = df_closes['fee'].sum()  # 手续费

    totaltimes = len(df_closes)  # 总交易次数
    wintimes = len(df_wins)  # 盈利次数
    losetimes = len(df_loses)  # 亏损次数
    winamout = float(df_wins["profit"].sum())  # 毛盈利
    loseamount = float(df_loses["profit"].sum())  # 毛亏损
    trdnetprofit = winamout + loseamount  # 交易净盈亏
    accnetprofit = trdnetprofit - total_fee  # 账户净盈亏
    winrate = (wintimes / totaltimes) if totaltimes > 0 else 0  # 胜率
    avgprof = (trdnetprofit / totaltimes) if totaltimes > 0 else 0  # 单次平均盈亏
    avgprof_win = (winamout / wintimes) if wintimes > 0 else 0  # 单次盈利均值
    avgprof_lose = (loseamount / losetimes) if losetimes > 0 else 0  # 单次亏损均值
    winloseratio = abs(avgprof_win / avgprof_lose) if avgprof_lose != 0 else "N/A"  # 单次盈亏均值比

    # 单笔最大盈利交易
    largest_profit = float(df_wins['profit'].max())
    # 单笔最大亏损交易
    largest_loss = float(df_loses['profit'].min())
    # 交易的平均持仓K线根数
    avgtrd_hold_bar = 0 if totaltimes==0 else ((df_closes['closebarno'] - df_closes['openbarno']).sum()) / totaltimes
    # 平均空仓K线根数
    avb = (df_closes['openbarno'] - df_closes['closebarno'].shift(1).fillna(value=0))
    avgemphold_bar = 0 if len(df_closes)==0 else avb.sum() / len(df_closes)

    # 两笔盈利交易之间的平均空仓K线根数
    win_holdbar_situ = (df_wins['openbarno'].shift(-1) - df_wins['closebarno']).dropna()
    winempty_avgholdbar = 0 if len(df_wins)== 0 or len(df_wins) == 1 else win_holdbar_situ.sum() / (len(df_wins)-1)
    # 两笔亏损交易之间的平均空仓K线根数
    loss_holdbar_situ = (df_loses['openbarno'].shift(-1) - df_loses['closebarno']).dropna()
    lossempty_avgholdbar = 0 if len(df_loses)== 0 or len(df_loses) == 1 else loss_holdbar_situ.sum() / (len(df_loses)-1)
    max_consecutive_wins = 0  # 最大连续盈利次数
    max_consecutive_loses = 0  # 最大连续亏损次数

    avg_bars_in_winner = total_winbarcnts / wintimes if wintimes > 0 else "N/A"
    avg_bars_in_loser = total_losebarcnts / losetimes if losetimes > 0 else "N/A"

    consecutive_wins = 0
    consecutive_loses = 0

    for idx, row in df_closes.iterrows():
        profit = row["profit"]
        if profit > 0:
            consecutive_wins += 1
            consecutive_loses = 0
        else:
            consecutive_wins = 0
            consecutive_loses += 1

        max_consecutive_wins = max(max_consecutive_wins, consecutive_wins)
        max_consecutive_loses = max(max_consecutive_loses, consecutive_loses)

    summary = dict()

    summary["total_trades"] = totaltimes
    summary["profit"] = float(winamout)
    summary["loss"] = float(loseamount)
    summary["net_profit"] = float(trdnetprofit)
    summary["fee"] = total_fee
    summary["accnet_profit"] = 0 if totaltimes == 0 else accnetprofit
    summary["winrate"] = winrate * 100
    summary["avgprof"] = avgprof
    summary["avgprof_win"] = avgprof_win
    summary["avgprof_lose"] = avgprof_lose
    summary["winloseratio"] = winloseratio
    summary["largest_profit"] = largest_profit
    summary["largest_loss"] = largest_loss
    summary["avgtrd_hold_bar"] = avgtrd_hold_bar
    summary["avgemphold_bar"] = avgemphold_bar
    summary["winempty_avgholdbar"] = winempty_avgholdbar
    summary["lossempty_avgholdbar"] = lossempty_avgholdbar
    summary["avg_bars_in_winner"] = avg_bars_in_winner
    summary["avg_bars_in_loser"] = avg_bars_in_loser
    summary["max_consecutive_wins"] = max_consecutive_wins
    summary["max_consecutive_loses"] = max_consecutive_loses


    return summary

class WtBtAnalyst:

    def __init__(self):
        self.__strategies__ = dict()
        return

    def add_strategy(self,  sname:str, folder:str, init_capital:float, rf:float=0.02, annual_trading_days:int = 240):
        self.__strategies__[sname] = {
            "folder": folder,
            "cap":init_capital,
            "rf":rf,
            "atd":annual_trading_days
        }

    def run_new(self, outFileName:str = ''):
        if len(self.__strategies__.keys()) == 0:
            raise Exception("strategies is empty")

        for sname in self.__strategies__:
            sInfo = self.__strategies__[sname]
            folder = os.path.join(sInfo["folder"], sname)
            print("start PnL analyzing for strategy %s……" % (sname))

            df_funds = pd.read_csv(os.path.join(folder,"funds.csv"))
            df_closes = pd.read_csv(os.path.join(folder, "closes.csv"))
            df_trades = pd.read_csv(os.path.join(folder, "trades.csv"))

            if len(outFileName) == 0:
                outFileName = 'Strategy[%s]_PnLAnalyzing_%s_%s.xlsx' % (sname, df_funds['date'][0], df_funds['date'].iloc[-1])

            workbook = Workbook(outFileName)
            init_capital = sInfo["cap"]
            annual_days = sInfo["atd"]
            rf = sInfo["rf"]

            strategy_analyze(workbook, df_closes.copy(), df_trades.copy(),df_funds.copy(), capital=init_capital, rf=rf, period=annual_days)
            output_closes(workbook, df_closes.copy(), capital=init_capital)
            trading_analyze(workbook, df_closes.copy(), df_funds.copy(), capital=init_capital)
            funds_analyze(workbook, df_funds.copy(), capital=init_capital, rf=rf, period=annual_days)

            workbook.close()

            filename = os.path.join(folder,"summary.json")
            sumObj = summary_analyze(df_funds, capital=init_capital, rf=rf, period=annual_days)
            sumObj["name"] = sname
            f = open(filename,"w")
            f.write(json.dumps(sumObj, indent=4, ensure_ascii=True))
            f.close()

            print("PnL analyzing of strategy %s done" % (sname))


    def run(self, outFileName:str = ''):
        if len(self.__strategies__.keys()) == 0:
            raise Exception("strategies is empty")

        for sname in self.__strategies__:
            sInfo = self.__strategies__[sname]
            # folder = sInfo["folder"]
            folder = os.path.join(sInfo["folder"], sname)
            print("start PnL analyzing for strategy %s……" % (sname))

            df_funds = pd.read_csv(os.path.join(folder, "funds.csv"))
            print("fund logs loaded……")

            init_capital = sInfo["cap"]
            annual_days = sInfo["atd"]
            rf = sInfo["rf"]
            
            if len(outFileName) == 0:
                outFileName = 'Strategy[%s]_PnLAnalyzing_%s_%s.xlsx' % (sname, df_funds['date'][0], df_funds['date'].iloc[-1])
            workbook = Workbook(outFileName)
            funds_analyze(workbook, df_funds, capital=init_capital, rf=rf, period=annual_days)
            workbook.close()

            print("PnL analyzing of strategy %s done" % (sname))

    def run_simple(self):
        if len(self.__strategies__.keys()) == 0:
            raise Exception("strategies is empty")

        for sname in self.__strategies__:
            sInfo = self.__strategies__[sname]
            folder = os.path.join(sInfo["folder"],sname)

            df_funds = pd.read_csv(os.path.join(folder, "funds.csv"))

            init_capital = sInfo["cap"]
            annual_days = sInfo["atd"]
            rf = sInfo["rf"]
            
            filename = folder + 'summary.json'
            sumObj = summary_analyze(df_funds, capital=init_capital, rf=rf, period=annual_days)
            sumObj["name"] = sname
            f = open(filename,"w")
            f.write(json.dumps(sumObj, indent=4, ensure_ascii=True))
            f.close()

    def run_flat(self):
        for sname in self.__strategies__:
            sInfo = self.__strategies__[sname]
            capital = sInfo["cap"]
            annual_days = sInfo["atd"]
            rf = sInfo["rf"]

            folder = os.path.join(sInfo["folder"],sname)

            df_funds = pd.read_csv(os.path.join(folder, "funds.csv"))
            df_closes = pd.read_csv(os.path.join(folder, "closes.csv"))

            df_closes['fee'] = df_closes['profit'] - df_closes['totalprofit'] + df_closes['totalprofit'].shift(1).fillna(value=0)
            df_long = df_closes[df_closes['direct'].apply(lambda x: 'LONG' in x)]
            df_short = df_closes[df_closes['direct'].apply(lambda x: 'SHORT' in x)]

            summary_all = do_trading_analyze2(df_closes, df_funds)
            summary_short = do_trading_analyze2(df_short, df_funds)
            summary_long = do_trading_analyze2(df_long, df_funds)

            filename = os.path.join(folder, 'trdana.json')
            f = open(filename,"w")
            f.write(json.dumps({
                "all": summary_all,
                "long": summary_long,
                "short": summary_short
            }, indent=4, ensure_ascii=True))
            f.close()

            df_closes = df_closes.copy()
            df_closes['fee'] = df_closes['profit'] - df_closes['totalprofit'] + df_closes['totalprofit'].shift(1).fillna(
                value=0)
            df_closes['profit'] = df_closes['profit'] - df_closes['fee']
            df_closes['profit_sum'] = df_closes['profit'].expanding(1).sum()
            df_closes['Withdrawal'] = df_closes['profit_sum'] - df_closes['profit_sum'].expanding(1).max()
            df_closes['profit_ratio'] = 100 * df_closes['profit_sum'] / capital
            withdrawal_ratio = []
            sim_equity = df_closes['profit_sum'] + capital
            for i in range(len(df_closes)):
                withdrawal_ratio.append(100 * (sim_equity[i] / sim_equity[:i + 1].max() - 1))
            df_closes['Withdrawal_ratio'] = withdrawal_ratio
            np_trade = np.array(df_closes).tolist()
            closes_all = list()
            for item in np_trade:
                litem = {
                    "opentime":int(item[2]),
                    "closetime":int(item[4]),
                    "profit":float(item[7]),
                    "direct":str(item[1]),
                    "openprice":float(item[3]),
                    "closeprice":float(item[5]),
                    "maxprofit":float(item[8]),
                    "maxloss":float(item[9]),
                    "qty":int(item[6]),
                    "capital": capital,
                    'profit_sum':float(item[16]),
                    'Withdrawal':float(item[17]),
                    'profit_ratio':float(item[18]),
                    'Withdrawal_ratio':float(item[19])
                }
                closes_all.append(litem)
            df_closes['time'] = df_closes['closetime'].apply(lambda x: datetime.strptime(str(x), '%Y%m%d%H%M'))
            df_c_m = df_closes.resample(rule='M', on='time', label='right',
                                                                    closed='right').agg({
                'profit': 'sum',
                'maxprofit': 'sum',
                'maxloss': 'sum',
            })
            df_c_m = df_c_m.reset_index()
            df_c_m['equity'] = df_c_m['profit'].expanding(1).sum() + capital
            df_c_m['monthly_profit'] = 100 * (df_c_m['equity'] / df_c_m['equity'].shift(1).fillna(value=capital) - 1)
            closes_month = list()
            np_m = np.array(df_c_m).tolist()
            for item in np_m:
                litem = {
                    "time":int(item[0].strftime('%Y%m')),
                    "profit":float(item[1]),
                    'maxprofit':float(item[2]),
                    'maxloss':float(item[3]),
                    'equity':float(item[4]),
                    'monthly_profit':float(item[5])
                }
                closes_month.append(litem)

            df_c_y = df_closes.resample(rule='Y', on='time', label='right',
                                        closed='right').agg({
                'profit': 'sum',
                'maxprofit': 'sum',
                'maxloss': 'sum',
            })
            df_c_y = df_c_y.reset_index()
            df_c_y['equity'] = df_c_y['profit'].expanding(1).sum() + capital
            df_c_y['monthly_profit'] = 100 * (df_c_y['equity'] / df_c_y['equity'].shift(1).fillna(value=capital) - 1)
            closes_year = list()
            np_y = np.array(df_c_y).tolist()
            for item in np_y:
                litem = {
                    "time":int(item[0].strftime('%Y%m')),
                    "profit":float(item[1]),
                    'maxprofit':float(item[2]),
                    'maxloss':float(item[3]),
                    'equity':float(item[4]),
                    'annual_profit':float(item[5])
                }
                closes_year.append(litem)

            df_long = df_closes[df_closes['direct'].apply(lambda x: 'LONG' in x)]
            df_short = df_closes[df_closes['direct'].apply(lambda x: 'SHORT' in x)]
            df_long = df_long.copy()
            df_short = df_short.copy()
            df_long["long_profit"] = df_long["profit"].expanding(1).sum()-df_long["fee"].expanding(1).sum()
            closes_long = list()
            closes_short = list()
            np_long = np.array(df_long).tolist()
            for item in np_long:
                litem = {
                    "date":int(item[4]),
                    "long_profit":float(item[-1]),
                    "capital":capital
                }
                closes_long.append(litem)
            df_short["short_profit"] = df_short["profit"].expanding(1).sum()-df_short["fee"].expanding(1).sum()
            np_short = np.array(df_short).tolist()
            for item in np_short:
                litem = {
                    "date":int(item[4]),
                    "short_profit":float(item[-1]),
                    "capital":capital
                }
                closes_short.append(litem)

            filename = os.path.join(folder, 'rndana.json')
            f = open(filename,"w")
            f.write(json.dumps({
                "long": closes_long,
                "short": closes_short,
                "all": closes_all,
                "month": closes_month,
                "year": closes_year
            }, indent=4, ensure_ascii=True))
            f.close()
            
            filename = os.path.join(folder,"summary.json")
            sumObj = summary_analyze(df_funds, capital=capital, rf=rf, period=annual_days)
            sumObj["name"] = sname
            f = open(filename,"w")
            f.write(json.dumps(sumObj, indent=4, ensure_ascii=True))
            f.close()