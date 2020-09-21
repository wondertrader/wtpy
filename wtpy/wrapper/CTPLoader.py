import platform
import os
import sys
import subprocess
import time

def isPythonX64():
    ret = platform.architecture()
    return (ret[0] == "64bit")

def isWindows():
    if "windows" in platform.system().lower():
        return True

    return False

class CTPLoader:

    def __init__(self, folder:str="./"):
        self.folder = folder

        paths = os.path.split(__file__)
        exename = ''
        if isWindows(): #windows平台
            if isPythonX64():
                exename = "x64/CTPLoader.exe"
            else:
                exename = "x86/CTPLoader.exe"
        else:#Linux平台
            exename = "linux/CTPLoader"
        a = (paths[:-1] + (exename,))
        self.exe_path = os.path.join(*a)

    def start(self):
        self._proc = subprocess.Popen([self.exe_path],  # 需要执行的文件路径
                            cwd=self.folder, creationflags=subprocess.CREATE_NEW_CONSOLE)
        while self._proc.poll() is None:                      # None表示正在执行中
            time.sleep(1)