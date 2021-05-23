from wtpy.wrapper import WtBtWrapper
from wtpy.CtaContext import CtaContext
from wtpy.SelContext import SelContext
from wtpy.HftContext import HftContext
from wtpy.StrategyDefs import BaseCtaStrategy, BaseSelStrategy, BaseHftStrategy
from wtpy.ExtToolDefs import BaseIndexWriter
from wtpy.WtCoreDefs import EngineType

from .ProductMgr import ProductMgr, ProductInfo
from .SessionMgr import SessionMgr, SessionInfo
from .ContractMgr import ContractMgr, ContractInfo

from .CodeHelper import CodeHelper

import os
import json

def singleton(cls):
    instances = {}
    def getinstance(*args,**kwargs):
        if cls not in instances:
            instances[cls] = cls(*args,**kwargs)
        return instances[cls]
    return getinstance


@singleton
class WtBtEngine:

    def __init__(self, eType:EngineType = EngineType.ET_CTA, logCfg:str = "logcfgbt.json", isFile:bool = True, bDumpCfg:bool = False):
        self.__wrapper__ = WtBtWrapper()  #api接口转换器
        self.__context__ = None      #策略ctx映射表
        self.__config__ = dict()        #框架配置项
        self.__cfg_commited__ = False   #配置是否已提交

        self.__idx_writer__ = None  #指标输出模块

        self.__dump_config__ = bDumpCfg #是否保存最终配置

        if eType == eType.ET_CTA:
            self.__wrapper__.initialize_cta(self, logCfg, isFile)   #初始化CTA环境
        elif eType == eType.ET_HFT:
            self.__wrapper__.initialize_hft(self, logCfg, isFile)   #初始化HFT环境
        elif eType == eType.ET_SEL:
            self.__wrapper__.initialize_sel(self, logCfg, isFile)   #初始化SEL环境

    def __check_config__(self):
        '''
        检查设置项\n
        主要会补充一些默认设置项
        '''
        if "replayer" not in self.__config__:
            self.__config__["replayer"] = dict()
            self.__config__["replayer"]["basefiles"] = dict()

        if "replayer" not in self.__config__:
            self.__config__["replayer"] = dict()
            self.__config__["replayer"]["mode"] = "csv"
            self.__config__["replayer"]["path"] = "./storage/"

        if "env" not in self.__config__:
            self.__config__["env"] = dict()
            self.__config__["env"]["mocker"] = "cta"

    def set_writer(self, writer:BaseIndexWriter):
        '''
        设置指标输出模块
        '''
        self.__writer__ = writer

    def write_indicator(self, id, tag, time, data):
        '''
        写入指标数据
        '''
        if self.__writer__ is not None:
            self.__writer__.write_indicator(id, tag, time, data)

    def init(self, folder:str, cfgfile:str = "configbt.json", commfile:str="commodities.json", contractfile:str="contracts.json"):
        '''
        初始化\n
        @folder     基础数据文件目录，\\结尾\n
        @cfgfile    配置文件，json格式
        '''
        f = open(cfgfile, "r")
        content =f.read()
        self.__config__ = json.loads(content)
        f.close()

        self.__check_config__()

        self.__config__["replayer"]["basefiles"]["commodity"] = folder + commfile
        self.__config__["replayer"]["basefiles"]["contract"] = folder + contractfile
        self.__config__["replayer"]["basefiles"]["holiday"] = folder + "holidays.json"
        self.__config__["replayer"]["basefiles"]["session"] = folder + "sessions.json"
        self.__config__["replayer"]["basefiles"]["hot"] = folder + "hots.json"

        self.productMgr = ProductMgr()
        self.productMgr.load(folder + commfile)

        self.contractMgr = ContractMgr()
        self.contractMgr.load(folder + contractfile)

        self.sessionMgr = SessionMgr()
        self.sessionMgr.load(folder + "sessions.json")

    def configMocker(self, name:str):
        '''
        设置模拟器
        '''
        self.__config__["env"]["mocker"] = name

    def configBacktest(self, stime:int, etime:int):
        '''
        配置回测设置项\n
        @stime  开始时间\n
        @etime  结束时间
        '''
        self.__config__["replayer"]["stime"] = int(stime)
        self.__config__["replayer"]["etime"] = int(etime)

    def configBTStorage(self, mode:str, path:str = None, dbcfg:dict = None):
        '''
        配置数据存储\n
        @mode   存储模式，csv-表示从csv直接读取，一般回测使用，wtp-表示使用wt框架自带数据存储
        '''
        self.__config__["replayer"]["mode"] = mode
        if path is not None:
            self.__config__["replayer"]["path"] = path
        if dbcfg is not None:
            self.__config__["replayer"]["db"] = dbcfg

    def setExternalCtaStrategy(self, id:str, module:str, typeName:str, params:dict):
        '''
        添加外部的CTA策略
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
        添加外部的HFT策略
        '''
        if "hft" not in self.__config__:
            self.__config__["hft"] = dict()

        self.__config__["hft"]["module"] = module

        if "strategy" not in self.__config__["hft"]:
            self.__config__["hft"]["strategy"] = dict()

        self.__config__["hft"]["strategy"]["id"] = id
        self.__config__["hft"]["strategy"]["name"] = typeName
        self.__config__["hft"]["strategy"]["params"] = params


    def commitBTConfig(self):
        '''
        提交配置\n
        只有第一次调用会生效，不可重复调用\n
        如果执行run之前没有调用，run会自动调用该方法
        '''
        if self.__cfg_commited__:
            return

        cfgfile = json.dumps(self.__config__, indent=4, sort_keys=True)
        self.__wrapper__.config_backtest(cfgfile, False)
        self.__cfg_commited__ = True

        if self.__dump_config__:
            f = open("config_run.json", 'w')
            f.write(cfgfile)
            f.close()

    def getSessionByCode(self, code:str) -> SessionInfo:
        '''
        通过合约代码获取交易时间模板\n
        @code   合约代码，格式如SHFE.rb.HOT
        '''
        pid = CodeHelper.stdCodeToStdCommID(code)

        pInfo = self.productMgr.getProductInfo(pid)
        if pInfo is None:
            return None

        return self.sessionMgr.getSession(pInfo.session)

    def getSessionByName(self, sname:str) -> SessionInfo:
        '''
        通过模板名获取交易时间模板\n
        @sname  模板名
        '''
        return self.sessionMgr.getSession(sname)

    def getProductInfo(self, code:str) -> ProductInfo:
        '''
        获取品种信息\n
        @code   合约代码，格式如SHFE.rb.HOT
        '''
        return self.productMgr.getProductInfo(code)

    def getContractInfo(self, code:str) -> ContractInfo:
        '''
        获取品种信息\n
        @code   合约代码，格式如SHFE.rb.HOT
        '''
        return self.contractMgr.getContractInfo(code)

    def getAllCodes(self) -> list:
        '''
        获取全部合约代码
        '''
        return self.contractMgr.getTotalCodes()

    def set_cta_strategy(self, strategy:BaseCtaStrategy, slippage:int = 0):
        '''
        添加策略\n
        @strategy   策略对象
        '''
        ctxid = self.__wrapper__.init_cta_mocker(strategy.name(), slippage)
        self.__context__ = CtaContext(ctxid, strategy, self.__wrapper__, self)

    def set_hft_strategy(self, strategy:BaseHftStrategy):
        '''
        添加策略\n
        @strategy   策略对象
        '''
        ctxid = self.__wrapper__.init_hft_mocker(strategy.name())
        self.__context__ = HftContext(ctxid, strategy, self.__wrapper__, self)

    def set_sel_strategy(self, strategy:BaseSelStrategy, date:int=0, time:int=0, period:str="d", trdtpl:str="CHINA", session:str="TRADING", slippage:int = 0):
        '''
        添加策略\n
        @strategy   策略对象
        '''
        ctxid = self.__wrapper__.init_sel_mocker(strategy.name(), date, time, period, trdtpl, session, slippage)
        self.__context__ = SelContext(ctxid, strategy, self.__wrapper__, self)

    def get_context(self, id:int):
        return self.__context__

    def run_backtest(self):
        '''
        运行框架
        '''
        if not self.__cfg_commited__:   #如果配置没有提交，则自动提交一下
            self.commitBTConfig()

        self.__wrapper__.run_backtest()

    def release_backtest(self):
        '''
        释放框架
        '''
        self.__wrapper__.release_backtest()

    def dump_kline(self, code:str, period:str, filename:str):
        '''
        将K线导出到文件\n
        @code   合约代码，格式如SHFE.rb.HOT\n
        @period 周期，一般使用d/m1/m5
        '''
        self.__wrapper__.dump_kline(code, period, filename)

    def on_init(self):
        return

    def on_schedule(self, date:int, time:int, taskid:int = 0):
        return

    def on_session_begin(self, date:int):
        return

    def on_session_end(self, date:int):
        return
