from wtpy.WtDataDefs import WtBarRecords, WtTickRecords
from wtpy.WtUtilDefs import singleton
from wtpy.wrapper import WtDtServoApi
from wtpy.WtCoreDefs import WTSBarStruct, WTSTickStruct
from wtpy.WtDataDefs import WtTickRecords,WtBarRecords

from fastapi import FastAPI, Body
from fastapi.middleware.gzip import GZipMiddleware
import uvicorn

import urllib.request
import io
import gzip
import json

import os

def httpPost(url, datas:dict, encoding='utf-8') -> dict:
    headers = {
        'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)',
        'Accept-encoding': 'gzip'
    }
    data = json.dumps(datas).encode("utf-8")
    request = urllib.request.Request(url, data, headers)
    if True:
        f = urllib.request.urlopen(request)
        ec = f.headers.get('Content-Encoding')
        if ec == 'gzip':
            cd = f.read()
            cs = io.BytesIO(cd)
            f = gzip.GzipFile(fileobj=cs)

        ret = json.loads(f.read().decode(encoding))
        f.close()
        return ret
    else:
        return None

@singleton
class WtDtServo:

    # 构造函数, 传入动态库名
    def __init__(self, logcfg:str="logcfg.yaml"):
        self.__config__ = None
        self.__cfg_commited__ = False
        self.local_api = None
        self.server_inst = None
        self.remote_api = None
        self.logCfg = logcfg

    def __check_config__(self):
        '''
        检查设置项
        主要会补充一些默认设置项
        '''
        if self.local_api is None:
            self.local_api = WtDtServoApi()

        if self.__config__ is None:
            self.__config__ = dict()

        if "basefiles" not in self.__config__:
            self.__config__["basefiles"] = dict()

        if "data" not in self.__config__:
            self.__config__["data"] = {
                "store":{
                    "path":"./storage/"
                }
            }

    def setRemoteUrl(self, url:str="http://127.0.0.1:8081"):
        if self.__config__ is not None:
            raise Exception('WtDtServo is already in local mode')
            return
        
        self.remote_api = WtDtRemoteServo(url)

    def setBasefiles(self, folder:str="./common/", commfile:str="commodities.json", contractfile:str="contracts.json", 
                holidayfile:str="holidays.json", sessionfile:str="sessions.json", hotfile:str="hots.json"):
        '''
        设置基础文件
        @folder 基础文件目录
        @commfile       品种文件, str/list
        @contractfile   合约文件, str/list
        @holidayfile    节假日文件
        @sessionfile    交易时间模板文件
        @hotfile        主力合约配置文件
        '''
        self.__check_config__()

        if type(commfile) == str:
            self.__config__["basefiles"]["commodity"] = os.path.join(folder, commfile)
        elif type(commfile) == list:
            absList = []
            for filename in commfile:
                absList.append(os.path.join(folder, filename))
            self.__config__["basefiles"]["commodity"] = ','.join(absList)

        if type(contractfile) == str:
            self.__config__["basefiles"]["contract"] = os.path.join(folder, contractfile)
        elif type(contractfile) == list:
            absList = []
            for filename in contractfile:
                absList.append(os.path.join(folder, filename))
            self.__config__["basefiles"]["contract"] = ','.join(absList)

        self.__config__["basefiles"]["holiday"] = os.path.join(folder, holidayfile)
        self.__config__["basefiles"]["session"] = os.path.join(folder, sessionfile)
        self.__config__["basefiles"]["hot"] = os.path.join(folder, hotfile)

    def setStorage(self, path:str = "./storage/", adjfactor:str = "adjfactors.json"):
        self.__config__["data"]["store"]["path"] = path
        self.__config__["data"]["store"]["adjfactor"] = adjfactor
    
    def commitConfig(self):
        if self.remote_api is not None:
            raise Exception('WtDtServo is already in remote mode')
            return
            
        if self.__cfg_commited__:
            return

        cfgfile = json.dumps(self.__config__, indent=4, sort_keys=True)
        try:
            self.local_api.initialize(cfgfile, False, self.logCfg)
            self.__cfg_commited__ = True
        except OSError as oe:
            print(oe)

    def __server_impl__(self, port:int, host:str):
        # self.server_inst.run(port = port, host = host)
        uvicorn.run(self.server_inst, port=port, host=host)

    def __init_apis__(self, app:FastAPI):

        @app.post("/clearcache")
        async def on_clear_cache():
            self.local_api.clear_cache()
                
        @app.post("/getbars")
        async def on_get_bars(
            code: str = Body(..., title="合约代码", embed=True),
            period: str = Body(..., title="K线周期", embed=True),
            stime: int = Body(None, title="开始时间", embed=True),
            etime: int = Body(..., title="结束时间", embed=True),
            count: int = Body(None, title="数据条数", embed=True)
        ):
            stdCode = code
            fromTime = stime
            dataCount = count
            endTime = etime

            if (fromTime is None and dataCount is None) or (fromTime is not None and dataCount is not None):
                return {
                    "result":-1,
                    "message":"Only one of stime and count must be valid at the same time"
                }
            else:
                bars = self.local_api.get_bars(stdCode=stdCode, period=period, fromTime=fromTime, dataCount=dataCount, endTime=endTime)
                if bars is None:
                    return {
                        "result":-2,
                        "message":"Data not found"
                    }
                else:
                    bar_list = [curBar.to_dict  for curBar in bars]
                    
                    return {
                        "result":0,
                        "message":"Ok",
                        "bars": bar_list
                    }

        @app.post("/getdaysbars")
        def on_get_day_sbars(
            code: str = Body(..., title="合约代码", embed=True),
            second: int = Body(..., title="秒线周期", embed=True),
            date: int = Body(..., title="交易日", embed=True)
        ):
            stdCode = code
            period = second
            date = date

            if date is None or period is None:
                ret = {
                    "result":-1,
                    "message":"date or second cannot be null"
                }
            else:
                bars = self.local_api.get_sbars_by_date(stdCode=stdCode, iSec=period, iDate=date)
                if bars is None:
                    ret = {
                        "result":-2,
                        "message":"Data not found"
                    }
                else:
                    bar_list = [curBar.to_dict  for curBar in bars]
                    
                    ret = {
                        "result":0,
                        "message":"Ok",
                        "bars": bar_list
                    }

            return ret

        @app.post("/getdaybars")
        def on_get_day_bars(
            code: str = Body(..., title="合约代码", embed=True),
            period: str = Body(..., title="K线周期", embed=True),
            date: int = Body(..., title="交易日", embed=True)
        ):
            stdCode = code
            if date is None or period is None:
                ret = {
                    "result":-1,
                    "message":"date or period cannot be null"
                }
            else:
                bars = self.local_api.get_bars_by_date(stdCode=stdCode, period=period, iDate=date)
                if bars is None:
                    ret = {
                        "result":-2,
                        "message":"Data not found"
                    }
                else:
                    bar_list = [curBar.to_dict  for curBar in bars]
                    
                    ret = {
                        "result":0,
                        "message":"Ok",
                        "bars": bar_list
                    }

            return ret

        @app.post("/getticks")
        def on_get_ticks(
            code: str = Body(..., title="合约代码", embed=True),
            stime: int = Body(None, title="开始时间", embed=True),
            etime: int = Body(..., title="结束时间", embed=True),
            count: int = Body(None, title="数据条数", embed=True)
        ):
            stdCode = code
            fromTime = stime
            dataCount = count
            endTime = etime

            if (fromTime is None and dataCount is None) or (fromTime is not None and dataCount is not None):
                ret = {
                    "result":-1,
                    "message":"Only one of stime and count must be valid at the same time"
                }
            else:
                ticks = self.local_api.get_ticks(stdCode=stdCode, fromTime=fromTime, dataCount=dataCount, endTime=endTime)
                if ticks is None:
                    ret = {
                        "result":-2,
                        "message":"Data not found"
                    }
                else:
                    tick_list = list()
                    for curTick in ticks:
                        curTick = curTick.to_dict
                        curTick["exchg"] = curTick["exchg"].decode()
                        curTick["code"] = curTick["code"].decode()

                        tick_list.append(curTick)
                    
                    ret = {
                        "result":0,
                        "message":"Ok",
                        "ticks": tick_list
                    }

            return ret
            
        @app.post("/getdayticks")
        def on_get_day_ticks(
            code: str = Body(..., title="合约代码", embed=True),
            date: int = Body(..., title="交易日", embed=True)
        ):
            stdCode = code

            if date is None:
                ret = {
                    "result":-1,
                    "message":"date cannot be null"
                }
            else:
                ticks = self.local_api.get_ticks_by_date(stdCode=stdCode, iDate=date)
                if ticks is None:
                    ret = {
                        "result":-2,
                        "message":"Data not found"
                    }
                else:
                    tick_list = list()
                    for curTick in ticks:
                        curTick = curTick.to_dict
                        curTick["exchg"] = curTick["exchg"].decode()
                        curTick["code"] = curTick["code"].decode()

                        tick_list.append(curTick)
                    
                    ret = {
                        "result":0,
                        "message":"Ok",
                        "ticks": tick_list
                    }

            return ret
        
    def runServer(self, port:int = 8081, host="0.0.0.0", bSync:bool = True):
        if self.remote_api is not None:
            raise Exception('WtDtServo is already in remote mode')

        app = FastAPI(title="WtDtServo", description="A http api of WtDtServo", redoc_url=None, version="1.0.0")
        app.add_middleware(GZipMiddleware, minimum_size=1000)

        self.server_inst = app 

        self.__init_apis__(app)

        self.commitConfig()
        if bSync:
            self.__server_impl__(port, host)
        else:
            import threading
            self.worker = threading.Thread(target=self.__server_impl__, args=(port,host,))
            self.worker.setDaemon(True)
            self.worker.start()

    def clear_cache(self):
        '''
        清除缓存数据
        '''
        if self.remote_api is not None:
            return self.remote_api.clear_cache()()
        
        self.local_api.clear_cache()

    def get_bars(self, stdCode:str, period:str, fromTime:int = None, dataCount:int = None, endTime:int = 0) -> WtBarRecords:
        '''
        获取K线数据
        @stdCode    标准合约代码
        @period     基础K线周期, m1/m5/d
        @fromTime   开始时间, 日线数据格式yyyymmdd, 分钟线数据为格式为yyyymmddHHMM
        @endTime    结束时间, 日线数据格式yyyymmdd, 分钟线数据为格式为yyyymmddHHMM, 为0则读取到最后一条
        '''
        if self.remote_api is not None:
            return self.remote_api.get_bars(stdCode=stdCode, period=period, fromTime=fromTime, dataCount=dataCount, endTime=endTime)
        
        self.commitConfig()

        if (fromTime is None and dataCount is None) or (fromTime is not None and dataCount is not None):
            raise Exception('Only one of fromTime and dataCount must be valid at the same time')

        return self.local_api.get_bars(stdCode=stdCode, period=period, fromTime=fromTime, dataCount=dataCount, endTime=endTime)

    def get_ticks(self, stdCode:str, fromTime:int = None, dataCount:int = None, endTime:int = 0) -> WtTickRecords:
        '''
        获取tick数据
        @stdCode    标准合约代码
        @fromTime   开始时间, 格式为yyyymmddHHMM
        @endTime    结束时间, 格式为yyyymmddHHMM, 为0则读取到最后一条
        '''
        if self.remote_api is not None:
            return self.remote_api.get_ticks(stdCode=stdCode, fromTime=fromTime, dataCount=dataCount, endTime=endTime)

        self.commitConfig()

        if (fromTime is None and dataCount is None) or (fromTime is not None and dataCount is not None):
            raise Exception('Only one of fromTime and dataCount must be valid at the same time')

        return self.local_api.get_ticks(stdCode=stdCode, fromTime=fromTime, dataCount=dataCount, endTime=endTime)

    def get_ticks_by_date(self, stdCode:str, iDate:int) -> WtTickRecords:
        '''
        按日期获取tick数据
        @stdCode    标准合约代码
        @iDate      日期, 格式为yyyymmdd
        '''
        if self.remote_api is not None:
            return self.remote_api.get_ticks_by_date(stdCode=stdCode, iDate=iDate)

        self.commitConfig()

        return self.local_api.get_ticks_by_date(stdCode=stdCode, iDate=iDate)

    def get_sbars_by_date(self, stdCode:str, iSec:int, iDate:int) -> WtTickRecords:
        '''
        按日期获取秒线数据
        @stdCode    标准合约代码
        @iSec       周期, 单位s
        @iDate      日期, 格式为yyyymmdd
        '''
        if self.remote_api is not None:
            return self.remote_api.get_sbars_by_date(stdCode=stdCode, iSec=iSec, iDate=iDate)

        self.commitConfig()

        return self.local_api.get_sbars_by_date(stdCode=stdCode, iSec=iSec, iDate=iDate)

    def get_bars_by_date(self, stdCode:str, period:str, iDate:int) -> WtTickRecords:
        '''
        按日期获取K线数据
        @stdCode    标准合约代码
        @period     周期，只支持分钟线
        @iDate      日期, 格式为yyyymmdd
        '''
        if self.remote_api is not None:
            return self.remote_api.get_bars_by_date(stdCode=stdCode, period=period, iDate=iDate)

        self.commitConfig()

        return self.local_api.get_bars_by_date(stdCode=stdCode, period=period, iDate=iDate)

