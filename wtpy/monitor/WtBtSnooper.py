import os
import json
import hashlib
import datetime
import pytz
from fastapi import FastAPI, Body
from starlette.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.sessions import SessionMiddleware
import uvicorn
import pandas as pd
import numpy as np

from wtpy import WtDtServo


def do_trading_analyze(df_closes, df_funds):
    df_wins = df_closes[df_closes["profit"] > 0]
    df_loses = df_closes[df_closes["profit"] <= 0]

    ay_WinnerBarCnts = df_wins["closebarno"] - df_wins["openbarno"]
    ay_LoserBarCnts = df_loses["closebarno"] - df_loses["openbarno"]
    total_winbarcnts = ay_WinnerBarCnts.sum()
    total_losebarcnts = ay_LoserBarCnts.sum()

    total_fee = df_closes['fee'].sum()  # 手续费

    totaltimes = len(df_closes)  # 总交易次数
    wintimes = len(df_wins)  # 盈利次数
    losetimes = len(df_loses)  # 亏损次数
    winamout = float(df_wins["profit"].sum())  # 毛盈利
    loseamount = float(df_loses["profit"].sum())  # 毛亏损
    trdnetprofit = winamout + loseamount  # 交易净盈亏
    accnetprofit = trdnetprofit - total_fee  # 账户净盈亏
    winrate = (wintimes / totaltimes) if totaltimes > 0 else 0  # 胜率
    avgprof = (trdnetprofit / totaltimes) if totaltimes > 0 else 0  # 单次平均盈亏
    avgprof_win = (winamout / wintimes) if wintimes > 0 else 0  # 单次盈利均值
    avgprof_lose = (loseamount / losetimes) if losetimes > 0 else 0  # 单次亏损均值
    winloseratio = abs(avgprof_win / avgprof_lose) if avgprof_lose != 0 else "N/A"  # 单次盈亏均值比

    # 单笔最大盈利交易
    largest_profit = float(df_wins['profit'].max())
    # 单笔最大亏损交易
    largest_loss = float(df_loses['profit'].min())
    # 交易的平均持仓K线根数
    avgtrd_hold_bar = 0 if totaltimes==0 else ((df_closes['closebarno'] - df_closes['openbarno']).sum()) / totaltimes
    # 平均空仓K线根数
    avb = (df_closes['openbarno'] - df_closes['closebarno'].shift(1).fillna(value=0))
    avgemphold_bar = 0 if len(df_closes)==0 else avb.sum() / len(df_closes)

    # 两笔盈利交易之间的平均空仓K线根数
    win_holdbar_situ = (df_wins['openbarno'].shift(-1) - df_wins['closebarno']).dropna()
    winempty_avgholdbar = 0 if len(df_wins)== 0 or len(df_wins) == 1 else win_holdbar_situ.sum() / (len(df_wins)-1)
    # 两笔亏损交易之间的平均空仓K线根数
    loss_holdbar_situ = (df_loses['openbarno'].shift(-1) - df_loses['closebarno']).dropna()
    lossempty_avgholdbar = 0 if len(df_loses)== 0 or len(df_loses) == 1 else loss_holdbar_situ.sum() / (len(df_loses)-1)
    max_consecutive_wins = 0  # 最大连续盈利次数
    max_consecutive_loses = 0  # 最大连续亏损次数

    avg_bars_in_winner = total_winbarcnts / wintimes if wintimes > 0 else "N/A"
    avg_bars_in_loser = total_losebarcnts / losetimes if losetimes > 0 else "N/A"

    consecutive_wins = 0
    consecutive_loses = 0

    for idx, row in df_closes.iterrows():
        profit = row["profit"]
        if profit > 0:
            consecutive_wins += 1
            consecutive_loses = 0
        else:
            consecutive_wins = 0
            consecutive_loses += 1

        max_consecutive_wins = max(max_consecutive_wins, consecutive_wins)
        max_consecutive_loses = max(max_consecutive_loses, consecutive_loses)

    summary = dict()

    summary["total_trades"] = totaltimes
    summary["profit"] = float(winamout)
    summary["loss"] = float(loseamount)
    summary["net_profit"] = float(trdnetprofit)
    summary["fee"] = total_fee
    summary["accnet_profit"] = 0 if totaltimes == 0 else accnetprofit
    summary["winrate"] = winrate * 100
    summary["avgprof"] = avgprof
    summary["avgprof_win"] = avgprof_win
    summary["avgprof_lose"] = avgprof_lose
    summary["winloseratio"] = winloseratio
    summary["largest_profit"] = largest_profit
    summary["largest_loss"] = largest_loss
    summary["avgtrd_hold_bar"] = avgtrd_hold_bar
    summary["avgemphold_bar"] = avgemphold_bar
    summary["winempty_avgholdbar"] = winempty_avgholdbar
    summary["lossempty_avgholdbar"] = lossempty_avgholdbar
    summary["avg_bars_in_winner"] = avg_bars_in_winner
    summary["avg_bars_in_loser"] = avg_bars_in_loser
    summary["max_consecutive_wins"] = max_consecutive_wins
    summary["max_consecutive_loses"] = max_consecutive_loses


    return summary


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

        @app.post("/bt/qrybtcloses", tags=["Backtest APIs"], description="读取成交数据")
        def qry_stra_bt_closes(
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
                "closes_long":self.get_bt_closes(path, straid)[0],
                "closes_short":self.get_bt_closes(path, straid)[1],
                "closes_all":self.get_bt_closes(path, straid)[2],
                "closes_month": self.get_bt_closes(path, straid)[3],
                "closes_year": self.get_bt_closes(path, straid)[4]
            }
            return ret

        @app.post("/bt/qrybtanalysis", tags=["Backtest APIs"], description="读取策略分析")
        def qry_stra_bt_analysis(
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
                "analysis":self.get_bt_analysis(path, straid)
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

    def get_bt_analysis(self, path: str, straid: str) -> dict:
        funds_filename = f"{straid}/funds.csv"
        funds_filename = os.path.join(path,funds_filename)
        closes_filename = f"{straid}/closes.csv"
        closes_filename = os.path.join(path,closes_filename)

        if not (os.path.exists(funds_filename) or os.path.exists(closes_filename)):
            return None

        df_funds = pd.read_csv(funds_filename)
        df_closes = pd.read_csv(closes_filename)
        df_closes['fee'] = df_closes['profit'] - df_closes['totalprofit'] + df_closes['totalprofit'].shift(1).fillna(
            value=0)
        df_long = df_closes[df_closes['direct'].apply(lambda x: 'LONG' in x)]
        df_short = df_closes[df_closes['direct'].apply(lambda x: 'SHORT' in x)]

        summary_all = do_trading_analyze(df_closes, df_funds)
        summary_short = do_trading_analyze(df_short, df_funds)
        summary_long = do_trading_analyze(df_long, df_funds)

        return {
            'summary_all': summary_all,
            'summary_short': summary_short,
            'summary_long': summary_long
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

    def get_bt_closes(self, path:str, straid:str):
        summary_file = f"{straid}/summary.json"
        summary_file = os.path.join(path, summary_file)
        closes_file = f"{straid}/closes.csv"
        closes_file = os.path.join(path, closes_file)
        if not (os.path.exists(closes_file) or os.path.exists(summary_file)):
            return None

        f = open(summary_file, 'r')
        content = f.read()
        f.close()
        summary = json.loads(content)
        capital = summary["capital"]
        df_closes = pd.read_csv(closes_file)
        df_closes = df_closes.copy()
        df_closes['fee'] = df_closes['profit'] - df_closes['totalprofit'] + df_closes['totalprofit'].shift(1).fillna(
            value=0)
        df_closes['profit'] = df_closes['profit'] - df_closes['fee']
        df_closes['profit_sum'] = df_closes['profit'].expanding(1).sum()
        df_closes['Withdrawal'] = df_closes['profit_sum'] - df_closes['profit_sum'].expanding(1).max()
        df_closes['profit_ratio'] = 100 * df_closes['profit_sum'] / capital
        withdrawal_ratio = []
        sim_equity = df_closes['profit_sum'] + capital
        for i in range(len(df_closes)):
            withdrawal_ratio.append(100 * (sim_equity[i] / sim_equity[:i + 1].max() - 1))
        df_closes['Withdrawal_ratio'] = withdrawal_ratio
        np_trade = np.array(df_closes).tolist()
        closes_all = list()
        for item in np_trade:
            litem = {
                "opentime":int(item[2]),
                "closetime":int(item[4]),
                "profit":float(item[7]),
                "direct":str(item[1]),
                "openprice":float(item[3]),
                "closeprice":float(item[5]),
                "maxprofit":float(item[8]),
                "maxloss":float(item[9]),
                "qty":int(item[6]),
                "capital": capital,
                'profit_sum':float(item[16]),
                'Withdrawal':float(item[17]),
                'profit_ratio':float(item[18]),
                'Withdrawal_ratio':float(item[19])
            }
            closes_all.append(litem)
        df_closes['time'] = df_closes['closetime'].apply(lambda x: datetime.datetime.strptime(str(x), '%Y%m%d%H%M'))
        df_c_m = df_closes.resample(rule='M', on='time', label='right',
                                                                 closed='right').agg({
            'profit': 'sum',
            'maxprofit': 'sum',
            'maxloss': 'sum',
        })
        df_c_m = df_c_m.reset_index()
        df_c_m['equity'] = df_c_m['profit'].expanding(1).sum() + capital
        df_c_m['monthly_profit'] = 100 * (df_c_m['equity'] / df_c_m['equity'].shift(1).fillna(value=capital) - 1)
        closes_month = list()
        np_m = np.array(df_c_m).tolist()
        for item in np_m:
            litem = {
                "time":int(item[0].strftime('%Y%m')),
                "profit":float(item[1]),
                'maxprofit':float(item[2]),
                'maxloss':float(item[3]),
                'equity':float(item[4]),
                'monthly_profit':float(item[5])
            }
            closes_month.append(litem)

        df_c_y = df_closes.resample(rule='Y', on='time', label='right',
                                    closed='right').agg({
            'profit': 'sum',
            'maxprofit': 'sum',
            'maxloss': 'sum',
        })
        df_c_y = df_c_y.reset_index()
        df_c_y['equity'] = df_c_y['profit'].expanding(1).sum() + capital
        df_c_y['monthly_profit'] = 100 * (df_c_y['equity'] / df_c_y['equity'].shift(1).fillna(value=capital) - 1)
        closes_year = list()
        np_y = np.array(df_c_y).tolist()
        for item in np_y:
            litem = {
                "time":int(item[0].strftime('%Y%m')),
                "profit":float(item[1]),
                'maxprofit':float(item[2]),
                'maxloss':float(item[3]),
                'equity':float(item[4]),
                'annual_profit':float(item[5])
            }
            closes_year.append(litem)

        df_long = df_closes[df_closes['direct'].apply(lambda x: 'LONG' in x)]
        df_short = df_closes[df_closes['direct'].apply(lambda x: 'SHORT' in x)]
        df_long = df_long.copy()
        df_short = df_short.copy()
        df_long["long_profit"] = df_long["profit"].expanding(1).sum()-df_long["fee"].expanding(1).sum()
        closes_long = list()
        closes_short = list()
        np_long = np.array(df_long).tolist()
        for item in np_long:
            litem = {
                "date":int(item[4]),
                "long_profit":float(item[-1]),
                "capital":capital
            }
            closes_long.append(litem)
        df_short["short_profit"] = df_short["profit"].expanding(1).sum()-df_short["fee"].expanding(1).sum()
        np_short = np.array(df_short).tolist()
        for item in np_short:
            litem = {
                "date":int(item[4]),
                "short_profit":float(item[-1]),
                "capital":capital
            }
            closes_short.append(litem)

        return closes_long, closes_short, closes_all, closes_month, closes_year

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

            if "index" in btchart:
                index = btchart["index"]

        filename = f"{straid}/marks.csv"
        filename = os.path.join(path, filename)
        if os.path.exists(filename):
            f = open(filename, "r")
            lines = f.readlines()
            f.close()

            if len(lines) > 2:
                marks = []
                for line in lines[1:-1]:
                    items = line.split(",")
                    marks.append({
                        "bartime": int(items[0]),
                        "price": float(items[1]),
                        "icon": items[2],
                        "tag": items[3]
                    })

        filename = f"{straid}/indice.csv"
        filename = os.path.join(path, filename)
        if os.path.exists(filename):
            f = open(filename, "r")
            lines = f.readlines()
            f.close()

            if len(lines) > 2:
                for line in lines[1:-1]:
                    items = line.split(",")
                    index_name = items[1]
                    line_name = items[2]
                    index_val = float(items[3])
                    for iInfo in index:
                        if iInfo["name"] != index_name:
                            continue

                        for lInfo in iInfo["lines"]:
                            if lInfo["name"] != line_name:
                                continue

                            if "values" not in lInfo:
                                lInfo["values"] = list()

                            lInfo["values"].append(index_val)

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
