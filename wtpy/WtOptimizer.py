import multiprocessing
import math
import time
import threading
import json

from wtpy import WtBtEngine,EngineType

class ParamInfo:
    '''
    参数信息类
    '''
    def __init__(self, name:str, start_val, end_val, step_val, ndigits = 1):
        self.name = name    #参数名
        self.start_val = start_val  #起始值
        self.end_val = end_val      #结束值
        self.step_val = step_val    #变化步长
        self.ndigits = ndigits      #小数位

    def gen_array(self):
        values = list()
        curVal =self.start_val
        while curVal < self.end_val:
            values.append(round(curVal, self.ndigits))

            curVal += self.step_val
            if curVal >= self.end_val:
                curVal = self.end_val
                break
        values.append(round(curVal, self.ndigits))
        return values

class WtOptimizer:
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
        self.mutable_params[name] = ParamInfo(name, start_val, end_val, step_val, ndigits)
        return

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

    def config_backtest_env(self, deps_dir:str, cfgfile:str="configbt.json", storage_type:str="csv", storage_path:str="./storage/"):
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
        self.env_params["storage_path"] = storage_path

    def config_backtest_time(self, start_time:int, end_time:int):
        '''
        配置回测时间\n

        @start_time 开始时间，精确到分钟，格式如201909100930\n
        @end_time   结束时间，精确到分钟，格式如201909100930
        '''
        self.env_params["start_time"] = start_time
        self.env_params["end_time"] = end_time

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
        for i in range(total_groups):
            k = i
            thisGrp = self.fixed_params.copy()  #复制固定参数
            endix = ''
            for name in param_names:
                cnt = len(param_values[name])
                curVal = param_values[name][k%cnt]
                thisGrp[name] = curVal
                endix += name 
                endix += "_"
                endix += str(curVal)
                endix += "_"
                k = math.floor(k / cnt)

            endix = endix[:-1]
            straName = self.name_prefix + endix
            thisGrp["name"] = straName
            stra_names[straName] = thisGrp
            param_groups.append(thisGrp)
        
        # 将每一组参数和对应的策略ID落地到文件中，方便后续的分析
        f = open(markerfile, "w")
        f.write(json.dumps(obj=stra_names, sort_keys=True, indent=4))
        f.close()
        return param_groups

    def __execute_task__(self, params:dict):
        '''
        执行单个回测任务\n

        @params kv形式的参数
        '''
        name = params["name"]
        f = open("logcfg_tpl.json", "r")
        content =f.read()
        f.close()
        content = content.replace("$NAME$", name)
        engine = WtBtEngine(eType=EngineType.ET_CTA, logCfg=content, isFile=False)
        engine.init(self.env_params["deps_dir"], self.env_params["cfgfile"])
        engine.configBacktest(self.env_params["start_time"],self.env_params["end_time"])
        engine.configBTStorage(mode=self.env_params["storage_type"], path=self.env_params["storage_path"])
        engine.commitBTConfig()

        straInfo = self.strategy_type(**params)
        engine.set_cta_strategy(straInfo)

        engine.run_backtest()
        engine.release_backtest()

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

    def go(self, interval:float = 0.2, markerfile:str = "strategies.json"):
        '''
        启动优化器\n
        @interval   时间间隔，单位秒
        @markerfile 标记文件名，回测完成以后分析会用到
        '''
        self.tasks = self.__gen_tasks__(markerfile)
        self.running_worker = 0
        total_task = len(self.tasks)
        left_task = total_task
        while True:
            if left_task == 0:
                break

            if self.running_worker < self.worker_num:
                params = self.tasks[total_task-left_task]
                left_task -= 1
                print("剩余任务%d个" % (left_task))
                p = threading.Thread(target=self.__start_task__, args=(params,))
                p.start()
                self.running_worker += 1
                print("工作进程%d个" % (self.running_worker))
            else:
                time.sleep(interval)

        #最后，全部任务都已经启动完了，再等待所有工作进程结束
        while True:
            if self.running_worker == 0:
                break
            else:
                time.sleep(interval)

                
