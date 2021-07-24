from wtpy.wrapper import WtDtWrapper
from wtpy.WtUtilDefs import singleton

@singleton
class WtDtEngine:

    def __init__(self):
        self.__wrapper__ = WtDtWrapper()  #api接口转换器

    def initialize(self, cfgfile:str = "dtcfg.json", logprofile:str = "logcfgdt.json"):
        '''
        数据引擎初始化\n
        @cfgfile    配置文件\n
        @logprofile 日志模块配置文件
        '''
        self.__wrapper__.initialize(cfgfile, logprofile)
    
    def run(self):
        '''
        运行数据引擎
        '''
        self.__wrapper__.run_datakit()