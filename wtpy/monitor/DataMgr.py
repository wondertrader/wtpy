import json
import os
import sqlite3
import hashlib
import datetime
from .WtLogger import WtLogger

class DataMgr:

    def __init__(self, datafile:str="mondata.db", logger:WtLogger=None):
        self.__grp_cache__ = dict()
        self.__logger__ = logger

        self.__db_conn__ = sqlite3.connect(datafile, check_same_thread=False)
        self.__check_db__()

        #加载组合列表
        cur = self.__db_conn__.cursor()
        self.__config__ = {
            "groups":{},
            "users":{}
        }

        for row in cur.execute("SELECT * FROM groups;"):
            grpInfo = dict()
            grpInfo["id"] = row[1]
            grpInfo["name"] = row[2]
            grpInfo["path"] = row[3]
            grpInfo["info"] = row[4]
            grpInfo["gtype"] = row[5]
            grpInfo["datmod"] = row[6]
            grpInfo["env"] = row[7]
            self.__config__["groups"][grpInfo["id"]] = grpInfo

        for row in cur.execute("SELECT * FROM users;"):
            usrInfo = dict()
            usrInfo["loginid"] = row[1]
            usrInfo["name"] = row[2]
            usrInfo["role"] = row[3]
            usrInfo["passwd"] = row[4]
            usrInfo["iplist"] = row[5]
            usrInfo["remark"] = row[6]
            usrInfo["createby"] = row[7]
            usrInfo["createtime"] = row[8]
            usrInfo["modifyby"] = row[9]
            usrInfo["modifytime"] = row[10]
            self.__config__["users"][usrInfo["loginid"]] = usrInfo

    def get_db(self):
        return self.__db_conn__

    def __check_db__(self):
        if self.__db_conn__ is None:
            return

        cur = self.__db_conn__.cursor()
        tables = []
        for row in cur.execute("select name from sqlite_master where type='table' order by name"):
            tables.append(row[0])
        
        if "actions" not in tables:
            sql = "CREATE TABLE [actions] (\n"
            sql += "[id] INTEGER PRIMARY KEY autoincrement, \n"
            sql += "[loginid] VARCHAR(20) NOT NULL DEFAULT '', \n"
            sql += "[actiontime] DATETIME default (datetime('now', 'localtime')), \n"
            sql += "[actionip] VARCHAR(30) NOT NULL DEFAULT '', \n"
            sql += "[actiontype] VARCHAR(20) NOT NULL DEFAULT '',\n"
            sql += "[remark] TEXT default '');"
            cur.execute(sql)
            cur.execute("CREATE INDEX [idx_actions_loginid] ON [actions] ([loginid]);")
            cur.execute("CREATE INDEX [idx_actions_actiontime] ON [actions] ([actiontime]);")
            self.__db_conn__.commit()

        if "groups" not in tables:
            sql = "CREATE TABLE [groups] (\n"
            sql += "[id] INTEGER PRIMARY KEY autoincrement,\n"
            sql += "[groupid] VARCHAR(20) NOT NULL DEFAULT '',\n"
            sql += "[name] VARCHAR(30) NOT NULL DEFAULT '',\n"
            sql += "[path] VARCHAR(256) NOT NULL DEFAULT '',\n"
            sql += "[info] TEXT DEFAULT '',\n"
            sql += "[gtype] VARCHAR(10) NOT NULL DEFAULT 'cta',\n"
            sql += "[datmod] VARCHAR(10) NOT NULL DEFAULT 'mannual',\n"
            sql += "[env] VARCHAR(20) NOT NULL DEFAULT 'product',\n"
            sql += "[createtime] DATETIME default (datetime('now', 'localtime')),\n"
            sql += "[modifytime] DATETIME default (datetime('now', 'localtime')));"
            cur.execute(sql)
            cur.execute("CREATE UNIQUE INDEX [idx_groupid] ON [groups] ([groupid]);")
            self.__db_conn__.commit()

        if "schedules" not in tables:
            sql = "CREATE TABLE [schedules] (\n"
            sql += "[id] INTEGER PRIMARY KEY autoincrement,\n"
            sql += "[appid] VARCHAR(20) NOT NULL DEFAULT '',\n"
            sql += "[path] VARCHAR(256) NOT NULL DEFAULT '',\n"
            sql += "[folder] VARCHAR(256) NOT NULL DEFAULT '',\n"
            sql += "[param] VARCHAR(50) NOT NULL DEFAULT '',\n"
            sql += "[type] INTEGER DEFAULT 0,\n"
            sql += "[span] INTEGER DEFAULT 3,\n"
            sql += "[guard] VARCHAR(20) DEFAULT 'false',\n"
            sql += "[redirect] VARCHAR(20) DEFAULT 'false',\n"
            sql += "[schedule] VARCHAR(20) DEFAULT 'false',\n"
            sql += "[weekflag] VARCHAR(20) DEFAULT '000000',\n"
            sql += "[task1] VARCHAR(100) NOT NULL DEFAULT '{\"active\": true,\"time\": 0,\"action\": 0}',\n"
            sql += "[task2] VARCHAR(100) NOT NULL DEFAULT '{\"active\": true,\"time\": 0,\"action\": 0}',\n"
            sql += "[task3] VARCHAR(100) NOT NULL DEFAULT '{\"active\": true,\"time\": 0,\"action\": 0}',\n"
            sql += "[task4] VARCHAR(100) NOT NULL DEFAULT '{\"active\": true,\"time\": 0,\"action\": 0}',\n"
            sql += "[task5] VARCHAR(100) NOT NULL DEFAULT '{\"active\": true,\"time\": 0,\"action\": 0}',\n"
            sql += "[task6] VARCHAR(100) NOT NULL DEFAULT '{\"active\": true,\"time\": 0,\"action\": 0}',\n"
            sql += "[createtime] DATETIME default (datetime('now', 'localtime')),\n"
            sql += "[modifytime] DATETIME default (datetime('now', 'localtime')));"
            cur.execute(sql)
            cur.execute("CREATE UNIQUE INDEX [idx_appid] ON [schedules] ([appid]);")
            self.__db_conn__.commit()

        if "users" not in tables:
            sql = "CREATE TABLE [users] (\n"
            sql += "[id] INTEGER PRIMARY KEY autoincrement,\n"
            sql += "[loginid] VARCHAR(20) NOT NULL DEFAULT '',\n"
            sql += "[name] VARCHAR(30) NOT NULL DEFAULT '',\n"
            sql += "[role] VARCHAR(10) NOT NULL DEFAULT '',\n"
            sql += "[passwd] VARCHAR(30) NOT NULL DEFAULT 'cta',\n"
            sql += "[iplist] VARCHAR(100) NOT NULL DEFAULT 'mannual',\n"
            sql += "[remark] VARCHAR(256) NOT NULL DEFAULT '',\n"
            sql += "[createby] VARCHAR(20) NOT NULL DEFAULT '',\n"
            sql += "[createtime] DATETIME default (datetime('now', 'localtime')),\n"
            sql += "[modifyby] VARCHAR(20) NOT NULL DEFAULT '',\n"
            sql += "[modifytime] DATETIME default (datetime('now', 'localtime')));"
            cur.execute(sql)
            cur.execute("CREATE UNIQUE INDEX [idx_loginid] ON [users] ([loginid]);")
            self.__db_conn__.commit()

    def __check_cache__(self, grpid, grpInfo):
        if grpid not in self.__grp_cache__:
            self.__grp_cache__[grpid] = dict()

        if "strategies" not in self.__grp_cache__[grpid]:
            filepath = "./generated/marker.json"
            filepath = os.path.join(grpInfo["path"], filepath)
            if not os.path.exists(filepath):
                return []
            else:
                try:
                    f = open(filepath, "r")
                    content = f.read()
                    marker = json.loads(content)
                    f.close()

                    self.__grp_cache__[grpid] = {
                        "strategies":marker["marks"],
                        "channels":marker["channels"]
                    } 

                except:
                    self.__grp_cache__[grpid] = {
                        "strategies":[],
                        "channels":[]
                    } 
            self.__grp_cache__[grpid]["strategies"].sort()
            self.__grp_cache__[grpid]["channels"].sort()

    def get_groups(self, tpfilter:str=''):
        ret = []
        for grpid in self.__config__["groups"]:
            grpinfo = self.__config__["groups"][grpid]
            if tpfilter == '':
                ret.append(grpinfo)
            elif grpinfo["gtype"] == tpfilter:
                ret.append(grpinfo)
        
        return ret

    def has_group(self, grpid:str):
        return (grpid in self.__config__["groups"])

    def get_group(self, grpid:str):
        if grpid in self.__config__["groups"]:
            return self.__config__["groups"][grpid]
        else:
            return None

    def get_group_cfg(self, grpid:str):
        if grpid not in self.__config__["groups"]:
            return "{}"
        else:
            grpInfo = self.__config__["groups"][grpid]
            filepath = "./config.json"
            filepath = os.path.join(grpInfo["path"], filepath)
            f = open(filepath, "r")
            content = f.read()
            f.close()
            return json.loads(content)

    def set_group_cfg(self, grpid:str, config:dict):
        if grpid not in self.__config__["groups"]:
            return False
        else:
            grpInfo = self.__config__["groups"][grpid]
            filepath = "./config.json"
            filepath = os.path.join(grpInfo["path"], filepath)
            f = open(filepath, "w")
            f.write(json.dumps(config, indent=4))
            f.close()
            return True

    def add_group(self, grpInfo:dict):
        grpid = grpInfo["id"]
        isNewGrp = not (grpid in self.__config__["groups"])

        bSucc = False
        try:
            cur = self.__db_conn__.cursor()
            sql = ''
            if isNewGrp:
                sql = "INSERT INTO groups(groupid,name,path,info,gtype,datmod,env) VALUES('%s','%s','%s','%s','%s','%s','%s');" % (grpid, grpInfo["name"], grpInfo["path"], grpInfo["info"], grpInfo["gtype"], grpInfo["datmod"], grpInfo["env"])
            else:
                sql = "UPDATE groups SET name='%s',path='%s',info='%s',gtype='%s',datmod='%s',env='%s',modifytime=datetime('now','localtime') WHERE groupid='%s';" % (grpInfo["name"], grpInfo["path"], grpInfo["info"], grpInfo["gtype"], grpInfo["datmod"], grpInfo["env"], grpid)
            cur.execute(sql)
            self.__db_conn__.commit()
            bSucc = True
        except sqlite3.Error as e:
            print(e)

        if bSucc:
            self.__config__["groups"][grpid] = grpInfo

        return bSucc

    def del_group(self, grpid:str):
        if grpid in self.__config__["groups"]:
            self.__config__["groups"].pop(grpid)
            
            cur = self.__db_conn__.cursor()
            cur.execute("DELETE FROM groups WHERE groupid='%s';" % (grpid))
            self.__db_conn__.commit()

    def get_users(self):
        ret = []
        for loginid in self.__config__["users"]:
            usrInfo = self.__config__["users"][loginid]
            ret.append(usrInfo.copy())                
        
        return ret

    def add_user(self, usrInfo, admin):
        loginid = usrInfo["loginid"]
        isNewUser = not (loginid in self.__config__["users"])

        cur = self.__db_conn__.cursor()
        now = datetime.datetime.now()
        if isNewUser:
            encpwd = hashlib.md5((loginid+usrInfo["passwd"]).encode("utf-8")).hexdigest()
            usrInfo["passwd"] = encpwd
            usrInfo["createby"] = admin
            usrInfo["modifyby"] = admin
            usrInfo["createtime"] = now.strftime("%Y-%m-%d %H:%M:%S")
            usrInfo["modifytime"] = now.strftime("%Y-%m-%d %H:%M:%S")
            cur.execute("INSERT INTO users(loginid,name,role,passwd,iplist,remark,createby,modifyby) VALUES(?,?,?,?,?,?,?,?);", 
                (loginid, usrInfo["name"], usrInfo["role"], encpwd, usrInfo["iplist"], usrInfo["remark"], admin, admin))
        else:
            usrInfo["modifyby"] = admin
            usrInfo["modifytime"] = now.strftime("%Y-%m-%d %H:%M:%S")
            cur.execute("UPDATE users SET name=?,role=?,iplist=?,remark=?,modifyby=?,modifytime=datetime('now','localtime') WHERE loginid=?;", 
                (usrInfo["name"], usrInfo["role"], usrInfo["iplist"], usrInfo["remark"], admin, loginid))
        self.__db_conn__.commit()

        self.__config__["users"][loginid] = usrInfo


    def del_user(self, loginid, admin):
        if loginid in self.__config__["users"]:
            self.__config__["users"].pop(loginid)
            
            cur = self.__db_conn__.cursor()
            cur.execute("DELETE FROM users WHERE loginid='%s';" % (loginid))
            self.__db_conn__.commit()
            return True
        else:
            return False

    def log_action(self, adminInfo, atype, remark):
        cur = self.__db_conn__.cursor()
        sql = "INSERT INTO actions(loginid,actiontime,actionip,actiontype,remark) VALUES('%s',datetime('now','localtime'),'%s','%s','%s');" % (
                adminInfo["loginid"], adminInfo["loginip"], atype, remark)
        cur.execute(sql)
        self.__db_conn__.commit()

    def get_user(self, loginid:str):
        if loginid in self.__config__["users"]:
            return self.__config__["users"][loginid].copy()
        elif loginid == 'superman':
            return {
                "loginid":loginid,
                "name":"超管",
                "role":"superman",
                "passwd":"25ed305a56504e95fd1ca9900a1da174",
                "iplist":"",
                "remark":"内置超管账号"
            }
        else:
            return None

    def get_strategies(self, grpid:str):
        if grpid not in self.__config__["groups"]:
            return []

        grpInfo = self.__config__["groups"][grpid]
        self.__check_cache__(grpid, grpInfo)
        
        return self.__grp_cache__[grpid]["strategies"]

    def get_channels(self, grpid:str):
        if grpid not in self.__config__["groups"]:
            return []

        grpInfo = self.__config__["groups"][grpid]
        self.__check_cache__(grpid, grpInfo)
        
        return self.__grp_cache__[grpid]["channels"]

    def get_trades(self, grpid:str, straid:str, limit:int = 200):
        if grpid not in self.__config__["groups"]:
            return []

        grpInfo = self.__config__["groups"][grpid]
        self.__check_cache__(grpid, grpInfo)
            
        if straid not in self.__grp_cache__[grpid]["strategies"]:
            return []

        if "trades" not in self.__grp_cache__[grpid]:
            self.__grp_cache__[grpid]["trades"] = dict()
        
        if straid not in self.__grp_cache__[grpid]["trades"]:
            filepath = "./generated/outputs/%s/trades.csv" % (straid)
            filepath = os.path.join(grpInfo["path"], filepath)
            if not os.path.exists(filepath):
                return []
            else:
                trdCache = dict()
                f = open(filepath, "r")
                trdCache["file"] = f
                trdCache["trades"] = list()
                self.__grp_cache__[grpid]["trades"][straid] = trdCache

        trdCache = self.__grp_cache__[grpid]["trades"][straid]
        lines = trdCache["file"].readlines()
        if len(trdCache["trades"]) == 0:
            lines = lines[1:]

        for line in lines:
            cells = line.split(",")
            if len(cells) > 10:
                continue

            tItem = {
                "strategy":straid,
                "code": cells[0],
                "time": int(cells[1]),
                "direction": cells[2],
                "offset": cells[3],
                "price": float(cells[4]),
                "volumn": float(cells[5]),
                "tag": cells[6],
                "fee": 0
            }

            if len(cells) > 7:
                tItem["fee"] = float(cells[7])

            trdCache["trades"].append(tItem)
        
        return trdCache["trades"][-limit:]

    def get_funds(self, grpid:str, straid:str):
        if grpid not in self.__config__["groups"]:
            return []

        grpInfo = self.__config__["groups"][grpid]
        self.__check_cache__(grpid, grpInfo)
            
        if straid not in self.__grp_cache__[grpid]["strategies"]:
            return []

        if "funds" not in self.__grp_cache__[grpid]:
            self.__grp_cache__[grpid]["funds"] = dict()
        
        if straid not in self.__grp_cache__[grpid]["funds"]:
            filepath = "./generated/outputs/%s/funds.csv" % (straid)
            filepath = os.path.join(grpInfo["path"], filepath)
            if not os.path.exists(filepath):
                return []
            else:
                trdCache = dict()
                f = open(filepath, "r")
                trdCache["file"] = f
                trdCache["funds"] = list()
                self.__grp_cache__[grpid]["funds"][straid] = trdCache

        trdCache = self.__grp_cache__[grpid]["funds"][straid]
        lines = trdCache["file"].readlines()
        if len(trdCache["funds"]) == 0:
            lines = lines[1:]

        for line in lines:
            cells = line.split(",")
            if len(cells) > 10:
                continue

            tItem = {
                "strategy":straid,
                "date": int(cells[0]),
                "closeprofit": float(cells[1]),
                "dynprofit": float(cells[2]),
                "dynbalance": float(cells[3]),
                "fee": 0
            }

            if len(cells) > 4:
                tItem["fee"] = float(cells[4])

            trdCache["funds"].append(tItem)
        
        return trdCache["funds"]

    def get_signals(self, grpid:str, straid:str, limit:int = 200):
        if grpid not in self.__config__["groups"]:
            return []

        grpInfo = self.__config__["groups"][grpid]
        self.__check_cache__(grpid, grpInfo)
            
        if straid not in self.__grp_cache__[grpid]["strategies"]:
            return []

        if "signals" not in self.__grp_cache__[grpid]:
            self.__grp_cache__[grpid]["signals"] = dict()
        
        if straid not in self.__grp_cache__[grpid]["signals"]:
            filepath = "./generated/outputs/%s/signals.csv" % (straid)
            filepath = os.path.join(grpInfo["path"], filepath)
            if not os.path.exists(filepath):
                return []
            else:
                trdCache = dict()
                f = open(filepath, "r")
                trdCache["file"] = f
                trdCache["signals"] = list()
                self.__grp_cache__[grpid]["signals"][straid] = trdCache

        trdCache = self.__grp_cache__[grpid]["signals"][straid]
        lines = trdCache["file"].readlines()
        if len(trdCache["signals"]) == 0:
            lines = lines[1:]

        for line in lines:
            cells = line.split(",")

            tItem = {
                "strategy":straid,
                "code": cells[0],
                "target": float(cells[1]),
                "sigprice": float(cells[2]),
                "gentime": cells[3],
                "tag": cells[4]
            }

            trdCache["signals"].append(tItem)
        
        return trdCache["signals"][-limit:]

    def get_rounds(self, grpid:str, straid:str, limit:int = 200):
        if grpid not in self.__config__["groups"]:
            return []

        grpInfo = self.__config__["groups"][grpid]
        self.__check_cache__(grpid, grpInfo)
            
        if straid not in self.__grp_cache__[grpid]["strategies"]:
            return []

        if "rounds" not in self.__grp_cache__[grpid]:
            self.__grp_cache__[grpid]["rounds"] = dict()
        
        if straid not in self.__grp_cache__[grpid]["rounds"]:
            filepath = "./generated/outputs/%s/closes.csv" % (straid)
            filepath = os.path.join(grpInfo["path"], filepath)
            if not os.path.exists(filepath):
                return []
            else:
                trdCache = dict()
                f = open(filepath, "r")
                trdCache["file"] = f
                trdCache["rounds"] = list()
                self.__grp_cache__[grpid]["rounds"][straid] = trdCache

        trdCache = self.__grp_cache__[grpid]["rounds"][straid]
        lines = trdCache["file"].readlines()
        if len(trdCache["rounds"]) == 0:
            lines = lines[1:]

        for line in lines:
            cells = line.split(",")

            tItem = {
                "strategy":straid,
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

            trdCache["rounds"].append(tItem)
        
        return trdCache["rounds"][-limit:]

    def get_positions(self, grpid:str, straid:str):
        if grpid not in self.__config__["groups"]:
            return []

        grpInfo = self.__config__["groups"][grpid]
        self.__check_cache__(grpid, grpInfo)
            
        ret = list()
        if straid != "all":
            if straid not in self.__grp_cache__[grpid]["strategies"]:
                return []
            
            filepath = "./generated/stradata/%s.json" % (straid)
            filepath = os.path.join(grpInfo["path"], filepath)
            if not os.path.exists(filepath):
                return []
            
            f = open(filepath, "r")
            try:
                content = f.read()
                json_data = json.loads(content)

                positions = json_data["positions"]
                for pItem in positions:
                    if pItem["volumn"] == 0.0:
                        continue

                    for dItem in pItem["details"]:
                        dItem["code"] = pItem["code"]
                        dItem["strategy"] = straid
                        ret.append(dItem)
            except:
                pass

            f.close()
        else:
            for straid in self.__grp_cache__[grpid]["strategies"]:
                filepath = "./generated/stradata/%s.json" % (straid)
                filepath = os.path.join(grpInfo["path"], filepath)
                if not os.path.exists(filepath):
                    return []
                
                f = open(filepath, "r")
                try:
                    content = f.read()
                    json_data = json.loads(content)

                    positions = json_data["positions"]
                    for pItem in positions:
                        if pItem["volumn"] == 0.0:
                            continue

                        for dItem in pItem["details"]:
                            dItem["code"] = pItem["code"]
                            dItem["strategy"] = straid
                            ret.append(dItem)
                except:
                    pass

                f.close()
        return ret

    def get_channel_orders(self, grpid:str, chnlid:str, limit:int = 200):
        if grpid not in self.__config__["groups"]:
            return []

        grpInfo = self.__config__["groups"][grpid]
        self.__check_cache__(grpid, grpInfo)
            
        if chnlid not in self.__grp_cache__[grpid]["channels"]:
            return []

        if "corders" not in self.__grp_cache__[grpid]:
            self.__grp_cache__[grpid]["corders"] = dict()
        
        if chnlid not in self.__grp_cache__[grpid]["corders"]:
            filepath = "./generated/traders/%s/orders.csv" % (chnlid)
            filepath = os.path.join(grpInfo["path"], filepath)
            if not os.path.exists(filepath):
                return []
            else:
                trdCache = dict()
                f = open(filepath, "r")
                trdCache["file"] = f
                trdCache["corders"] = list()
                self.__grp_cache__[grpid]["corders"][chnlid] = trdCache

        trdCache = self.__grp_cache__[grpid]["corders"][chnlid]
        lines = trdCache["file"].readlines()
        if len(trdCache["corders"]) == 0:
            lines = lines[1:]

        for line in lines:
            cells = line.split(",")

            tItem = {
                "channel":chnlid,
                "localid":int(cells[0]),
                "time":int(cells[2]),
                "code": cells[3],
                "action": cells[4],
                "total": float(cells[5]),
                "traded": float(cells[6]),
                "price": float(cells[7]),
                "orderid": cells[8],
                "canceled": cells[9],
                "remark": cells[10]
            }

            trdCache["corders"].append(tItem)
        
        return trdCache["corders"][-limit:]

    def get_channel_trades(self, grpid:str, chnlid:str, limit:int = 200):
        if grpid not in self.__config__["groups"]:
            return []

        grpInfo = self.__config__["groups"][grpid]
        self.__check_cache__(grpid, grpInfo)
            
        if chnlid not in self.__grp_cache__[grpid]["channels"]:
            return []

        if "ctrades" not in self.__grp_cache__[grpid]:
            self.__grp_cache__[grpid]["ctrades"] = dict()
        
        if chnlid not in self.__grp_cache__[grpid]["ctrades"]:
            filepath = "./generated/traders/%s/trades.csv" % (chnlid)
            filepath = os.path.join(grpInfo["path"], filepath)
            if not os.path.exists(filepath):
                return []
            else:
                trdCache = dict()
                f = open(filepath, "r")
                trdCache["file"] = f
                trdCache["ctrades"] = list()
                self.__grp_cache__[grpid]["ctrades"][chnlid] = trdCache

        trdCache = self.__grp_cache__[grpid]["ctrades"][chnlid]
        lines = trdCache["file"].readlines()
        if len(trdCache["ctrades"]) == 0:
            lines = lines[1:]

        for line in lines:
            cells = line.split(",")

            tItem = {
                "channel":chnlid,
                "localid":int(cells[0]),
                "time":int(cells[2]),
                "code": cells[3],
                "action": cells[4],
                "volumn": float(cells[5]),
                "price": float(cells[6]),
                "tradeid": cells[7],
                "orderid": cells[8]
            }

            trdCache["ctrades"].append(tItem)
        
        return trdCache["ctrades"][-limit:]

    def get_channel_positions(self, grpid:str, chnlid:str):
        if self.__config__ is None:
            return []

        if "groups" not in self.__config__:
            return []

        if grpid not in self.__config__["groups"]:
            return []

        grpInfo = self.__config__["groups"][grpid]
        self.__check_cache__(grpid, grpInfo)
            
        ret = list()
        if chnlid not in self.__grp_cache__[grpid]["channels"]:
            return []
        
        filepath = "./generated/traders/%s/rtdata.json" % (chnlid)
        filepath = os.path.join(grpInfo["path"], filepath)
        if not os.path.exists(filepath):
            return []
        
        f = open(filepath, "r")
        try:
            content = f.read()
            json_data = json.loads(content)

            positions = json_data["positions"]
            for pItem in positions:
                pItem["channel"] = chnlid
                ret.append(pItem)
        except:
            pass

        f.close()
        return ret

    def get_actions(self, sdate, edate):
        ret = list()

        cur = self.__db_conn__.cursor()
        for row in cur.execute("SELECT id,loginid,actiontime,actionip,actiontype,remark FROM actions WHERE actiontime>=? and actiontime<=?;", (sdate, edate)):
            aInfo = dict()
            aInfo["id"] = row[0]
            aInfo["loginid"] = row[1]
            aInfo["actiontime"] = row[2]
            aInfo["actionip"] = row[3]
            aInfo["action"] = row[4]
            aInfo["remark"] = row[5]

            ret.append(aInfo)

        return ret
        


            

