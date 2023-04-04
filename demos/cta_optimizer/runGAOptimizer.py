# -- coding: utf-8 --

from wtpy.apps.WtCtaGAOptimizer import WtCtaGAOptimizer

import sys
sys.path.append('../Strategies')
from DualThrust import StraDualThrust

# 适应度函数
def my_optimizing_target(summary: dict):  # 单目标优化
    """ 编写优化目标 """
    target_value = summary["单次盈利均值"] / abs(summary["单次亏损均值"]) if summary["单次亏损均值"] != 0 else summary["单次盈利均值"]
    return target_value,  # 必须返回tuple类型


def runBaseOptimizer():
    # 新建一个优化器，并设置工作进程数为2
    population_size = 100  # 种群数
    mu = 80  # 每代个体选取数
    ngen_size = 5  # 进化代数
    cx_prb = 0.9  # 交叉概率
    mut_prb = 0.005  # 变异概率
    optimizer = WtCtaGAOptimizer(worker_num=2,
                                 population_size=population_size,
                                 MU=mu,
                                 ngen_size=ngen_size,
                                 cx_prb=cx_prb,
                                 mut_prb=mut_prb)

    # 引入适应度函数
    target_name = "单次盈亏比率"  # 默认为None
    optimizer.set_optimizing_func(calculator=my_optimizing_target, target_name=target_name)

    # 设置要使用的策略，只需要传入策略类型即可，同时设置策略ID的前缀，用于区分每个策略的实例
    optimizer.set_strategy(StraDualThrust, "Dt_IF_")

    # 添加固定参数
    optimizer.add_fixed_param(name="barCnt", val=50)
    optimizer.add_fixed_param(name="period", val="m5")
    optimizer.add_fixed_param(name="days", val=30)
    optimizer.add_fixed_param(name="code", val="CFFEX.IF.HOT")

    # 添加预设范围的参数，即参数只能在预设列表中选择，适用于标的代码、周期等参数
    # optimizer.add_listed_param(name="code", val_list=["CFFEX.IF.HOT","CFFEX.IC.HOT"])

    # 添加可变参数，适用于一般数值类参数
    optimizer.add_mutable_param(name="k1", start_val=0.1, end_val=1.0, step_val=0.1, ndigits=1)
    optimizer.add_mutable_param(name="k2", start_val=0.1, end_val=1.0, step_val=0.1, ndigits=1)

    # 配置回测环境，主要是将直接回测的一些参数通过这种方式动态传递，优化器中会在每个子进程动态构造回测引擎
    optimizer.config_backtest_env(deps_dir='../common/', cfgfile='configbt.yaml', storage_type="csv",
                                  storage_path="../storage/")
    # optimizer.config_backtest_time(start_time=201909100930, end_time=202009251500)
    optimizer.config_backtest_time(start_time=201909260930, end_time=202010121500)

    # 启动优化器
    optimizer.go(out_marker_file="strategies.json", out_summary_file="total_summary.csv")


def runStopLossOptimizer():
    # 新建一个优化器，并设置最大工作进程数为8
    optimizer = WtCtaGAOptimizer(worker_num=2)

    # 设置要使用的策略，只需要传入策略类型即可，同时设置策略ID的前缀，用于区分每个策略的实例
    optimizer.set_strategy(StraDualThrust, "Dt_IF_SL_")

    # 添加固定参数
    optimizer.add_fixed_param(name="barCnt", val=50)
    optimizer.add_fixed_param(name="period", val="m5")
    optimizer.add_fixed_param(name="days", val=30)
    optimizer.add_fixed_param(name="code", val="CFFEX.IF.HOT")
    optimizer.add_fixed_param(name="k1", val=0.4)
    optimizer.add_fixed_param(name="k2", val=0.4)

    # 添加可变参数，适用于一般数值类参数
    optimizer.add_mutable_param(name="slTicks", start_val=-10, end_val=0, step_val=0.2, ndigits=1)

    # 配置回测环境，主要是将直接回测的一些参数通过这种方式动态传递，优化器中会在每个子进程动态构造回测引擎
    optimizer.config_backtest_env(deps_dir='../common/', cfgfile='configbt.yaml', storage_type="csv",
                                  storage_path="../storage/")
    optimizer.config_backtest_time(start_time=201909100930, end_time=202010121500)

    # 启动优化器
    optimizer.go(out_marker_file="strategies.json", out_summary_file="total_summary_sl.csv")


def runStopProfOptimizer():
    # 新建一个优化器，并设置最大工作进程数为8
    optimizer = WtCtaGAOptimizer(worker_num=4)

    # 设置要使用的策略，只需要传入策略类型即可，同时设置策略ID的前缀，用于区分每个策略的实例
    optimizer.set_strategy(StraDualThrust, "Dt_IF_SP_")

    # 添加固定参数
    optimizer.add_fixed_param(name="barCnt", val=50)
    optimizer.add_fixed_param(name="period", val="m5")
    optimizer.add_fixed_param(name="days", val=30)
    optimizer.add_fixed_param(name="code", val="CFFEX.IF.HOT")
    optimizer.add_fixed_param(name="k1", val=0.4)
    optimizer.add_fixed_param(name="k2", val=0.4)

    # 添加可变参数，适用于一般数值类参数
    optimizer.add_mutable_param(name="spTicks", start_val=0, end_val=500, step_val=5, ndigits=0)

    # 配置回测环境，主要是将直接回测的一些参数通过这种方式动态传递，优化器中会在每个子进程动态构造回测引擎
    optimizer.config_backtest_env(deps_dir='../common/', cfgfile='configbt.yaml', storage_type="csv",
                                  storage_path="../storage/")
    optimizer.config_backtest_time(start_time=201909100930, end_time=202010121500)

    # 启动优化器
    optimizer.go(out_marker_file="strategies.json", out_summary_file="total_summary_sp.csv")


def runStopAllOptimizer():
    # 新建一个优化器，并设置最大工作进程数为8
    optimizer = WtCtaGAOptimizer(worker_num=4)

    # 设置要使用的策略，只需要传入策略类型即可，同时设置策略ID的前缀，用于区分每个策略的实例
    optimizer.set_strategy(StraDualThrust, "Dt_IF_ALL_")

    # 添加固定参数
    optimizer.add_fixed_param(name="barCnt", val=50)
    optimizer.add_fixed_param(name="period", val="m5")
    optimizer.add_fixed_param(name="days", val=30)
    optimizer.add_fixed_param(name="code", val="CFFEX.IF.HOT")
    optimizer.add_fixed_param(name="k1", val=0.4)
    optimizer.add_fixed_param(name="k2", val=0.4)

    # 添加可变参数，适用于一般数值类参数
    optimizer.add_mutable_param(name="slTicks", start_val=-30, end_val=-10, step_val=1, ndigits=1)
    optimizer.add_mutable_param(name="spTicks", start_val=150, end_val=230, step_val=2, ndigits=1)

    # 配置回测环境，主要是将直接回测的一些参数通过这种方式动态传递，优化器中会在每个子进程动态构造回测引擎
    optimizer.config_backtest_env(deps_dir='../common/', cfgfile='configbt.yaml', storage_type="csv",
                                  storage_path="../storage/")
    optimizer.config_backtest_time(start_time=201909100930, end_time=202010121500)

    # 启动优化器
    optimizer.go(out_marker_file="strategies.json", out_summary_file="total_summary_all.csv")


if __name__ == "__main__":
    runBaseOptimizer()
    kw = input('press any key to exit\n')