class WtDtRemoteServo:

    def __init__(self, url:str="http://127.0.0.1:8081"):
        self.remote_url = url

    def clear_cache(self):
        '''
        清除缓存数据
        '''
        url = self.remote_url + "/clearcache"
        data = {}

        resObj = httpPost(url, data)
        if resObj["result"] < 0:
            print(resObj["message"])

    def get_bars(self, stdCode:str, period:str, fromTime:int = None, dataCount:int = None, endTime:int = 0) -> WtBarRecords:
        '''
        获取K线数据
        @stdCode    标准合约代码
        @period     基础K线周期, m1/m5/d
        @fromTime   开始时间, 日线数据格式yyyymmdd, 分钟线数据为格式为yyyymmddHHMM
        @endTime    结束时间, 日线数据格式yyyymmdd, 分钟线数据为格式为yyyymmddHHMM, 为0则读取到最后一条
        '''
        if (fromTime is None and dataCount is None) or (fromTime is not None and dataCount is not None):
            raise Exception('Only one of fromTime and dataCount must be valid at the same time')

        url = self.remote_url + "/getbars"
        data = {
            "code":stdCode,
            "period":period,
            "etime":endTime
        }

        if fromTime is not None:
            data["stime"] = fromTime
        elif dataCount is not None:
            data["count"] = dataCount

        resObj = httpPost(url, data)
        if resObj["result"] < 0:
            print(resObj["message"])
            return None

        barCache = WtBarRecords(len(resObj["bars"]))
        for curBar in resObj["bars"]:
            bs = WTSBarStruct()
            bs.date = curBar["date"]
            bs.time = curBar["time"]
            bs.open = curBar["open"]
            bs.high = curBar["high"]
            bs.low = curBar["low"]
            bs.close = curBar["close"]
            bs.settle = curBar["settle"]
            bs.money = curBar["money"]
            bs.vol = curBar["vol"]
            bs.hold = curBar["hold"]
            bs.diff = curBar["diff"]
            barCache.append(bs)
        return barCache
            
    def get_ticks(self, stdCode:str, fromTime:int = None, dataCount:int = None, endTime:int = 0) -> WtTickRecords:
        '''
        获取tick数据
        @stdCode    标准合约代码
        @fromTime   开始时间, 格式为yyyymmddHHMM
        @endTime    结束时间, 格式为yyyymmddHHMM, 为0则读取到最后一条
        '''
        if (fromTime is None and dataCount is None) or (fromTime is not None and dataCount is not None):
            raise Exception('Only one of fromTime and dataCount must be valid at the same time')

        url = self.remote_url + "/getticks"
        data = {
            "code":stdCode,
            "etime":endTime
        }

        if fromTime is not None:
            data["stime"] = fromTime
        elif dataCount is not None:
            data["count"] = dataCount

        resObj = httpPost(url, data)
        if resObj["result"] < 0:
            print(resObj["message"])
            return None

        tickCache = WtTickRecords(len(resObj["ticks"]))
        for curTick in resObj["ticks"]:
            ts = WTSTickStruct()
            ts.exchg = curTick["exchg"].encode('utf-8')
            ts.code = stdCode.encode('utf-8')
            ts.open = curTick["open"]
            ts.high = curTick["high"]
            ts.low = curTick["low"]
            ts.price = curTick["price"]
            ts.settle_price = curTick["settle_price"]

            ts.upper_limit = curTick["upper_limit"]
            ts.lower_limit = curTick["lower_limit"]

            ts.total_volume = curTick["total_volume"]
            ts.volume = curTick["volume"]
            ts.total_turnover = curTick["total_turnover"]
            ts.turn_over = curTick["turn_over"]
            ts.open_interest = curTick["open_interest"]
            ts.diff_interest = curTick["diff_interest"]

            ts.trading_date = curTick["trading_date"]
            ts.action_date = curTick["action_date"]
            ts.action_time = curTick["action_time"]

            ts.pre_close = curTick["pre_close"]
            ts.pre_settle = curTick["pre_settle"]
            ts.pre_interest = curTick["pre_interest"]

            # TODO 还有bid和ask档位没处理

            tickCache.append(ts)
        return tickCache

    def get_ticks_by_date(self, stdCode:str, iDate:int) -> WtTickRecords:
        '''
        按日期获取tick数据
        @stdCode    标准合约代码
        @iDate      日期, 格式为yyyymmdd
        '''
        url = self.remote_url + "/getdayticks"
        data = {
            "code":stdCode,
            "date":iDate
        }

        resObj = httpPost(url, data)
        if resObj["result"] < 0:
            print(resObj["message"])
            return None

        tickCache = WtTickRecords(len(resObj["ticks"]))
        for curTick in resObj["ticks"]:
            ts = WTSTickStruct()
            ts.exchg = curTick["exchg"].encode('utf-8')
            ts.code = stdCode.encode('utf-8')
            ts.open = curTick["open"]
            ts.high = curTick["high"]
            ts.low = curTick["low"]
            ts.price = curTick["price"]
            ts.settle_price = curTick["settle_price"]

            ts.upper_limit = curTick["upper_limit"]
            ts.lower_limit = curTick["lower_limit"]

            ts.total_volume = curTick["total_volume"]
            ts.volume = curTick["volume"]
            ts.total_turnover = curTick["total_turnover"]
            ts.turn_over = curTick["turn_over"]
            ts.open_interest = curTick["open_interest"]
            ts.diff_interest = curTick["diff_interest"]

            ts.trading_date = curTick["trading_date"]
            ts.action_date = curTick["action_date"]
            ts.action_time = curTick["action_time"]

            ts.pre_close = curTick["pre_close"]
            ts.pre_settle = curTick["pre_settle"]
            ts.pre_interest = curTick["pre_interest"]

            # TODO 还有bid和ask档位没处理

            tickCache.append(ts)
        return tickCache

    def get_sbars_by_date(self, stdCode:str, iSec:int, iDate:int) -> WtTickRecords:
        '''
        按日期获取秒线数据
        @stdCode    标准合约代码
        @iSec       周期, 单位s
        @iDate      日期, 格式为yyyymmdd
        '''
        url = self.remote_url + "/getdaysbars"
        data = {
            "code":stdCode,
            "second":iSec,
            "date":iDate
        }

        resObj = httpPost(url, data)
        if resObj["result"] < 0:
            print(resObj["message"])
            return None

        barCache = WtBarRecords(len(resObj["bars"]))
        for curBar in resObj["bars"]:
            bs = WTSBarStruct()
            bs.date = curBar["date"]
            bs.time = curBar["time"]
            bs.open = curBar["open"]
            bs.high = curBar["high"]
            bs.low = curBar["low"]
            bs.close = curBar["close"]
            bs.settle = curBar["settle"]
            bs.money = curBar["money"]
            bs.vol = curBar["vol"]
            bs.hold = curBar["hold"]
            bs.diff = curBar["diff"]
            barCache.append(bs)
        return barCache

    def get_bars_by_date(self, stdCode:str, period:str, iDate:int) -> WtTickRecords:
        '''
        按日期获取K线数据
        @stdCode    标准合约代码
        @period     周期，只支持分钟线
        @iDate      日期, 格式为yyyymmdd
        '''
        url = self.remote_url + "/getdaybars"
        data = {
            "code":stdCode,
            "second":period,
            "date":iDate
        }

        resObj = httpPost(url, data)
        if resObj["result"] < 0:
            print(resObj["message"])
            return None

        barCache = WtBarRecords(len(resObj["bars"]))
        for curBar in resObj["bars"]:
            bs = WTSBarStruct()
            bs.date = curBar["date"]
            bs.time = curBar["time"]
            bs.open = curBar["open"]
            bs.high = curBar["high"]
            bs.low = curBar["low"]
            bs.close = curBar["close"]
            bs.settle = curBar["settle"]
            bs.money = curBar["money"]
            bs.vol = curBar["vol"]
            bs.hold = curBar["hold"]
            bs.diff = curBar["diff"]
            barCache.append(bs)
        return barCache