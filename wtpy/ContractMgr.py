import json
import yaml
import chardet

from .ProductMgr import ProductMgr, ProductInfo

class ContractInfo:

    def __init__(self):
        self.exchg:str = ''     #交易所
        self.code:str = ''      #合约代码
        self.name:str = ''      #合约名称
        self.product:str = ''   #品种代码
        self.stdCode:str = ''   #标准代码

        self.isOption:bool = False      # 是否期权合约
        self.underlying:str = ''        # underlying
        self.strikePrice:float = 0      # 行权价
        self.underlyingScale:float = 0  # 放大倍数
        self.isCall:bool = True         # 是否看涨期权

        self.openDate:int = 19000101    # 上市日期
        self.expireDate:int = 20991231  # 到期日

        self.longMarginRatio:float = 0  # 多头保证金率
        self.shortMarginRatio:float = 0 # 空头保证金率


class ContractMgr:

    def __init__(self, prodMgr:ProductMgr = None):
        self.__contracts__ = dict()
        self.__underlyings__ = dict()   # 期权专用
        self.__products__ = dict()   # 期权专用
        self.__prod_mgr__ = prodMgr

    def load(self, fname:str):
        '''
        从文件加载品种信息
        '''
        f = open(fname, 'rb')
        content = f.read()
        f.close()
        encoding = chardet.detect(content[:500])["encoding"]
        content = content.decode(encoding)

        if fname.lower().endswith(".yaml"):
            exchgMap = yaml.full_load(content)
        else:
            exchgMap = json.loads(content)
        for exchg in exchgMap:
            exchgObj = exchgMap[exchg]

            for code in exchgObj:
                cObj = exchgObj[code]
                cInfo = ContractInfo()
                cInfo.exchg = exchg
                cInfo.code = code
                cInfo.name = cObj["name"]

                # By Wesley @ 2021-03-31 
                # 增加了对合约的上市日期和到期日的读取
                # 增加了对合约的保证金率的读取
                if "opendate" in cObj:
                    cInfo.openDate = int(cObj["opendate"])
                if "expiredate" in cObj:
                    cInfo.expireDate = int(cObj["expiredate"])
                if "longmarginratio" in cObj:
                    cInfo.longMarginRatio = float(cObj["longmarginratio"])
                if "shortmarginratio" in cObj:
                    cInfo.shortMarginRatio = float(cObj["shortmarginratio"])

                if "product" in cObj:
                    cInfo.product = cObj["product"]                    
                    #股票标准代码为SSE.000001，期货标准代码为SHFE.rb.2010
                    if cInfo.code[:len(cInfo.product)] == cInfo.product:
                        month = cInfo.code[len(cInfo.product):]
                        if len(month) < 4:
                            month = "2" + month
                        cInfo.stdCode = exchg + "." + cInfo.product + "." + month
                    else:
                        cInfo.stdCode = exchg + "." + cInfo.product + "." + cInfo.code

                    stdPID = exchg + "." + cInfo.product
                    if stdPID not in self.__products__:
                        self.__products__[stdPID] = list()

                    self.__products__[stdPID].append(cInfo.stdCode)
                else:
                    cInfo.product = cInfo.code
                    cInfo.stdCode = exchg + "." + cInfo.code
                    if "rules" in cObj:
                        pObj = cObj["rules"]
                        pInfo = ProductInfo()
                        pInfo.exchg = exchg
                        pInfo.product = cInfo.code
                        pInfo.name = cInfo.name
                        pInfo.session = pObj["session"]
                        pInfo.volscale = int(pObj["volscale"])
                        pInfo.pricetick = float(pObj["pricetick"])

                        if "minlots" in pObj:
                            pInfo.minlots = float(pObj["minlots"])
                        if "lotstick" in pObj:
                            pInfo.lotstick = float(pObj["lotstick"])

                if "option" in cObj:
                    oObj = cObj["option"]
                    cInfo.isOption = True
                    cInfo.isCall = (int(oObj["optiontype"])==49)
                    cInfo.underlying = oObj["underlying"]
                    cInfo.strikePrice = float(oObj["strikeprice"])
                    cInfo.underlyingScale = float(oObj["underlyingscale"])

                self.__contracts__[cInfo.stdCode] = cInfo
                if cInfo.isOption:
                    stdUnderlying = f"{exchg}.{cInfo.underlying}"
                    if stdUnderlying not in self.__underlyings__:
                        self.__underlyings__[stdUnderlying] = list()

                    self.__underlyings__[stdUnderlying].append(cInfo.stdCode)

    def getContractInfo(self, stdCode:str, uDate:int = 0) -> ContractInfo:
        '''
        获取合约信息
        @stdCode    合约代码，格式如SHFE.rb.2305
        '''
        if stdCode not in self.__contracts__:
            return None
            
        cInfo:ContractInfo = self.__contracts__[stdCode]
        if uDate != 0 and (cInfo.openDate > uDate or cInfo.expireDate < uDate):
            return None
        
        return cInfo

    def getTotalCodes(self, uDate:int = 0) -> list:
        '''
        获取全部合约代码列表
        @uDate  交易日, 格式如20210101
        '''
        codes = list()
        for code in self.__contracts__:
            cInfo:ContractInfo = self.__contracts__[code]
            if uDate == 0 or (cInfo.openDate <= uDate and cInfo.expireDate >= uDate):
                codes.append(self.__contracts__[code].stdCode)
        return codes
    
    def getCodesByUnderlying(self, underlying:str, uDate:int = 0) -> list:
        '''
        根据underlying读取合约列表
        @underlying 格式如CFFEX.IM2304
        @uDate      交易日, 格式如20210101
        '''
        ret = list()
        if underlying in self.__underlyings__:
            codes = self.__underlyings__[underlying]
            for code in codes:
                cInfo:ContractInfo = self.__contracts__[code]
                if uDate == 0 or (cInfo.openDate <= uDate and cInfo.expireDate >= uDate):
                    ret.append(self.__contracts__[code].stdCode)

        return ret
    
    def getCodesByProduct(self, stdPID:str, uDate:int = 0) -> list:
        '''
        根据品种代码读取合约列表
        @stdPID 品种代码, 格式如SHFE.rb
        @uDate  交易日, 格式如20210101
        '''
        ret = list()
        if stdPID in self.__products__:
            codes = self.__products__[stdPID]
            for code in codes:
                cInfo:ContractInfo = self.__contracts__[code]
                if uDate == 0 or (cInfo.openDate <= uDate and cInfo.expireDate >= uDate):
                    ret.append(self.__contracts__[code].stdCode)
        return ret
        

