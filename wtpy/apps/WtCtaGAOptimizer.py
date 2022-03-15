# -*- encoding: utf-8 -*-

from json import encoder
import multiprocessing
import time
import json
import yaml

import os
import math
import numpy as np
import pandas as pd
from pandas import DataFrame as df
from itertools import product
from random import random, choice, seed
from typing import Tuple

from deap import creator, base, tools, algorithms

from wtpy import WtBtEngine, EngineType
from wtpy.apps import WtBtAnalyst


def fmtNAN(val, defVal=0):
    if math.isnan(val):
        return defVal

    return val


class ParamInfo:
    '''
    参数信息类
    '''

    def __init__(self, name: str, start_val=None, end_val=None, step_val=None, ndigits=1, val_list: list = None):
        self.name = name  # 参数名
        self.start_val = start_val  # 起始值
        self.end_val = end_val  # 结束值
        self.step_val = step_val  # 变化步长
        self.ndigits = ndigits  # 小数位
        self.val_list = val_list  # 指定参数

    def gen_array(self):
        if self.val_list is not None:
            return self.val_list

        values = list()
        curVal = round(self.start_val, self.ndigits)
        while curVal < self.end_val:
            values.append(curVal)

            curVal += self.step_val
            curVal = round(curVal, self.ndigits)
            if curVal >= self.end_val:
                curVal = self.end_val
                break
        values.append(round(curVal, self.ndigits))
        return values


creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)


