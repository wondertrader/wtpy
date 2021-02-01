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