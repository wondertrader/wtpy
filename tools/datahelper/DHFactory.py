from tools.datahelper.DHDefs import BaseDataHelper
from tools.datahelper.DHBaostock import DHBaostock
from tools.datahelper.DHTushare import DHTushare
from tools.datahelper.DHRqData import DHRqData

class DHFactory:
    
    @staticmethod
    def createHelper(name:str) -> BaseDataHelper:
        '''
        创建数据辅助模块\n
        @name   模块名称，目前支持的有tushare、baostock、rqdata
        '''
        name = name.lower()
        if name == "baostock":
            return DHBaostock()
        elif name == "tushare":
            return DHTushare()
        elif name == "rqdata":
            return DHRqData()