class WtCtaGAOptimizer:
    '''
    参数优化器\n
    主要用于做策略参数优化的
    '''

    def __init__(self, worker_num: int = 2, MU: int = 80, population_size: int = 100, ngen_size: int = 20,
                 cx_prb: float = 0.9, mut_prb: float = 0.1):
        '''
        构造函数\n

        @worker_num 工作进程个数，默认为2，可以根据CPU核心数设置，由于计算回测值是从文件里读取，因此进程过多可能会出现冲突\n
        @MU        每一代选择的个体数\n
        @population_size 种群数\n
        @ngen_size 进化代数\n
        @cx_prb    交叉概率\n
        @mut_prb   变异概率
        '''
        self.worker_num = worker_num
        self.running_worker = 0
        self.mutable_params = dict()
        self.fixed_params = dict()
        self.env_params = dict()

        # 遗传算法优化参数设置
        self.optimizing_target = "胜率"
        self.optimizing_target_func = None  # 适应度函数，原则上要求为非负

        self.population_size = population_size  # 种群数
        self.ngen_size = ngen_size  # 进化代数，即优化迭代次数，根据population_size大小设定
        self.MU = MU  # 每一代选择的个体数，可以取个体数的0.8倍
        self.lambda_ = self.population_size  # 下一代产生的个体数
        self.cx_prb = cx_prb  # 建议取0.4~0.99之间
        self.mut_prb = mut_prb  # 建议取0.0001~0.1之间

        self.cpp_stra_module = None

        self.cache_dict = multiprocessing.Manager().dict()  # 缓存中间结果

    def add_mutable_param(self, name: str, start_val, end_val, step_val, ndigits=1):
        '''
        添加可变参数\n

        @name       参数名\n
        @start_val  起始值\n
        @end_val    结束值\n
        @step_val   步长\n
        @ndigits    小数位
        '''
        self.mutable_params[name] = ParamInfo(name=name, start_val=start_val, end_val=end_val, step_val=step_val,
                                              ndigits=ndigits)

    def add_listed_param(self, name: str, val_list: list):
        '''
        添加限定范围的可变参数\n

        @name       参数名\n
        @val_list   参数值列表
        '''
        self.mutable_params[name] = ParamInfo(name=name, val_list=val_list)

    def add_fixed_param(self, name: str, val):
        '''
        添加固定参数\n

        @name       参数名\n
        @val        值\n
        '''
        self.fixed_params[name] = val

    def generate_settings(self):
        ''' 生成优化参数组合 '''
        # 参数名列表
        name_list = self.mutable_params.keys()

        param_list = []
        for name in name_list:
            paramInfo = self.mutable_params[name]
            values = paramInfo.gen_array()
            param_list.append(values)

        # 使用迭代工具产生参数对组合
        products = list(product(*param_list))

        # 把参数对组合打包到字典列表里
        settings = []
        [settings.append(dict(zip(name_list, p))) for p in products]
        return settings

    def set_optimizing_target(self, target: str):
        ''' 设置优化目标名称，可从summary中已有数据中选取优化目标 '''
        self.optimizing_target = target

    def set_optimizing_func(self, calculator, target_name: str = None):
        ''' 根据summary数据自定义优化目标值 '''
        self.optimizing_target_func = calculator

        if target_name is None:
            target_name = "适应值"

        self.set_optimizing_target(target_name)

    def mututate_individual(self, individual, indpb):
        """
        变异函数
        :param individual: 个体，实际为策略参数
        :param indpb: 变异概率
        :return: 变异后的个体
        """
        size = len(individual)
        param_list = self.generate_settings()
        settings = [list(item.items()) for item in param_list]

        for i in range(size):
            if random() < indpb:
                individual[i] = settings[i]
        return individual,

    def evaluate_func(self, start_time, end_time, cache_dict: dict, params):
        """
        适应度函数
        :return:
        """
        # 参数传递可能出现异常
        # 比如[(k1, 0.1), (k2, 0.1)]可能在编码出新的参数组时变为[[(k1, 0.1), (k2, 0.2)], (k2, 0.3)]的情况
        tmp_params = dict()

        temp = []
        [[temp.append(jj) for jj in ii] if isinstance(ii, list) else temp.append(ii) for ii in params]
        names = [itm[0] for itm in temp]
        names1 = list({}.fromkeys(names).keys())
        if len(names1) < len(names):
            indexes = [names.index(ii) for ii in names1]
            temp = [temp[i] for i in indexes]

        if len(temp) < 1:
            print(f"Empty parameters: {params}")
            return 0,

        for cell in temp:
            tmp_params[cell[0]] = cell[1]

        # strategy name
        strName = [self.name_prefix[:-1]]
        [strName.extend([key, tmp_params[key]]) for key in tmp_params.keys()]
        strName.extend([start_time, end_time])
        strName = [str(item) for item in strName]
        strName = "_".join(strName)

        is_yaml = True
        fname = "logcfg_tpl.yaml"
        if not os.path.exists(fname):
            is_yaml = True
            fname = "logcfg_tpl.json"

        f = open(fname, "r")
        content = f.read()
        f.close()
        content = content.replace("$NAME$", strName)
        if is_yaml:
            content = json.dumps(yaml.full_load(content))

        engine = WtBtEngine(eType=EngineType.ET_CTA, logCfg=content, isFile=False)
        engine.init(self.env_params["deps_dir"], self.env_params["cfgfile"])
        engine.configBacktest(int(start_time), int(end_time))
        engine.configBTStorage(mode=self.env_params["storage_type"], path=self.env_params["storage_path"],
                               storage=self.env_params["storage"])

        time_range = (int(start_time), int(end_time))

        tmp_params["name"] = strName

        tmp_params.update(self.fixed_params)

        if self.cpp_stra_module is not None:
            tmp_params.pop("name")
            engine.setExternalCtaStrategy(strName, self.cpp_stra_module, self.cpp_stra_type, tmp_params)
        else:
            straInfo = self.strategy_type(**tmp_params)
            engine.set_cta_strategy(straInfo)

        engine.commitBTConfig()
        engine.run_backtest()
        engine.release_backtest()

        summary = self.__ayalyze_result__(strName, time_range, tmp_params)

        if self.optimizing_target_func:
            result = self.optimizing_target_func(summary)  # tuple类型
        else:
            result = summary[self.optimizing_target],

        # if strName not in cache_dict.keys():  # 缓存结果
        #     tmp_params.update({self.optimizing_target: result[0]})
        #     cache_dict[strName] = tmp_params

        tmp_params.update({self.optimizing_target: result[0]})
        cache_dict[strName] = tmp_params

        return result

    def set_strategy(self, typeName: type, name_prefix: str):
        '''
        设置策略\n

        @typeName       策略类名\n
        @name_prefix    命名前缀，用于自动命名用，一般为格式为"前缀_参数1名_参数1值_参数2名_参数2值"
        '''
        self.strategy_type = typeName
        self.name_prefix = name_prefix
        return

    def set_cpp_strategy(self, module: str, type_name: type, name_prefix: str):
        '''
        设置CPP策略\n

        @module         模块文件\n
        @typeName       策略类名\n
        @name_prefix    命名前缀，用于自动命名用，一般为格式为"前缀_参数1名_参数1值_参数2名_参数2值"
        '''
        self.cpp_stra_module = module
        self.cpp_stra_type = type_name
        self.name_prefix = name_prefix
        return

    def config_backtest_env(self, deps_dir: str, cfgfile: str = "configbt.yaml", storage_type: str = "csv",
                            storage_path: str = None, storage: dict = None):
        '''
        配置回测环境\n

        @deps_dir   依赖文件目录\n
        @cfgfile    配置文件名\n
        @storage_type   存储类型，csv/bin等\n
        @storage_path   存储路径
        '''
        self.env_params["deps_dir"] = deps_dir
        self.env_params["cfgfile"] = cfgfile
        self.env_params["storage_type"] = storage_type
        self.env_params["storage"] = storage
        self.env_params["storage_path"] = storage_path

    def config_backtest_time(self, start_time: int, end_time: int):
        '''
        配置回测时间，可多次调用配置多个回测时间区间\n

        @start_time 开始时间，精确到分钟，格式如201909100930\n
        @end_time   结束时间，精确到分钟，格式如201909100930
        '''
        if "time_ranges" not in self.env_params:
            self.env_params["time_ranges"] = []

        self.env_params["time_ranges"].append([start_time, end_time])

    def gen_params(self, markerfile: str = "strategies.json"):
        '''
        生成回测任务
        '''
        # name_list = self.mutable_params.keys()

        param_list = self.generate_settings()

        stra_names = dict()
        time_range = self.env_params["time_ranges"]

        start_time = time_range[0][0]
        end_time = time_range[0][1]
        thisGrp = self.fixed_params.copy()  # 复制固定参数
        for setting in param_list:
            straName = self.name_prefix
            temp_setting = []
            [temp_setting.extend([key, setting[key]]) for key in setting.keys()]
            temp_setting.extend([start_time, end_time])
            straName += "_".join([str(i) for i in temp_setting])
            thisGrp["name"] = straName
            thisGrp["start_time"] = start_time
            thisGrp["end_time"] = end_time
            stra_names[straName] = thisGrp

        param_group = {"start_time": start_time, "end_time": end_time}

        # 将每一组参数和对应的策略ID落地到文件中，方便后续的分析
        f = open(markerfile, "w")
        f.write(json.dumps(obj=stra_names, sort_keys=True, indent=4))
        f.close()
        return param_group

    def __ayalyze_result__(self, strName: str, time_range: tuple, params: dict):
        folder = "./outputs_bt/%s/" % (strName)

        try:
            df_closes = pd.read_csv(folder + "closes.csv", engine="python")
            df_funds = pd.read_csv(folder + "funds.csv", engine="python")
        except Exception as e:  # 如果读取csv文件出现异常，则按文本格式读取
            df_closes = read_closes(folder + "closes.csv")
            df_funds = read_funds(folder + "funds.csv")

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

        summary = params.copy()
        summary["开始时间"] = time_range[0]
        summary["结束时间"] = time_range[1]
        summary["总交易次数"] = totaltimes
        summary["盈利次数"] = wintimes
        summary["亏损次数"] = losetimes
        summary["毛盈利"] = float(winamout)
        summary["毛亏损"] = float(loseamount)
        summary["交易净盈亏"] = float(trdnetprofit)
        summary["胜率"] = winrate * 100
        summary["单次平均盈亏"] = avgprof
        summary["单次盈利均值"] = avgprof_win
        summary["单次亏损均值"] = avgprof_lose
        summary["单次盈亏均值比"] = winloseratio
        summary["最大连续盈利次数"] = max_consecutive_wins
        summary["最大连续亏损次数"] = max_consecutive_loses
        summary["平均盈利周期"] = avg_bars_in_winner
        summary["平均亏损周期"] = avg_bars_in_loser
        summary["平均账户收益率"] = accnetprofit / totaltimes if totaltimes > 0 else 0

        f = open(folder + "summary.json", mode="w")
        f.write(json.dumps(obj=summary, indent=4))
        f.close()

        return summary

    def run_ga_optimizer(self, params: dict = None):
        """ 执行GA优化 """
        # 遗传算法参数空间
        buffer = self.generate_settings()
        settings = [list(itm.items()) for itm in buffer]

        def generate_parameter():
            return choice(settings)

        pool = multiprocessing.Pool(self.worker_num)  # 多线程设置
        toolbox = base.Toolbox()
        toolbox.register("individual", tools.initIterate, creator.Individual, generate_parameter)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)

        toolbox.register("evaluate", self.evaluate_func, params["start_time"], params["end_time"], self.cache_dict)
        toolbox.register("mate", tools.cxTwoPoint)
        toolbox.register("mutate", self.mututate_individual, indpb=0.05)
        toolbox.register("select", tools.selNSGA2)
        toolbox.register("map", pool.map)  # 多线程优化，可能会报错
        # seed(12555888)  # 固定随机数种子

        pop = toolbox.population(self.population_size)
        # hof = tools.ParetoFront()  # 非占优最优集
        hof = tools.HallOfFame(1)
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        # stats.register("avg", np.mean, axis=0)
        # stats.register("std", np.std, axis=0)
        # stats.register("min", np.min, axis=0)
        stats.register("max", np.max, axis=0)

        # Run ga optimization
        print("*" * 50)
        print(f"开始执行遗传算法优化...")
        print(f"参数优化空间: {len(settings)}")
        print(f"每代族群总数: {self.population_size}")
        print(f"优良个体筛选数: {self.MU}")
        print(f"迭代次数: {self.ngen_size}")
        print(f"交叉几率: {self.cx_prb:.2%}")
        print(f"变异几率: {self.mut_prb:.2%}")

        begin = time.perf_counter()
        _, logbook = algorithms.eaMuPlusLambda(pop, toolbox, self.MU, self.lambda_, self.cx_prb, self.mut_prb,
                                               self.ngen_size, stats, verbose=False, halloffame=hof)

        end = time.perf_counter()
        print(f"算法优化完成，耗时: {end - begin: .2f} 秒")
        print("*" * 50)

        # # 处理结果
        # optimizing_value = [item['max'][0] for item in logbook]
        # optimizing_params = [{item[0]: item[1]} for item in hof[0]]
        # optimizing_params.append({f"{self.optimizing_target}": max(optimizing_value)})
        return

    def go(self, out_marker_file: str = "strategies.json",
           out_summary_file: str = "total_summary.csv"):
        '''
        启动优化器\n
        @markerfile 标记文件名，回测完成以后分析会用到
        '''
        params = self.gen_params(out_marker_file)
        self.run_ga_optimizer(params)

        # 获取所有的值
        results = list(self.cache_dict.values())
        header = list(results[0].keys())
        data = [list(itm.values()) for itm in results]
        df_results = pd.DataFrame(data, columns=header)
        df_results = df_results[["name", self.optimizing_target]]

        # 开始汇总回测结果
        f = open(out_marker_file, "r")
        content = f.read()
        f.close()

        obj_stras = json.loads(content)
        total_summary = list()
        for straName in obj_stras:
            filename = "./outputs_bt/%s/summary.json" % (straName)
            if not os.path.exists(filename):
                # print("%s不存在，请检查数据" % (filename))
                continue

            f = open(filename, "r")
            content = f.read()
            f.close()
            obj_summary = json.loads(content)
            total_summary.append(obj_summary)

        df_summary = df(total_summary)

        # 汇总结果
        df_summary = pd.merge(df_summary, df_results, how="inner", on="name")
        df_summary.sort_values(by=self.optimizing_target, ascending=False, inplace=True)
        df_summary.reset_index(inplace=True, drop=True)

        # df_summary = df_summary.drop(labels=["name"], axis='columns')
        df_summary.to_csv(out_summary_file, encoding='utf-8-sig')

    def analyze(self, out_marker_file: str = "strategies.json", out_summary_file: str = "total_summary.csv"):
        # 获取所有的值
        results = list(self.cache_dict.values())
        header = list(results[0].keys())
        data = [list(itm.values()) for itm in results]
        df_results = pd.DataFrame(data, columns=header)
        df_results = df_results[["name", self.optimizing_target]]

        # 开始汇总回测结果
        f = open(out_marker_file, "r")
        content = f.read()
        f.close()

        total_summary = list()
        obj_stras = json.loads(content)
        for straName in obj_stras:
            params = obj_stras[straName]
            filename = "./outputs_bt/%s/summary.json" % (straName)
            if not os.path.exists(filename):
                # print("%s不存在，请检查数据" % (filename))
                continue

            time_range = (params["start_time"], params["end_time"])
            self.__ayalyze_result__(straName, time_range, params)

            f = open(filename, "r")
            content = f.read()
            f.close()
            obj_summary = json.loads(content)
            total_summary.append(obj_summary)

        df_summary = df(total_summary)

        # 汇总结果
        df_summary = pd.merge(df_summary, df_results, how="inner", on="name")
        df_summary.sort_values(by=self.optimizing_target, ascending=False, inplace=True)
        df_summary.reset_index(inplace=True, drop=True)

        df_summary = df_summary.drop(labels=["name"], axis='columns')
        df_summary.to_csv(out_summary_file)

    def analyzer(self, out_marker_file: str = "strategies.json", init_capital=500000, rf=0.02, annual_trading_days=240):
        for straname in json.load(open(out_marker_file, mode='r')).keys():
            try:
                analyst = WtBtAnalyst()
                analyst.add_strategy(straname, folder="./outputs_bt/%s/" % straname, init_capital=init_capital, rf=rf,
                                     annual_trading_days=annual_trading_days)
                analyst.run()
            except:
                pass


# 按文本格式读取回测closes文件
def read_closes(file):
    lines = open(file, 'r').readlines()
    header = lines[0]
    data = lines[1:]
    header = header.strip('\n').split(',')
    data = [line.strip('\n').split(',') for line in data]

    df = pd.DataFrame(data, columns=header)
    df.iloc[:, [2, 4, 6, 7, 8, 9, 13, 14]] = df.iloc[:, [2, 4, 6, 7, 8, 9, 13, 14]].astype(np.int64)
    df.iloc[:, [3, 5, 10]] = df.iloc[:, [3, 5, 10]].astype(np.float64)
    return df


# 按文本格式读取funds文件
def read_funds(file):
    lines = open(file, 'r').readlines()
    header = lines[0]
    data = lines[1:]
    header = header.strip('\n').split(',')
    data = [line.strip('\n').split(',') for line in data]

    df = pd.DataFrame(data, columns=header)
    df.iloc[:, 0] = df.iloc[:, 0].astype(np.int64)
    df.iloc[:, 1:] = df.iloc[:, 1:].astype(np.float64)
    return df
