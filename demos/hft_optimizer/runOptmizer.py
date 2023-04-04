from wtpy.apps import WtHftOptimizer
import sys
import os
os.chdir(sys.path[0])

def runBaseOptimizer():
    # 新建一个优化器，并设置最大工作进程数为8
    optimizer = WtHftOptimizer(worker_num=1)

    # 设置要使用的策略，只需要传入策略类型即可，同时设置策略ID的前缀，用于区分每个策略的实例
    optimizer.set_cpp_strategy(r"../Strategies/WtHftStraFact.dll","HftDemo","HFT_")
    # 添加固定参数
    optimizer.add_fixed_param(name="barCnt", val=50)
    optimizer.add_fixed_param(name="period", val="m5")
    optimizer.add_fixed_param(name="days", val=30)
    optimizer.add_fixed_param(name="code", val="CFFEX.IF.HOT")
    optimizer.add_fixed_param(name="k1", val=0.4)
    optimizer.add_fixed_param(name="k2", val=0.4)

    # 添加预设范围的参数，即参数只能在预设列表中选择，适用于标的代码、周期等参数
    # optimizer.add_listed_param(name="code", val_list=["CFFEX.IF.HOT","CFFEX.IC.HOT"])

    # 添加可变参数，适用于一般数值类参数
    optimizer.add_mutable_param(name="count", start_val=10, end_val=1000, step_val=10, ndigits = 1)
    optimizer.add_mutable_param(name="multiple", start_val=1, end_val=3, step_val=0.1, ndigits = 1)
    # optimizer.add_mutable_param(name="k2", start_val=0.1, end_val=1.0, step_val=0.1, ndigits = 1)

    # 配置回测环境，主要是将直接回测的一些参数通过这种方式动态传递，优化器中会在每个子进程动态构造回测引擎
    optimizer.config_backtest_env(deps_dir='../common/', cfgfile='configbt.yaml', storage_type="bin", storage_path="../storage/")
    optimizer.config_backtest_time(start_time=202104112100, end_time=202104201500)
    # optimizer.config_backtest_time(start_time=201909260930, end_time=202010121500)

    # 启动优化器
    optimizer.go(interval=0.2, out_marker_file="strategies.json",out_summary_file="total_summary.csv")

if __name__ == "__main__":
    runBaseOptimizer()
    kw = input('press any key to exit\n')