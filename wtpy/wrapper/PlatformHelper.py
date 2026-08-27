import platform

class PlatformHelper:

    @staticmethod
    def isPythonX64() -> bool:
        ret = platform.architecture()
        return (ret[0] == "64bit")

    @staticmethod
    def isWindows() -> bool:
        if "windows" in platform.system().lower():
            return True

        return False

    @staticmethod
    def getModule(moduleName:str, subdir:str="") -> str:
        dllname = ""
        ext = ""
        prefix = ""
        if PlatformHelper.isWindows(): #windows平台
            ext = ".dll"
            if PlatformHelper.isPythonX64():
                dllname = "x64/"
            else:
                dllname = "x86/"
        else:#Linux平台
            dllname = "linux/"
            prefix = "lib"
            ext = ".so"

        if subdir != "":
            dllname += subdir + "/"

        dllname += prefix + moduleName + ext
        return dllname
    
    @staticmethod
    def auto_encode(s:str) -> bytes:
        # 统一输出UTF-8字节流: 现代终端(Windows Terminal/VSCode/opencode等)默认按UTF-8解码,
        # 原来的GBK转换在UTF-8终端下中文乱码; 日志文件本身也是UTF-8写入
        return bytes(s, encoding = "utf-8")
            