from datetime import datetime

class DBHelper:

    def __init__(self):
        pass

    def initDB(self):
        '''
        初始化数据库，主要是建表等工作
        '''
        pass

    def writeBars(self, bars:list, period="day"):
        '''
        将K线存储到数据库中
        @bars   K线序列
        @period K线周期
        '''
        pass

    def writeFactors(self, factors:dict):
        '''
        将复权因子存储到数据库中
        @factors   复权因子
        '''
        pass


class BaseDataHelper:

    def __init__(self):
        self.isAuthed = False
        pass

    def __check__(self):
        if not self.isAuthed:
            raise Exception("This module has not authorized yet!")

    def auth(self, **kwargs):
        '''
        模块认证
        '''
        pass

    def dmpCodeListToFile(self, filename:str, hasIndex:bool=True, hasStock:bool=True):
        '''
        将代码列表导出到文件
        @filename   要输出的文件名，json格式
        @hasIndex   是否包含指数
        @hasStock   是否包含股票
        '''
        pass

    def dmpAdjFactorsToFile(self, codes:list, filename:str):
        '''
        将除权因子导出到文件
        @codes  股票列表，格式如["SSE.600000","SZSE.000001"]
        @filename   要输出的文件名，json格式
        '''
        pass

    def dmpBarsToFile(self, folder:str, codes:list, start_date:datetime=None, end_date:datetime=None, period="day"):
        '''
        将K线导出到指定的目录下的csv文件，文件名格式如SSE.600000_d.csv
        @folder 要输出的文件夹
        @codes  股票列表，格式如["SSE.600000","SZSE.000001"]
        @start_date 开始日期，datetime类型，传None则自动设置为1990-01-01
        @end_date   结束日期，datetime类型，传None则自动设置为当前日期
        @period K线周期，支持day、min1、min5
        '''
        pass

    def dmpAdjFactorsToDB(self, dbHelper:DBHelper, codes:list):
        '''
        将除权因子导出到数据库
        @codes  股票列表，格式如["SSE.600000","SZSE.000001"]
        @dbHelper   数据库辅助模块
        '''
        pass

    def dmpBarsToDB(self, dbHelper:DBHelper, codes:list, start_date:datetime=None, end_date:datetime=None, period:str="day"):
        '''
        将K线导出到数据库
        @dbHelper 数据库辅助模块
        @codes  股票列表，格式如["SSE.600000","SZSE.000001"]
        @start_date 开始日期，datetime类型，传None则自动设置为1990-01-01
        @end_date   结束日期，datetime类型，传None则自动设置为当前日期
        @period K线周期，支持day、min1、min5
        '''
        pass


    def dmpBars(self, codes:list, cb, start_date:datetime=None, end_date:datetime=None, period:str="day"):
        '''
        将K线导出到指定的目录下的csv文件，文件名格式如SSE.600000_d.csv
        @cb     回调函数，格式如cb(exchg:str, code:str, firstBar:POINTER(WTSBarStruct), count:int, period:str)
        @codes  股票列表，格式如["SSE.600000","SZSE.000001"]
        @start_date 开始日期，datetime类型，传None则自动设置为1990-01-01
        @end_date   结束日期，datetime类型，传None则自动设置为当前日期
        @period K线周期，支持day、min1、min5
        '''
        pass