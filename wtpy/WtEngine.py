from wtpy.wrapper import WtWrapper
from wtpy.CtaContext import CtaContext
from wtpy.SelContext import SelContext
from wtpy.HftContext import HftContext
from wtpy.StrategyDefs import BaseCtaStrategy, BaseSelStrategy, BaseHftStrategy
from wtpy.ExtToolDefs import BaseIndexWriter, BaseDataReporter
from wtpy.WtCoreDefs import EngineType
from wtpy.ExtModuleDefs import BaseExtParser, BaseExtExecuter, BaseExtDataLoader
from wtpy.WtUtilDefs import singleton

from .ProductMgr import ProductMgr, ProductInfo
from .SessionMgr import SessionMgr, SessionInfo
from .ContractMgr import ContractMgr, ContractInfo
from .CodeHelper import CodeHelper

import json
import yaml
import chardet
import os

@singleton
class WtEngine:
    '''
    实盘交易引擎
    '''

    def __init__(self, eType:EngineType, logCfg:str = "logcfg.yaml", genDir:str = "generated", bDumpCfg:bool = False):
        '''
        WtEngine构造函数
        @eType  引擎类型: EngineType.ET_CTA、EngineType.ET_HFT、EngineType.ET_SEL
        @logCfg 日志配置文件
        @genDir 数据输出目录
        @bDumpCfg   是否保存最终配置文件
        '''
        self.is_backtest = False

        self.__wrapper__:WtWrapper = WtWrapper(self)  #api接口转换器
        self.__cta_ctxs__ = dict()      #CTA策略ctx映射表
        self.__sel_ctxs__ = dict()      #SEL策略ctx映射表
        self.__hft_ctxs__ = dict()      #HFT策略ctx映射表
        self.__config__ = dict()        #框架配置项
        self.__cfg_commited__ = False   #配置是否已提交

        self.__writer__:BaseIndexWriter = None          #指标输出模块
        self.__reporter__:BaseDataReporter = None        #数据提交模块

        self.__ext_data_loader__:BaseExtDataLoader = None   #扩展历史数据加载器

        self.__ext_parsers__ = dict()   #外接的行情接入模块
        self.__ext_executers__ = dict() #外接的执行器

        self.__dump_config__ = bDumpCfg #是否保存最终配置
        self.__is_cfg_yaml__ = True

        self.__engine_type:EngineType = eType
        if eType == EngineType.ET_CTA:
            self.__wrapper__.initialize_cta(logCfg=logCfg, isFile=True, genDir=genDir)
        elif eType == EngineType.ET_HFT:
            self.__wrapper__.initialize_hft(logCfg=logCfg, isFile=True, genDir=genDir)
        elif eType == EngineType.ET_SEL:
            self.__wrapper__.initialize_sel(logCfg=logCfg, isFile=True, genDir=genDir)

    def __check_config__(self):
        '''
        检查设置项
        主要会补充一些默认设置项
        '''
        if "basefiles" not in self.__config__:
            self.__config__["basefiles"] = dict()

        if "env" not in self.__config__:
            self.__config__["env"] = dict()
            self.__config__["env"]["name"] = "cta"
            self.__config__["env"]["mode"] = "product"
            self.__config__["env"]["product"] = {
                "session":"TRADING"
            }
    
    def get_engine_type(self) -> EngineType:
        return self.__engine_type

    def set_extended_data_loader(self, loader:BaseExtDataLoader):
        self.__ext_data_loader__ = loader
        self.__wrapper__.register_extended_data_loader()

    def get_extended_data_loader(self) -> BaseExtDataLoader:
        return self.__ext_data_loader__

    def add_exetended_parser(self, parser:BaseExtParser):
        id = parser.id()
        if id not in self.__ext_parsers__:
            if self.__wrapper__.create_extended_parser(id):
                self.__ext_parsers__[id] = parser

    def add_exetended_executer(self, executer:BaseExtExecuter):
        id = executer.id()
        if id not in self.__ext_executers__:
            if self.__wrapper__.create_extended_executer(id):
                self.__ext_executers__[id] = executer

    def get_extended_parser(self, id:str)->BaseExtParser:
        if id not in self.__ext_parsers__:
            return None
        return self.__ext_parsers__[id]

    def get_extended_executer(self, id:str)->BaseExtExecuter:
        if id.decode() not in self.__ext_executers__:
            return None
        return self.__ext_executers__[id.decode()]

    def push_quote_from_extended_parser(self, id:str, newTick, uProcFlag:int):
        '''
        向底层推送tick数据

        @id parserid
        @newTick    POINTER(WTSTickStruct)
        @uProcFlag  预处理标记，0-不处理，1-切片，2-累加
        '''
        self.__wrapper__.push_quote_from_exetended_parser(id, newTick, uProcFlag)

    def set_writer(self, writer:BaseIndexWriter):
        '''
        设置指标输出模块
        '''
        self.__writer__ = writer

    def write_indicator(self, id:str, tag:str, time:int, data:dict):
        '''
        写入指标数据
        '''
        if self.__writer__ is not None:
            self.__writer__.write_indicator(id, tag, time, data)

    def set_data_reporter(self, reporter:BaseDataReporter):
        '''
        设置数据报告器
        '''
        self.__reporter__ = reporter

    def init(self, folder:str, 
        cfgfile:str = "config.yaml", 
        contractfile:str = None,
        sessionfile:str = None,
        commfile:str = None, 
        holidayfile:str = None,
        hotfile:str = None,
        secondfile:str = None):
        '''
        初始化
        @folder     基础数据文件目录，\\结尾
        @cfgfile    配置文件，json格式
        '''
        f = open(cfgfile, "rb")
        content = f.read()
        f.close()
        encoding = chardet.detect(content[:500])["encoding"]
        content = content.decode(encoding)

        if cfgfile.lower().endswith(".json"):
            self.__config__ = json.loads(content)
            self.__is_cfg_yaml__ = False
        else:
            self.__config__ = yaml.full_load(content)
            self.__is_cfg_yaml__ = True

        self.__check_config__()

        if contractfile is not None:        
            self.__config__["basefiles"]["contract"] = os.path.join(folder, contractfile)
        
        if sessionfile is not None:
            self.__config__["basefiles"]["session"] = os.path.join(folder, sessionfile)

        if commfile is not None:
            self.__config__["basefiles"]["commodity"] = os.path.join(folder, commfile)

        if holidayfile is not None:
            self.__config__["basefiles"]["holiday"] = os.path.join(folder, holidayfile)

        if hotfile is not None:
            self.__config__["basefiles"]["hot"] = os.path.join(folder, hotfile)

        if secondfile is not None:
            self.__config__["basefiles"]["second"] = os.path.join(folder, secondfile)

        self.productMgr = ProductMgr()
        if "commodity" in self.__config__["basefiles"] and self.__config__["basefiles"]["commodity"] is not None:
            if type(self.__config__["basefiles"]["commodity"]) == str:
                self.productMgr.load(self.__config__["basefiles"]["commodity"])
            elif type(self.__config__["basefiles"]["commodity"]) == list:
                for fname in self.__config__["basefiles"]["commodity"]:
                    self.productMgr.load(fname)

        self.contractMgr = ContractMgr(self.productMgr)
        if type(self.__config__["basefiles"]["contract"]) == str:
            self.contractMgr.load(self.__config__["basefiles"]["contract"])
        elif type(self.__config__["basefiles"]["contract"]) == list:
            for fname in self.__config__["basefiles"]["contract"]:
                self.contractMgr.load(fname)

        self.sessionMgr = SessionMgr()
        self.sessionMgr.load(self.__config__["basefiles"]["session"])

    def configEngine(self, name:str, mode:str = "product"):
        '''
        设置引擎和运行模式
        '''
        self.__config__["env"]["name"] = name
        self.__config__["env"]["mode"] = mode

    def addExternalCtaStrategy(self, id:str, params:dict):
        '''
        添加外部的CTA策略
        '''
        if "strategies" not in self.__config__:
            self.__config__["strategies"] = dict()

        if "cta" not in self.__config__["strategies"]:
            self.__config__["strategies"]["cta"] = list()

        params["id"] = id
        self.__config__["strategies"]["cta"].append(params)

    def addExternalHftStrategy(self, id:str, params:dict):
        '''
        添加外部的HFT策略
        '''
        if "strategies" not in self.__config__:
            self.__config__["strategies"] = dict()

        if "hft" not in self.__config__["strategies"]:
            self.__config__["strategies"]["hft"] = list()

        params["id"] = id
        self.__config__["strategies"]["hft"].append(params)

    def configStorage(self, path:str, module:str=""):
        '''
        配置数据存储
        @mode   存储模式，csv-表示从csv直接读取，一般回测使用，wtp-表示使用wt框架自带数据存储
        '''
        self.__config__["data"]["store"]["module"] = module
        self.__config__["data"]["store"]["path"] = path

    def registerCustomRule(self, ruleTag:str, filename:str):
        '''
        注册自定义连续合约规则
        @ruleTag    规则标签，如ruleTag为THIS，对应的连续合约代码为CFFEX.IF.THIS
        @filename   规则定义文件名，和hots.json格式一样
        '''
        if "rules" not in self.__config__["basefiles"]:
            self.__config__["basefiles"]["rules"] = dict()

        self.__config__["basefiles"]["rules"][ruleTag] = filename

    def commitConfig(self):
        '''
        提交配置
        只有第一次调用会生效，不可重复调用
        如果执行run之前没有调用，run会自动调用该方法
        '''
        if self.__cfg_commited__:
            return

        cfgfile = json.dumps(self.__config__, indent=4, sort_keys=True)
        self.__wrapper__.config(cfgfile, False)
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

    def regCtaStraFactories(self, factFolder:str):
        '''
        向底层模块注册CTA工厂模块目录
        !!!CTA策略只会被CTA引擎加载!!!
        @factFolder 工厂模块所在的目录
        '''
        return self.__wrapper__.reg_cta_factories(factFolder)

    def regHftStraFactories(self, factFolder:str):
        '''
        向底层模块注册HFT工厂模块目录
        !!!HFT策略只会被HFT引擎加载!!!
        @factFolder 工厂模块所在的目录
        '''
        return self.__wrapper__.reg_hft_factories(factFolder)

    def regExecuterFactories(self, factFolder:str):
        '''
        向底层模块注册执行器模块目录
        !!!执行器只在CTA引擎有效!!!
        @factFolder 工厂模块所在的目录
        '''
        return self.__wrapper__.reg_exe_factories(factFolder)

    def addExecuter(self, id:str, trader:str, policies:dict, scale:int = 1):
        if "executers" not in self.__config__:
            self.__config__["executers"] = list()

        exeItem = {
            "active":True,
            "id": id,
            "scale": scale,
            "policy": policies,
            "trader":trader
        }

        self.__config__["executers"].append(exeItem)

    def addTrader(self, id:str, params:dict):
        if "traders" not in self.__config__:
            self.__config__["traders"] = list()

        tItem = params
        tItem["active"] = True
        tItem["id"] = id

        self.__config__["traders"].append(tItem)

    def getSessionByCode(self, stdCode:str) -> SessionInfo:
        '''
        通过合约代码获取交易时间模板
        @stdCode   合约代码，格式如SHFE.rb.HOT
        '''
        pid = CodeHelper.stdCodeToStdCommID(stdCode)
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

    def getProductInfo(self, stdCode:str) -> ProductInfo:
        '''
        获取品种信息
        @stdCode   合约代码，格式如SHFE.rb.HOT
        '''
        return self.productMgr.getProductInfo(stdCode)

    def getContractInfo(self, stdCode:str) -> ContractInfo:
        '''
        获取品种信息
        @stdCode   合约代码，格式如SHFE.rb.HOT
        '''
        return self.contractMgr.getContractInfo(stdCode)

    def getAllCodes(self) -> list:
        '''
        获取全部合约代码
        '''
        return self.contractMgr.getTotalCodes()
    
    def getCodesByProduct(self, stdPID:str) -> list:
        '''
        根据品种id获取对应合约代码
        @stdPID 品种代码, 格式如SHFE.rb
        '''
        return self.contractMgr.getCodesByProduct(stdPID)
    
    def getCodesByUnderlying(self, underlying:str) -> list:
        '''
        根据underlying获取对应合约代码
        @underlying 品种代码, 格式如SHFE.rb2305
        '''
        return self.contractMgr.getCodesByUnderlying(underlying)

    def getRawStdCode(self, stdCode:str):
        '''
        根据连续合约代码获取原始合约代码
        '''
        return self.__wrapper__.get_raw_stdcode(stdCode)

    def add_cta_strategy(self, strategy:BaseCtaStrategy, slippage:int = 0):
        '''
        添加CTA策略
        @strategy   策略对象
        '''
        id = self.__wrapper__.create_cta_context(strategy.name(), slippage)
        self.__cta_ctxs__[id] = CtaContext(id, strategy, self.__wrapper__, self)

    def add_hft_strategy(self, strategy:BaseHftStrategy, trader:str, agent:bool = True, slippage:int = 0):
        '''
        添加HFT策略
        @strategy   策略对象
        '''
        id = self.__wrapper__.create_hft_context(strategy.name(), trader, agent, slippage)
        self.__hft_ctxs__[id] = HftContext(id, strategy, self.__wrapper__, self)

    def add_sel_strategy(self, strategy:BaseSelStrategy, date:int, time:int, period:str, slippage:int = 0):
        id = self.__wrapper__.create_sel_context(strategy.name(), date, time, period, slippage)
        self.__sel_ctxs__[id] = SelContext(id, strategy, self.__wrapper__, self)

    def get_context(self, id:int):
        '''
        根据ID获取策略上下文
        @id     上下文id，一般添加策略的时候会自动生成一个唯一的上下文id
        '''
        if self.__engine_type == EngineType.ET_CTA:
            if id not in self.__cta_ctxs__:
                return None

            return self.__cta_ctxs__[id]
        elif self.__engine_type == EngineType.ET_HFT:
            if id not in self.__hft_ctxs__:
                return None

            return self.__hft_ctxs__[id]
        elif self.__engine_type == EngineType.ET_SEL:
            if id not in self.__sel_ctxs__:
                return None

            return self.__sel_ctxs__[id]

    def run(self, bAsync:bool = True):
        '''
        运行框架
        '''
        if not self.__cfg_commited__:   #如果配置没有提交，则自动提交一下
            self.commitConfig()

        self.__wrapper__.run(bAsync)

    def release(self):
        '''
        释放框架
        '''
        self.__wrapper__.release()

    def on_init(self):
        if self.__reporter__ is not None:
            self.__reporter__.report_init_data()
        return

    def on_schedule(self, date:int, time:int, taskid:int = 0):
        # print("engine scheduled")
        if self.__reporter__ is not None:
            self.__reporter__.report_rt_data()

    def on_session_begin(self, date:int):
        # print("session begin")
        return

    def on_session_end(self, date:int):
        if self.__reporter__ is not None:
            self.__reporter__.report_settle_data()
        return
