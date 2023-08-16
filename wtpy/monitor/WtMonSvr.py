from fastapi import FastAPI, Body, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse, FileResponse
import uvicorn

import json
import yaml
import datetime
import os
import hashlib
import sys
import chardet
import pytz
import base64

from .WtLogger import WtLogger
from .DataMgr import DataMgr, backup_file
from .PushSvr import PushServer
from .WatchDog import WatchDog, WatcherSink
from .WtBtMon import WtBtMon
from wtpy import WtDtServo
import signal
import platform

def isWindows():
    if "windows" in platform.system().lower():
        return True

    return False

def get_session(request: Request, key: str):
    if key not in request["session"]:
        return None
    return request["session"][key]

def set_session(request: Request, key: str, val):
    request["session"][key] = val

def pop_session(request: Request, key: str):
    if key not in request["session"]:
        return
    request["session"].pop(key)

def AES_Encrypt(key:str, data:str):
    from Crypto.Cipher import AES # pip install pycryptodome
    vi = '0102030405060708'
    pad = lambda s: s + (16 - len(s) % 16) * chr(16 - len(s) % 16)
    data = pad(data)
    # 字符串补位
    cipher = AES.new(key.encode('utf8'), AES.MODE_CBC, vi.encode('utf8'))
    encryptedbytes = cipher.encrypt(data.encode('utf8'))
    # 加密后得到的是bytes类型的数据
    encodestrs = base64.b64encode(encryptedbytes)
    # 使用Base64进行编码,返回byte字符串
    enctext = encodestrs.decode('utf8')
    # 对byte字符串按utf-8进行解码
    return enctext

def AES_Decrypt(key:str, data:str):
    from Crypto.Cipher import AES # pip install pycryptodome
    vi = '0102030405060708'
    data = data.encode('utf8')
    encodebytes = base64.decodebytes(data)
    # 将加密数据转换位bytes类型数据
    cipher = AES.new(key.encode('utf8'), AES.MODE_CBC, vi.encode('utf8'))
    text_decrypted = cipher.decrypt(encodebytes)
    unpad = lambda s: s[0:-s[-1]]
    text_decrypted = unpad(text_decrypted)
    # 去补位
    text_decrypted = text_decrypted.decode('utf8')
    return text_decrypted


