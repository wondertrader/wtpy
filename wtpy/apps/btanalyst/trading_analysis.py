import numpy as np
import pandas as pd
from dateutil.parser import parse

def __ayalyze_result__(df_closes, df_funds):

    df_wins = df_closes[df_closes["profit"] > 0]
    df_loses = df_closes[df_closes["profit"] <= 0]

    ay_WinnerBarCnts = df_wins["closebarno"] - df_wins["openbarno"]
    ay_LoserBarCnts = df_loses["closebarno"] - df_loses["openbarno"]

    total_winbarcnts = ay_WinnerBarCnts.sum()
    total_losebarcnts = ay_LoserBarCnts.sum()

    total_fee = df_funds.iloc[-1]["fee"]

    totaltimes = len(df_closes)  # 总交易次数
    wintimes = len(df_wins)  # 盈利次数
    losetimes = len(df_loses)  # 亏损次数
    winamout = df_wins["profit"].sum()  # 毛盈利
    loseamount = df_loses["profit"].sum()  # 毛亏损
    trdnetprofit = winamout + loseamount  # 交易净盈亏
    accnetprofit = trdnetprofit - total_fee  # 账户净盈亏
    winrate = wintimes / totaltimes if totaltimes > 0 else 0  # 胜率
    avgprof = trdnetprofit / totaltimes if totaltimes > 0 else 0  # 单次平均盈亏
    avgprof_win = winamout / wintimes if wintimes > 0 else 0  # 单次盈利均值
    avgprof_lose = loseamount / losetimes if losetimes > 0 else 0  # 单次亏损均值
    winloseratio = abs(avgprof_win / avgprof_lose) if avgprof_lose != 0 else "N/A"  # 单次盈亏均值比

    # 单笔最大盈利交易
    largest_profit = df_wins['profit'].max()
    # 单笔最大亏损交易
    largest_loss = df_loses['profit'].min()
    # 交易的平均持仓K线根数
    avgtrd_hold_bar = ((df_closes['closebarno'] - df_closes['openbarno']).sum()) / totaltimes
    # 平均空仓K线根数
    avb = (df_closes['openbarno'].shift(-1) - df_closes['closebarno']).dropna()
    avgemphold_bar = avb.sum() / len(df_closes)

    # 两笔盈利交易之间的平均空仓K线根数
    win_holdbar_situ = (df_wins['openbarno'].shift(-1) - df_wins['closebarno']).dropna()
    winempty_avgholdbar = win_holdbar_situ.sum() / len(df_wins)
    # 两笔亏损交易之间的偶平均空仓K线根数
    loss_holdbar_situ = (df_loses['openbarno'].shift(-1) - df_loses['closebarno']).dropna()
    lossempty_avgholdbar = loss_holdbar_situ.sum() / len(df_loses)

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

    summary = df_wins

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
    summary["账户净盈亏"] = accnetprofit / totaltimes
    summary['单笔最大盈利交易'] = largest_profit
    summary['单笔最大亏损交易'] = largest_loss
    summary['交易的平均持仓K线根数'] = avgtrd_hold_bar
    summary['平均空仓K线根数'] = avgemphold_bar
    summary['两笔盈利交易之间的平均空仓K线根数'] = winempty_avgholdbar
    summary['两笔亏损交易之间的平均空仓K线根数'] = lossempty_avgholdbar
    summary = summary.drop(columns=['code', 'direct', 'opentime', 'openprice', 'closetime', 'closeprice',
                                    'qty', 'profit', 'totalprofit', 'entertag', 'exittag', 'openbarno', 'closebarno'])

    summary = summary.iloc[0, :]
    summary = pd.DataFrame([summary]).T
    summary = summary.reset_index()
    return summary


def sum_closes_data(data):

    data['opentime'] = data['opentime'].apply(lambda x: parse(str(int(x / 10000))))
    data['win'] = data['profit'].apply(lambda x: abs(x + 1) / (x + 1))
    data['gross_profit'] = data['profit'].apply(lambda x: x if x > 0 else 0)
    data['gross_loss'] = data['profit'].apply(lambda x: x if x < 0 else 0)
    profit = data.groupby(data['opentime']).sum()
    profit['win_rate'] = (profit['qty'] + profit['win']) * 0.5 / profit['qty']
    res = profit[['profit', 'gross_profit', 'gross_loss', 'qty', 'win_rate']]
    return res

