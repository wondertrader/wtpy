import math
import time
from wtpy import BaseExtParser
from wtpy import WTSTickStruct
from ctypes import byref

# if not exists, install websocket-client v1.2.3+
import websocket

import json   
import threading
import ssl

import datetime

from wtpy import WtDtEngine

class MyParser(BaseExtParser):
    def __init__(self, id: str, url:str, proxy:dict = None, trace:bool = False):
        super().__init__(id)
        self.__worker__ = None

        self._url = url
        self._proxy = proxy
        self._ws = None
        self.connected = False
        websocket.enableTrace(trace)
        self.subs = list()

        self.oi_cache = dict()
        self.depth_cache = dict()

    def init(self, engine:WtDtEngine):
        '''
        初始化
        '''
        super().init(engine)

    def run(self):
        if self._proxy is not None:
            self._ws.run_forever(
                http_proxy_host=self._proxy["host"], 
                http_proxy_port=self._proxy["port"],
                proxy_type="http",
                sslopt={"cert_reqs": ssl.CERT_NONE})
        else:
            self._ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        print("worker died")

    def connect(self):
        '''
        开始连接
        '''
        print("connect")

        self._ws = websocket.WebSocketApp(self._url,
                    on_message=self.on_message,
                    on_open=self.on_open,
                    on_close=self.on_close,
                    on_error=self.on_error)
        if self.__worker__ is None:
            self.__worker__ = threading.Thread(target=self.run, daemon=True)
            self.__worker__.start()
        return

    def do_subscribe(self, codeList:list):
        
        if len(codeList) == 0:
            return

        obj = {
            "op":"subscribe",
            "args":[]
        }

        count = 0
        for fullCode in codeList:
            realCode = fullCode.split(".")[-1]
            # 快照
            obj["args"].append({
                "channel":"tickers",
                "instId":realCode
            })

            # 五档
            obj["args"].append({
                "channel":"books5",
                "instId":realCode
            })

            # 总持
            obj["args"].append({
                "channel":"open-interest",
                "instId":realCode
            })
            count += 1

            if count == 100:
                data = json.dumps(obj)
                self._ws.send(data)

                obj["args"] = []
                count = 0

        if len(obj["args"]) > 0:
            data = json.dumps(obj)
            self._ws.send(data)

    def on_open(self, ws):
        self.connected = True
        self.do_subscribe(self.subs)

    def on_close(self, ws, ec, errmsg):
        print("onclose:")
        if errmsg is not None:
            print(errmsg)

    def on_error(self, ws, error):
        print("on_error")
        print(error)
        return
    
    def on_message(self, ws, message):
        # print(message)
        root = json.loads(message)
        if "event" in root:
            print(root)
            return

        if "arg" in root:
            args = root["arg"]
            channel = args["channel"]
            if channel == "tickers":
                # 快照
                code = args["instId"]
                data = root["data"][0]

                curTick = WTSTickStruct()
                curTick.exchg = bytes("OKEX", encoding="UTF8")
                curTick.code = bytes(code, encoding="UTF8")

                curTick.price = float(data["last"])
                curTick.open = float(data["open24h"])
                curTick.high = float(data["high24h"])
                curTick.low = float(data["low24h"])

                curTick.volume = float(data["lastSz"])
                curTick.ask_price_0 = float(data["askPx"])
                curTick.ask_qty_0 = float(data["askSz"])
                curTick.bid_prices_0 = float(data["bidPx"])
                curTick.bid_qty_0 = float(data["bidSz"])

                #先处理本地时间
                tm = datetime.datetime.fromtimestamp(int(data["ts"])/1000)
                curTick.action_date = tm.year*10000 + tm.month*100 + tm.day
                curTick.action_time = tm.hour*10000000 + tm.minute*100000 + tm.second*1000 + math.floor(tm.microsecond/1000)

                #再转成utc时间获取交易日
                tm = datetime.datetime.utcfromtimestamp(int(data["ts"])/1000)
                curTick.trading_date = tm.year*10000 + tm.month*100 + tm.day
                
                if code in self.depth_cache:
                    myDepth = self.depth_cache[code]
                    for i in range(1,len(myDepth["asks"])):
                        setattr(curTick, f"ask_price_{i}", float(myDepth["asks"][i][0]))
                        setattr(curTick, f"ask_qty_{i}", float(myDepth["asks"][i][1]))
                        # curTick.ask_prices[i] = float(myDepth["asks"][i][0])
                        # curTick.ask_qty[i] = float(myDepth["asks"][i][1])
                    for i in range(1,len(myDepth["bids"])):
                        setattr(curTick, f"bid_price_{i}", float(myDepth["bids"][i][0]))
                        setattr(curTick, f"bid_qty_{i}", float(myDepth["bids"][i][1]))
                        # curTick.bid_prices[i] = float(myDepth["bids"][i][0])
                        # curTick.bid_qty[i] = float(myDepth["bids"][i][1])

                if code in self.oi_cache:
                    myOI = self.oi_cache[code]
                    curTick.open_interest = myOI["total"]
                    curTick.diff_interest = myOI["diff"]

                self.__engine__.push_quote_from_extended_parser(self.id(), byref(curTick), False)
                pass
            elif channel == "books5":
                # 五档
                code = args["instId"]
                data = root["data"][0]
                if code not in self.depth_cache:
                    self.depth_cache[code] = {
                        "bids":list(),
                        "asks":list()
                    }

                myDepth = self.depth_cache[code]
                myDepth["bids"] = data["bids"]
                myDepth["asks"] = data["asks"]
            elif channel == "open-interest":
                # 总持
                code = args["instId"]
                data = root["data"][0]
                if code not in self.oi_cache:
                    self.oi_cache[code] = {
                        "total":0,
                        "diff":0
                    }
                myOI = self.oi_cache[code]
                prev = myOI["total"]
                myOI["total"] = float(data["oi"])
                if prev != 0:
                    myOI["diff"] = myOI["total"] - prev
                

    def disconnect(self):
        '''
        断开连接
        '''
        print("disconnect")
        self._ws.close()
        return

    def release(self):
        '''
        释放，一般是进程退出时调用
        '''
        print("release")
        self.disconnect()
        return

    def subscribe(self, fullCode:str):
        '''
        订阅实时行情\n
        @fullCode   合约代码，格式如CFFEX.IF2106
        '''
        if self.connected:
            self.do_subscribe([fullCode])
        else:
            self.subs.append(fullCode)
        return

    def unsubscribe(self, fullCode:str):
        '''
        退订实时行情\n
        @fullCode   合约代码，格式如CFFEX.IF2106
        '''
        return

if __name__ == "__main__":
    #创建一个运行环境，并加入策略
    #创建一个运行环境，并加入策略
    engine = WtDtEngine()
    engine.initialize("dtcfg.yaml", "logcfgdt.yaml")
    
    myParser = MyParser("test", url="wss://ws.okex.com:8443/ws/v5/public", proxy={
        "host": "192.168.61.1",
        "port": 10811
    }, trace=False)
    myParser.init(engine)
    engine.add_exetended_parser(myParser)

    engine.run(True)

    print('press ctrl-c to exit')
    try:
    	while True:
            time.sleep(1)
    except KeyboardInterrupt as e:
    	exit(0)