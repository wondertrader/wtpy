import json
import yaml
import os
import chardet

class ProductInfo:
    '''
    品种信息
    '''

    def __init__(self):
        self.exchg = ''     #交易所
        self.product = ''   #品种代码
        self.name = ''      #品种名称
        self.session = ''   #交易时段名
        self.pricetick = 0  #价格变动单位
        self.volscale = 1   #数量乘数
        self.minlots = 1    #最小交易数量
        self.lotstick = 1    #交易数量变动单位

class ProductMgr:
    '''
    品种信息管理器
    '''
    def __init__(self):
        self.__products__ = dict()
        return

    def load(self, fname:str):
        '''
        从文件加载品种信息
        '''
        if not os.path.exists(fname):
            return
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
            for pid in exchgObj:
                pObj = exchgObj[pid]
                pInfo = ProductInfo()
                pInfo.exchg = exchg
                pInfo.product = pid
                pInfo.name = pObj["name"]
                pInfo.session = pObj["session"]
                pInfo.precision = int(pObj["precision"])
                pInfo.volscale = int(pObj["volscale"])
                pInfo.pricetick = float(pObj["pricetick"])

                if "minlots" in pObj:
                    pInfo.minlots = float(pObj["minlots"])
                if "lotstick" in pObj:
                    pInfo.lotstick = float(pObj["lotstick"])

                key = "%s.%s" % (exchg, pid)
                self.__products__[key] = pInfo
    
    def addProductInfo(self, key:str, pInfo:ProductInfo):
        self.__products__[key] = pInfo

    def getProductInfo(self, pid:str) -> ProductInfo:
        #pid形式可能为SHFE.ag.HOT，或者SHFE.ag.1912，或者SHFE.ag
        items = pid.split(".")
        key = items[0] + "." + items[1]
        if key not in self.__products__:
            return None

        return self.__products__[key]