from ctypes import cdll, c_char_p

import platform
import os
import sys

def isPythonX64():
    ret = platform.architecture()
    return (ret[0] == "64bit")

def isWindows():
    if "windows" in platform.system().lower():
        return True

    return False

class WtExecApi:

    # api可以作为公共变量
    api = None
    ver = "Unknown"

    def __init__(self):
        paths = os.path.split(__file__)
        if isWindows(): #windows平台
            if isPythonX64():
                dllname = "x64/WtExecMon.dll"
                a = (paths[:-1] + (dllname,))
                _path = os.path.join(*a)
                self.api = cdll.LoadLibrary(_path)
            else:
                dllname = "x86/WtExecMon.dll"
                a = (paths[:-1] + (dllname,))
                _path = os.path.join(*a)
                self.api = cdll.LoadLibrary(_path)
        else:#Linux平台
            dllname = "linux/libWtExecMon.so"
            a = (paths[:-1] + (dllname,))
            _path = os.path.join(*a)
            self.api = cdll.LoadLibrary(_path)

        self.api.get_version.restype = c_char_p
        self.ver = bytes.decode(self.api.get_version())

    def run(self):
        self.api.run_exec()

    def release(self):
        self.api.release_exec()

    def write_log(self, level, message:str, catName:str = ""):
        self.api.write_log(level, bytes(message, encoding = "utf8").decode('utf-8').encode('gbk'), bytes(catName, encoding = "utf8"))

    def config(self, cfgfile:str = 'cfgexec.json'):
        self.api.config_exec(bytes(cfgfile, encoding = "utf8"))

    def initialize(self, engine, logProfile:str = "logcfgexec.json"):
        '''
        C接口初始化
        '''
        self.api.init_exec(bytes(logProfile, encoding = "utf8"))
        self.write_log(102, "Wt独立执行器已初始化完成，基础框架版本号：%s" % (self.ver))

    def set_position(self, stdCode:str, target:float):
        self.api.set_position(bytes(stdCode, encoding = "utf8"), target)
