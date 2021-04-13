# -*- coding: utf-8 -*-
import numpy as np
from wtpy.apps.btanalyst.calculate import Calculate


def performance_summary(input_data, input_data1, capital = 500000):
    """
    :param input_data:
    :param input_data1:
    :return:
    """
    # 指标计算准备
    input_data['principal'] = input_data['totalprofit'] + capital
    input_data['principal'] = input_data['principal'].shift(1)
    input_data = input_data.fillna(value=capital)
    ret = input_data['profit'] / input_data['principal']
    mar = 0
    rf = 0.00
    period = 240
    trade = len(input_data)
    #trade = input_data['closebarno'][len(input_data)-1] / 47

    # 指标class
    factors = Calculate(ret, mar, rf, period, trade)
    # 毛利
    profit = input_data[input_data['profit'].apply(lambda x: x >= 0)]
    total_profit = profit['profit'].sum()
    # 毛损
    loss = input_data[input_data['profit'].apply(lambda x: x < 0)]
    total_loss = loss['profit'].sum()
    # 净利
    net_profit = total_profit + total_loss
    input_data1['adjust_profit'] = input_data1['profit'] - input_data1['transaction_fee']
    # 调整毛利
    adjust_profit = input_data1[input_data1['adjust_profit'].apply(lambda x: x >= 0)]
    total_adjust_profit = adjust_profit['adjust_profit'].sum()
    # 调整毛损
    adjust_loss = input_data1[input_data1['adjust_profit'].apply((lambda x: x < 0))]
    total_adjust_loss = adjust_loss['adjust_profit'].sum()
    # 调整净利
    adjust_net_profit = total_adjust_profit + total_adjust_loss
    # 盈利因子
    profit_factor = np.abs(total_profit / total_loss)
    # 调整盈利因子
    adjust_profit_factor = np.abs(total_adjust_profit / total_adjust_loss)
    # 最大持有合约数量
    max_holding_number = 1
    # 已付手续费
    paid_trading_fee = input_data1['transaction_fee'].sum()
    # 单笔最大亏损
    single_loss = input_data[input_data['profit'].apply(lambda x: x < 0)]
    single_loss = single_loss['profit']
    single_largest_loss = abs(single_loss.min())
    # 平仓交易最大亏损
    trading_loss = single_largest_loss
    # 平仓交易最大亏损比
    trading_loss_rate = trading_loss / capital
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
              '调整毛利': adjust_net_profit,
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
