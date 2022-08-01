import os
import json
import hashlib
import datetime
import pytz

from fastapi import FastAPI, Body
from starlette.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.sessions import SessionMiddleware
import uvicorn

from wtpy import WtDtServo

class WtBtSnooper:
    '''
    回测管理器
    '''
    def __init__(self, dtServo:WtDtServo = None):
        self.path = ""
        self.dt_servo = dtServo
        self.workspaces = list()

        self.static_folders = list()

        self.load_data()

    def load_data(self):
        if not os.path.exists("data.json"):
            return

        f = open("data.json")
        content = f.read()
        f.close()

        if len(content) == 0:
            return

        obj =  json.loads(content)
        if "workspace" in obj:
            self.workspaces = obj["workspace"]

    def save_data(self):
        obj =  {
            "workspace": self.workspaces
        }
        content = json.dumps(obj, ensure_ascii=False, indent=4)
        f = open("data.json", "w")
        f.write(content)
        f.close() 

    def add_static_folder(self, folder:str, path:str = "/static", name:str = "static"):
        self.static_folders.append({
            "path": path,
            "folder": folder,
            "name": name
        })

    def __server_impl__(self, port:int, host:str):
        uvicorn.run(self.server_inst, port = port, host = host)

    def run_as_server(self, port:int = 8081, host="127.0.0.1", bSync:bool = True):
        tags_info = [
            {"name":"Backtest APIs","description":"回测查探器接口"}
        ]

        app = FastAPI(title="WtBtSnooper", description="A simple http api of WtBtSnooper", openapi_tags=tags_info, redoc_url=None, version="1.0.0")
        app.add_middleware(GZipMiddleware, minimum_size=1000)
        app.add_middleware(SessionMiddleware, secret_key='!@#$%^&*()', max_age=25200, session_cookie='WtBtSnooper_sid')

        if len(self.static_folders) > 0:
            for static_item in self.static_folders:
                app.mount(static_item["path"], StaticFiles(directory = static_item["folder"]), name=static_item["name"])
        else:
            paths = os.path.split(__file__)
            a = (paths[:-1] + ("static/console",))
            path = os.path.join(*a)
            app.mount("/backtest", StaticFiles(directory = path), name="static")

        self.server_inst = app

        self.init_bt_apis(app)

        if bSync:
            self.__server_impl__(port, host)
        else:
            import threading
            self.worker = threading.Thread(target=self.__server_impl__, args=(port,host,))
            self.worker.setDaemon(True)
            self.worker.start()

    def get_workspace_path(self, id:str) ->str:
        for wInfo in self.workspaces:
            if wInfo["id"] == id:
                return wInfo["path"]
                
        return ""

    def init_bt_apis(self, app:FastAPI):
        @app.get("/")
        async def console_entry():
            return RedirectResponse("/backtest/backtest.html")

        @app.post("/bt/qryws", tags=["Backtest APIs"], description="获取工作空间")
        async def qry_workspaces():
            ret = {
                "result":0,
                "message":"Ok",
                "workspaces": self.workspaces
            }                

            return ret

        @app.post("/bt/addws", tags=["Backtest APIs"], description="添加工作空间")
        async def add_workspace(
            path:str = Body(..., title="工作空间路径", embed=True),
            name:str = Body(..., title="工作空间名称", embed=True)
        ):
            md5 = hashlib.md5()
            now = datetime.datetime.now().replace(tzinfo=pytz.timezone('UTC')).strftime("%Y.%m.%d %H:%M:%S")
            md5.update(now.encode("UTF8"))
            id = md5.hexdigest()
            self.workspaces.append({
                "name": name,
                "path": path,
                "id": id
            })

            self.workspaces.sort(key=lambda x: x["name"])

            self.save_data()

            return {
                "result":0,
                "message":"Ok"
            }

        @app.post("/bt/delws", tags=["Backtest APIs"], description="删除工作空间")
        async def del_workspace(
            wsid:str = Body(..., title="工作空间ID", embed=True)
        ):
            for wInfo in self.workspaces:
                if wInfo["id"] == wsid:
                    self.workspaces.remove(wInfo)
                    self.save_data()
                    break

            return {
                "result":0,
                "message":"Ok"
            }

        # 获取策略回测回合
        @app.post("/bt/qrybtstras", tags=["Backtest APIs"], description="读取全部回测策略")
        def qry_stra_bt_strategies(
            wsid:str = Body(..., title="工作空间ID", embed=True)
        ):
            path = self.get_workspace_path(wsid)
            if len(path) == 0:
                ret = {
                    "result":-1,
                    "message":"Invalid workspace"
                }

            ret = {
                "result":0,
                "message":"OK",
                "strategies": self.get_all_strategy(path)
            }
            return ret

        # 拉取K线数据
        @app.post("/bt/qrybars", tags=["Backtest APIs"], description="获取K线")
        async def qry_bt_bars(
            wsid:str = Body(..., title="工作空间ID", embed=True),
            straid:str = Body(..., title="策略ID", embed=True)
        ):
            path = self.get_workspace_path(wsid)
            if len(path) == 0:
                ret = {
                    "result":-1,
                    "message":"Invalid workspace"
                }

            code, bars, index, marks = self.get_bt_kline(path, straid)
            if bars is None:
                ret = {
                    "result":-2,
                    "message":"Data not found"
                }
            else:
                
                ret = {
                    "result":0,
                    "message":"Ok",
                    "bars": bars,
                    "code": code
                }

                if index is not None:
                    ret["index"] = index

                if marks is not None:
                    ret["marks"] = marks

            return ret

    
        # 获取策略回测信号
        @app.post("/bt/qrybtsigs", tags=["Backtest APIs"], description="读取信号明细")
        def qry_stra_bt_signals(
            wsid:str = Body(..., title="工作空间ID", embed=True),
            straid:str = Body(..., title="策略ID", embed=True)
        ):
            path = self.get_workspace_path(wsid)
            if len(path) == 0:
                ret = {
                    "result":-1,
                    "message":"Invalid workspace"
                }

            ret = {
                "result":0,
                "message":"OK",
                "signals":self.get_bt_signals(path, straid)
            }
                    
            return ret

        # 获取策略回测成交
        @app.post("/bt/qrybttrds", tags=["Backtest APIs"], description="读取成交明细")
        def qry_stra_bt_trades(
            wsid:str = Body(..., title="工作空间ID", embed=True),
            straid:str = Body(..., title="策略ID", embed=True)
        ):
            path = self.get_workspace_path(wsid)
            if len(path) == 0:
                ret = {
                    "result":-1,
                    "message":"Invalid workspace"
                }

            ret = {
                "result":0,
                "message":"OK",
                "trades":self.get_bt_trades(path, straid)
            }
                    
            return ret

        # 获取策略回测资金
        @app.post("/bt/qrybtfunds", tags=["Backtest APIs"], description="读取资金明细")
        def qry_stra_bt_funds(
            wsid:str = Body(..., title="工作空间ID", embed=True),
            straid:str = Body(..., title="策略ID", embed=True)
        ):
            path = self.get_workspace_path(wsid)
            if len(path) == 0:
                ret = {
                    "result":-1,
                    "message":"Invalid workspace"
                }

            ret = {
                "result":0,
                "message":"OK",
                "funds":self.get_bt_funds(path, straid)
            }
                    
            return ret

        # 获取策略回测回合
        @app.post("/bt/qrybtrnds", tags=["Backtest APIs"], description="读取回合明细")
        def qry_stra_bt_rounds(
            wsid:str = Body(..., title="工作空间ID", embed=True),
            straid:str = Body(..., title="策略ID", embed=True)
        ):
            path = self.get_workspace_path(wsid)
            if len(path) == 0:
                ret = {
                    "result":-1,
                    "message":"Invalid workspace"
                }

            ret = {
                "result":0,
                "message":"OK",
                "rounds":self.get_bt_rounds(path, straid)
            }
            return ret

        # 获取策略回测回合
        @app.post("/bt/qrybtinfo", tags=["Backtest APIs"], description="读取回合明细")
        def qry_stra_bt_rounds(
            wsid:str = Body(..., title="工作空间ID", embed=True),
            straid:str = Body(..., title="策略ID", embed=True)
        ):
            path = self.get_workspace_path(wsid)
            if len(path) == 0:
                ret = {
                    "result":-1,
                    "message":"Invalid workspace"
                }

            ret = {
                "result":0,
                "message":"OK",
                "info":self.get_bt_info(path, straid)
            }
            return ret

    def get_all_strategy(self, path) -> list:
        files = os.listdir(path)
        ret = list()
        for filename in files:
            filepath = os.path.join(path, filename)
            if os.path.isdir(filepath):
                ret.append(filename)
        return ret

    def get_bt_info(self, path:str, straid:str) -> dict:
        filename = f"{straid}/summary.json"
        filename = os.path.join(path, filename)
        if not os.path.exists(filename):
            return None

        f = open(filename, 'r')
        content = f.read()
        f.close()
        summary = json.loads(content)
        
        filename = f"{straid}/btenv.json"
        filename = os.path.join(path, filename)
        if not os.path.exists(filename):
            return None

        f = open(filename, 'r')
        content = f.read()
        f.close()
        env = json.loads(content)

        return {
            'summary': summary,
            'env': env
        }

    def get_bt_funds(self, path:str, straid:str) -> list:
        filename = f"{straid}/funds.csv"
        filename = os.path.join(path, filename)
        if not os.path.exists(filename):
            return None

        f = open(filename, "r")
        lines = f.readlines()
        f.close()
        lines = lines[1:]

        funds = list()
        for line in lines:
            cells = line.split(",")
            if len(cells) > 10:
                continue

            tItem = {
                "date": int(cells[0]),
                "closeprofit": float(cells[1]),
                "dynprofit": float(cells[2]),
                "dynbalance": float(cells[3]),
                "fee": 0
            }

            if len(cells) > 4:
                tItem["fee"] = float(cells[4])

            funds.append(tItem)
        
        return funds

    def get_bt_trades(self, path:str, straid:str) -> list:
        filename = f"{straid}/trades.csv"
        filename = os.path.join(path, filename)
        if not os.path.exists(filename):
            return None

        f = open(filename, "r")
        lines = f.readlines()
        f.close()
        lines = lines[1:]

        items = list()
        for line in lines:
            cells = line.split(",")
            if len(cells) > 10:
                continue

            item = {
                "code": cells[0],
                "time": int(cells[1]),
                "direction": cells[2],
                "offset": cells[3],
                "price": float(cells[4]),
                "volume": float(cells[5]),
                "tag": cells[6],
                "fee": 0
            }

            if len(cells) > 7:
                item["fee"] = float(cells[7])

            if len(cells) > 4:
                item["fee"] = float(cells[4])

            items.append(item)
        
        return items

    def get_bt_rounds(self, path:str, straid:str) -> list:
        filename = f"{straid}/closes.csv"
        filename = os.path.join(path, filename)
        if not os.path.exists(filename):
            return None

        f = open(filename, "r")
        lines = f.readlines()
        f.close()
        lines = lines[1:]

        items = list()
        for line in lines:
            cells = line.split(",")

            item = {
                "code": cells[0],
                "direct": cells[1],
                "opentime": int(cells[2]),
                "openprice": float(cells[3]),
                "closetime": int(cells[4]),
                "closeprice": float(cells[5]),
                "qty": float(cells[6]),
                "profit": float(cells[7]),
                "maxprofit": float(cells[8]),
                "maxloss": float(cells[9]),
                "entertag": cells[11],
                "exittag": cells[12]
            }

            items.append(item)
        
        return items

    def get_bt_signals(self, path:str, straid:str) -> list:
        filename = f"{straid}/signals.csv"
        filename = os.path.join(path, filename)
        if not os.path.exists(filename):
            return None

        f = open(filename, "r")
        lines = f.readlines()
        f.close()
        lines = lines[1:]

        items = list()
        for line in lines:
            cells = line.split(",")
            if len(cells) > 10:
                continue

            item = {
                "code": cells[0],
                "target": float(cells[1]),
                "sigprice": float(cells[2]),
                "gentime": cells[3],
                "tag": cells[4]
            }

            items.append(item)
        
        return items
        

    def get_bt_kline(self, path:str, straid:str) -> list:
        if self.dt_servo is None:
            return None

        filename = f"{straid}/btenv.json"
        filename = os.path.join(path, filename)
        if not os.path.exists(filename):
            return None

        f = open(filename, "r")
        content = f.read()
        f.close()

        btState = json.loads(content)

        code = btState["code"]
        period = btState["period"]
        stime = btState["stime"]
        etime = btState["etime"]

        index = None
        marks = None

        #如果有btchart，就用btchart定义的K线
        filename = f"{straid}/btchart.json"
        filename = os.path.join(path, filename)
        if os.path.exists(filename):
            f = open(filename, "r")
            content = f.read()
            f.close()

            btchart = json.loads(content)
            code = btchart['kline']["code"]
            period = btchart['kline']["period"]

            if "index":
                index = btchart["index"]

            if "marks" in btchart:
                marks = btchart["marks"]

        barList = self.dt_servo.get_bars(stdCode=code, period=period, fromTime=stime, endTime=etime)
        if barList is None:
            return None

        isDay = period[0]=='d'

        bars = list()
        for realBar in barList:
            bar = dict()
            bar["bartime"] = int(realBar.date if isDay  else 199000000000 + realBar.bartime)
            bar["open"] = realBar.open
            bar["high"] = realBar.high
            bar["low"] = realBar.low
            bar["close"] = realBar.close
            bar["volume"] = realBar.volume
            bar["turnover"] = realBar.money
            bars.append(bar)

        return code, bars, index, marks