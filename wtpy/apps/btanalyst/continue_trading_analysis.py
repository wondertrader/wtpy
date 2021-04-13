# -*- coding: utf-8 -*-
"""
Created on Tue Jan  5 13:13:39 2021
@author: Jing

"""
import pandas as pd
import numpy
from collections import Counter


def continue_trading_analysis(data, x_value):
    mean = data['profit'].mean()
    std = data['profit'].std()
    z_score = (x_value - mean) / std
    times = 0
    win_time = 0
    ltimes = 0
    loss_time = 0
    for i in range(len(data)-1):
        sss = data['profit'][i]
        if sss > 0:
            times += 1
            ltimes = 0
            rem = i
            if times > win_time:
                win_time = times
                con_win_p_end = rem
        else:
            times = 0
            ltimes += 1
            rem = i
            if ltimes > loss_time:
                loss_time = ltimes
                con_loss_p_end = rem

    capital = 500000
    con_win_profit = (data['profit'].loc[con_win_p_end-win_time + 1:con_win_p_end]).sum()
    con_lose_loss = (data['profit'].loc[con_loss_p_end-loss_time + 1:con_loss_p_end]).sum()
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


# 极端交易
def extreme_trading(data, time_of_std=1):
    std = data['profit'].std()
    df_wins = data[data["profit"] > 0]
    df_loses = data[data["profit"] <= 0]
    winamout = df_wins["profit"].sum()  # 毛盈利
    loseamount = df_loses["profit"].sum()  # 毛亏损
    trdnetprofit = winamout + loseamount  # 交易净盈亏
    totaltimes = len(data)  # 总交易次数
    avgprof = trdnetprofit / totaltimes if totaltimes > 0 else 0  # 单次平均盈亏

    # 单笔盈利 + 标准差
    sin_profit_plstd = avgprof + (std * time_of_std)
    # 单笔盈利 - 标准差
    sin_profit_mistd = avgprof - (std * time_of_std)

    # 极端交易数量
    extreme_result = data[data['profit'].apply(lambda x: x > sin_profit_plstd or x < sin_profit_mistd)]
    extreme_num = len(extreme_result)

    # 极端交易盈亏 1 Std. Deviation of Avg. Trade
    extreme_profit = extreme_result['profit'].sum()

    result = {'1 Std. Deviation of Avg. Trade': std,
              '单笔净利 +1倍标准差': sin_profit_plstd,
              '单笔盈利 - 标准差': sin_profit_mistd,
              '极端交易数量': extreme_num,
              '极端交易盈亏': extreme_profit
              }
    return result


# 连续交易分析
def average_profit(data):
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


if __name__ =='__main__':
    data = pd.read_csv('C:/Users/wzer/Desktop/data/ssd/closes.csv', header=0)
    ssaa = 1000
    s = continue_trading_analysis(data, ssaa)
    s3 = average_profit(data)

    s2f = s3.get('连续盈利次数')