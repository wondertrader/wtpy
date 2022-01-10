from wtpy import BaseExtParser
from wtpy import WTSTickStruct
from ctypes import byref

import websocket
import json   
import threading
import ssl

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
                curTick.code = bytes("OKEX", encoding="UTF8")
                curTick.exchg = bytes(code, encoding="UTF8")

                curTick.price = float(data["last"])
                curTick.open = float(data["open24h"])
                curTick.high = float(data["high24h"])
                curTick.low = float(data["low24h"])

                curTick.volume = float(data["lastSz"])
                curTick.ask_prices[0] = float(data["askPx"])
                curTick.ask_qty[0] = float(data["askSz"])
                curTick.bid_prices[0] = float(data["bidPx"])
                curTick.bid_qty[0] = float(data["bidSz"])
                
                if code in self.depth_cache:
                    myDepth = self.depth_cache[code]
                    for i in range(1,len(myDepth["asks"])):
                        curTick.ask_prices[i] = float(myDepth["asks"][i][0])
                        curTick.ask_qty[i] = float(myDepth["asks"][i][1])
                    for i in range(1,len(myDepth["bids"])):
                        curTick.bid_prices[i] = float(myDepth["bids"][i][0])
                        curTick.bid_qty[i] = float(myDepth["bids"][i][1])

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
        "host": "127.0.0.1",
        "port": 10809
    }, trace=False)
    myParser.init(engine)
    engine.add_exetended_parser(myParser)

    engine.run()

    kw = input('press any key to exit\n')