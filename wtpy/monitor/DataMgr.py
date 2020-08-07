import json
import os

class DataMgr:

    def __init__(self, cfgfile:str="monitor.cfg"):
        self.__grp_cache__ = dict()

        self.__cfg_file__ = cfgfile
        try:
            f = open(cfgfile, "r")
            content =f.read()
            self.__config__ = json.loads(content)
            f.close()
        except:
            self.__config__ = None
            pass

    def __save_config__(self):
        if self.__config__ is None:
            self.__config__ = dict()

        f = open(self.__cfg_file__, "w")
        f.write(json.dumps(self.__config__, indent=4))
        f.close()

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
    
    def add_group(self, grpInfo:dict):
        if self.__config__ is None:
            self.__config__ = dict()

        if "groups" not in self.__config__:
            self.__config__["groups"] = dict()

        grpid = grpInfo["id"]
        self.__config__["groups"][grpid] = grpInfo

        self.__save_config__()

    def del_group(self, grpid:str):
        if self.__config__ is None:
            self.__config__ = dict()

        if "groups" not in self.__config__:
            self.__config__["groups"] = dict()

        if grpid in self.__config__["groups"]:
            self.__config__["groups"].pop(grpid)
            
        self.__save_config__()


    def has_group(self, grpid:str):
        if self.__config__ is None:
            return False

        if "groups" not in self.__config__:
            return False

        return (grpid in self.__config__["groups"])

    def get_group(self, grpid:str):
        if self.__config__ is None:
            return None

        if "groups" not in self.__config__:
            return None

        if grpid in self.__config__["groups"]:
            return self.__config__["groups"][grpid]
        else:
            return None

    def get_strategies(self, grpid:str):
        if self.__config__ is None:
            return []

        if "groups" not in self.__config__:
            return []

        if grpid not in self.__config__["groups"]:
            return []

        grpInfo = self.__config__["groups"][grpid]
        self.__check_cache__(grpid, grpInfo)
        
        return self.__grp_cache__[grpid]["strategies"]

    def get_channels(self, grpid:str):
        if self.__config__ is None:
            return []

        if "groups" not in self.__config__:
            return []

        if grpid not in self.__config__["groups"]:
            return []

        grpInfo = self.__config__["groups"][grpid]
        self.__check_cache__(grpid, grpInfo)
        
        return self.__grp_cache__[grpid]["channels"]


    def get_groups(self, tpfilter:str=''):
        if self.__config__ is None:
            return []

        if "groups" not in self.__config__:
            return []

        ret = []
        for grpid in self.__config__["groups"]:
            grpinfo = self.__config__["groups"][grpid]
            if tpfilter == '':
                ret.append(grpinfo)
            elif grpinfo["gtype"] == tpfilter:
                ret.append(grpinfo)
        
        return ret

    def get_trades(self, grpid:str, straid:str, limit:int = 200):
        if self.__config__ is None:
            return []

        if "groups" not in self.__config__:
            return []

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
        if self.__config__ is None:
            return []

        if "groups" not in self.__config__:
            return []

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
        if self.__config__ is None:
            return []

        if "groups" not in self.__config__:
            return []

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
        if self.__config__ is None:
            return []

        if "groups" not in self.__config__:
            return []

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
        if self.__config__ is None:
            return []

        if "groups" not in self.__config__:
            return []

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
        if self.__config__ is None:
            return []

        if "groups" not in self.__config__:
            return []

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
        if self.__config__ is None:
            return []

        if "groups" not in self.__config__:
            return []

        if grpid not in self.__config__["groups"]:
            return []

        grpInfo = self.__config__["groups"][grpid]
        self.__check_cache__(grpid, grpInfo)
            
        if chnlid not in self.__grp_cache__[grpid]["channels"]:
            return []

        if "ctrades" not in self.__grp_cache__[grpid]:
            self.__grp_cache__[grpid]["ctrades"] = dict()
        
        if chnlid not in self.__grp_cache__[grpid]["ctrades"]:
            filepath = "./generated/traders/%s/orders.csv" % (chnlid)
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
                "orderid": cells[8],
                "canceled": cells[9],
                "remark": cells[10]
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
        


            

