from .DataHelperDefs import BaseDataHelper
from .DataHelperBaoStk import DataHelperBaoStk

class DatHlperFactory:
    
    @staticmethod
    def createDataHelper(name:str) -> BaseDataHelper:
        name = name.lower()
        if name == "baostock":
            return DataHelperBaoStk()
