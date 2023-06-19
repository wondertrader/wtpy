from wtpy.apps.datahelper.DHDefs import BaseDataHelper, DBHelper
from wtpy.WtCoreDefs import WTSBarStruct
from tqsdk import TqApi, TqAuth
from datetime import datetime
import json
import os
import logging


def stdCodeToTQ(stdCode:str):
    items = stdCode.split(".")
    exchg = items[0]
    if len(items) == 2 and exchg in ['SSE', 'SZSE']:
        # 简单股票代码，格式如SSE.600000
        return stdCode
    elif items[1] in ["IDX","ETF","STK","OPT"]:
        # 标准股票代码，格式如SSE.IDX.000001
        return exchg + "." + items[2]
    elif len(items) == 3 and exchg in ["SHFE", "CFFEX", "DCE", "CZCE", "INE", "GFEX"]:
        # 标准期货代码，格式如CFFEX.IF.2103
        if items[2] != 'HOT':
            return exchg + '.' + items[1] + items[2]
        else:
            return "KQ.m@" + exchg + '.' +items[1]
    else:
        return stdCode


class DHTqSdk(BaseDataHelper):

    def __init__(self):
        BaseDataHelper.__init__(self)
        self.username = None
        self.password = None
        logging.info("TqSdk helper has been created.")
        return

    def auth(self, **kwargs):
        if self.isAuthed:
            return
        self.username = kwargs["username"]
        self.password = kwargs["password"]
        api = TqApi(auth=TqAuth(kwargs["username"], kwargs["password"]))
        self.isAuthed = True
        api.close()
        logging.info("TqSdk has been authorized.")

    def dmpCodeListToFile(self, filename:str, hasIndex:bool=True, hasStock:bool=True):
        api = TqApi(auth=TqAuth(self.username, self.password))
        stocks = {
            "SSE": {},
            "SZSE": {}
        }
        futures = {
            "SHFE": {},
            "CFFEX": {},
            "DCE": {},
            "CZCE": {},
            "INE": {},
            "GFEX": {}
        }
        if hasStock:
            logging.info("Fetching stock list...")
            for exchange in stocks.keys():
                code_list = api.query_quotes(ins_class="STOCK", exchange_id=exchange)
                code_list_info = api.query_symbol_info(code_list)
                for idx, row in code_list_info.iterrows():
                    sInfo = dict()
                    rawcode = row["instrument_id"].split('.')[-1]
                    sInfo["exchg"] = exchange
                    sInfo["code"] = rawcode
                    sInfo["name"] = row["instrument_name"]
                    sInfo["product"] = "STK"
                    stocks[sInfo["exchg"]][rawcode] = sInfo
        if hasIndex:
            logging.info("Fetching Index list...")
            for exchange in stocks.keys():
                code_list = api.query_quotes(ins_class="INDEX", exchange_id=exchange)
                code_list_info = api.query_symbol_info(code_list)
                for idx, row in code_list_info.iterrows():
                    sInfo = dict()
                    rawcode = row["instrument_id"].split('.')[-1]
                    sInfo["exchg"] = exchange
                    sInfo["code"] = rawcode
                    sInfo["name"] = row["instrument_name"]
                    sInfo["product"] = "IDX"
                    stocks[sInfo["exchg"]][rawcode] = sInfo
        logging.info("Writing code list into file %s..." % (filename))
        stocks.update(futures)
        f = open(filename, 'w', encoding='utf-8')
        f.write(json.dumps(stocks, sort_keys=True, indent=4, ensure_ascii=False))
        f.close()
        api.close()

    def dmpAdjFactorsToFile(self, codes: list, filename: str):
        raise Exception("TqSdk has not Adj Factors api")

    def dmpAdjFactorsToDB(self, dbHelper: DBHelper, codes: list):
        raise Exception("TqSdk has not Adj Factors api")

    def dmpBarsToFile(self, folder:str, codes:list, start_date:datetime=None, end_date:datetime=None, period="day"):
        api = TqApi(auth=TqAuth(self.username, self.password))
        if start_date is None:
            start_date = datetime(year=1990, month=1, day=1)
        if end_date is None:
            end_date = datetime.now()
        freq = ''
        filetag = ''
        if period == 'day':
            freq = 86400
            filetag = 'd'
        elif period == 'min5':
            freq = 300
            filetag = 'm5'
        elif period == "min1":
            freq = 60
            filetag = 'm1'
        elif isinstance(period, int):
            freq = period
            if (0 < period <= 86400) or period % 86400 == 0:
                filetag = str(freq)
            else:
                raise Exception("Unrecognized period")
        else:
            raise Exception("Unrecognized period")

        count = 0
        length = len(codes)
        for stdCode in codes:
            count += 1
            logging.info("Fetching %s bars of %s(%d/%s)..." % (period, stdCode, count, length))
            code = stdCodeToTQ(stdCode)
            try:
                df_bars = api.get_kline_data_series(symbol=code, duration_seconds=freq, start_dt=start_date, end_dt=end_date, adj_type=None)
            except Exception as e:
                api.close()
                raise Exception(f"{e}")
            content = "date,time,open,high,low,close,volume\n"
            for idx, row in df_bars.iterrows():
                trade_date = datetime.fromtimestamp(row["datetime"] / 1000000000)
                date = trade_date.strftime("%Y-%m-%d")
                if freq == 86400:
                    time = '0'
                else:
                    time = trade_date.strftime("%H:%M:%S")
                o = str(row["open"])
                h = str(row["high"])
                l = str(row["low"])
                c = str(row["close"])
                v = str(row["volume"])
                items = [date, time, o, h, l, c, v]
                content += ','.join(items) + "\n"
                filename = "%s_%s.csv" % (stdCode, filetag)
                filepath = os.path.join(folder, filename)
                logging.info("Writing bars into file %s..." % (filepath))
                f = open(filepath, "w", encoding="utf-8")
                f.write(content)
                f.close()
        api.close()

    def dmpBarsToDB(self, dbHelper: DBHelper, codes: list, start_date: datetime = None, end_date: datetime = None,
                    period: str = "day"):
        api = TqApi(auth=TqAuth(self.username, self.password))
        if start_date is None:
            start_date = datetime(year=1990, month=1, day=1)

        if end_date is None:
            end_date = datetime.now()
        freq = ''
        if period == 'day':
            freq = 86400
        elif period == 'min5':
            freq = 300
        elif period == "min1":
            freq = 60
        else:
            raise Exception("Unrecognized period")
        count = 0
        length = len(codes)
        for stdCode in codes:
            count += 1
            logging.info("Fetching %s bars of %s(%d/%s)..." % (period, stdCode, count, length))
            code = stdCodeToTQ(stdCode)
            df_bars = api.get_kline_data_series(symbol=code, duration_seconds=freq, start_dt=start_date, end_dt=end_date, adj_type=None)
            exchg = code.split('.')[0]
            rawcode = code.split('.')[-1]
            total_nums = len(df_bars)
            bars = []
            cur_num = 0
            for idx, row in df_bars.iterrows():
                trade_date = datetime.fromtimestamp(row["datetime"] / 1000000000)
                date = int(trade_date.strftime("%Y%m%d"))
                if freq == 86400:
                    time = '0'
                else:
                    time = int(trade_date.strftime("%H%M"))
                curBar = {
                    "exchange": exchg,
                    "code": rawcode,
                    "date": date,
                    "time": time,
                    "open": row["open"],
                    "high": row["high"],
                    "low": row["low"],
                    "close": row["close"],
                    "volume": row["volume"],
                }

                bars.append(curBar)
                cur_num += 1
                if cur_num % 500 == 0:
                    logging.info("Processing bars %d/%d..." % (cur_num, total_nums))

            logging.info("Writing bars into database...")
            dbHelper.writeBars(bars, period)
        api.close()

    def dmpBars(self, codes:list, cb, start_date:datetime=None, end_date:datetime=None, period:str="day"):
        api = TqApi(auth=TqAuth(self.username, self.password))
        if start_date is None:
            start_date = datetime(year=1990, month=1, day=1)

        if end_date is None:
            end_date = datetime.now()

        freq = ''
        if period == 'day':
            freq = 86400
        elif period == 'min5':
            freq = 300
        elif period == "min1":
            freq = 60
        elif isinstance(period, int):
            if (0 < period <= 86400) or period % 86400 == 0:
                freq = period
            else:
                raise Exception("Unrecognized period")
        else:
            raise Exception("Unrecognized period")
        count = 0
        length = len(codes)
        for stdCode in codes:
            count += 1
            logging.info("Fetching %s bars of %s(%d/%s)..." % (period, stdCode, count, length))
            code = stdCodeToTQ(stdCode)
            try:
                df_bars = api.get_kline_data_series(symbol=code, duration_seconds=freq, start_dt=start_date, end_dt=end_date, adj_type=None)
            except Exception as e:
                api.close()
                raise Exception(f"{e}")
            total_nums = len(df_bars)
            BUFFER = WTSBarStruct*len(df_bars)
            buffer = BUFFER()
            cur_num = 0
            for idx, row in df_bars.iterrows():
                curBar = buffer[cur_num]
                trade_date = datetime.fromtimestamp(row["datetime"] / 1000000000)
                curBar.date = int(trade_date.strftime("%Y%m%d"))
                if period == 'day':
                    curBar.time = 0
                else:
                    curBar.time = int(trade_date.strftime("%H%M")) + (curBar.date-19900000)*10000
                curBar.open = row["open"]
                curBar.high = row["high"]
                curBar.low = row["low"]
                curBar.close = row["close"]
                curBar.vol = row["volume"]
                # curBar.money = None
                # if "open_interest" in row:
                #     curBar.hold = row["open_interest"]
                cur_num += 1
                if cur_num % 500 == 0:
                    logging.info("Processing bars %d/%d..." % (cur_num, total_nums))
            ay = stdCode.split(".")
            cb(ay[0], stdCode, buffer, total_nums, period)
        api.close()

