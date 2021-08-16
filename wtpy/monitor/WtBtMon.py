'''
Descripttion: 回测管理模块
version: 
Author: Wesley
Date: 2021-08-11 14:03:33
LastEditors: Wesley
LastEditTime: 2021-08-16 16:10:44
'''
import os
import json
import subprocess
import platform
import sys
import psutil
import hashlib
import datetime

from wtpy import WtDtServo
from .WtLogger import WtLogger
from .EventReceiver import BtEventReceiver, BtEventSink

def isWindows():
    if "windows" in platform.system().lower():
        return True

    return False

def md5_str(v:str) -> str:
    return hashlib.md5(v.encode()).digest()

def gen_btid(strid:str) -> str:
    now = datetime.datetime()
    s = straid + "_" + str(now.timestamp())
    return md5_str(s)

class WtBtTask(BtEventSink):
    '''
    回测任务类
    '''
    def __init__(self, user:str, straid:str, btid:str, folder:str, logger:WtLogger = None):
        self.user = user
        self.straid = straid
        self.btid = btid
        self.logger = logger
        self.folder = folder
        
        self._cmd_line = None
        self._mq_url = "ipc:///wtpy/bt_%s.ipc" % (btid)
        self._ticks = 0
        self._state = 0
        self._procid = None
        self._evt_receiver = BtEventReceiver(url=self._mq_url, logger=self.logger)

    def run(self):
        if self._state != 0:
            return

        self._evt_receiver.run()
        self.logger.info("回测%s开始接收%s的通知信息" % (self.btid, self._mq_url))

        try:
            fullPath = os.path.join(self.folder, "runBT.py")
            if isWindows():
                self._procid = subprocess.Popen([sys.executable, fullPath],  # 需要执行的文件路径
                                cwd=self.folder, creationflags=subprocess.CREATE_NEW_CONSOLE).pid
            else:
                self._procid = subprocess.Popen([sys.executable, fullPath],  # 需要执行的文件路径
                                cwd=self.folder).pid

            self._cmd_line = sys.executable + " " + fullPath
        except:
            self.logger.info("回测%s启动异常" % (self.btid))

        self._state = 1

        self.logger.info("回测%s的已启动，进程ID: %d" % (self.btid, self._procid))

    @property
    def cmd_line(self) -> str:
        fullPath = os.path.join(self.folder, "runBT.py")
        if self._cmd_line is None:
            self._cmd_line = sys.executable + " " + fullPath
        return self._cmd_line

    def is_running(self, pids) -> bool:
        bNeedCheck = (self._procid is None) or (not psutil.pid_exists(self._procid))
        if bNeedCheck:
            for pid in pids:
                try:
                    pInfo = psutil.Process(pid)
                    cmdLine = pInfo.cmdline()
                    if len(cmdLine) == 0:
                        continue
                    # print(cmdLine)
                    cmdLine = ' '.join(cmdLine)
                    if self.cmd_line.upper() == cmdLine.upper():
                        self._procid = pid
                        self.logger.info("回测%s挂载成功，进程ID: %d" % (self.btid, self._procid))

                        if self._mq_url != '':
                            self._evt_receiver.run()
                            self.logger.info("回测%s开始接收%s的通知信息" % (self.btid, self._mq_url))
                except:
                    pass
            return False

        return True


