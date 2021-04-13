# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from wtpy.apps.btanalyst.calculate import Calculate
from wtpy.apps.btanalyst.performance_of_strategy import performance_summary


def ratio_calculate(data, after_merge):
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
    result1 = performance_summary(data, after_merge)
    # 净利/单笔最大亏损
    net_s_loss = result1.get('净利') / result1.get('单笔最大亏损')
    # 净利/单笔最大回撤
    net_s_drawdown = result1.get('净利') / factors.single_largest_maxdrawdown()
    # 净利/ 策略最大回撤
    net_strategy_drawdown =  result1.get('净利') / factors.maxDrawdown()
    # 调整净利/单笔最大亏损
    adjust_s_loss = result1.get('调整净利') / result1.get('单笔最大亏损')
    # 调整净利/单笔最大回撤
    adjust_s_drawdown = result1.get('调整净利') / factors.single_largest_maxdrawdown()
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

