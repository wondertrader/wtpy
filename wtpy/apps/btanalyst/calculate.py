# -*- coding: utf-8 -*-
"""
Created on Mon Dec 22 15:10:09 2020
@author: Jing
"""

import numpy as np
import pandas as pd
import math

# 绩效比率计算
class Calculate():

    def __init__(self, ret, mar, rf, period, trade):
        """
        :param ret: 收益率序列
        :param mar: 最低可接受回报
        :param rf: 无风险利率
        :param period: 年交易日（用来年化）240
        """
        self.ret = ret
        self.mar = mar
        self.rf = rf
        self.trade = math.ceil(trade)
        self.period = period
        self.daily_rf = (self.rf + 1) ** (1 / self.period) - 1

    # 潜在上行比率
    def calculate_upside_ratio(self):
        acess_return = np.sum(self.ret - self.mar)
        downside_std = self.ret[self.ret.apply(lambda x: x < 0)].std()
        upside_ratio = acess_return / downside_std
        return upside_ratio

    # 夏普率
    def sharp_ratio(self):
        expect_return = self.ret.mean()
        std = self.ret.std()
        sharp_ratio = (expect_return - self.daily_rf) / std
        return sharp_ratio

    # 索提诺比率
    def sortion_ratio(self):
        expect_return = self.ret.mean()
        downside_std = self.ret[self.ret.apply(lambda x: x < 0)].std()
        sortion_ratio = (expect_return - self.daily_rf) / downside_std
        return sortion_ratio

    # 最大回撤
    def maxDrawdown(self):
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
        maxdrawdown = Calculate.maxDrawdown(self)
        annual_return = Calculate.get_annual_return(self)
        calmar_ratio = annual_return / maxdrawdown
        return calmar_ratio

    # 斯特林比率
    def sterling_a_ratio(self):
        average_drawdown = abs(self.ret.where(self.ret < 0, 0).mean())
        annual_return = Calculate.get_annual_return(self)
        sterling_a_ratio = (annual_return - self.rf) / average_drawdown
        return sterling_a_ratio

    # 单笔最大回撤
    def single_largest_maxdrawdown(self):
        single_largest_mdd = self.ret[self.ret.apply(lambda x: x < 0)]
        if len(single_largest_mdd) == 0:
            single_largest_mxd = 0
            return single_largest_mxd
        single_largest_mxd = abs(single_largest_mdd.min())
        return single_largest_mxd

    # 单笔最大回撤索引
    def single_maxdrawdown_time(self):
        i = np.argmin(self.ret)
        return i

    # 年化收益率
    def get_annual_return(self):
        annual_return = (1 + self.ret.sum()) ** (self.period / self.trade) - 1
        return annual_return

    # 月化收益率
    def monthly_return(self):
        ann = Calculate.get_annual_return(self)
        monthly_return = (ann + 1) ** (1/12) - 1
        return monthly_return

    # 月平均收益
    def monthly_average_return(self):
        monthly = self.ret.mean() * (self.period / 12)
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



if __name__ =='__main__':
    daa = pd.read_excel('C:/Users/wzer/Desktop/data/new_dat.xlsx', header=0)
    ret = daa['ret']
    mar = 0
    rf = 0.00
    period = 240
    trade = len(daa)
    factor =Calculate(ret, mar, rf, period, trade)
    s = factor.decay_time()
    print(s)