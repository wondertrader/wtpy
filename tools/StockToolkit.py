import tushare as ts
import json
import os
import datetime

import urllib.request
import io
import gzip

import struct
import time
import re

import baostock as bs

import rqdatac as rq

def create_dirs(path):
    lst = path.replace("/","\\").split("\\")
    dir = lst[0] + "/"
    if not os.path.exists(dir):
        os.mkdir(dir)

    for idx in range(1,len(lst)):
        dir += lst[idx] + "//"
        if not os.path.exists(dir):
            os.mkdir(dir)

def is_file_empty(path):
    if not os.path.exists(path):
        return True

    flen = os.path.getsize(path)
    if flen == 0:
        return True
    
    return False
    
    
def httpGet(url, encoding='utf-8'):
    request = urllib.request.Request(url)
    request.add_header('Accept-encoding', 'gzip')
    request.add_header(
        'User-Agent', 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)')
    try:
        f = urllib.request.urlopen(request)
        ec = f.headers.get('Content-Encoding')
        if ec == 'gzip':
            cd = f.read()
            cs = io.BytesIO(cd)
            f = gzip.GzipFile(fileobj=cs)

        return f.read().decode(encoding)
    except:
        return ""

def recordToDict(rs, obj):
    if rs.next():
        row = rs.get_row_data()
        for idx,field in enumerate(rs.fields):
            if field not in ['code','pubDate','statDate']:
                obj[field] = row[idx]
    return obj
        
