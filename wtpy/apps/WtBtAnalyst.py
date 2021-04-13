from pandas import DataFrame as df
import pandas as pd
import numpy as np
import math
import xlsxwriter

from wtpy.apps.btanalyst.performance_of_strategy import performance_summary
from wtpy.apps.btanalyst.ratio_calculation import ratio_calculate
from wtpy.apps.btanalyst.time_analysis import time_analysis

from wtpy.apps.btanalyst.continue_trading_analysis import average_profit, continue_trading_analysis, extreme_trading
from wtpy.apps.btanalyst.trading_analysis import __ayalyze_result__
from wtpy.apps.btanalyst.trading_analysis import sum_closes_data

def fmtNAN(val, defVal = 0):
    if math.isnan(val):
        return defVal

    return val

def trading_analyze(excelwriter, df_closes, df_funds):

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

    ssaa = 1000
    # 连续交易系列分析
    s = continue_trading_analysis(df_closes, ssaa)
    # 极端交易
    ss = extreme_trading(df_closes)
    extre_pro = ss.get('单笔净利 +1倍标准差')
    extre_los = ss.get('单笔盈利 - 标准差')
    data1 = df_closes[df_closes['profit'].apply(lambda x: x > extre_pro)]
    data2 = df_closes[df_closes['profit'].apply(lambda x: x < extre_los)]
    ss_1 = extreme_trading(data1)
    ss_2 = extreme_trading(data2)
    ss_1 = pd.DataFrame([ss_1]).T
    ss_2 = pd.DataFrame([ss_2]).T
    sss = pd.concat([ss_1, ss_2], axis=1)
    ss = pd.DataFrame([ss]).T
    sss = pd.concat([ss, sss], axis=1)
    sss.columns = ['总计', '极端盈利', '极端亏损']

    s = pd.DataFrame([s]).T
    s.columns = ['']
    s.to_excel(excelwriter, sheet_name='交易分析')
    sss.to_excel(excelwriter, sheet_name='交易分析', startrow=10)
    f_result.to_excel(excelwriter, sheet_name='交易分析', startrow=20)
    f_2_result.to_excel(excelwriter, sheet_name='交易分析', startrow=30)
    #
    trade_s = __ayalyze_result__(df_closes, df_funds)

    data_1 = df_closes[df_closes['direct'].apply(lambda x: 'LONG' in x)]
    trade_s_long = __ayalyze_result__(data_1, df_funds)

    data_2 = df_closes[df_closes['direct'].apply(lambda x: 'SHORT' in x)]

    trade_s_short = __ayalyze_result__(data_2, df_funds)
    trade_s = trade_s.merge(trade_s_long, how='inner', on='index')
    trade_s = trade_s.merge(trade_s_short,how='inner', on='index')

    trade_s.columns =['', '所有交易', '多头', '空头']
    trade_s.to_excel(excelwriter, sheet_name='交易分析', startrow=45)

    res = sum_closes_data(df_closes)
    res.to_excel(excelwriter, sheet_name='周期分析')


