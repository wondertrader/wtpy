from tools.datahelper.DHDefs import BaseDataHelper, DBHelper
import tushare as ts
from datetime import datetime
import json
import os

def transCode(stdCode:str) -> str:
    items = stdCode.split(".")
    exchg = items[0]
    if exchg == "SSE":
        exchg = "SH"
    elif exchg == "SZSE":
        exchg = "SZ"
    
    if exchg in ['SH','SZ']:
        rawCode = ''
        if len(items) > 2:
            rawCode = items[2]
        else:
            rawCode = items[1]
    else:
        # 期货合约代码，格式为DCE.a.2018
        rawCode = ''
        if exchg == "CZCE":
            rawCode = items[1] + items[2][1:]
        else:
            rawCode = ''.join(items[1:])
    return rawCode.upper() + "." + exchg

    

class DHTushare(BaseDataHelper):

    def __init__(self):
        BaseDataHelper.__init__(self)
        self.api = None
        return

    def auth(self, **kwargs):
        if self.isAuthed:
            return

        self.api = ts.pro_api(**kwargs)
        self.isAuthed = True

    def unauth(self):
        self.isAuthed = False

    def dmpCodeListToFile(self, filename:str, hasIndex:bool=True, hasStock:bool=True):
        stocks = {
            "SSE":{},
            "SZSE":{}
        }
        
        #个股列表
        if hasStock:
            df_stocks = self.api.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
            for idx, row in df_stocks.iterrows():
                code = row["ts_code"]
                rawcode = row["symbol"]
                sInfo = dict()
                pid = "STK"
                if code[-2:] == "SH":
                    sInfo["exchg"] = "SSE"
                else:
                    sInfo["exchg"] = "SZSE"
                code = rawcode #code[-2:] + rawcode
                sInfo["code"] = code
                sInfo["name"] = row["name"]
                sInfo["product"] = pid            
                
                stocks[sInfo["exchg"]][code] = sInfo

        if hasIndex:
            #上证指数列表
            df_stocks = self.api.index_basic(market='SSE')
            for idx, row in df_stocks.iterrows():
                code = row["ts_code"]
                rawcode = code[:6]
                if rawcode[0] != '0':
                    continue
                
                sInfo = dict()
                sInfo["exchg"] = "SSE"
                code = rawcode #"SH" + rawcode
                sInfo["code"] = code
                sInfo["name"] = row["name"]
                sInfo["product"] = "IDX"            
                
                stocks[sInfo["exchg"]][code] = sInfo

            #深证指数列表
            df_stocks = self.api.index_basic(market='SZSE')
            for idx, row in df_stocks.iterrows():
                code = row["ts_code"]
                rawcode = code[:6]
                if rawcode[:3] != '399':
                    continue
                
                sInfo = dict()
                sInfo["exchg"] = "SZSE"
                code = rawcode  #"SZ" + rawcode
                sInfo["code"] = code
                sInfo["name"] = row["name"]
                sInfo["product"] = "IDX"            
                
                stocks[sInfo["exchg"]][code] = sInfo

        f = open(filename, 'w')
        f.write(json.dumps(stocks, sort_keys=True, indent=4, ensure_ascii=False))
        f.close()


    def dmpAdjFactorsToFile(self, codes:list, filename:str):
        stocks = {
            "SSE":{},
            "SZSE":{}
        }
        for stdCode in codes:
            ts_code = transCode(stdCode)
            exchg = stdCode.split(".")[0]
            code = stdCode[-6:]

            stocks[exchg][code] = list()
            df_factors = self.api.adj_factor(ts_code=ts_code)

            items = list()
            for idx, row in df_factors.iterrows():
                date = row["trade_date"]
                factor = row["adj_factor"]
                items.append({
                    "date": date,
                    "factor": factor
                })

            items.reverse()
            pre_factor = 0
            for item in items:
                if item["factor"] != pre_factor:
                    stocks[exchg][code].append(item)
                    pre_factor = item["factor"]

        f = open(filename, 'w+')
        f.write(json.dumps(stocks, sort_keys=True, indent=4, ensure_ascii=False))
        f.close()

    def dmpBarsToFile(self, folder:str, codes:list, start_date:datetime=None, end_date:datetime=None, period:str="day"):
        if start_date is None:
            start_date = datetime(year=1990, month=1, day=1)
        
        if end_date is None:
            end_date = datetime.now()

        freq = ''
        isDay = False
        filetag = ''
        if period == 'day':
            freq = 'D'
            isDay = True
            filetag = 'd'
        elif period == "min5":
            freq = '5min'
            filetag = 'm5'
        elif period == "min1":
            freq = '1min'
            filetag = 'm1'
        else:
            raise Exception("Unrecognized period")

        if isDay:
            start_date = start_date.strftime("%Y%m%d")
            end_date = end_date.strftime("%Y%m%d")
        else:
            start_date = start_date.strftime("%Y-%m-%d") + " 09:00:00"
            end_date = end_date.strftime("%Y-%m-%d") + " 15:15:00"

        for stdCode in codes:
            ts_code = transCode(stdCode)
            exchg = stdCode.split(".")[0]
            code = stdCode[-6:]
            asset_type = "E"
            if (exchg == 'SSE' and code[0] == '0') | (exchg == 'SZSE' and code[:3] == '399'):
                    asset_type =  "I"
            elif exchg not in ['SSE','SZSE']:
                asset_type = "FT"
                
            
            df_bars = ts.pro_bar(api=self.api, ts_code=ts_code, start_date=start_date, end_date=end_date, freq=freq)
            df_bars = df_bars.iloc[::-1]
            content = "date,time,open,high,low,close,volume,turnover\n"
            for idx, row in df_bars.iterrows():
                trade_date = row["trade_date"]
                if isDay:
                    date = trade_date + ''
                    time = '0'
                else:
                    date = trade_date.split(' ')[0]
                    time = trade_date.split(' ')[1]
                o = str(row["open"])
                h = str(row["high"])
                l = str(row["low"])
                c = str(row["close"])
                v = str(row["vol"]*100)
                t = str(row["amount"]*100)
                items = [date, time, o, h, l, c, v, t]

                content += ",".join(items) + "\n"

            filename = "%s.%s_%s.csv" % (exchg, code, filetag)
            filepath = os.path.join(folder, filename)
            f = open(filepath, "w", encoding="utf-8")
            f.write(content)
            f.close()

    def dmpCodeListToDB(self, dbHelper:DBHelper, hasIndex:bool=True, hasStock:bool=True):
        raise Exception("Baostock has not code list api")

    def dmpAdjFactorsToDB(self, dbHelper:DBHelper, codes:list):
        stocks = {
            "SSE":{},
            "SZSE":{}
        }

        for stdCode in codes:
            ts_code = transCode(stdCode)
            exchg = stdCode.split(".")[0]
            code = stdCode[-6:]

            stocks[exchg][code] = list()
            df_factors = self.api.adj_factor(ts_code=ts_code)

            items = list()
            for idx, row in df_factors.iterrows():
                date = row["trade_date"]
                factor = row["adj_factor"]
                items.append({
                    "date": int(date),
                    "factor": factor
                })

            items.reverse()
            pre_factor = 0
            for item in items:
                if item["factor"] != pre_factor:
                    stocks[exchg][code].append(item)
                    pre_factor = item["factor"]

        dbHelper.writeFactors(stocks)

    def dmpBarsToDB(self, dbHelper:DBHelper, codes:list, start_date:datetime=None, end_date:datetime=None, period:str="day"):
        if start_date is None:
            start_date = datetime(year=1990, month=1, day=1)
        
        if end_date is None:
            end_date = datetime.now()

        freq = ''
        isDay = False
        filetag = ''
        if period == 'day':
            freq = 'D'
            isDay = True
            filetag = 'd'
        elif period == "min5":
            freq = '5min'
            filetag = 'm5'
        elif period == "min1":
            freq = '1min'
            filetag = 'm1'
        else:
            raise Exception("Unrecognized period")

        if isDay:
            start_date = start_date.strftime("%Y%m%d")
            end_date = end_date.strftime("%Y%m%d")
        else:
            start_date = start_date.strftime("%Y-%m-%d") + " 09:00:00"
            end_date = end_date.strftime("%Y-%m-%d") + " 15:15:00"

        for stdCode in codes:
            ts_code = transCode(stdCode)
            exchg = stdCode.split(".")[0]
            code = stdCode[-6:]
            asset_type = "E"
            if (exchg == 'SSE' and code[0] == '0') | (exchg == 'SZSE' and code[:3] == '399'):
                    asset_type =  "I"
            elif exchg not in ['SSE','SZSE']:
                asset_type = "FT"
                
            df_bars = ts.pro_bar(api=self.api, ts_code=ts_code, start_date=start_date, end_date=end_date, freq=freq)
            bars = []
            for idx, row in df_bars.iterrows():
                trade_date = row["trade_date"]                
                if isDay:
                    bars.append({
                        "exchange":exchg,
                        "code": code,
                        "date": int(trade_date),
                        "time": 0,
                        "open": row["open"],
                        "high": row["high"],
                        "low": row["low"],
                        "close": row["close"],
                        "volume": row["vol"]*100,
                        "turnover": row["amount"]*100
                    })
                else:
                    date = int(trade_date.split(' ')[0].replace("-"))
                    time = int(trade_date.split(' ')[1].replace(":")[:4])
                    bars.append({
                        "exchange":exchg,
                        "code":code,
                        "date": date,
                        "time": time,
                        "open": row["open"],
                        "high": row["high"],
                        "low": row["low"],
                        "close": row["close"],
                        "volume": row["vol"]*100,
                        "turnover": row["amount"]*100
                    })

            dbHelper.writeBars(bars, period)