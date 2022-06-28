from wtpy.apps import WtCacheMon
import rqdatac as rq
import datetime
import urllib
import pandas as pd
from tqdm import tqdm

import urllib.request
import io
import gzip
import xml.dom.minidom
from pyquery import PyQuery as pq
import re
import json
import pickle
import os
rq.init()
class DayData:
    '''
    每日行情数据
    '''

    def __init__(self):
        self.pid = ''
        self.month = 0
        self.code = ''  # 代码
        self.close = 0  # 今收盘(收盘价)
        self.volume = 0  # 成交量(手)
        self.hold = 0  # 空盘量(总持？持仓量)

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
    
def httpPost(url, datas, encoding='utf-8'):
    headers = {
        'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)',
        'Accept-encoding': 'gzip'
    }
    data = urllib.parse.urlencode(datas).encode('utf-8')
    request = urllib.request.Request(url, data, headers)
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
    
class RqCacheMonExchg(WtCacheMon):
    '''
    米筐数据缓存器
    '''
    
    def __init__ (self,start_date,end_date,pkl_file=""):
        super().__init__()
        self.pkl_file = pkl_file
        self.all_info = rq.all_instruments("Future")
        self.all_info = self.all_info[(self.all_info["listed_date"]!="0000-00-00") & (self.all_info["de_listed_date"]!="0000-00-00")]
        self.all_info["listed_date"] = pd.to_datetime(self.all_info["listed_date"])
        self.all_info["de_listed_date"] = pd.to_datetime(self.all_info["de_listed_date"])
        if start_date == None:
            start_date = self.all_info["listed_date"].min()
        if end_date == None:
            end_date = self.all_info["de_listed_date"].max()
        self.all_info = self.all_info[(self.all_info["de_listed_date"] > start_date) & (self.all_info["listed_date"] < end_date)]
        self.init_cache()
        self.all_info = self.all_info.set_index("order_book_id")
    def init_cache(self):
        try:
            with open(self.pkl_file,"rb") as f:
                self.day_cache = pickle.load(f)
        except:
            pass
        # 过滤已有的数据
        loaded_date = {}
        for key,value in self.day_cache.items():
            for exchg,item in value.items():
                for comm in item.keys():
                    loaded_date[comm.upper()] = max(datetime.datetime.strptime(key,"%Y%m%d"),loaded_date.get(comm,datetime.datetime(1996,1,1)))
        exchgs = ["CFFEX","SHFE","DCE","CZCE","INE"]
        df = self.all_info[self.all_info["exchange"].isin(exchgs)]
        now = datetime.datetime.now()
        for exchg in exchgs:
            df = self.all_info[self.all_info["exchange"] == exchg]
            comms = set()
            for index,row in df.iterrows():
                comm = row["order_book_id"]
                de_listed_date = row["de_listed_date"]
                last_loaded = loaded_date.get(comm,datetime.datetime(1996,1,1))
                if (de_listed_date > last_loaded) and (now.date() > last_loaded.date()):
                    comms.add(comm)
            if len(comms) == 0:
                continue
            data = rq.get_price(comms,start_date = df["listed_date"].min(),end_date=df["de_listed_date"].max(),frequency="1d")
            for index,row in tqdm(data.iterrows(),desc=exchg,total=len(data)):
                dtStr = index[1].strftime('%Y%m%d')
                code = index[0]
                month = re.search("(\d+)",code)[0]
                pid = re.search("[a-zA-Z]+",code)[0]
                item = DayData()
                if exchg in ["CZCE","CFFEX"]:
                    pid = pid.upper()
                    if exchg == "CZCE":
                        month = month[-3:]
                else:
                    pid = pid.lower()
                item.code = f"{pid}{month}"
                item.month = int(month)
                item.pid = pid
                item.hold = row["open_interest"]
                item.close = row["close"]
                item.volume = row["volume"]
                if dtStr not in self.day_cache.keys():
                    self.day_cache[dtStr] = dict()
                if exchg not in self.day_cache[dtStr].keys():
                    self.day_cache[dtStr][exchg] = dict()
                self.day_cache[dtStr][exchg][item.code] = item
                
        if self.pkl_file != "":
            with open(self.pkl_file,"wb") as f:
                pickle.dump(self.day_cache,f)

    def get_cache(self, exchg:str, curDT:datetime.datetime):
        '''
        获取指定日期的某个交易所合约的快照数据

        @exchg  交易所代码
        @curDT  指定日期
        '''
        dtStr = curDT.strftime('%Y%m%d')

        if dtStr not in self.day_cache:
            return None

        if exchg not in self.day_cache[dtStr]:
            return None
        return self.day_cache[dtStr][exchg]
    
    def get_delivery_day(self,code,work_day_delay=0,month=False):
        code = code.upper()
        try:
            date = datetime.datetime.strptime(self.all_info.loc[code,"maturity_date"],"%Y-%m-%d")
        except:
            date = None
        
        if work_day_delay == 0:
            return date
        if date is not None:
            if month:
                date = date.replace(day=1)
            date = rq.get_previous_trading_date(date,work_day_delay)
        return date

 if __name__ == '__main__':
    root = r".\common"
    start_date = dt.datetime(2010,1,1)
    end_date = None
    
    hotFile = "hots.json"
    secFile = "seconds.json"
    cacher = RqCacheMonExchg(start_date,end_date,"rq_daily_cache.pkl") 

    # 从datakit落地的行情快照直接读取
    # cacher = WtCacheMonSS("./FUT_DATA/his/snapshot/")

    picker = hotpicker.WtHotPicker(hotFile=hotFile, secFile=secFile)
    picker.set_cacher(cacher)

    sDate = start_date
    eDate = None # 可以设置为None，None则自动设置为当前日期
    hotRules,secRules = picker.execute_rebuild(sDate, eDate, wait=True)
    print(hotRules)
    print(secRules)
