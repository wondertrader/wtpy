from .PlatformHelper import PlatformHelper as ph
import os
import subprocess
import time


class CTPLoader:

    def __init__(self, folder:str="./", isMini:bool = False):
        self.folder = folder

        filename = "MiniLoader" if isMini else "CTPLoader"

        paths = os.path.split(__file__)
        exename = ''
        if ph.isWindows(): #windows平台
            if ph.isPythonX64():
                exename = "x64/%s.exe" % (filename)
            else:
                exename = "x86/%s.exe" % (filename)
        else:#Linux平台
            exename = "linux/" + filename
        a = (paths[:-1] + (exename,))
        self.exe_path = os.path.join(*a)

    def start(self):
        self._proc = subprocess.Popen([self.exe_path],  # 需要执行的文件路径
                            cwd=self.folder, creationflags=subprocess.CREATE_NEW_CONSOLE)
        while self._proc.poll() is None:                      # None表示正在执行中
            time.sleep(1)