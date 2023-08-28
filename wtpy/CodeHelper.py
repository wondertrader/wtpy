import re

class CodeHelper:
    
    @staticmethod
    def isStdChnFutOptCode(stdCode:str) -> bool:
        pattern = re.compile("^[A-Z]+.[A-z]+\\d{4}.(C|P).\\d+$")
        if re.match(pattern, stdCode) is not None:
            return True

        return False

    @staticmethod
    def stdCodeToStdCommID(stdCode:str) -> str:
        ay = stdCode.split(".")
        if not CodeHelper.isStdChnFutOptCode(stdCode):
            return ay[0] + "." + ay[1]
        else:
            exchg = ay[0]
            pid = ay[1][:-4]
            flag = ay[2]
            if exchg == 'CZCE':
                return exchg + "." + pid + flag
            elif exchg == 'CFFEX':
                return exchg + "." + pid
            else:
                return exchg + "." + pid + '_o'