class WtBtMon:
    '''
    回测管理器
    '''
    def __init__(self, deploy_folder:str, data_folder:str = "", commFolder:str = ""):
        self.path = deploy_folder
        self.user_stras = dict()
        self.user_bts = dict()
        self.dt_servo = None
        if len(commFolder) > 0:
            self.dt_servo = WtDtServo()
            self.dt_servo.setStorage(data_folder)
            self.dt_servo.setBasefiles(commFolder + "commodities.json",
                            commFolder + "contracts.json",
                            commFolder + "holidays.json",
                            commFolder + "sessions.json",
                            commFolder + "hots.json")
            self.dt_servo.commitConfig()
        pass

    def __load_user_data__(self, user:str):
        folder = os.path.join(self.path, user)
        if not os.path.exists(folder):
            os.mkdir(folder)

        filepath = os.path.join(folder, "marker.json")
        if not os.path.exists(filepath):
            return False

        f = open(filepath, "r")
        content = f.read()
        f.close()

        obj = json.loads(content)
        self.user_stras[user] = obj["strategies"]
        self.user_bts[user] = obj["backtests"]
        return True

    def get_strategies(self, user:str) -> list:
        if user not in self.user_stras:
            bSucc = self.__load_user_data__(user)
        
        if not bSucc:
            return None

        '''
        {
            "49ba59abbe56e057":
            {
                "id":"49ba59abbe56e057",
                "name":"策略名称",
                "perform":{
                    "return":19.3,
                    "mdd":7.86,
                    "capital":500000,
                    "
                }
            }
        }
        '''
        ay = list()
        for straid in self.user_stras[user]:
            ay.append(self.user_stras[user][straid])
        return ay


    def get_backtests(self, user:str, straid:str) -> list:
        bSucc = False
        if user not in self.user_bts:
            bSucc = self.__load_user_data__(user)

        if not bSucc:
            return None

        if straid not in self.user_bts:
            return None

        '''
        {
            "49ba59abbe56e057":
            {
                "id":"49ba59abbe56e057",
                "code":"CFFEX.IC.HOT",
                "period":"m5",
                "stime":202107010930,
                "etime":202108151500,
                "progress":100.0
            }
        }
        '''
        ay = list()
        for btid in self.user_bts[straid]:
            ay.append(self.user_bts[straid][btid])

        return ay

    def get_bt_funds(self, user:str, straid:str, btid:str) -> list:
        if user not in self.user_bts:
            bSucc = self.__load_user_data__(user)

        if not bSucc:
            return None

        thisBts = self.user_bts[user]
        if btid not in thisBts:
            return None

        filename = "%s/%s/backtests/%s/outputs_bt/%s/funds.csv" % (user, straid, btid, btid)
        filename = os.path.join(self.path, filename)
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

    def get_bt_trads(self, user:str, straid:str, btid:str) -> list:
        if user not in self.user_bts:
            bSucc = self.__load_user_data__(user)

        if not bSucc:
            return None

        thisBts = self.user_bts[user]
        if btid not in thisBts:
            return None

        filename = "%s/%s/backtests/%s/outputs_bt/%s/trades.csv" % (user, straid, btid, btid)
        filename = os.path.join(self.path, filename)
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


    def get_bt_rounds(self, user:str, straid:str, btid:str) -> list:
        if user not in self.user_bts:
            bSucc = self.__load_user_data__(user)

        if not bSucc:
            return None

        thisBts = self.user_bts[user]
        if btid not in thisBts:
            return None

        filename = "%s/%s/backtests/%s/outputs_bt/%s/closes.csv" % (user, straid, btid, btid)
        filename = os.path.join(self.path, filename)
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
                "direct": cells[1],
                "opentime": int(cells[2]),
                "openprice": float(cells[3]),
                "closetime": int(cells[4]),
                "closeprice": float(cells[5]),
                "qty": float(cells[6]),
                "profit": float(cells[7]),
                "entertag": cells[9],
                "exittag": cells[10]
            }

            items.append(item)
        
        return items

    def get_bt_signals(self, user:str, straid:str, btid:str) -> list:
        if user not in self.user_bts:
            bSucc = self.__load_user_data__(user)

        if not bSucc:
            return None

        thisBts = self.user_bts[user]
        if btid not in thisBts:
            return None

        filename = "%s/%s/backtests/%s/outputs_bt/%s/signals.csv" % (user, straid, btid, btid)
        filename = os.path.join(self.path, filename)
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

    def get_bt_summary(self, user:str, straid:str, btid:str) -> list:
        if user not in self.user_bts:
            bSucc = self.__load_user_data__(user)

        if not bSucc:
            return None

        thisBts = self.user_bts[user]
        if btid not in thisBts:
            return None

        filename = "%s/%s/backtests/%s/outputs_bt/%s/summary.json" % (user, straid, btid, btid)
        filename = os.path.join(self.path, filename)
        if not os.path.exists(filename):
            return None

        f = open(filename, "r")
        content = f.read()
        f.close()

        obj = json.loads(content)
        return obj

    def get_bt_state(self, user:str, straid:str, btid:str) -> dict:
        if user not in self.user_bts:
            bSucc = self.__load_user_data__(user)

        if not bSucc:
            return None

        thisBts = self.user_bts[user]
        if btid not in thisBts:
            return None

        if "state" not in thisBts[btid]:
            filename = "%s/%s/backtests/%s/outputs_bt/%s/btenv.json" % (user, straid, btid, btid)
            filename = os.path.join(self.path, filename)
            if not os.path.exists(filename):
                return None

            f = open(filename, "r")
            content = f.read()
            f.close()

            thisBts[btid]["state"] = json.loads(content)

        return thisBts[btid]["state"]

    def update_bt_state(self, user:str, straid:str, btid:str, stateObj:dict):
        if user not in self.user_bts:
            bSucc = self.__load_user_data__(user)

        if not bSucc:
            return None

        thisBts = self.user_bts[user]
        if btid not in thisBts:
            return None

        thisBts[btid]["state"] = stateObj

    def get_bt_kline(self, user:str, straid:str, btid:str) -> list:
        if self.dt_servo is None:
            return None

        if user not in self.user_bts:
            bSucc = self.__load_user_data__(user)

        if not bSucc:
            return None
        
        btState = self.get_bt_state(user, straid, btid)
        if btState is None:
            return None

        thisBts = self.user_bts[user]
        if "kline" not in thisBts[btid]:
            code = btState["code"]
            period = btState["period"]
            stime = btState["stime"]
            etime = btState["etime"]
            barList = self.dt_servo.get_bars(stdCode=code, period=period, fromTime=stime, endTime=etime)
            if barList is None:
                return None

            bars = list()
            for realBar in barList:
                bar = dict()
                if period[0] == 'd':
                    bar["time"] = realBar.date
                else:
                    bar["time"] = 1990*100000000 + realBar.time
                    bar["bartime"] = bar["time"]
                    bar["open"] = realBar.open
                    bar["high"] = realBar.high
                    bar["low"] = realBar.low
                    bar["close"] = realBar.close
                    bar["volume"] = realBar.vol
                bars.append(bar)
            thisBts[btid]["kline"] = bars

        return thisBts[btid]["kline"]



    