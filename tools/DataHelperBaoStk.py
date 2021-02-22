from .DataHelperDefs import BaseDataHelper, DBHelper
import baostock as bs
import datetime
import json
import pandas as pd

def transCodes(codes:list) -> list:
    ret = list()
    for code in codes:
        items = code.split(".")
        exchg = items[0]
        if exchg == "SSE":
            ret.append("sh."+items[1])
        else:
            ret.append("sz."+items[1])

    return ret

class DataHelperBaoStk(BaseDataHelper):

    def __init__(self):
        BaseDataHelper.__init__(self)
        return

    def auth(self, **kwargs):
        if self.isAuthed:
            return

        bs.login()
        self.isAuthed = True

    def unauth(self):
        bs.logout()
        self.isAuthed = False

    def dmpCodeListToFile(self, filename:str, hasIndex:bool=True, hasStock:bool=True):
        raise Exception("Baostock has not code list api")

    def dmpAdjFactorsToFile(self, codes:list, filename:str):
        codes = transCodes(codes)
        stocks = {
            "SSE":{},
            "SZSE":{}
        }
        for code in codes:
            exchg = code[:2]
            if exchg == 'sh':
                exchg = 'SSE'
            else:
                exchg = 'SZSE'

            stocks[exchg][code[3:]] = list()
            rs = bs.query_adjust_factor(code=code, start_date="1990-01-01")
    
            while (rs.error_code == '0') & rs.next():
                items = rs.get_row_data()
                date = int(items[1].replace("-",""))
                factor = float(items[4])
                stocks[exchg][code[3:]].append({
                    "date": date,
                    "factor": factor
                })
        f = open(filename, 'w+')
        f.write(json.dumps(stocks, sort_keys=True, indent=4, ensure_ascii=False))
        f.close()

    def dmpBarsToFile(self, folder:str, codes:list, start_date=None, end_date=None, period:str="day"):
        pass

    def dmpCodeListToDB(self, dbHelper:DBHelper, hasIndex:bool=True, hasStock:bool=True):
        raise Exception("Baostock has not code list api")

    def dmpAdjFactorsToDB(self, codes:list, dbHelper:DBHelper):
        stocks = {
            "SSE":{},
            "SZSE":{}
        }
        for code in codes:
            exchg = code[:2]
            if exchg == 'sh':
                exchg = 'SSE'
            else:
                exchg = 'SZSE'

            stocks[exchg][code[3:]] = list()
            rs = bs.query_adjust_factor(code=code, start_date="1990-01-01")
    
            while (rs.error_code == '0') & rs.next():
                items = rs.get_row_data()
                date = int(items[1].replace("-",""))
                factor = float(items[4])
                stocks[exchg][code[3:]].append({
                    "date": date,
                    "factor": factor
                })
        dbHelper.writeFactors(stocks)

    def dmpBarsToDB(self, dbHelper:DBHelper, codes:list, start_date=None, end_date=None, period:str="day"):
        pass