import numpy as np
import pandas as pd
from dateutil.parser import parse

from wtpy.apps.btanalyst.calculate import Calculate

def time_analysis(data):
    # 交易时间
    trading_time = data['closebarno'][len(data) - 1] * 5

    def time_trans(x):
        d = x // (24 * 60)
        h = x % (24 * 60) // 60
        m = x % (24 * 60) % 60
        return d, h, m
    # 转化为日，时，分
    s_trading_time = time_trans(trading_time)

    # 策略运行时间
    str_time = (data['closebarno'] - data['openbarno']).sum() * 5
    s_str_time = time_trans(str_time)
    # 比率
    porition = str_time / trading_time * 100

    # 最大空仓时间
    empty_time = (data['openbarno'].shift(-1) - data['closebarno']).max() * 5
    s_empty_time = time_trans(empty_time)

    capital = 500000
    data['principal'] = data['totalprofit'] + capital
    data['principal'] = data['principal'].shift(1)
    input_data = data.fillna(value=500000)
    ret = input_data['profit'] / input_data['principal']
    mar = 0
    rf = 0.02
    period = 240
    trade = input_data['closebarno'][len(input_data) - 1] / 47
    factors = Calculate(ret, mar, rf, period, trade)

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

    result = {'交易周期': s_trading_time,
              '策略运行时间': s_str_time,
              '策略运行时间%': porition,
              '最长空仓时间': s_empty_time,
              '策略最大回撤开始日期': start_time,
              '策略最大回撤结束日期': end_time,
              '单笔最大回撤日期': signe_drawdown_date,
              '平仓交易最大损失日期': loss_time}

    return result