class StockToolkit:

    def __init__(self, tushare_toke:str = None):
        self.__pro__ = None
        if tushare_toke is not None:
            self.__pro__ = ts.pro_api(tushare_toke)
        self.__stocks__ = dict()
        self.__indice__ = dict()

    def getFinDataFromBS(self, codes:list, year:int, quarter:int):
        
        #盈利能力
        bs.login()
        for code in codes:
            ay = code.split(".")
            exchg = ay[0]
            rawcode = ay[1]
            bscode = ''
            if exchg == 'SSE':
                bscode = 'sh.' + rawcode
            else:
                bscode = 'sz.' + rawcode
            
            fdata = dict()
            fdata['code'] = code
            rs = bs.query_profit_data(bscode, year, quarter)
            fdata = recordToDict(rs, fdata)

            rs = bs.query_operation_data(bscode, year, quarter)
            fdata = recordToDict(rs, fdata)

            rs = bs.query_growth_data(bscode, year, quarter)
            fdata = recordToDict(rs, fdata)

            rs = bs.query_balance_data(bscode, year, quarter)
            fdata = recordToDict(rs, fdata)

            rs = bs.query_cash_flow_data(bscode, year, quarter)
            fdata = recordToDict(rs, fdata)

            rs = bs.query_dupont_data(bscode, year, quarter)
            fdata = recordToDict(rs, fdata)
            
            # rs = bs.query_performance_express_report(bscode, year, quarter)
            # fdata = recordToDict(rs, fdata)
            
            # rs = bs.query_forcast_report(bscode, year, quarter)
            # fdata = recordToDict(rs, fdata)

        bs.logout()
        return fdata

    def loadStocks(self, filename:str = ''):
        if not os.path.exists(filename):
            return False

        f = open("stocks.json", "r")
        content = f.read()
        stk_dict = json.loads(content)

        for exchg in stk_dict:
            for code in stk_dict[exchg]:
                cInfo = stk_dict[exchg][code]
                stdCode = ''
                if exchg == "SSE":
                    stdCode = "SH" + code
                else:
                    stdCode = "SZ" + code
                if cInfo["product"] == "IDX":
                    self.__indice__[stdCode] = cInfo
                else:
                    self.__stocks__[stdCode] = cInfo

        f.close()
        return True

    def getAllCodes(self, isIndex:bool = False):
        if not isIndex:
            return list(self.__stocks__.keys())
        else:
            return list(self.__indice__.keys())

    def dmpStksFromTS(self, filename:str = "", hasIndice:bool = True):
        '''
        从tushare导出股票列表\n
        @filename   导出的json文件名
        @hasIndice  是否包含指数
        '''
        stocks = {
            "SSE":{},
            "SZSE":{}
        }

        #个股列表
        df_stocks = self.__pro__.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
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
            sInfo["indust"] = row["industry"]
            sInfo["area"] = row["area"]
            sInfo["product"] = pid            
            
            stocks[sInfo["exchg"]][code] = sInfo

            self.__stocks__[row["ts_code"][-2:] + code] = sInfo

        if hasIndice:
            #上证指数列表
            df_stocks = self.__pro__.index_basic(market='SSE')
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
                self.__indice__["SH" + rawcode] = sInfo

            #深证指数列表
            df_stocks = self.__pro__.index_basic(market='SZSE')
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
                self.__indice__["SZ" + rawcode] = sInfo

        if len(filename) > 0:
            f = open(filename, 'w')
            f.write(json.dumps(stocks, sort_keys=True, indent=4, ensure_ascii=False))
            f.close()

    def dmpAdjFromSINA(self, filename:str):
        '''
        从新浪导出除权因子
        '''
        #https://finance.sina.com.cn/realstock/company/sh600000/qfq.js
        total = len(self.__stocks__.keys())
        if total == 0:
            raise Exception("stock list has not been initialized")

        stocks = {
            "SSE":{},
            "SZSE":{}
        }

        count = 0
        for code in self.__stocks__:
            count += 1
            url = "https://finance.sina.com.cn/realstock/company/%s/qfq.js" % (code)
            print("正在拉取%s[%d/%d]的除权因子……" % (code, count, total))
            cInfo = self.__stocks__[code]
            exchg = cInfo["exchg"]
            content = httpGet(url.lower())
            if len(content) == 0:
                continue

            if code[2:] not in stocks[exchg]:
                stocks[exchg][code[2:]] = list()

            content = content[16:]
            content = content.split("\n")[0]
            resObj = json.loads(content)
            for item in resObj["data"]:
                date = int(item["d"].replace("-",""))
                factor = float(item["f"])
                stocks[exchg][code[2:]].append({
                    "date": date,
                    "factor": factor
                })

        f = open(filename, 'w+')
        f.write(json.dumps(stocks, sort_keys=True, indent=4, ensure_ascii=False))
        f.close()

    def dmpStkDaysFromTS(self, folder:str, sdate:str="1990-01-01", edate:str="", codes:list = None, bNeedAdj:bool = True, isIndex:bool = False):
        '''
        从tushare导出日线数据，慢！！！\n
        @sdate  开始日期，格式如2020-06-09\n
        @edate  结束日期，格式同上\n
        @codes  代码列表，为空时自动获取\n
        @bNeedAdj   是否除权，默认为True\n
        @isIndex    是否指数数据，默认为False\n
        '''
        if edate == "":
            edate = datetime.datetime.now().strftime('%Y-%m-%d')

        if not os.path.exists(folder + 'day/'):
            create_dirs(folder + 'day/')
    
        if not os.path.exists(folder + 'min5/'):
            create_dirs(folder + 'min5/')

        if codes is None:
            if isIndex:
                codes = self.__indice__.keys()
            else:
                codes = self.__stocks__.keys()

        total = len(codes)

        count = 0
        for code in codes:
            count += 1
            print("正在拉取%s的日线[%d/%d]……" % (code, count, total))
            exchg = ""
            if code[:2] == "SH":
                exchg = "SSE"
            else:
                exchg = "SZSE"

            thisFolder = folder + 'day/' + exchg + "/"
            if not os.path.exists(thisFolder):
                create_dirs(thisFolder)

            thisFolder = folder + 'min5/' + exchg + "/"
            if not os.path.exists(thisFolder):
                create_dirs(thisFolder)
            
            df_bars = None
            try:
                # get_h_data貌似也可以
                df_bars = ts.get_k_data(code[2:], start=sdate, end=edate, ktype='D', autype='qfq' if bNeedAdj else None, index=isIndex)

                csvpath = (folder + 'day/%s/%s%s.csv') % (exchg, code[2:], "Q" if bNeedAdj and not isIndex else "")

                isEmpty = is_file_empty(csvpath)
                f = open(csvpath, 'a')
                if isEmpty:
                    f.write("date, time, open, high, low, close, volumn\n")

                for idx, row in df_bars.iterrows():
                    f.write(datetime.datetime.strptime(str(row["date"]), '%Y-%m-%d').strftime("%Y/%m/%d") + ", ")
                    f.write("0, ")
                    f.write(str(row["open"]) + ", ")
                    f.write(str(row["high"]) + ", ")
                    f.write(str(row["low"]) + ", ")
                    f.write(str(row["close"]) + ", ")
                    f.write(str(row["volume"]) + "\n")
                f.close()
            except:
                print("正在拉取%s的日线异常" % (code))

            print("正在拉取%s的5分钟线[%d/%d]……" % (code, count, total))
            df_bars = None
            try:
                df_bars = ts.get_k_data(code[2:], sdate, edate, ktype='5', autype='qfq' if bNeedAdj else None)

                csvpath = (folder + 'min5/%s/%s%s.csv') % (exchg, code[2:], "Q" if bNeedAdj and not isIndex else "")

                f = open(csvpath, 'w')
                f.write("date, time, open, high, low, close, volumn\n")

                for idx, row in df_bars.iterrows():
                    curDt = datetime.datetime.strptime(str(row["date"]), '%Y-%m-%d %H:%M')
                    f.write(curDt.strftime("%Y/%m/%d") + ", ")
                    f.write(curDt.strftime("%H:%M") + ", ")
                    f.write(str(row["open"]) + ", ")
                    f.write(str(row["high"]) + ", ")
                    f.write(str(row["low"]) + ", ")
                    f.write(str(row["close"]) + ", ")
                    f.write(str(row["volume"]) + "\n")
                f.close()
            except:
                print("正在拉取%s的5分钟线异常" % (code))

    def dmpStkMin1FromWind(self, folder:str, sdate:int=19900101, edate:int=0, codes:list = None, isIndex:bool = False):
        from WindPy import w
        if edate == 0:
            edate = int(datetime.datetime.now().strftime('%Y%m%d'))

        if codes is None:
            if isIndex:
                codes = self.__indice__.keys()
            else:
                codes = self.__stocks__.keys()
        total = len(codes)

        endtime = str(edate)
        endtime = endtime[0:4] + "-" + endtime[4:6] + "-" + endtime[6:] + " 15:30:00"
        begintime = str(sdate)
        begintime = begintime[0:4] + "-" + begintime[4:6] + "-" + begintime[6:] + " 09:00:00"

        count = 0
        w.start()
        for code in codes:
            count += 1

            rawcode = code
            code = code[2:]  + "." + code[:2]

            exchg = ""
            if rawcode[:2] == "SH":
                exchg = "SSE"
            else:
                exchg = "SZSE"

            print("正在拉取%s[%d/%d]的1分钟线数据[%d-%d]……" % (rawcode, count, total, sdate, edate))

            if not os.path.exists(folder + 'min/' + exchg + "/"):
                create_dirs(folder + 'min/' + exchg + "/")

            csvpath = (folder + 'min/%s/%s.csv') % (exchg, rawcode[2:])
           
            err, df_bars = w.wsi(code, fields="open,high,low,close,volume", beginTime=begintime, endTime=endtime, options="BarSize=1;Fill=Previous", usedf=True)
            if err != 0:
                print("拉取出错")
                print(df_bars)
                continue

            if len(df_bars) == 0:
                print("历史数据为空,跳过处理")
                continue
            
            print("正在写入数据文件")
            isEmpty = is_file_empty(csvpath)
            f = open(csvpath, 'a')
            if isEmpty:
                f.write("date, time, open, high, low, close, volumn\n")

            df_bars.fillna(0, inplace=True)
            content = ""
            for idx in range(0,len(df_bars)):
                curBar = df_bars.iloc[idx]
                bartime = df_bars.index[idx]
                curMin = int(bartime.strftime("%H%M"))
                if curMin == 1130 or curMin == 1500:
                    continue

                if curMin == 1129 or curMin == 1459:
                    nextBar = df_bars.iloc[idx+1]
                    if curBar["volume"] != 0:
                        if nextBar["volume"] != 0:
                            curBar["volume"] += nextBar["volume"]
                            curBar["close"] = nextBar["close"]
                            curBar["high"] = max(curBar["high"], nextBar["high"])
                            curBar["low"] = min(curBar["low"], nextBar["low"])
                    else:
                        curBar = nextBar
                bartime = bartime + datetime.timedelta(minutes=1)
                line = ""
                line += (bartime.strftime("%Y/%m/%d") + ", ")
                line += (bartime.strftime("%H:%M:%S") + ", ")
                line += (str(curBar["open"]) + ",")
                line += (str(curBar["high"]) + ",")
                line += (str(curBar["low"]) + ",")
                line += (str(curBar["close"]) + ",")
                line += (str(curBar["volume"]) + "\n")

                content += line
            f.write(content)
            f.close()

        w.stop()

    def dmpStkMin1FromTqsdk(self, folder:str, sdate:int=19900101, edate:int=0, codes:list = None, isIndex:bool = False):
        from tqsdk import TqApi
        if edate == 0:
            edate = int(datetime.datetime.now().strftime('%Y%m%d'))

        if codes is None:
            if isIndex:
                codes = self.__indice__.keys()
            else:
                codes = self.__stocks__.keys()
        total = len(codes)

        count = 0
        api = TqApi(_stock=True)
        for code in codes:
            count += 1
            if code == 'SZ000029' or code == 'SZ300362':
                continue

            rawcode = code
            if code[:2] == "SH":
                code = "SSE." + code[2:]
            else:
                code = "SZSE." + code[2:]

            exchg = ""
            if rawcode[:2] == "SH":
                exchg = "SSE"
            else:
                exchg = "SZSE"

            print("正在拉取%s[%d/%d]的1分钟线数据[%d-%d]……" % (rawcode, count, total, sdate, edate))

            if not os.path.exists(folder + 'min/' + exchg + "/"):
                create_dirs(folder + 'min/' + exchg + "/")

            csvpath = (folder + 'min/%s/%s.csv') % (exchg, rawcode[2:])
           
            df_bars = api.get_kline_serial(code, 60, 1000000)
            if len(df_bars) == 0:
                continue
            
            isEmpty = is_file_empty(csvpath)
            f = open(csvpath, 'a')
            if isEmpty:
                f.write("date, time, open, high, low, close, volumn\n")
            for idx,row in df_bars.iterrows():
                if row["datetime"] == 0:
                    continue
                bartime = datetime.datetime.fromtimestamp(row["datetime"]/1e9)
                bardate = int(bartime.strftime("%Y%m%d"))
                if bardate > edate:
                    break
                f.write(bartime.strftime("%Y/%m/%d") + ", ")
                barmin = (int)(bartime.strftime("%H"))*60 + (int)(bartime.strftime("%M"))
                barmin += 1
                barmin = "%02d:%02d" % ((int)(barmin/60), barmin%60)
                f.write( barmin +":00,")
                f.write(str(row["open"]) + ",")
                f.write(str(row["high"]) + ",")
                f.write(str(row["low"]) + ",")
                f.write(str(row["close"]) + ",")
                f.write(str(row["volume"]) + "\n")
            f.close()

        api.close()

    def dmpStkBarsFromBS(self, folder:str, sdate:int=19900101, edate:int=0, codes:list = None, isIndex:bool = False, isDay:bool = True, bAdjust:bool=True):
        if edate == 0:
            edate = int(datetime.datetime.now().strftime('%Y%m%d'))

        if codes is None:
            if isIndex:
                codes = self.__indice__.keys()
            else:
                codes = self.__stocks__.keys()
        total = len(codes)

        count = 0
        bs.login()
        for code in codes:
            count += 1
            rawcode = code
            if code[:2] == "SH":
                code = "sh." + code[2:]
            else:
                code = "sz." + code[2:]

            exchg = ""
            if rawcode[:2] == "SH":
                exchg = "SSE"
            else:
                exchg = "SZSE"
            
            print("正在拉取%s[%d/%d]的K线数据[%d-%d]……" % (rawcode, count, total, sdate, edate))

            start_dt = datetime.datetime.strptime(str(sdate), '%Y%m%d').strftime('%Y-%m-%d')
            end_dt = datetime.datetime.strptime(str(edate), '%Y%m%d').strftime('%Y-%m-%d')

            freq = "d"
            subdir = "day"
            if not isDay:
                freq = "5"
                subdir = "min5"

            adjflag = '3'
            if bAdjust:
                adjflag = '2'
            fields = "date,code,open,high,low,close,volume,amount"
            if not isDay:
                fields = "date,time,code,open,high,low,close,volume,amount"
            rs = bs.query_history_k_data_plus(code, fields, 
                start_date=start_dt, end_date=end_dt, frequency=freq, adjustflag=adjflag)

            if not os.path.exists(folder + subdir + '/' + exchg + "/"):
                create_dirs(folder + subdir + '/' + exchg + "/")

            if isIndex or not bAdjust:
                csvpath = (folder + subdir + '/%s/%s.csv') % (exchg, rawcode[2:])
            else:
                csvpath = (folder + subdir + '/%s/%sQ.csv') % (exchg, rawcode[2:])

            isEmpty = is_file_empty(csvpath)
            f = open(csvpath, 'a')
            if isEmpty:
                f.write("date, time, open, high, low, close, volumn, amount\n")

            while (rs.error_code=='0') & rs.next():
                row = rs.get_row_data()
                if isDay:
                    f.write(datetime.datetime.strptime(row[0], '%Y-%m-%d').strftime("%Y/%m/%d") + ", ")
                    f.write( "0,")
                    f.write(row[2] + ",")
                    f.write(row[3] + ",")
                    f.write(row[4] + ",")
                    f.write(row[5] + ",")
                    if isIndex:
                        f.write(str(float(row[6])/100) + ",") #指数日线成交量改成手数
                    else:
                        f.write(row[6] + ",")
                    f.write(row[7] + "\n")                        
                else:
                    f.write(datetime.datetime.strptime(row[0], '%Y-%m-%d').strftime("%Y/%m/%d") + ", ")
                    time = row[1][8:10] + ":" + row[1][10:12]
                    f.write( time +":00,")
                    f.write(row[3] + ",")
                    f.write(row[4] + ",")
                    f.write(row[5] + ",")
                    f.write(row[6] + ",")
                    f.write(row[7] + ",")
                    f.write(row[8] + "\n")
            
        bs.logout()
    
    def authRiceQuant(self, loginid:str, passwd:str):
        rq.init(username=loginid, password=passwd)
    
    def dmpStkBarsFromRQ(self, folder:str, sdate:int=19900101, edate:int=0, codes:list = None, isIndex:bool = False, period:str = 'day', bAdjust:bool=True):
        if edate == 0:
            edate = int(datetime.datetime.now().strftime('%Y%m%d'))

        if codes is None:
            if isIndex:
                codes = self.__indice__.keys()
            else:
                codes = self.__stocks__.keys()
        total = len(codes)

        count = 0
        for code in codes:
            count += 1
            rawcode = code
            if code[:2] == "SH":
                code = code[2:] + '.XSHG'
            else:
                code = code[2:] + '.XSHE'

            exchg = ""
            if rawcode[:2] == "SH":
                exchg = "SSE"
            else:
                exchg = "SZSE"
            
            print("正在拉取%s[%d/%d]的K线数据[%d-%d]……" % (rawcode, count, total, sdate, edate))

            start_dt = datetime.datetime.strptime(str(sdate), '%Y%m%d').strftime('%Y-%m-%d')
            end_dt = datetime.datetime.strptime(str(edate), '%Y%m%d').strftime('%Y-%m-%d')

            freq = "d"
            subdir = period
            if period == 'day':
                freq = "1d"
            elif period == 'min1':
                freq = '1m'
            else:
                freq = "5m"

            adjflag = 'none'
            if bAdjust:
                adjflag = 'pre'

            if not os.path.exists(folder + subdir + '/' + exchg + "/"):
                create_dirs(folder + subdir + '/' + exchg + "/")

            if isIndex or not bAdjust:
                csvpath = (folder + subdir + '/%s/%s.csv') % (exchg, rawcode[2:])
            else:
                csvpath = (folder + subdir + '/%s/%sQ.csv') % (exchg, rawcode[2:])

            isEmpty = is_file_empty(csvpath)
            if not isEmpty:
                continue
            
            try:
                df_stocks = rq.get_price (order_book_ids = code,  
                    start_date=start_dt, end_date=end_dt, frequency=freq, adjust_type=adjflag)
            except:
                continue
            
            if df_stocks is None:
                continue

            f = open(csvpath, 'a')
            if isEmpty:
                f.write("date, time, open, high, low, close, volumn, amount\n")
            
            content = ""
            for idx, row in df_stocks.iterrows():
                line = ''
                if period=='day':
                    line += idx.strftime("%Y/%m/%d") + ", "
                    line += "0,"
                    line += str(row['open']) + ","
                    line += str(row['high']) + ","
                    line += str(row['low']) + ","
                    line += str(row['close']) + ","
                    if isIndex:
                        line += str(row['volume'])/100 + "," #指数日线成交量改成手数
                    else:
                        line += str(row['volume']) + ","
                    line += str(row["total_turnover"]) + "\n"               
                else:
                    line += idx.strftime("%Y/%m/%d") + ", "
                    line += idx.strftime("%H:%M") + ", "
                    line += str(row['open']) + ","
                    line += str(row['high']) + ","
                    line += str(row['low']) + ","
                    line += str(row['close']) + ","
                    line += str(row['volume']) + ","
                    line += str(row["total_turnover"]) + "\n"
                content += line
            f.write(content)
            f.close()
        