def strategy_analyze(excelwriter, df_closes, df_trades, init_capital):
    data1_open = df_trades[df_trades['action'].apply(lambda x: 'OPEN' in x)].reset_index()
    data1_open = data1_open.drop(columns=['index'])
    data1_close = df_trades[df_trades['action'].apply(lambda x: 'CLOSE' in x)].reset_index()
    data1_close = data1_close.drop(columns=['index'])
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
    result1 = performance_summary(df_closes, after_merge, init_capital)

    result1_2 = performance_summary(data_long, after_merge_long, init_capital)

    result1_3 = performance_summary(data_short,after_merge_short, init_capital)
    result2 = ratio_calculate(df_closes, after_merge)
    result3 = time_analysis(df_closes)

    result1 = pd.DataFrame(pd.Series(result1), columns=['所有交易'])
    result1 = result1.reset_index().rename(columns={'index': '策略绩效概要'})

    result1_2 = pd.DataFrame(pd.Series(result1_2), columns=['多头交易'])
    result1_2 = result1_2.reset_index().rename(columns={'index': '策略绩效概要'})

    result1_3 = pd.DataFrame(pd.Series(result1_3), columns=['空头交易'])
    result1_3 = result1_3.reset_index().rename(columns={'index': '策略绩效概要'})

    result1 = result1.merge(result1_2,how='inner',on='策略绩效概要')
    result1 = result1.merge(result1_3,how='inner',on='策略绩效概要')

    result2 = pd.DataFrame(pd.Series(result2), columns=[''])
    result2 = result2.reset_index().rename(columns={'index': '绩效比率'})

    result3 = pd.DataFrame(pd.Series(result3), columns=[''])
    result3 = result3.reset_index().rename(columns={'index': '时间分析'})

    # excelwriter = pd.ExcelWriter('test.xlsx')

    result1.to_excel(excelwriter, sheet_name='策略分析')
    result2.to_excel(excelwriter, sheet_name='策略分析', startrow=20)
    result3.to_excel(excelwriter, sheet_name='策略分析', startrow=35)
    # excelwriter.save()

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

    def run_new(self):
        if len(self.__strategies__.keys()) == 0:
            raise Exception("strategies is empty")

        for sname in self.__strategies__:
            sInfo = self.__strategies__[sname]
            folder = sInfo["folder"]
            print("start PnL analyzing for strategy %s……" % (sname))

            df_funds = pd.read_csv(folder + "funds.csv")
            df_closes = pd.read_csv(folder + "closes.csv")
            df_trades = pd.read_csv(folder + "trades.csv")

            writer = pd.ExcelWriter('Strategy[%s]_PnLAnalyzing_%s_%s.xlsx' % (sname, df_funds['date'][0], df_funds['date'].iloc[-1]))
            init_capital = sInfo["cap"]
            strategy_analyze(writer, df_closes, df_trades, init_capital)
            trading_analyze(writer, df_closes, df_funds)
            writer.save()

            print("PnL analyzing of strategy %s done" % (sname))


    def run(self):
        if len(self.__strategies__.keys()) == 0:
            raise Exception("strategies is empty")

        for sname in self.__strategies__:
            sInfo = self.__strategies__[sname]
            folder = sInfo["folder"]
            print("start PnL analyzing for strategy %s……" % (sname))

            df_funds = pd.read_csv(folder + "funds.csv")
            print("fund logs loaded……")
            # df_closes = pd.read_csv(folder + "closes.csv")
            # df_signals = pd.read_csv(folder + "signals.csv")
            # df_trades = pd.read_csv(folder + "trades.csv")

            days = len(df_funds)
            init_capital = sInfo["cap"]
            annual_days = sInfo["atd"]
            rf = sInfo["rf"]

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
            print("outputting results to excel……")
            workbook = xlsxwriter.Workbook('Strategy[%s]_PnLAnalyzing_%s_%s.xlsx' % (sname, df_funds['date'][0], df_funds['date'].iloc[-1]))
            sheetName = '策略绩效概览'
            worksheet = workbook.add_worksheet(sheetName)

            #   设置合并单元格及格式   #
            # ~~~~~~ 写入数据 ~~~~~~ #
            title_format = workbook.add_format({
                'bold':     True,
                'border': 1,
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

            headings = ['日期', '累计净值']
            worksheet.write_row('A1', headings, title_format)
            worksheet.write_column('A2', df_funds['date'], fund_data_format)
            worksheet.write_column('B2', ayNetVals, fund_data_format_4)

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
            worksheet.merge_range('F1:I1', '收益率统计指标', merge_format)
            worksheet.merge_range('J1:M1', '风险统计指标', merge_format)
            worksheet.merge_range('N1:P1', '综合指标', merge_format)

            key_indicator = ['交易天数', '累积收益（%）', '年化收益率（%）', '胜率（%）', '最大回撤（%）', '最大上涨（%）', '标准差（%）',
                 '下行波动率（%）', 'Sharpe比率', 'Sortino比率', 'Calmar比率']
            key_data = [(ayNetVals.iloc[-1]-1)*100, ar*100, (windays/days)*100, mdd*100, mup*100, delta*100, down_delta*100, sr, sortino, calmar]
            worksheet.write_row('F2', key_indicator, indicator_format)
            worksheet.write_column('F3', [days], fund_data_format)
            worksheet.write_row('G3', key_data, fund_data_format_3)

            #   画图   #
            chart_col = workbook.add_chart({'type': 'line'})
            length = days
            chart_col.add_series(                                   # 给图表设置格式，填充内容
                {
                    'name': '=%s!$B$1' % (sheetName),
                    'categories': '=%s!$A$2:$A$%s' % (sheetName, length+1),
                    'values':   '=%s!$B$2:$B$%s' % (sheetName, length+1),
                    'line': {'color': 'blue'},
                }
            )
            chart_col.set_title({'name': '累计净值'})
            worksheet.insert_chart('F8', chart_col)

            #  准备第二张表格  #
            sheetName = '策略绩效分析'
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

            worksheet.write_column('A3', df_funds['date'], fund_data_format)
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
            #  输出IF指数值和IF净值###
            # worksheet.write_column('O3', data_funds['close'], fund_data_format_2)
            # net = data_funds['close']/data_funds['close'][0]
            # worksheet.write_column('P3', net, fund_data_format_4)
            #  画图设定#
            chart_col = workbook.add_chart({'type': 'line'})
            #  配置第一个系列
            chart_col.add_series({
                'name': '=%s!$G$1' % (sheetName),
                'categories': '=%s!$A$3:$A$%s' % (sheetName, length+2),
                'values':   '=%s!$G$3:$G$%s' % (sheetName, length+2),
                'line': {'color': 'blue'},
            })
            #  配置第二个系列
            # chart_col.add_series({
            #     'name': '=组合盘绩效统计!$P$1',
            #     'categories':  '=组合盘绩效统计!$A$3:$A$%s' % ((length+2)),
            #     'values':   '=组合盘绩效统计!$P$3:$P$%s' % ((length+2)),
            #     'line': {'color': 'red'},
            # })    
            chart_col.set_title({'name': '策略净值图'})
            worksheet.insert_chart('B16', chart_col)
            workbook.close()

            print("PnL analyzing of strategy %s done" % (sname))

        