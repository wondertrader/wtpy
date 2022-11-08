'''
Descripttion: HFT参数寻优模块
version: 
Author: HeJ
Date: 2022-06-22 14:03:33
LastEditors: Wesley
LastEditTime: 2022-06-22 14:03:33
'''
import multiprocessing
import json
import yaml

import os
import math
import numpy as np
import pandas as pd
from pandas import DataFrame as df
import datetime
from wtpy import WtBtEngine,EngineType
from wtpy.apps import WtBtAnalyst

def fmtNAN(val, defVal = 0):
    if math.isnan(val):
        return defVal

    return val

class ParamInfo:
    '''
    参数信息类
    '''
    def __init__(self, name:str, start_val = None, end_val = None, step_val = None, ndigits = 1, val_list:list = None):
        self.name = name    #参数名
        self.start_val = start_val  #起始值
        self.end_val = end_val      #结束值
        self.step_val = step_val    #变化步长
        self.ndigits = ndigits      #小数位
        self.val_list = val_list    #指定参数

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

class WtHftOptimizer:
    '''
    参数优化器\n
    主要用于做策略参数优化的
    '''
    def __init__(self, worker_num:int = 8):
        '''
        构造函数\n

        @worker_num 工作进程个数，默认为8，可以根据CPU核心数设置
        '''
        self.worker_num = worker_num
        self.running_worker = 0
        self.mutable_params = dict()
        self.fixed_params = dict()
        self.env_params = dict()

        self.cpp_stra_module = None
        return

    def add_mutable_param(self, name:str, start_val, end_val, step_val, ndigits = 1):
        '''
        添加可变参数\n

        @name       参数名\n
        @start_val  起始值\n
        @end_val    结束值\n
        @step_val   步长\n
        @ndigits    小数位
        '''
        self.mutable_params[name] = ParamInfo(name=name, start_val=start_val, end_val=end_val, step_val=step_val, ndigits=ndigits)

    def add_listed_param(self, name:str, val_list:list):
        '''
        添加限定范围的可变参数\n

        @name       参数名\n
        @val_list   参数值列表
        '''
        self.mutable_params[name] = ParamInfo(name=name, val_list=val_list)

    def add_fixed_param(self, name:str, val):
        '''
        添加固定参数\n

        @name       参数名\n
        @val        值\n
        '''
        self.fixed_params[name] = val
        return
    
    def set_strategy(self, typeName:type, name_prefix:str):
        '''
        设置策略\n

        @typeName       策略类名\n
        @name_prefix    命名前缀，用于自动命名用，一般为格式为"前缀_参数1名_参数1值_参数2名_参数2值"
        '''
        self.strategy_type = typeName
        self.name_prefix = name_prefix
        return

    def set_cpp_strategy(self, module:str, type_name:type, name_prefix:str):
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

    def config_backtest_env(self, deps_dir:str, cfgfile:str="configbt.yaml", storage_type:str="csv", storage_path:str = None, storage:dict = None):
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

    def config_backtest_time(self, start_time:int, end_time:int):
        '''
        配置回测时间，可多次调用配置多个回测时间区间\n

        @start_time 开始时间，精确到分钟，格式如201909100930\n
        @end_time   结束时间，精确到分钟，格式如201909100930
        '''
        if "time_ranges" not in self.env_params:
            self.env_params["time_ranges"] = []

        self.env_params["time_ranges"].append([start_time,end_time])

    def __gen_tasks__(self, markerfile:str = "strategies.json"):
        '''
        生成回测任务
        '''
        param_names = self.mutable_params.keys()
        param_values = dict()
        # 先生成各个参数的变量数组
        # 并计算总的参数有多少组
        total_groups = 1
        for name in param_names:
            paramInfo = self.mutable_params[name]
            values = paramInfo.gen_array()
            param_values[name] = values
            total_groups *= len(values)

        #再生成最终每一组的参数dict
        param_groups = list()
        stra_names = dict()
        time_ranges = self.env_params["time_ranges"]
        for time_range in time_ranges:
            start_time = time_range[0]
            end_time = time_range[1]
            for i in range(total_groups):
                k = i
                thisGrp = self.fixed_params.copy()  #复制固定参数
                endix = ''
                for name in param_names:
                    cnt = len(param_values[name])
                    curVal = param_values[name][k%cnt]
                    tname = type(curVal)
                    if tname.__name__ == "list":
                        val_str  = ''
                        for item in curVal:
                            val_str += str(item)
                            val_str += "_"

                        val_str = val_str[:-1]
                        thisGrp[name] = curVal
                        endix += name 
                        endix += "_"
                        endix += val_str
                        endix += "_"
                    else:
                        thisGrp[name] = curVal
                        endix += name 
                        endix += "_"
                        endix += str(curVal)
                        endix += "_"
                    k = math.floor(k / cnt)

                endix = endix[:-1]
                straName = self.name_prefix + endix
                straName += "_%d_%d" % (start_time, end_time)
                thisGrp["name"] = straName
                thisGrp["start_time"] = start_time
                thisGrp["end_time"] = end_time
                stra_names[straName] = thisGrp
                param_groups.append(thisGrp)
        
        # 将每一组参数和对应的策略ID落地到文件中，方便后续的分析
        f = open(markerfile, "w")
        f.write(json.dumps(obj=stra_names, sort_keys=True, indent=4))
        f.close()
        return param_groups

    def __ayalyze_result__(self, strName:str, time_range:tuple, params:dict):
        folder = "./outputs_bt/%s/" % (strName)
        df_closes = pd.read_csv(folder + "closes.csv",encoding="gbk")
        df_funds = pd.read_csv(folder + "funds.csv")
        
        df_closes["opentime"] = df_closes["opentime"].astype("str").apply(lambda dt: datetime.datetime.strptime(dt,"%Y%m%d%H%M%S%f"))
        df_closes["closetime"] = df_closes["closetime"].astype("str").apply(lambda dt: datetime.datetime.strptime(dt,"%Y%m%d%H%M%S%f"))
        df_closes["holdperiod"] = (df_closes["closetime"] - df_closes["opentime"]).astype('timedelta64[s]')
        
        df_wins = df_closes[df_closes["profit"]>0]
        df_loses = df_closes[df_closes["profit"]<=0]

        total_win_holdperiod = df_wins["holdperiod"].sum()
        total_lose_holdperiod = df_loses["holdperiod"].sum()

        total_fee = df_funds.iloc[-1]["fee"]

        totaltimes = len(df_closes) # 总交易次数
        wintimes = len(df_wins)     # 盈利次数
        losetimes = len(df_loses)   # 亏损次数
        winamout = df_wins["profit"].sum()      #毛盈利
        loseamount = df_loses["profit"].sum()   #毛亏损
        trdnetprofit = winamout + loseamount    #交易净盈亏
        accnetprofit = trdnetprofit - total_fee #账户净盈亏
        winrate = wintimes / totaltimes if totaltimes>0 else 0      # 胜率
        avgprof = trdnetprofit/totaltimes if totaltimes>0 else 0    # 单次平均盈亏
        avgprof_win = winamout/wintimes if wintimes>0 else 0        # 单次盈利均值
        avgprof_lose = loseamount/losetimes if losetimes>0 else 0   # 单次亏损均值
        winloseratio = abs(avgprof_win/avgprof_lose) if avgprof_lose!=0 else "N/A"   # 单次盈亏均值比
            
        max_consecutive_wins = 0    # 最大连续盈利次数
        max_consecutive_loses = 0   # 最大连续亏损次数
        
        avg_time_in_winner = total_win_holdperiod/wintimes if wintimes>0 else "N/A"
        avg_time_in_loser = total_lose_holdperiod/losetimes if losetimes>0 else "N/A"

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

        total_fee = df_funds["fee"].sum()
        yearRet = round(df_funds["closeprofit"].mean() * np.float(244),3) 
        vol = (df_funds["closeprofit"].std() * np.sqrt(244)).round(3)
        sr = yearRet / vol
        sr = sr.round(3)
        df_funds["dd"] = (df_funds['dynbalance'].rolling(len(df_funds)+1,min_periods=1).max()- df_funds['dynbalance'])
        maxdd = df_funds["dd"].max()
        maxdd_t = df_funds[df_funds['dd']==maxdd]["date"].values[0]
        maxdd = maxdd + 0.1
        cr = yearRet/ maxdd
        cr = np.round(cr,3)
        
        summary = params.copy()
        summary["开始时间"] = time_range[0]
        summary["结束时间"] = time_range[1]
        summary["总交易次数"] = totaltimes
        summary["手续费"] = total_fee
        summary["盈利次数"] = wintimes
        summary["亏损次数"] = losetimes
        summary["毛盈利"] = float(winamout)
        summary["毛亏损"] = float(loseamount)
        summary["交易净盈亏"] = float(trdnetprofit)
        summary["胜率"] = winrate*100
        summary["单次平均盈亏"] = avgprof
        summary["单次盈利均值"] = avgprof_win
        summary["单次亏损均值"] = avgprof_lose
        summary["单次盈亏均值比"] = winloseratio
        summary["最大连续盈利次数"] = max_consecutive_wins
        summary["最大连续亏损次数"] = max_consecutive_loses
        summary["平均盈利周期(s)"] = avg_time_in_winner
        summary["平均亏损周期(s)"] = avg_time_in_loser
        summary["平均账户收益率"] = accnetprofit/totaltimes
        summary["年均收入"] = yearRet
        summary["波动率"] = vol
        summary["夏普"] = sr
        summary["最大回撤"] = maxdd
        summary["最大回撤发生时间"] = str(maxdd_t)
        summary["卡玛"] = cr

        f = open(folder+"summary.json", mode="w")
        f.write(json.dumps(obj=summary, indent=4))
        f.close()

        return

    def __execute_task__(self, params:dict):
        '''
        执行单个回测任务\n

        @params kv形式的参数
        '''
        name = params["name"]
        
        is_yaml = True
        fname = "logcfg_tpl.yaml"
        if not os.path.exists(fname):
            is_yaml = True
            fname = "logcfg_tpl.json"

        f = open(fname, "r")
        content =f.read()
        f.close()
        content = content.replace("$NAME$", name)
        if is_yaml:
            content = json.dumps(yaml.full_load(content))
        engine = WtBtEngine(eType=EngineType.ET_HFT, logCfg=content, isFile=False)
        engine.init(self.env_params["deps_dir"], self.env_params["cfgfile"])
        engine.configBacktest(params["start_time"], params["end_time"])
        engine.configBTStorage(mode=self.env_params["storage_type"], path=self.env_params["storage_path"], storage=self.env_params["storage"])

        time_range = (params["start_time"], params["end_time"])

        # 去掉多余的参数
        params.pop("start_time")
        params.pop("end_time")
        
        if self.cpp_stra_module is not None:
            params.pop("name")
            engine.setExternalHftStrategy(name, self.cpp_stra_module, self.cpp_stra_type, params)
        else:
            straInfo = self.strategy_type(**params)
            engine.set_hft_strategy(straInfo)

        engine.commitBTConfig()
        engine.run_backtest()
        engine.release_backtest()

        self.__ayalyze_result__(name, time_range, params)

    def __start_task__(self, params:dict):
        '''
        启动单个回测任务\n
        这里用线程启动子进程的目的是为了可以控制总的工作进程个数\n
        可以在线程中join等待子进程结束，再更新running_worker变量\n
        如果在__execute_task__中修改running_worker，因为在不同进程中，数据并不同步\n

        @params kv形式的参数
        '''
        p = multiprocessing.Process(target=self.__execute_task__, args=(params,))
        p.start()
        p.join()
        self.running_worker -= 1
        print("工作进程%d个" % (self.running_worker))
        
    def __start_task_group__(self, params:list):
        '''
        启动多个回测任务，来回测一组参数，这里共用一个engine，因此可以避免多次io
        @params 参数组
        '''
        is_yaml = True
        fname = "logcfg_tpl.yaml"
        if not os.path.exists(fname):
            is_yaml = True
            fname = "logcfg_tpl.json"

        f = open(fname, "r")
        content =f.read()
        f.close()
        engine = WtBtEngine(eType=EngineType.ET_CTA, logCfg=content, isFile=False)
        # 配置类型的参数相对固定
        engine.init(self.env_params["deps_dir"], self.env_params["cfgfile"])
        engine.configBTStorage(mode=self.env_params["storage_type"], path=self.env_params["storage_path"], storage=self.env_params["storage"])
        # 遍历参数组
        for param in params:
            name = param["name"]
            param_content = content.replace("$NAME$", name)
            if is_yaml:
                param_content = json.dumps(yaml.full_load(param_content))
            
            engine.configBacktest(param["start_time"], param["end_time"])
            time_range = (param["start_time"], param["end_time"])
            # 去掉多余的参数
            param.pop("start_time")
            param.pop("end_time")
            if self.cpp_stra_module is not None:
                param.pop("name")
                engine.setExternalCtaStrategy(name, self.cpp_stra_module, self.cpp_stra_type, param)
            else:
                straInfo = self.strategy_type(**param)
                engine.set_cta_strategy(straInfo)
            engine.commitBTConfig()
            engine.run_backtest()
            self.__ayalyze_result__(name, time_range, param)
        engine.release_backtest()

    def go(self, interval:float = 0.2, out_marker_file:str = "strategies.json", out_summary_file:str = "total_summary.csv"):
        '''
        启动优化器\n
        @interval   时间间隔，单位秒
        @markerfile 标记文件名，回测完成以后分析会用到
        '''
        self.tasks = self.__gen_tasks__(out_marker_file)
        pool = []
        total_size = len(self.tasks)
        one_size = round(total_size / self.worker_num)
        work_id = 0
        for i in range(0,total_size,one_size):
            work_id += 1
            params = self.tasks[i:i+one_size]
            p = multiprocessing.Process(target=self.__start_task_group__, args=(params,))
            p.start()
            print("工人%d开始工作" % (work_id))
            pool.append(p)
        
        work_id = 0
        for task in pool:
            work_id += 1
            task.join()
            print("工人%d结束工作" % (work_id))

        #开始汇总回测结果
        f = open(out_marker_file, "r")
        content = f.read()
        f.close()

        obj_stras = json.loads(content)
        total_summary = list()
        for straName in obj_stras:
            filename = "./outputs_bt/%s/summary.json" % (straName)
            if not os.path.exists(filename):
                print("%s不存在，请检查数据" % (filename))
                continue
                
            f = open(filename, "r")
            content = f.read()
            f.close()
            obj_summary = json.loads(content)
            total_summary.append(obj_summary)

        df_summary = df(total_summary)
        # df_summary = df_summary.drop(labels=["name"], axis='columns')
        df_summary.to_csv(out_summary_file, encoding='utf-8-sig')

    def analyze(self, out_marker_file:str = "strategies.json", out_summary_file:str = "total_summary.csv"):
        #开始汇总回测结果
        f = open(out_marker_file, "r")
        content = f.read()
        f.close()

        total_summary = list()
        obj_stras = json.loads(content)
        for straName in obj_stras:
            params = obj_stras[straName]
            filename = "./outputs_bt/%s/summary.json" % (straName)
            if not os.path.exists(filename):
                print("%s不存在，请检查数据" % (filename))
                continue
                
            time_range = (params["start_time"],params["end_time"])
            self.__ayalyze_result__(straName, time_range, params)
            
            f = open(filename, "r")
            content = f.read()
            f.close()
            obj_summary = json.loads(content)
            total_summary.append(obj_summary)

        df_summary = df(total_summary)
        df_summary = df_summary.drop(labels=["name"], axis='columns')
        df_summary.to_csv(out_summary_file)

    def analyzer(self, out_marker_file:str = "strategies.json", init_capital=500000, rf=0.02, annual_trading_days=240):
        for straname in json.load(open(out_marker_file, mode='r')).keys():
            try:
                analyst = WtBtAnalyst()
                analyst.add_strategy(straname, folder="./outputs_bt/%s/"%straname, init_capital=init_capital, rf=rf, annual_trading_days=annual_trading_days)
                analyst.run()
            except:
                pass

                
