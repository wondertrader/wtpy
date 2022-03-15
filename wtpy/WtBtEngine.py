from wtpy.wrapper import WtBtWrapper
from wtpy.CtaContext import CtaContext
from wtpy.SelContext import SelContext
from wtpy.HftContext import HftContext
from wtpy.StrategyDefs import BaseCtaStrategy, BaseSelStrategy, BaseHftStrategy
from wtpy.ExtToolDefs import BaseIndexWriter
from wtpy.WtCoreDefs import EngineType
from wtpy.WtUtilDefs import singleton
from wtpy.ExtModuleDefs import BaseExtDataLoader

from .ProductMgr import ProductMgr, ProductInfo
from .SessionMgr import SessionMgr, SessionInfo
from .ContractMgr import ContractMgr, ContractInfo

from .CodeHelper import CodeHelper

import json
import yaml


@singleton
class WtBtEngine:

    def __init__(self, eType:EngineType = EngineType.ET_CTA, logCfg:str = "logcfgbt.yaml", isFile:bool = True, bDumpCfg:bool = False, outDir:str = "./outputs_bt"):
        '''
        构造函数
        @eType  引擎类型
        @logCfg 日志模块配置文件，也可以直接是配置内容字符串
        @isFile 是否文件，如果是文件，则将logCfg当做文件路径处理，如果不是文件，则直接当成json格式的字符串进行解析
        @bDumpCfg   回测的实际配置文件是否落地
        @outDir 回测数据输出目录
        '''
        self.is_backtest = True

        self.__wrapper__ = WtBtWrapper(self)  #api接口转换器
        self.__context__ = None      #策略ctx映射表
        self.__config__ = dict()        #框架配置项
        self.__cfg_commited__ = False   #配置是否已提交

        self.__idx_writer__ = None  #指标输出模块

        self.__dump_config__ = bDumpCfg #是否保存最终配置
        self.__is_cfg_yaml__ = True

        self.__ext_data_loader__:BaseExtDataLoader = None   #扩展历史数据加载器

        if eType == eType.ET_CTA:
            self.__wrapper__.initialize_cta(logCfg, isFile, outDir)   #初始化CTA环境
        elif eType == eType.ET_HFT:
            self.__wrapper__.initialize_hft(logCfg, isFile, outDir)   #初始化HFT环境
        elif eType == eType.ET_SEL:
            self.__wrapper__.initialize_sel(logCfg, isFile, outDir)   #初始化SEL环境

    def __check_config__(self):
        '''
        检查设置项
        主要会补充一些默认设置项
        '''
        if "replayer" not in self.__config__:
            self.__config__["replayer"] = dict()
            self.__config__["replayer"]["basefiles"] = dict()

            self.__config__["replayer"]["mode"] = "csv"
            self.__config__["replayer"]["store"] = {
                "path":"./storage/"
            }

        if "env" not in self.__config__:
            self.__config__["env"] = dict()
            self.__config__["env"]["mocker"] = "cta"

    def set_writer(self, writer:BaseIndexWriter):
        '''
        设置指标输出模块
        '''
        self.__idx_writer__ = writer

    def write_indicator(self, id:str, tag:str, time:int, data:dict):
        '''
        写入指标数据
        @id     指标id
        @tag    标签，主要用于区分指标对应的周期，如m5/d
        @time   时间，如yyyymmddHHMM
        @data   指标值
        '''
        if self.__idx_writer__ is not None:
            self.__idx_writer__.write_indicator(id, tag, time, data)

    def init(self, folder:str, 
        cfgfile:str = "configbt.yaml", 
        commfile:str="commodities.json", 
        contractfile:str="contracts.json",
        sessionfile:str="sessions.json",
        holidayfile:str="holidays.json",
        hotfile:str="hots.json",
        secondfile:str="seconds.json"):
        '''
        初始化
        @folder     基础数据文件目录，\\结尾
        @cfgfile    配置文件，json/yaml格式
        @commfile   品种定义文件，json/yaml格式
        @contractfile   合约定义文件，json/yaml格式
        '''
        f = open(cfgfile, "r")
        content =f.read()
        f.close()

        if cfgfile.lower().endswith(".json"):
            self.__config__ = json.loads(content)
            self.__is_cfg_yaml__ = False
        else:
            self.__config__ = yaml.full_load(content)
            self.__is_cfg_yaml__ = True

        self.__check_config__()

        self.__config__["replayer"]["basefiles"]["contract"] = folder + contractfile
        self.__config__["replayer"]["basefiles"]["session"] = folder + sessionfile
        if commfile is not None:
            self.__config__["replayer"]["basefiles"]["commodity"] = folder + commfile
        if holidayfile is not None:
            self.__config__["replayer"]["basefiles"]["holiday"] = folder + holidayfile
        if hotfile is not None:
            self.__config__["replayer"]["basefiles"]["hot"] = folder + hotfile
        if secondfile is not None:
            self.__config__["replayer"]["basefiles"]["second"] = folder + secondfile

        self.productMgr = ProductMgr()
        if commfile is not None:
            self.productMgr.load(folder + commfile)

        self.contractMgr = ContractMgr(self.productMgr)
        self.contractMgr.load(folder + contractfile)

        self.sessionMgr = SessionMgr()
        self.sessionMgr.load(folder + sessionfile)

    def configMocker(self, name:str):
        '''
        设置模拟器
        '''
        self.__config__["env"]["mocker"] = name

    def configBacktest(self, stime:int, etime:int):
        '''
        配置回测设置项
        @stime  开始时间
        @etime  结束时间
        '''
        self.__config__["replayer"]["stime"] = int(stime)
        self.__config__["replayer"]["etime"] = int(etime)

    def configBTStorage(self, mode:str, path:str = None, storage:dict = None):
        '''
        配置数据存储
        @mode   存储模式，csv-表示从csv直接读取，一般回测使用，wtp-表示使用wt框架自带数据存储
        '''
        self.__config__["replayer"]["mode"] = mode
        if path is not None:
            self.__config__["replayer"]["store"] = {
                "path":path
            }

        if storage is not None:
            self.__config__["replayer"]["store"] = storage

    def setExternalCtaStrategy(self, id:str, module:str, typeName:str, params:dict):
        '''
        添加C++的CTA策略
        @id 策略ID
        @module     策略模块文件名，包含后缀，如：WzCtaFact.dll
        @typeName   模块内的策略类名
        @params     策略参数
        '''
        if "cta" not in self.__config__:
            self.__config__["cta"] = dict()

        self.__config__["cta"]["module"] = module

        if "strategy" not in self.__config__["cta"]:
            self.__config__["cta"]["strategy"] = dict()

        self.__config__["cta"]["strategy"]["id"] = id
        self.__config__["cta"]["strategy"]["name"] = typeName
        self.__config__["cta"]["strategy"]["params"] = params
        

    def setExternalHftStrategy(self, id:str, module:str, typeName:str, params:dict):
        '''
        添加C++的HFT策略
        @id 策略ID
        @module     策略模块文件名，包含后缀，如：WzHftFact.dll
        @typeName   模块内的策略类名
        @params     策略参数
        '''
        if "hft" not in self.__config__:
            self.__config__["hft"] = dict()

        self.__config__["hft"]["module"] = module

        if "strategy" not in self.__config__["hft"]:
            self.__config__["hft"]["strategy"] = dict()

        self.__config__["hft"]["strategy"]["id"] = id
        self.__config__["hft"]["strategy"]["name"] = typeName
        self.__config__["hft"]["strategy"]["params"] = params

    def set_extended_data_loader(self, loader:BaseExtDataLoader, bAutoTrans:bool = True):
        '''
        设置扩展数据加载器
        @loader     数据加载器模块
        @bAutoTrans 是否自动转储，如果是的话底层就转成dsb文件
        '''
        self.__ext_data_loader__ = loader
        self.__wrapper__.register_extended_data_loader(bAutoTrans)

    def get_extended_data_loader(self) -> BaseExtDataLoader:
        '''
        获取扩展的数据加载器
        '''
        return self.__ext_data_loader__

    def commitBTConfig(self):
        '''
        提交配置
        只有第一次调用会生效，不可重复调用
        如果执行run之前没有调用，run会自动调用该方法
        '''
        if self.__cfg_commited__:
            return

        cfgfile = json.dumps(self.__config__, indent=4, sort_keys=True)
        self.__wrapper__.config_backtest(cfgfile, False)
        self.__cfg_commited__ = True

        if self.__dump_config__:
            if self.__is_cfg_yaml__:
                f = open("config_run.yaml", 'w')
                f.write(yaml.dump_all(self.__config__, indent=4, allow_unicode=True))
                f.close()
            else:
                f = open("config_run.json", 'w')
                f.write(cfgfile)
                f.close()

    def getSessionByCode(self, code:str) -> SessionInfo:
        '''
        通过合约代码获取交易时间模板
        @code   合约代码，格式如SHFE.rb.HOT
        '''
        pid = CodeHelper.stdCodeToStdCommID(code)

        pInfo = self.productMgr.getProductInfo(pid)
        if pInfo is None:
            return None

        return self.sessionMgr.getSession(pInfo.session)

    def getSessionByName(self, sname:str) -> SessionInfo:
        '''
        通过模板名获取交易时间模板
        @sname  模板名
        '''
        return self.sessionMgr.getSession(sname)

    def getProductInfo(self, code:str) -> ProductInfo:
        '''
        获取品种信息
        @code   合约代码，格式如SHFE.rb.HOT
        '''
        return self.productMgr.getProductInfo(code)

    def getContractInfo(self, code:str) -> ContractInfo:
        '''
        获取品种信息
        @code   合约代码，格式如SHFE.rb.HOT
        '''
        return self.contractMgr.getContractInfo(code)

    def getAllCodes(self) -> list:
        '''
        获取全部合约代码
        '''
        return self.contractMgr.getTotalCodes()

    def set_time_range(self, beginTime:int, endTime:int):
        '''
        设置回测时间
        一般用于一个进程中多次回测的时候启动下一轮回测之前重设之间范围
        @beginTime  开始时间，格式如yyyymmddHHMM
        @endTime    结束时间，格式如yyyymmddHHMM
        '''
        self.__wrapper__.set_time_range(beginTime, endTime)

    def set_cta_strategy(self, strategy:BaseCtaStrategy, slippage:int = 0, hook:bool = False, persistData:bool = True):
        '''
        添加CTA策略
        @strategy   策略对象
        @slippage   滑点大小
        @hook       是否安装钩子，主要用于单步控制重算
        @persistData    回测生成的数据是否落地，默认为True
        '''
        ctxid = self.__wrapper__.init_cta_mocker(strategy.name(), slippage, hook, persistData)
        self.__context__ = CtaContext(ctxid, strategy, self.__wrapper__, self)

    def set_hft_strategy(self, strategy:BaseHftStrategy, hook:bool = False):
        '''
        添加HFT策略
        @strategy   策略对象
        @hook       是否安装钩子，主要用于单步控制重算
        '''
        ctxid = self.__wrapper__.init_hft_mocker(strategy.name(), hook)
        self.__context__ = HftContext(ctxid, strategy, self.__wrapper__, self)

    def set_sel_strategy(self, strategy:BaseSelStrategy, date:int=0, time:int=0, period:str="d", trdtpl:str="CHINA", session:str="TRADING", slippage:int = 0):
        '''
        添加SEL策略
        @strategy   策略对象
        '''
        ctxid = self.__wrapper__.init_sel_mocker(strategy.name(), date, time, period, trdtpl, session, slippage)
        self.__context__ = SelContext(ctxid, strategy, self.__wrapper__, self)

    def get_context(self, id:int):
        return self.__context__

    def run_backtest(self, bAsync:bool = False, bNeedDump:bool = True):
        '''
        运行框架

        @bAsync 是否异步运行，默认为false。如果不启动异步模式，则强化学习的训练环境也不能生效，即使策略下了钩子
        '''
        if not self.__cfg_commited__:   #如果配置没有提交，则自动提交一下
            self.commitBTConfig()

        self.__wrapper__.run_backtest(bNeedDump = bNeedDump, bAsync = bAsync)

    def cta_step(self, remark:str = "") -> bool:
        '''
        CTA策略单步执行

        @remark 单步备注信息，没有实际作用，主要用于外部调用区分步骤
        '''
        return self.__wrapper__.cta_step(self.__context__.id)

    def hft_step(self):
        '''
        HFT策略单步执行
        '''
        self.__wrapper__.hft_step(self.__context__.id)

    def stop_backtest(self):
        '''
        手动停止回测
        '''
        self.__wrapper__.stop_backtest()

    def release_backtest(self):
        '''
        释放框架
        '''
        self.__wrapper__.release_backtest()

    def on_init(self):
        return

    def on_schedule(self, date:int, time:int, taskid:int = 0):
        return

    def on_session_begin(self, date:int):
        return

    def on_session_end(self, date:int):
        return

    def on_backtest_end(self):
        if self.__context__ is None:
            return

        self.__context__.on_backtest_end()

    def clear_cache(self):
        '''
        清除缓存的数据，即加已经加载到内存中的数据全部清除
        '''
        self.__wrapper__.clear_cache()