# 获取文件最后N行的函数
def get_tail(filename, N: int = 100, encoding="GBK"):
    filesize = os.path.getsize(filename)
    blocksize = 10240
    dat_file = open(filename, 'r', encoding=encoding)
    last_line = ""
    if filesize > blocksize:
        maxseekpoint = (filesize // blocksize)
        dat_file.seek((maxseekpoint - 1) * blocksize)
    elif filesize:
        dat_file.seek(0, 0)
    lines = dat_file.readlines()
    if lines:
        last_line = lines[-N:]
    dat_file.close()
    return ''.join(last_line), len(last_line)


def check_auth(request: Request, token:str = None, seckey:str = None):
    if token is None:
        tokeninfo = get_session(request, "tokeninfo")
        # session里没有用户信息
        if tokeninfo is None:
            return False, {
                "result": -999,
                "message": "请先登录"
            }

        # session里有用户信息，则要读取
        exptime = tokeninfo["expiretime"]
        now = datetime.datetime.now().replace(tzinfo=pytz.timezone('UTC')).strftime("%Y.%m.%d %H:%M:%S")
        if now > exptime:
            return False, {
                "result": -999,
                "message": "登录已超时，请重新登录"
            }

        return True, tokeninfo
    else:
        tokeninfo = AES_Decrypt(seckey, token)
        # session里没有用户信息
        if tokeninfo is None:
            return False, {
                "result": -999,
                "message": "请先登录"
            }

        # session里有用户信息，则要读取
        exptime = tokeninfo["expiretime"]
        now = datetime.datetime.now().replace(tzinfo=pytz.timezone('UTC')).strftime("%Y.%m.%d %H:%M:%S")
        if now > exptime:
            return False, {
                "result": -999,
                "message": "登录已超时，请重新登录"
            }

        return True, tokeninfo

def get_cfg_tree(root: str, name: str):
    if not os.path.exists(root):
        return {
            "label": name,
            "path": root,
            "exist": False,
            "isfile": False,
            "children": []
        }

    if os.path.isfile(root):
        return {
            "label": name,
            "path": root,
            "exist": False,
            "isfile": True
        }

    ret = {
        "label": name,
        "path": root,
        "exist": True,
        "isfile": False,
        "children": []
    }

    filepath = os.path.join(root, "run.py")
    ret['children'].append({
        "label": "run.py",
        "path": filepath,
        "exist": True,
        "isfile": True,
        "children": []
    })

    filepath = os.path.join(root, "config.json")
    isYaml = False
    if not os.path.exists(filepath):
        filepath = os.path.join(root, "config.yaml")
        isYaml = True

    ret['children'].append({
        "label": "config.yaml" if isYaml else "config.json",
        "path": filepath,
        "exist": True,
        "isfile": True,
        "children": []
    })

    f = open(filepath, "rb")
    content = f.read()
    f.close()

    # 加一段编码检查的逻辑
    encoding = chardet.detect(content[:500])["encoding"]
    content = content.decode(encoding)

    if isYaml:
        cfgObj = yaml.full_load(content)
    else:
        cfgObj = json.loads(content)

    if "executers" in cfgObj:
        filename = cfgObj["executers"]
        if type(filename) == str:
            filepath = os.path.join(root, filename)
            ret['children'].append({
                "label": filename,
                "path": filepath,
                "exist": True,
                "isfile": True,
                "children": []
            })

    if "parsers" in cfgObj:
        filename = cfgObj["parsers"]
        if type(filename) == str:
            filepath = os.path.join(root, filename)
            ret['children'].append({
                "label": filename,
                "path": filepath,
                "exist": True,
                "isfile": True,
                "children": []
            })

    if "traders" in cfgObj:
        filename = cfgObj["traders"]
        if type(filename) == str:
            filepath = os.path.join(root, filename)
            ret['children'].append({
                "label": filename,
                "path": filepath,
                "exist": True,
                "isfile": True,
                "children": []
            })

    filepath = os.path.join(root, 'generated')
    ret["children"].append(get_path_tree(filepath, 'generated', True))

    return ret


def get_path_tree(root: str, name: str, hasFile: bool = True):
    if not os.path.exists(root):
        return {
            "label": name,
            "path": root,
            "exist": False,
            "isfile": False,
            "children": []
        }

    if os.path.isfile(root):
        return {
            "label": name,
            "path": root,
            "exist": False,
            "isfile": True
        }

    ret = {
        "label": name,
        "path": root,
        "exist": True,
        "isfile": False,
        "children": []
    }
    files = os.listdir(root, )
    for filename in files:
        if filename in ['__pycache__', '.vscode', 'wtpy', '__init__.py']:
            continue
        if filename[-3:] == 'pyc':
            continue

        filepath = os.path.join(root, filename)
        if os.path.isfile(filepath):
            if not hasFile:
                continue
            else:
                ret["children"].append({
                    "label": filename,
                    "path": filepath,
                    "exist": True,
                    "isfile": True})
        else:
            ret["children"].append(get_path_tree(filepath, filename, hasFile))

        ay1 = list()
        ay2 = list()
        for item in ret["children"]:
            if item["isfile"]:
                ay2.append(item)
            else:
                ay1.append(item)
        ay = ay1 + ay2
        ret["children"] = ay
    return ret


class WtMonSink:

    def __init__(self):
        return

    def notify(self, level: str, msg: str):
        return

from fastapi.middleware.cors import CORSMiddleware

class WtMonSvr(WatcherSink):

    def __init__(self, static_folder: str = "static/", deploy_dir="C:/", sink: WtMonSink = None, notifyTimeout:bool = True):
        '''
        WtMonSvr构造函数

        @static_folder      静态文件根目录
        @static_url_path    静态文件访问路径
        @deploy_dir         实盘部署目录
        '''

        self.logger = WtLogger(__name__, "WtMonSvr.log")
        self._sink_ = sink

        # 数据管理器，主要用于缓存各组合的数据
        self.__data_mgr__ = DataMgr('data.db', logger=self.logger)

        self.__bt_mon__: WtBtMon = None
        self.__dt_servo__: WtDtServo = None

        # 秘钥和开启token访问，单独控制，减少依赖项
        self.__sec_key__ = ""
        self.__token_enabled__ = False

        # 看门狗模块，主要用于调度各个组合启动关闭
        self._dog = WatchDog(sink=self, db=self.__data_mgr__.get_db(), logger=self.logger)

        app = FastAPI(title="WtMonSvr", description="A http api of WtMonSvr", redoc_url=None, version="1.0.0")
        app.add_middleware(GZipMiddleware, minimum_size=1000)
        app.add_middleware(SessionMiddleware, secret_key='!@#$%^&*()', max_age=25200, session_cookie='WtMonSvr_sid')
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"])

        script_dir = os.path.dirname(__file__)
        static_folder = os.path.join(script_dir, static_folder)
        target_dir = os.path.join(static_folder,"console")
        app.mount("/console", StaticFiles(directory=target_dir), name="console")

        target_dir = os.path.join(static_folder,"mobile")
        app.mount("/mobile", StaticFiles(directory=target_dir), name="mobile")

        self.app = app
        self.worker = None
        self.deploy_dir = deploy_dir
        self.deploy_tree = None
        self.static_folder = static_folder
        self.notifyTimeout = notifyTimeout

        self.push_svr = PushServer(app, self.__data_mgr__, self.logger)

        self.init_mgr_apis(app)
        self.init_comm_apis(app)

    def enable_token(self, seckey: str = "WtMonSvr@2021"):
        '''
        启用访问令牌, 默认通过session方式验证
        注意: 这里如果启用令牌访问的话, 需要安装pycryptodome, 所以改成单独控制
        '''
        
        self.__sec_key__ = seckey
        self.__token_enabled__ = True

    def set_bt_mon(self, btMon: WtBtMon):
        '''
        设置回测管理器

        @btMon      回测管理器WtBtMon实例
        '''
        self.__bt_mon__ = btMon
        self.init_bt_apis(self.app)

    def set_dt_servo(self, dtServo: WtDtServo):
        '''
        设置DtServo

        @dtServo    本地数据伺服WtDtServo实例
        '''
        self.__dt_servo__ = dtServo

    def init_bt_apis(self, app: FastAPI):

        # 拉取K线数据
        @app.post("/bt/qrybars", tags=["回测管理接口"])
        async def qry_bt_bars(
            request: Request,
            token: str = Body(None, title="访问令牌", embed=True),
            code: str = Body(..., title="合约代码", embed=True),
            period: str = Body(..., title="K线周期", embed=True),
            stime: int = Body(None, title="开始时间", embed=True),
            etime: int = Body(..., title="结束时间", embed=True),
            count: int = Body(None, title="数据条数", embed=True)
        ):
            bSucc, userInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return userInfo

            user = userInfo["loginid"]
            role = userInfo["role"]
            if role not in ['researcher', 'superman']:
                ret = {
                    "result": -1,
                    "message": "没有权限"
                }
                return ret

            if self.__dt_servo__ is None:
                ret = {
                    "result": -2,
                    "message": "没有配置数据伺服"
                }
                return ret

            stdCode = code
            fromTime = stime
            dataCount = count
            endTime = etime

            bars = self.__dt_servo__.get_bars(stdCode=stdCode, period=period, fromTime=fromTime, dataCount=dataCount,
                                              endTime=endTime)
            if bars is None:
                ret = {
                    "result": -2,
                    "message": "Data not found"
                }
            else:
                bar_list = [curBar.to_dict for curBar in bars]

                ret = {
                    "result": 0,
                    "message": "Ok",
                    "bars": bar_list
                }

            return ret

        # 拉取用户策略列表
        @app.post("/bt/qrystras", tags=["回测管理接口"])
        @app.get("/bt/qrystras", tags=["回测管理接口"])
        async def qry_my_stras(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True)
        ):
            bSucc, userInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return userInfo

            user = userInfo["loginid"]
            role = userInfo["role"]
            if role not in ['researcher', 'superman']:
                ret = {
                    "result": -1,
                    "message": "没有权限"
                }
                return ret

            ret = {
                "result": 0,
                "message": "OK",
                "strategies": self.__bt_mon__.get_strategies(user)
            }

            return ret

        # 拉取策略代码
        @app.post("/bt/qrycode", tags=["回测管理接口"])
        async def qry_stra_code(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                straid: str = Body(..., title="策略ID", embed=True)
        ):
            bSucc, userInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return userInfo

            user = userInfo["loginid"]
            role = userInfo["role"]
            if role not in ['researcher', 'superman']:
                ret = {
                    "result": -1,
                    "message": "没有权限"
                }
                return ret

            if self.__bt_mon__ is None:
                ret = {
                    "result": -1,
                    "message": "回测管理器未配置"
                }
            else:
                if not self.__bt_mon__.has_strategy(user, straid):
                    ret = {
                        "result": -2,
                        "message": "策略代码不存在"
                    }
                else:
                    content = self.__bt_mon__.get_strategy_code(user, straid)
                    ret = {
                        "result": 0,
                        "message": "OK",
                        "content": content
                    }

            return ret

        # 提交策略代码
        @app.post("/bt/setcode", tags=["回测管理接口"])
        def set_stra_code(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                straid: str = Body(..., title="策略ID", embed=True),
                content: str = Body(..., title="策略代码", embed=True)
        ):
            bSucc, userInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return userInfo

            user = userInfo["loginid"]
            role = userInfo["role"]
            if role not in ['researcher', 'superman']:
                ret = {
                    "result": -1,
                    "message": "没有权限"
                }
                return ret

            if len(content) == 0 or len(straid) == 0:
                ret = {
                    "result": -2,
                    "message": "策略ID和代码不能为空"
                }
                return ret

            if self.__bt_mon__ is None:
                ret = {
                    "result": -1,
                    "message": "回测管理器未配置"
                }
            else:
                if not self.__bt_mon__.has_strategy(user, straid):
                    ret = {
                        "result": -2,
                        "message": "策略不存在"
                    }
                else:
                    ret = self.__bt_mon__.set_strategy_code(user, straid, content)
                    if ret:
                        ret = {
                            "result": 0,
                            "message": "OK"
                        }
                    else:
                        ret = {
                            "result": -3,
                            "message": "保存策略代码失败"
                        }

            return ret

        # 添加用户策略
        @app.post("/bt/addstra", tags=["回测管理接口"])
        async def cmd_add_stra(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                name: str = Body(..., title="策略名称", embed=True)
        ):
            bSucc, userInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return userInfo

            user = userInfo["loginid"]
            role = userInfo["role"]
            if role not in ['researcher', 'superman']:
                ret = {
                    "result": -1,
                    "message": "没有权限"
                }
                return ret

            if len(name) == 0:
                ret = {
                    "result": -2,
                    "message": "策略名称不能为空"
                }
                return ret

            if self.__bt_mon__ is None:
                ret = {
                    "result": -3,
                    "message": "回测管理器未配置"
                }
                return ret

            straInfo = self.__bt_mon__.add_strategy(user, name)
            if straInfo is None:
                ret = {
                    "result": -4,
                    "message": "策略添加失败"
                }
            else:
                ret = {
                    "result": 0,
                    "message": "OK",
                    "strategy": straInfo
                }

            return ret

        # 删除用户策略
        @app.post("/bt/delstra", tags=["回测管理接口"])
        async def cmd_del_stra(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                straid: str = Body(..., title="策略ID", embed=True)
        ):
            bSucc, userInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return userInfo

            user = userInfo["loginid"]
            role = userInfo["role"]
            if role not in ['researcher', 'superman']:
                ret = {
                    "result": -1,
                    "message": "没有权限"
                }
                return ret

            if len(straid) == 0:
                ret = {
                    "result": -2,
                    "message": "策略ID不能为空"
                }
                return ret

            if self.__bt_mon__ is None:
                ret = {
                    "result": -1,
                    "message": "回测管理器未配置"
                }
            else:
                if not self.__bt_mon__.has_strategy(user, straid):
                    ret = {
                        "result": -2,
                        "message": "策略不存在"
                    }
                else:
                    ret = self.__bt_mon__.del_strategy(user, straid)
                    if ret:
                        ret = {
                            "result": 0,
                            "message": "OK"
                        }
                    else:
                        ret = {
                            "result": -3,
                            "message": "保存策略代码失败"
                        }

            return ret

        # 获取策略回测列表
        @app.post("/bt/qrystrabts", tags=["回测管理接口"])
        async def qry_stra_bts(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                straid: str = Body(..., title="策略ID", embed=True),
        ):
            bSucc, userInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return userInfo

            user = userInfo["loginid"]
            role = userInfo["role"]
            if role not in ['researcher', 'superman']:
                ret = {
                    "result": -1,
                    "message": "没有权限"
                }
                return ret

            if len(straid) == 0:
                ret = {
                    "result": -2,
                    "message": "策略ID不能为空"
                }
                return ret

            if self.__bt_mon__ is None:
                ret = {
                    "result": -1,
                    "message": "回测管理器未配置"
                }
            else:
                if not self.__bt_mon__.has_strategy(user, straid):
                    ret = {
                        "result": -2,
                        "message": "策略不存在"
                    }
                else:
                    ret = {
                        "result": 0,
                        "message": "OK",
                        "backtests": self.__bt_mon__.get_backtests(user, straid)
                    }

            return ret

        # 获取策略回测信号
        @app.post("/bt/qrybtsigs", tags=["回测管理接口"])
        async def qry_stra_bt_signals(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                straid: str = Body(..., title="策略ID", embed=True),
                btid: str = Body(..., title="回测ID", embed=True)
        ):
            bSucc, userInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return userInfo

            user = userInfo["loginid"]
            role = userInfo["role"]
            if role not in ['researcher', 'superman']:
                ret = {
                    "result": -1,
                    "message": "没有权限"
                }
                return ret

            if len(straid) == 0 or len(btid) == 0:
                ret = {
                    "result": -2,
                    "message": "策略ID和回测ID不能为空"
                }
                return ret

            if self.__bt_mon__ is None:
                ret = {
                    "result": -1,
                    "message": "回测管理器未配置"
                }
            else:
                if not self.__bt_mon__.has_strategy(user, straid):
                    ret = {
                        "result": -2,
                        "message": "策略不存在"
                    }
                else:
                    ret = {
                        "result": 0,
                        "message": "OK",
                        "signals": self.__bt_mon__.get_bt_signals(user, straid, btid)
                    }

            return ret

        # 删除策略回测列表
        @app.post("/bt/delstrabt", tags=["回测管理接口"])
        async def cmd_del_stra_bt(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                btid: str = Body(..., title="回测ID", embed=True)
        ):
            bSucc, userInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return userInfo

            user = userInfo["loginid"]
            role = userInfo["role"]
            if role not in ['researcher', 'superman']:
                ret = {
                    "result": -1,
                    "message": "没有权限"
                }
                return ret

            if len(btid) == 0:
                ret = {
                    "result": -2,
                    "message": "回测ID不能为空"
                }
                return ret

            if self.__bt_mon__ is None:
                ret = {
                    "result": -1,
                    "message": "回测管理器未配置"
                }
            else:
                self.__bt_mon__.del_backtest(user, btid)
                ret = {
                    "result": 0,
                    "message": "OK"
                }

            return ret

        # 获取策略回测成交
        @app.post("/bt/qrybttrds", tags=["回测管理接口"])
        async def qry_stra_bt_trades(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                straid: str = Body(..., title="策略ID", embed=True),
                btid: str = Body(..., title="回测ID", embed=True)
        ):
            bSucc, userInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return userInfo

            user = userInfo["loginid"]
            role = userInfo["role"]
            if role not in ['researcher', 'superman']:
                ret = {
                    "result": -1,
                    "message": "没有权限"
                }
                return ret

            if len(straid) == 0 or len(btid) == 0:
                ret = {
                    "result": -2,
                    "message": "策略ID和回测ID不能为空"
                }
                return ret

            if self.__bt_mon__ is None:
                ret = {
                    "result": -1,
                    "message": "回测管理器未配置"
                }
            else:
                if not self.__bt_mon__.has_strategy(user, straid):
                    ret = {
                        "result": -2,
                        "message": "策略不存在"
                    }
                else:
                    ret = {
                        "result": 0,
                        "message": "OK",
                        "trades": self.__bt_mon__.get_bt_trades(user, straid, btid)
                    }

            return ret

        # 获取策略回测资金
        @app.post("/bt/qrybtfunds", tags=["回测管理接口"])
        async def qry_stra_bt_funds(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                straid: str = Body(..., title="策略ID", embed=True),
                btid: str = Body(..., title="回测ID", embed=True)
        ):
            bSucc, userInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return userInfo

            user = userInfo["loginid"]
            role = userInfo["role"]
            if role not in ['researcher', 'superman']:
                ret = {
                    "result": -1,
                    "message": "没有权限"
                }
                return ret

            if len(straid) == 0 or len(btid) == 0:
                ret = {
                    "result": -2,
                    "message": "策略ID和回测ID不能为空"
                }
                return ret

            if self.__bt_mon__ is None:
                ret = {
                    "result": -1,
                    "message": "回测管理器未配置"
                }
            else:
                if not self.__bt_mon__.has_strategy(user, straid):
                    ret = {
                        "result": -2,
                        "message": "策略不存在"
                    }
                else:
                    ret = {
                        "result": 0,
                        "message": "OK",
                        "funds": self.__bt_mon__.get_bt_funds(user, straid, btid)
                    }

            return ret

        # 获取策略回测回合
        @app.post("/bt/qrybtrnds", tags=["回测管理接口"])
        async def qry_stra_bt_rounds(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                straid: str = Body(..., title="策略ID", embed=True),
                btid: str = Body(..., title="回测ID", embed=True)
        ):
            bSucc, userInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return userInfo

            user = userInfo["loginid"]
            role = userInfo["role"]
            if role not in ['researcher', 'superman']:
                ret = {
                    "result": -1,
                    "message": "没有权限"
                }
                return ret

            if len(straid) == 0 or len(btid) == 0:
                ret = {
                    "result": -2,
                    "message": "策略ID和回测ID不能为空"
                }
                return ret

            if self.__bt_mon__ is None:
                ret = {
                    "result": -1,
                    "message": "回测管理器未配置"
                }
            else:
                if not self.__bt_mon__.has_strategy(user, straid):
                    ret = {
                        "result": -2,
                        "message": "策略不存在"
                    }
                else:
                    ret = {
                        "result": 0,
                        "message": "OK",
                        "rounds": self.__bt_mon__.get_bt_rounds(user, straid, btid)
                    }

            return ret

        # 启动策略回测
        @app.post("/bt/runstrabt", tags=["回测管理接口"])
        def cmd_run_stra_bt(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                straid: str = Body(..., title="策略ID", embed=True),
                stime: int = Body(None, title="开始时间", embed=True),
                etime: int = Body(None, title="结束时间", embed=True),
                capital: int = Body(500000, title="本金", embed=True),
                slippage: int = Body(0, title="滑点", embed=True)
        ):
            bSucc, userInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return userInfo

            user = userInfo["loginid"]
            role = userInfo["role"]
            if role not in ['researcher', 'superman']:
                ret = {
                    "result": -1,
                    "message": "没有权限"
                }
                return ret

            curDt = int(datetime.datetime.now().strftime("%Y%m%d"))
            fromtime = stime
            endtime = etime

            if len(straid) == 0:
                ret = {
                    "result": -2,
                    "message": "策略ID不能为空"
                }
                return ret

            if fromtime > endtime:
                fromtime, endtime = endtime, fromtime

            fromtime = fromtime * 10000 + 900
            endtime = endtime * 10000 + 1515

            if self.__bt_mon__ is None:
                ret = {
                    "result": -1,
                    "message": "回测管理器未配置"
                }
            else:
                if not self.__bt_mon__.has_strategy(user, straid):
                    ret = {
                        "result": -2,
                        "message": "策略不存在"
                    }
                else:
                    btInfo = self.__bt_mon__.run_backtest(user, straid, fromtime, endtime, capital, slippage)
                    ret = {
                        "result": 0,
                        "message": "OK",
                        "backtest": btInfo
                    }

            return ret

    def init_mgr_apis(self, app: FastAPI):

        '''下面是API接口的编写'''

        @app.post("/mgr/login", tags=["用户接口"])
        async def cmd_login(
            request: Request,
            loginid: str = Body(..., title="用户名", embed=True),
            passwd: str = Body(..., title="用户密码", embed=True)
        ):
            if True:
                user = loginid
                pwd = passwd

                if len(user) == 0 or len(pwd) == 0:
                    ret = {
                        "result": -1,
                        "message": "用户名和密码不能为空"
                    }
                else:
                    encpwd = hashlib.md5((user + pwd).encode("utf-8")).hexdigest()
                    now = datetime.datetime.now()
                    usrInf = self.__data_mgr__.get_user(user)
                    if usrInf is None or encpwd != usrInf["passwd"]:
                        ret = {
                            "result": -1,
                            "message": "用户名或密码错误"
                        }
                    else:
                        usrInf.pop("passwd")
                        usrInf["loginip"] = request.client.host
                        usrInf["logintime"] = now.strftime("%Y/%m/%d %H:%M:%S")
                        products = usrInf["products"]

                        exptime = now + datetime.timedelta(minutes=360)  # 360分钟令牌超时
                        tokenInfo = {
                            "loginid": user,
                            "role": usrInf["role"],
                            "logintime": now.strftime("%Y/%m/%d %H:%M:%S"),
                            "expiretime": exptime.replace(tzinfo=pytz.timezone('UTC')).strftime("%Y.%m.%d %H:%M:%S"),
                            "products": products,
                            "loginip": request.client.host
                        }
                        set_session(request, "tokeninfo", tokenInfo)

                        if self.__token_enabled__:
                            token = AES_Encrypt(self.__sec_key__, json.dumps(tokenInfo))
                            ret = {
                                "result": 0,
                                "message": "Ok",
                                "userinfo": usrInf,
                                "token": token
                            }
                        else:
                            ret = {
                                "result": 0,
                                "message": "Ok",
                                "userinfo": usrInf
                            }

                        self.__data_mgr__.log_action(usrInf, "login", json.dumps(request.headers.get('User-Agent')))
            else:
                ret = {
                    "result": -1,
                    "message": "请求处理出现异常",
                }
                if get_session(request, "userinfo") is not None:
                    pop_session("userinfo")

            return ret

        # 修改密码
        # 修改密码
        @app.post("/mgr/modpwd", tags=["用户接口"])
        async def mod_pwd(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                oldpwd: str = Body(..., title="旧密码", embed=True),
                newpwd: str = Body(..., title="新密码", embed=True)
        ):
            bSucc, adminInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return adminInfo

            if len(oldpwd) == 0 or len(newpwd) == 0:
                ret = {
                    "result": -1,
                    "message": "新旧密码都不能为空"
                }
            else:
                user = adminInfo["loginid"]
                oldencpwd = hashlib.md5((user + oldpwd).encode("utf-8")).hexdigest()
                usrInf = self.__data_mgr__.get_user(user)
                if usrInf is None:
                    ret = {
                        "result": -1,
                        "message": "用户不存在"
                    }
                else:
                    if oldencpwd != usrInf["passwd"]:
                        ret = {
                            "result": -1,
                            "message": "旧密码错误"
                        }
                    else:
                        if 'builtin' in usrInf and usrInf["builtin"]:
                            # 如果是内建账号要改密码，则先添加用户
                            usrInf["passwd"] = oldpwd
                            self.__data_mgr__.add_user(usrInf, user)
                            print("%s是内建账户，自动添加到数据库中" % user)

                        newencpwd = hashlib.md5((user + newpwd).encode("utf-8")).hexdigest()
                        self.__data_mgr__.mod_user_pwd(user, newencpwd, user)

                        ret = {
                            "result": 0,
                            "message": "Ok"
                        }

            return ret

        # 添加组合
        @app.post("/mgr/addgrp", tags=["策略组管理接口"])
        async def cmd_add_group(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                groupid: str = Body(..., title="组合ID", embed=True),
                name: str = Body('', title="组合名称", embed=True),
                path: str = Body('', title="组合路径", embed=True),
                gtype: str = Body('', title="组合类型", embed=True),
                info: str = Body('', title="组合信息",embed=True),
                env: str = Body('', title="组合环境，实盘/回测", embed=True),
                datmod: str = Body('mannual', title="数据模式，mannal/auto", embed=True),
                mqurl: str = Body('', title="消息队列地址", embed=True),
                action: str = Body('add', title="操作类型，add/mod", embed=True)
        ):
            bSucc, adminInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return adminInfo

            id = groupid

            if action == "":
                action = "add"

            if len(id) == 0 or len(name) == 0 or len(gtype) == 0:
                ret = {
                    "result": -1,
                    "message": "组合ID、名称、类型都不能为空"
                }
            elif not os.path.exists(path) or not os.path.isdir(path):
                ret = {
                    "result": -2,
                    "message": "组合运行目录不正确"
                }
            elif action == "add" and self.__data_mgr__.has_group(id):
                ret = {
                    "result": -3,
                    "message": "组合ID不能重复"
                }
            else:
                try:
                    grpInfo = {
                        "id": id,
                        "name": name,
                        "path": path,
                        "info": info,
                        "gtype": gtype,
                        "datmod": datmod,
                        "env": env,
                        "mqurl": mqurl
                    }

                    if self.__data_mgr__.add_group(grpInfo):
                        ret = {
                            "result": 0,
                            "message": "Ok"
                        }

                        if action == "add":
                            self.__data_mgr__.log_action(adminInfo, "addgrp", json.dumps(grpInfo))
                        else:
                            self.__data_mgr__.log_action(adminInfo, "modgrp", json.dumps(grpInfo))

                        self._dog.updateMQURL(id, mqurl)
                    else:
                        ret = {
                            "result": -2,
                            "message": "添加用户失败"
                        }
                except:
                    ret = {
                        "result": -1,
                        "message": "请求解析失败"
                    }

            return ret

        # 删除组合
        @app.post("/mgr/delgrp", tags=["策略组管理接口"])
        async def cmd_del_group(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                groupid: str = Body(..., title="组合ID", embed=True)
        ):
            bSucc, adminInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return adminInfo

            id = groupid

            if len(id) == 0:
                ret = {
                    "result": -1,
                    "message": "组合ID不能为空"
                }
            elif not self.__data_mgr__.has_group(id):
                ret = {
                    "result": -3,
                    "message": "该组合不存在"
                }
            elif self._dog.isRunning(id):
                ret = {
                    "result": -3,
                    "message": "请先停止该组合"
                }
            else:
                if True:
                    self._dog.delApp(id)
                    self.__data_mgr__.del_group(id)
                    ret = {
                        "result": 0,
                        "message": "Ok"
                    }

                    self.__data_mgr__.log_action(adminInfo, "delgrp", id)
                else:
                    ret = {
                        "result": -1,
                        "message": "请求解析失败"
                    }

            return ret

        # 组合停止
        @app.post("/mgr/stopgrp", tags=["策略组管理接口"])
        async def cmd_stop_group(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                groupid: str = Body(..., title="组合ID", embed=True)
        ):
            bSucc, adminInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return adminInfo

            grpid = groupid

            if not self.__data_mgr__.has_group(grpid):
                ret = {
                    "result": -1,
                    "message": "组合不存在"
                }
            else:
                if self._dog.isRunning(grpid):
                    self._dog.stop(grpid)
                ret = {
                    "result": 0,
                    "message": "Ok"
                }

                self.__data_mgr__.log_action(adminInfo, "stopgrp", grpid)

            return ret

        # 组合启动
        @app.post("/mgr/startgrp", tags=["策略组管理接口"])
        async def cmd_start_group(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                groupid: str = Body(..., title="组合ID", embed=True)
        ):
            bSucc, adminInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return adminInfo

            grpid = groupid

            if not self.__data_mgr__.has_group(grpid):
                ret = {
                    "result": -1,
                    "message": "组合不存在"
                }
            else:
                if not self._dog.isRunning(grpid):
                    self._dog.start(grpid)
                ret = {
                    "result": 0,
                    "message": "Ok"
                }
                self.__data_mgr__.log_action(adminInfo, "startgrp", grpid)

            return ret

        # 获取执行的python进程的路径
        @app.post("/mgr/qryexec", tags=["通用接口"])
        def qry_exec_path(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True)
        ):
            bSucc, adminInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return adminInfo

            ret = {
                "result": 0,
                "message": "Ok",
                "path": sys.executable
            }
            return ret

        # 配置监控
        @app.post("/mgr/qrymon", tags=["调度器管理接口"])
        async def qry_mon_cfg(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                groupid: str = Body(..., title="组合ID", embed=True)
        ):
            bSucc, adminInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return adminInfo

            grpid = groupid

            if not self.__data_mgr__.has_group(grpid):
                ret = {
                    "result": -1,
                    "message": "组合不存在"
                }
            else:
                monCfg = self._dog.getAppConf(grpid)
                if monCfg is None:
                    ret = {
                        "result": 0,
                        "message": "ok"
                    }
                else:
                    ret = {
                        "result": 0,
                        "message": "ok",
                        "config": monCfg
                    }

            return ret

        # 配置监控
        @app.post("/mgr/cfgmon", tags=["调度器管理接口"])
        async def cmd_config_monitor(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                config: dict = Body(..., title="监控配置", embed=True)
        ):
            bSucc, adminInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return adminInfo

            # 这里本来是要做检查的，算了，先省事吧
            isGrp = False
            if "group" in config:
                isGrp = config["group"]

            self._dog.applyAppConf(config, isGrp)
            ret = {
                "result": 0,
                "message": "ok"
            }
            self.__data_mgr__.log_action(adminInfo, "cfgmon", json.dumps(config))

            return ret

        # 查询目录结构
        @app.post("/mgr/qrydir", tags=["通用接口"])
        async def qry_directories(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True)
        ):
            bSucc, usrInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return usrInfo

            if True:
                if self.deploy_tree is None:
                    self.deploy_tree = get_path_tree(self.deploy_dir, "root")

                ret = {
                    "result": 0,
                    "message": "Ok",
                    "tree": self.deploy_tree
                }
            else:
                ret = {
                    "result": -1,
                    "message": "请求解析失败"
                }

            return ret

        # 查询目录结构
        @app.post("/mgr/qrygrpdir", tags=["策略组管理接口"])
        async def qry_grp_directories(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                groupid: str = Body(..., title="组合ID", embed=True)
        ):
            bSucc, usrInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return usrInfo

            grpid = groupid

            if not self.__data_mgr__.has_group(grpid):
                ret = {
                    "result": -1,
                    "message": "组合不存在"
                }
            else:
                monCfg = self.__data_mgr__.get_group(grpid)

                ret = {
                    "result": 0,
                    "message": "Ok",
                    "tree": get_cfg_tree(monCfg["path"], "root")
                }

            return ret

        # 查询组合列表
        @app.post("/mgr/qrygrp", tags=["策略组管理接口"])
        @app.get("/mgr/qrygrp", tags=["策略组管理接口"])
        async def qry_groups(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True)
        ):
            bSucc, tokenInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return tokenInfo

            products = tokenInfo["products"]
            
            try:
                groups = self.__data_mgr__.get_groups()
                rets = list()
                for grpInfo in groups:
                    if len(products) == 0 or grpInfo["id"] in products:
                        grpInfo["running"] = self._dog.isRunning(grpInfo["id"])
                        rets.append(grpInfo)

                ret = {
                    "result": 0,
                    "message": "Ok",
                    "groups": rets
                }
            except:
                ret = {
                    "result": -1,
                    "message": "请求解析失败"
                }

            return ret

        # 查询文件信息
        @app.post("/mgr/qrygrpfile", tags=["策略组管理接口"])
        async def qry_group_file(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                groupid: str = Body(..., title="组合ID", embed=True),
                path: str = Body(..., title="文件路径", embed=True),
        ):
            bSucc, usrInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return usrInfo

            grpid = groupid

            if not self.__data_mgr__.has_group(grpid):
                ret = {
                    "result": -1,
                    "message": "组合不存在"
                }
            else:
                monCfg = self.__data_mgr__.get_group(grpid)
                root = monCfg["path"]
                if path[:len(root)] != root:
                    ret = {
                        "result": -1,
                        "message": "目标文件不在当前组合下"
                    }
                else:
                    f = open(path, 'rb')
                    content = f.read()
                    f.close()

                    encoding = chardet.detect(content)["encoding"]
                    content = content.decode(encoding)

                    ret = {
                        "result": 0,
                        "message": "Ok",
                        "content": content
                    }

            return ret

        # 提交组合文件
        @app.post("/mgr/cmtgrpfile", tags=["策略组管理接口"])
        async def cmd_commit_group_file(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                groupid: str = Body(..., title="组合ID", embed=True),
                path: str = Body(..., title="文件路径", embed=True),
                content: str = Body(..., title="文件内容", embed=True)
        ):
            bSucc, usrInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return usrInfo

            grpid = groupid

            if not self.__data_mgr__.has_group(grpid):
                ret = {
                    "result": -1,
                    "message": "组合不存在"
                }
            else:
                monCfg = self.__data_mgr__.get_group(grpid)
                root = monCfg["path"]
                if path[:len(root)] != root:
                    ret = {
                        "result": -1,
                        "message": "目标文件不在当前组合下"
                    }
                else:
                    try:
                        f = open(path, 'rb')
                        old_content = f.read()
                        f.close()
                        encoding = chardet.detect(old_content)["encoding"]

                        backup_file(path)

                        f = open(path, 'wb')
                        f.write(content.encode(encoding))
                        f.close()

                        ret = {
                            "result": 0,
                            "message": "Ok"
                        }
                    except:
                        ret = {
                            "result": -1,
                            "message": "文件保存失败"
                        }

            return ret

        # 查询策略列表
        @app.post("/mgr/qrystras", tags=["策略组管理接口"])
        async def qry_strategys(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                groupid: str = Body(..., title="组合ID", embed=True)
        ):
            bSucc, usrInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return usrInfo

            grpid = groupid

            if not self.__data_mgr__.has_group(grpid):
                ret = {
                    "result": -1,
                    "message": "组合不存在"
                }
            else:
                ret = {
                    "result": 0,
                    "message": "Ok",
                    "strategies": self.__data_mgr__.get_strategies(grpid)
                }

            return ret

        # 查询通道列表
        @app.post("/mgr/qrychnls", tags=["策略组管理接口"])
        async def qry_channels(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                groupid: str = Body(..., title="组合ID", embed=True)
        ):
            bSucc, usrInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return usrInfo

            grpid = groupid

            if not self.__data_mgr__.has_group(grpid):
                ret = {
                    "result": -1,
                    "message": "组合不存在"
                }
            else:
                ret = {
                    "result": 0,
                    "message": "Ok",
                    "channels": self.__data_mgr__.get_channels(grpid)
                }

            return ret

        # 查询组合日志
        @app.post("/mgr/qrylogs", tags=["策略组管理接口"])
        async def qry_logs(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                id: str = Body(..., title="组合ID", embed=True),
                type: str = Body(..., title="日志类型", embed=True),
        ):
            bSucc, usrInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return usrInfo

            grpid = id
            logtype = type

            if not self.__data_mgr__.has_group(grpid):
                ret = {
                    "result": -1,
                    "message": "组合不存在"
                }
            else:
                grpInfo = self.__data_mgr__.get_group(grpid)
                try:
                    logfolder = os.path.join(grpInfo["path"], "./Logs/")
                    file_list = os.listdir(logfolder)
                    targets = list()
                    for fname in file_list:
                        if fname[:6] == "Runner":
                            targets.append(fname)

                    targets.sort()
                    filename = os.path.join(logfolder, targets[-1])
                    content, lines = get_tail(filename, 100)
                    ret = {
                        "result": 0,
                        "message": "Ok",
                        "content": content,
                        "lines": lines
                    }
                except:
                    ret = {
                        "result": -1,
                        "message": "请求解析失败"
                    }

            return ret

        # 查询策略成交
        @app.post("/mgr/qrytrds", tags=["策略管理接口"])
        async def qry_trades(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                groupid: str = Body(..., title="组合ID", embed=True),
                strategyid: str = Body(..., title="策略ID", embed=True)
        ):
            bSucc, usrInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return usrInfo

            gid = groupid
            sid = strategyid

            if not self.__data_mgr__.has_group(gid):
                ret = {
                    "result": -1,
                    "message": "组合不存在"
                }
            else:
                ret = {
                    "result": 0,
                    "message": "",
                    "trades": self.__data_mgr__.get_trades(gid, sid)
                }

            return ret

        # 查询策略信号
        @app.post("/mgr/qrysigs", tags=["策略管理接口"])
        async def qry_signals(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                groupid: str = Body(..., title="组合ID", embed=True),
                strategyid: str = Body(..., title="策略ID", embed=True)
        ):
            bSucc, usrInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return usrInfo

            gid = groupid
            sid = strategyid

            if not self.__data_mgr__.has_group(gid):
                ret = {
                    "result": -1,
                    "message": "组合不存在"
                }
            else:
                ret = {
                    "result": 0,
                    "message": "",
                    "signals": self.__data_mgr__.get_signals(gid, sid)
                }

            return ret

        # 查询策略回合
        @app.post("/mgr/qryrnds", tags=["策略管理接口"])
        async def qry_rounds(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                groupid: str = Body(..., title="组合ID", embed=True),
                strategyid: str = Body(..., title="策略ID", embed=True)
        ):
            bSucc, usrInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return usrInfo

            gid = groupid
            sid = strategyid

            if not self.__data_mgr__.has_group(gid):
                ret = {
                    "result": -1,
                    "message": "组合不存在"
                }
            else:
                ret = {
                    "result": 0,
                    "message": "",
                    "rounds": self.__data_mgr__.get_rounds(gid, sid)
                }

            return ret

        # 查询策略持仓
        @app.post("/mgr/qrypos", tags=["策略管理接口"])
        async def qry_positions(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                groupid: str = Body(..., title="组合ID", embed=True),
                strategyid: str = Body(..., title="策略ID", embed=True)
        ):
            bSucc, usrInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return usrInfo

            gid = groupid
            sid = strategyid

            if not self.__data_mgr__.has_group(gid):
                ret = {
                    "result": -1,
                    "message": "组合不存在"
                }
            else:
                ret = {
                    "result": 0,
                    "message": "",
                    "positions": self.__data_mgr__.get_positions(gid, sid)
                }

            return ret

        # 查询策略绩效
        @app.post("/mgr/qryfunds", tags=["策略管理接口"])
        async def qry_funds(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                groupid: str = Body(..., title="组合ID", embed=True),
                strategyid: str = Body(..., title="策略ID", embed=True)
        ):
            bSucc, usrInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return usrInfo

            gid = groupid
            sid = strategyid

            if not self.__data_mgr__.has_group(gid):
                ret = {
                    "result": -1,
                    "message": "组合不存在"
                }
            else:
                ret = {
                    "result": 0,
                    "message": "",
                    "funds": self.__data_mgr__.get_funds(gid, sid)
                }

            return ret

        # 查询通道订单
        @app.post("/mgr/qrychnlords", tags=["交易通道管理接口"])
        async def qry_channel_orders(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                groupid: str = Body(..., title="组合ID", embed=True),
                channelid: str = Body(..., title="通道ID", embed=True)
        ):
            bSucc, usrInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return usrInfo

            gid = groupid
            cid = channelid

            if not self.__data_mgr__.has_group(gid):
                ret = {
                    "result": -1,
                    "message": "组合不存在"
                }
            else:
                ret = {
                    "result": 0,
                    "message": "",
                    "orders": self.__data_mgr__.get_channel_orders(gid, cid)
                }

            return ret

        # 查询通道成交
        @app.post("/mgr/qrychnltrds", tags=["交易通道管理接口"])
        async def qry_channel_trades(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                groupid: str = Body(..., title="组合ID", embed=True),
                channelid: str = Body(..., title="通道ID", embed=True)
        ):
            bSucc, usrInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return usrInfo

            gid = groupid
            cid = channelid

            if not self.__data_mgr__.has_group(gid):
                ret = {
                    "result": -1,
                    "message": "组合不存在"
                }
            else:
                ret = {
                    "result": 0,
                    "message": "",
                    "trades": self.__data_mgr__.get_channel_trades(gid, cid)
                }

            return ret

        # 查询通道持仓
        @app.post("/mgr/qrychnlpos", tags=["交易通道管理接口"])
        async def qry_channel_position(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                groupid: str = Body(..., title="组合ID", embed=True),
                channelid: str = Body(..., title="通道ID", embed=True)
        ):
            bSucc, usrInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return usrInfo

            gid = groupid
            cid = channelid

            if not self.__data_mgr__.has_group(gid):
                ret = {
                    "result": -1,
                    "message": "组合不存在"
                }
            else:
                ret = {
                    "result": 0,
                    "message": "",
                    "positions": self.__data_mgr__.get_channel_positions(gid, cid)
                }

            return ret

        # 查询通道资金
        @app.post("/mgr/qrychnlfund", tags=["交易通道管理接口"])
        async def qry_channel_funds(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                groupid: str = Body(..., title="组合ID", embed=True),
                channelid: str = Body(..., title="通道ID", embed=True)
        ):
            bSucc, usrInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return usrInfo

            gid = groupid
            cid = channelid

            if not self.__data_mgr__.has_group(gid):
                ret = {
                    "result": -1,
                    "message": "组合不存在"
                }
            else:
                ret = {
                    "result": 0,
                    "message": "",
                    "funds": self.__data_mgr__.get_channel_funds(gid, cid)
                }

            return ret

        # 查询用户列表
        @app.post("/mgr/qryusers", tags=["系统管理接口"])
        @app.get("/mgr/qryusers", tags=["系统管理接口"])
        async def qry_users(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True)
        ):
            bSucc, usrInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return usrInfo

            users = self.__data_mgr__.get_users()
            for usrInfo in users:
                usrInfo.pop("passwd")

            ret = {
                "result": 0,
                "message": "",
                "users": users
            }

            return ret

        # 提交用户信息
        @app.post("/mgr/cmtuser", tags=["系统管理接口"])
        async def cmd_commit_user(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                loginid: str = Body(..., title="登录名", embed=True),
                name: str = Body(..., title="用户姓名", embed=True),
                passwd: str = Body("", title="登录密码", embed=True),
                role: str = Body("", title="用户角色", embed=True),
                iplist: str = Body("", title="限定ip", embed=True),
                products: list = Body([], title="产品列表", embed=True),
                remark: str = Body("", title="备注信息", embed=True)
        ):
            bSucc, adminInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return adminInfo

            userinfo = {
                "loginid": loginid,
                "name": name,
                "passwd": passwd,
                "role": role,
                "iplist": iplist,
                "products": ",".join(products),
                "remark": remark
            }

            self.__data_mgr__.add_user(userinfo, adminInfo["loginid"])
            ret = {
                "result": 0,
                "message": "Ok"
            }

            self.__data_mgr__.log_action(adminInfo, "cmtuser", json.dumps(userinfo))

            return ret

        # 删除用户
        @app.post("/mgr/deluser", tags=["系统管理接口"])
        async def cmd_delete_user(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                loginid: str = Body(..., title="用户名", embed=True)
        ):
            bSucc, adminInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return adminInfo

            if self.__data_mgr__.del_user(loginid, adminInfo["loginid"]):
                self.__data_mgr__.log_action(adminInfo, "delusr", loginid)
            ret = {
                "result": 0,
                "message": "Ok"
            }

            return ret

        # 修改密码
        @app.post("/mgr/resetpwd", tags=["系统管理接口"])
        async def reset_pwd(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                loginid: str = Body(..., title="用户名", embed=True),
                passwd: str = Body(..., title="新密码", embed=True)
        ):
            bSucc, adminInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return adminInfo

            user = loginid
            pwd = passwd

            if len(pwd) == 0 or len(user) == 0:
                ret = {
                    "result": -1,
                    "message": "密码都不能为空"
                }
            else:
                encpwd = hashlib.md5((user + pwd).encode("utf-8")).hexdigest()
                usrInf = self.__data_mgr__.get_user(user)
                if usrInf is None:
                    ret = {
                        "result": -1,
                        "message": "用户不存在"
                    }
                else:
                    self.__data_mgr__.mod_user_pwd(user, encpwd, adminInfo["loginid"])
                    self.__data_mgr__.log_action(adminInfo, "resetpwd", loginid)
                    ret = {
                        "result": 0,
                        "message": "Ok"
                    }

            return ret

        # 查询操作记录
        @app.post("/mgr/qryacts", tags=["系统管理接口"])
        async def qry_actions(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                sdate: int = Body(..., title="开始日期", embed=True),
                edate: int = Body(..., title="结束日期", embed=True)
        ):
            bSucc, adminInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return adminInfo

            ret = {
                "result": 0,
                "message": "",
                "actions": self.__data_mgr__.get_actions(sdate, edate)
            }

            return ret

        # 查询全部调度
        @app.post("/mgr/qrymons", tags=["调度器管理接口"])
        @app.get("/mgr/qrymons", tags=["调度器管理接口"])
        async def qry_mon_apps(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True)
        ):
            bSucc, adminInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return adminInfo

            schedules = self._dog.get_apps()
            for appid in schedules:
                schedules[appid]["group"] = self.__data_mgr__.has_group(appid)

            ret = {
                "result": 0,
                "message": "",
                "schedules": schedules
            }

            return ret

        @app.post("/mgr/startapp", tags=["调度器管理接口"])
        async def cmd_start_app(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                appid: str = Body(..., title="AppID", embed=True)
        ):
            bSucc, adminInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return adminInfo

            if not self._dog.has_app(appid):
                ret = {
                    "result": -1,
                    "message": "App不存在"
                }
            else:
                if not self._dog.isRunning(appid):
                    self._dog.start(appid)
                ret = {
                    "result": 0,
                    "message": "Ok"
                }
                self.__data_mgr__.log_action(adminInfo, "startapp", appid)

            return ret

        # 组合停止
        @app.post("/mgr/stopapp", tags=["调度器管理接口"])
        async def cmd_stop_app(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                appid: str = Body(..., title="AppID", embed=True)
        ):
            bSucc, adminInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return adminInfo

            if not self._dog.has_app(appid):
                ret = {
                    "result": -1,
                    "message": "App不存在"
                }
            else:
                if self._dog.isRunning(appid):
                    self._dog.stop(appid)
                ret = {
                    "result": 0,
                    "message": "Ok"
                }

                self.__data_mgr__.log_action(adminInfo, "stopapp", appid)

            return ret

        # 查询调度日志
        @app.post("/mgr/qrymonlog", tags=["调度器管理接口"])
        @app.get("/mgr/qrymonlog", tags=["调度器管理接口"])
        async def qry_mon_logs(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True)
        ):
            bSucc, adminInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return adminInfo

            filename = os.getcwd() + "/logs/WtMonSvr.log"
            content, lines = get_tail(filename, 100, "UTF-8")
            ret = {
                "result": 0,
                "message": "Ok",
                "content": content,
                "lines": lines
            }

            return ret

        # 删除调度任务
        @app.post("/mgr/delapp", tags=["调度器管理接口"])
        async def cmd_del_app(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                appid: str = Body(..., title="AppID", embed=True)
        ):
            bSucc, adminInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return adminInfo

            id = appid

            if len(id) == 0:
                ret = {
                    "result": -1,
                    "message": "组合ID不能为空"
                }
            elif self.__data_mgr__.has_group(id):
                ret = {
                    "result": -2,
                    "message": "该调度任务是策略组合，请从组合管理删除"
                }
            elif not self._dog.has_app(id):
                ret = {
                    "result": -3,
                    "message": "该调度任务不存在"
                }
            elif self._dog.isRunning(id):
                ret = {
                    "result": -4,
                    "message": "请先停止该任务"
                }
            else:
                if True:
                    self._dog.delApp(id)
                    ret = {
                        "result": 0,
                        "message": "Ok"
                    }

                    self.__data_mgr__.log_action(adminInfo, "delapp", id)
                else:
                    ret = {
                        "result": -1,
                        "message": "请求解析失败"
                    }

            return ret

        # 查询组合持仓
        @app.post("/mgr/qryportpos", tags=["组合盘管理接口"])
        async def qry_group_positions(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                groupid: str = Body(..., title="组合ID", embed=True)
        ):
            bSucc, usrInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return usrInfo

            gid = groupid

            if not self.__data_mgr__.has_group(gid):
                ret = {
                    "result": -1,
                    "message": "组合不存在"
                }
            else:
                ret = {
                    "result": 0,
                    "message": "",
                    "positions": self.__data_mgr__.get_group_positions(gid)
                }

            return ret

        # 查询组合成交
        @app.post("/mgr/qryporttrd", tags=["组合盘管理接口"])
        async def qry_group_trades(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                groupid: str = Body(..., title="组合ID", embed=True)
        ):
            bSucc, usrInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return usrInfo

            gid = groupid

            if not self.__data_mgr__.has_group(gid):
                ret = {
                    "result": -1,
                    "message": "组合不存在"
                }
            else:
                ret = {
                    "result": 0,
                    "message": "",
                    "trades": self.__data_mgr__.get_group_trades(gid)
                }

            return ret

        # 查询组合回合
        @app.post("/mgr/qryportrnd", tags=["组合盘管理接口"])
        async def qry_group_rounds(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                groupid: str = Body(..., title="组合ID", embed=True)
        ):
            bSucc, usrInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return usrInfo

            gid = groupid

            if not self.__data_mgr__.has_group(gid):
                ret = {
                    "result": -1,
                    "message": "组合不存在"
                }
            else:
                ret = {
                    "result": 0,
                    "message": "",
                    "rounds": self.__data_mgr__.get_group_rounds(gid)
                }

            return ret

        # 查询组合资金
        @app.post("/mgr/qryportfunds", tags=["组合盘管理接口"])
        async def qry_group_funds(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                groupid: str = Body(..., title="组合ID", embed=True)
        ):
            bSucc, usrInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return usrInfo

            gid = groupid

            if not self.__data_mgr__.has_group(gid):
                ret = {
                    "result": -1,
                    "message": "组合不存在"
                }
            else:
                ret = {
                    "result": 0,
                    "message": "",
                    "funds": self.__data_mgr__.get_group_funds(gid)
                }

            return ret

        # 查询组合绩效分析
        @app.post("/mgr/qryportperfs", tags=["组合盘管理接口"])
        async def qry_group_perfs(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                groupid: str = Body(..., title="组合ID", embed=True)
        ):
            bSucc, usrInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return usrInfo

            gid = groupid

            if not self.__data_mgr__.has_group(gid):
                ret = {
                    "result": -1,
                    "message": "组合不存在"
                }
            else:
                ret = {
                    "result": 0,
                    "message": "",
                    "performance": self.__data_mgr__.get_group_performances(gid)
                }

            return ret

        # 查询组合过滤器
        @app.post("/mgr/qryportfilters", tags=["组合盘管理接口"])
        async def qry_group_filters(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                groupid: str = Body(..., title="组合ID", embed=True)
        ):
            bSucc, usrInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return usrInfo

            gid = groupid

            if not self.__data_mgr__.has_group(gid):
                ret = {
                    "result": -1,
                    "message": "组合不存在"
                }
            else:
                ret = {
                    "result": 0,
                    "message": "",
                    "filters": self.__data_mgr__.get_group_filters(gid)
                }

            return ret

        # 提交组合过滤器
        @app.post("/mgr/cmtgrpfilters", tags=["组合盘管理接口"])
        async def cmd_commit_group_filters(
                request: Request,
                token: str = Body(None, title="访问令牌", embed=True),
                groupid: str = Body(..., title="组合ID", embed=True),
                filters: dict = Body(..., title="过滤器", embed=True)
        ):
            bSucc, usrInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return usrInfo

            grpid = groupid

            if not self.__data_mgr__.has_group(grpid):
                ret = {
                    "result": -1,
                    "message": "组合不存在"
                }
            else:
                try:
                    self.__data_mgr__.set_group_filters(grpid, filters)
                    ret = {
                        "result": 0,
                        "message": "Ok"
                    }
                except:
                    ret = {
                        "result": -1,
                        "message": "过滤器保存失败"
                    }

            return ret
        
        @app.get("/mgr/auth", tags=["令牌认证"])
        @app.post("/mgr/auth")
        async def authority(
            request: Request,
            token: str = Body(None, title="访问令牌", embed=True)
        ):
            bSucc, userInfo = check_auth(request, token, self.__sec_key__)
            if not bSucc:
                return userInfo
            else:
                return {
                    "result": 0,
                    "message": "Ok",
                    "userinfo": userInfo
                }

    def init_comm_apis(self, app: FastAPI):
        @app.get("/console")
        async def console_entry():
            return RedirectResponse("/console/index.html")
        
        @app.get("/mobile")
        async def mobile_entry():
            return RedirectResponse("/mobile/index.html")

        @app.get("/favicon.ico")
        async def favicon_entry():
            return FileResponse(os.path.join(self.static_folder, "favicon.ico"))
        
        @app.get("/hasbt")
        @app.post("/hasbt")
        async def check_btmon():
            if self.__bt_mon__ is None:
                return {
                    "result": -1,
                    "message": "不支持在线回测"
                }
            else:
                return {
                    "result": 0,
                    "message": "Ok"
                }

    def __run_impl__(self, port: int, host: str):
        self._dog.run()
        self.push_svr.run()
        uvicorn.run(self.app, port=port, host=host)

    def run(self, port: int = 8080, host="0.0.0.0", bSync: bool = True):
        # 仅linux生效，在linux中，子进程会一直等待父进程处理其结束信号才能释放，如果不加这一句忽略子进程的结束信号，子进程就无法结束
        if not isWindows():
            signal.signal(signal.SIGCHLD, signal.SIG_IGN)
        if bSync:
            self.__run_impl__(port, host)
        else:
            import threading
            self.worker = threading.Thread(target=self.__run_impl__, args=(port, host,))
            self.worker.setDaemon(True)
            self.worker.start()

    def init_logging(self):
        pass

    def on_start(self, grpid: str):
        if self.__data_mgr__.has_group(grpid):
            self.push_svr.notifyGrpEvt(grpid, 'start')

    def on_stop(self, grpid: str, isErr: bool):
        if self.__data_mgr__.has_group(grpid):
            self.push_svr.notifyGrpEvt(grpid, 'stop')

        # 如果是错误，要通知管理员
        if isErr and self._sink_:
            grpInfo = self.__data_mgr__.get_group(grpid)
            self._sink_.notify("fatal", "检测到 %s[%s] 意外停止, 请及时处理!!!" % (grpInfo["name"], grpid))

    def on_output(self, grpid: str, tag: str, time: int, message: str):
        if self.__data_mgr__.has_group(grpid):
            self.push_svr.notifyGrpLog(grpid, tag, time, message)

    def on_order(self, grpid: str, chnl: str, ordInfo: dict):
        self.push_svr.notifyGrpChnlEvt(grpid, chnl, 'order', ordInfo)

    def on_trade(self, grpid: str, chnl: str, trdInfo: dict):
        self.push_svr.notifyGrpChnlEvt(grpid, chnl, 'trade', trdInfo)

    def on_notify(self, grpid: str, chnl: str, message: str):
        self.push_svr.notifyGrpChnlEvt(grpid, chnl, 'notify', message)

    def on_timeout(self, grpid: str):
        if not self.notifyTimeout:
            return
            
        if self._sink_:
            grpInfo = self.__data_mgr__.get_group(grpid)
            self._sink_.notify("fatal", f'检测到 {grpInfo["name"]}[{grpid}]的MQ消息超时，请及时检查并处理!!!')
