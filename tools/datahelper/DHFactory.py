from tools.datahelper.DHDefs import BaseDataHelper
from tools.datahelper.DHBaostock import DHBaostock
from tools.datahelper.DHTushare import DHTushare

class DHFactory:
    
    @staticmethod
    def createHelper(name:str) -> BaseDataHelper:
        name = name.lower()
        if name == "baostock":
            return DHBaostock()
        elif name == "tushare":
            return DHTushare()
