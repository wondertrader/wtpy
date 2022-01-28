import urllib.request
import io
import gzip

import json


def httpGet(url, encoding:str='utf-8', proxy:str = None, headers:dict = {}) -> str:
    
    headers['Accept-encoding'] = 'gzip'
    headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)'
    handler = None
    if proxy is not None:
        proxy_value = "%(ip)s" % {"ip":proxy}
        proxies = {
            "http":proxy_value,
            "https":proxy_value
        }
        handler = urllib.request.ProxyHandler(proxies)

    opener = urllib.request.build_opener(handler)
    request = urllib.request.Request(url, headers=headers)
    if True:
        f = opener.open(request)
        ec = f.headers.get('Content-Encoding')
        if ec == 'gzip':
            cd = f.read()
            cs = io.BytesIO(cd)
            f = gzip.GzipFile(fileobj=cs)

        return f.read().decode(encoding)
    else:
        return ""

def wrap_category(iType:str):
    #20-币币SPOT, 21-永续SWAP, 22-期货Future, 23-杠杆Margin
    if iType.upper() == "SPOT":
        return 20
    elif iType.upper() == "SWAP":
        return 21
    elif iType.upper() == "FUTURES" or iType.upper() == "FUTURE":
        return 22
    elif iType.upper() == "MARGIN":
        return 23
    else:
        return 24

class WtCCLoader:

    @staticmethod
    def load_from_okex(filename:str, instTypes:list = ["SPOT"], proxy:str = None) -> bool:

        contracts = dict()

        for iType in instTypes:
            cat = wrap_category(iType)
            tMode = 1 if iType=='SPOT' else 0 #0-多空, 1-做多, 2-做多T+1
            content  = httpGet('https://www.okex.com/api/v5/public/instruments?instType='+iType, proxy=proxy, headers={
                "Accept":"application/json"
            })
            if len(content) == 0:
                return False

            try:
                root = json.loads(content)
                code = int(root["code"])
                msg = root["msg"]
                if code != 0:
                    print("加载合约列表出错: %s" % msg)
                    return False

                for item in root["data"]:
                    cInfo = dict()
                    cInfo["name"] = item["instId"]
                    cInfo["code"] = item["instId"]
                    cInfo["exchg"] = "OKEX"

                    #这些是wt不用的额外信息，做一个保存
                    extInfo = dict()
                    extInfo["instType"] = iType
                    extInfo["baseCcy"] = item["baseCcy"]    
                    extInfo["quoteCcy"] = item["quoteCcy"]
                    extInfo["category"] = item["category"]
                    extInfo["ctVal"] = item["ctVal"]
                    extInfo["ctValCcy"] = item["ctValCcy"]
                    extInfo["lever"] = item["lever"]
                    extInfo["ctType"] = item["ctType"]
                    cInfo["extras"] = extInfo

                    ruleInfo = dict()
                    ruleInfo["session"] = "ALLDAY"
                    ruleInfo["holiday"] = ""

                    ruleInfo["covermode"] = 3       #0-开平, 1-区分平今, 3-不分开平
                    ruleInfo["pricemode"] = 0       #0-支持限价市价, 1-只支持限价, 2-只支持市价  
                    ruleInfo["category"] = cat      #20-币币SPOT, 21-永续SWAP, 22-期货Future, 23-币币杠杆Margin
                    ruleInfo["trademode"] = tMode   #0-多空, 1-做多, 2-做多T+1

                    ruleInfo["pricetick"] = float(item["tickSz"])
                    ruleInfo["lotstick"] = float(item["lotSz"])
                    ruleInfo["minlots"] = float(item["minSz"])
                    ruleInfo["volscale"] = int(item["ctMult"]) if len(item["ctMult"])>0 else 1

                    cInfo["rules"] = ruleInfo

                    contracts[cInfo['code']] = cInfo
            except:
                continue

        # 这里将下载到的合约列表落地
        f = open(filename, "w")
        f.write(json.dumps({"OKEX":contracts}, indent=4, ensure_ascii=False))
        f.close()


    @staticmethod
    def load_spots_from_binance(filename:str, proxy:str = None) -> bool:

        contracts = dict()

        content  = httpGet('https://api.binance.com/api/v3/exchangeInfo', proxy=proxy, headers={
            "Accept":"application/json"
        })
        if len(content) == 0:
            return False

        try:
            root = json.loads(content)
        except:
            print("加载合约列表出错")
            return False

        for item in root["symbols"]:
            cInfo = dict()
            cInfo["name"] = item["symbol"]
            cInfo["code"] = item["symbol"]
            cInfo["exchg"] = "BINANCE"

            if "MARGIN" in item["permissions"]:
                iType = "MARGIN"
            elif "SPOT" in item["permissions"]:
                iType = "SPOT"
            else:
                continue
                
            tMode = 1 if iType=='SPOT' else 0 #0-多空, 1-做多, 2-做多T+1

            #这些是wt不用的额外信息，做一个保存
            extInfo = dict()
            extInfo["instType"] = iType
            extInfo["baseAsset"] = item["baseAsset"]    
            extInfo["quoteAsset"] = item["quoteAsset"]
            extInfo["icebergAllowed"] = item["icebergAllowed"]
            extInfo["ocoAllowed"] = item["ocoAllowed"]
            extInfo["quoteOrderQtyMarketAllowed"] = item["quoteOrderQtyMarketAllowed"]
            extInfo["baseAssetPrecision"] = item["baseAssetPrecision"]
            extInfo["quoteAssetPrecision"] = item["quoteAssetPrecision"]
            extInfo["isSpotTradingAllowed"] = item["isSpotTradingAllowed"]
            # extInfo["permissions"] = item["permissions"]
            extInfo["orderTypes"] = item["orderTypes"]
            cInfo["extras"] = extInfo

            ruleInfo = dict()
            ruleInfo["session"] = "ALLDAY"
            ruleInfo["holiday"] = ""

            ruleInfo["covermode"] = 3       #0-开平, 1-区分平今, 3-不分开平
            ruleInfo["pricemode"] = 0       #0-支持限价市价, 1-只支持限价, 2-只支持市价  
            ruleInfo["category"] = wrap_category(iType)      #20-币币SPOT, 21-永续SWAP, 22-期货Future, 23-币币杠杆Margin
            ruleInfo["trademode"] = tMode   #0-多空, 1-做多, 2-做多T+1

            for fItem in item["filters"]:
                if fItem["filterType"] == "PRICE_FILTER":
                    ruleInfo["pricetick"] = float(fItem["tickSize"])
                if fItem["filterType"] == "LOT_SIZE":
                    ruleInfo["lotstick"] = float(fItem["stepSize"])
                    ruleInfo["minlots"] = float(fItem["minQty"])
                ruleInfo["volscale"] = 1

            cInfo["rules"] = ruleInfo

            contracts[cInfo['code']] = cInfo
            

        # 这里将下载到的合约列表落地
        f = open(filename, "w")
        f.write(json.dumps({"BINANCE":contracts}, indent=4, ensure_ascii=False))
        f.close()

    @staticmethod
    def load_fpairs_from_binance(filename:str, proxy:str = None) -> bool:

        contracts = dict()

        content  = httpGet('https://fapi.binance.com/fapi/v1/exchangeInfo', proxy=proxy, headers={
            "Accept":"application/json"
        })
        if len(content) == 0:
            return False

        try:
            root = json.loads(content)
        except:
            print("加载合约列表出错")
            return False

        for item in root["symbols"]:
            cInfo = dict()
            cInfo["name"] = item["symbol"]
            cInfo["code"] = item["symbol"]
            cInfo["exchg"] = "BINANCE"

            iType = item["contractType"]
            if len(iType.strip()) == 0:
                continue
            if iType == "PERPETUAL":
                iType = "SWAP"
            else:
                iType = "FUTURES"
            tMode = 0 #0-多空, 1-做多, 2-做多T+1

            #这些是wt不用的额外信息，做一个保存
            extInfo = dict()
            extInfo["instType"] = iType
            extInfo["baseAsset"] = item["baseAsset"]    
            extInfo["quoteAsset"] = item["quoteAsset"]
            extInfo["marginAsset"] = item["marginAsset"]
            extInfo["pricePrecision"] = item["pricePrecision"]
            extInfo["quantityPrecision"] = item["quantityPrecision"]
            extInfo["baseAssetPrecision"] = item["baseAssetPrecision"]
            extInfo["quotePrecision"] = item["quotePrecision"]
            extInfo["underlyingType"] = item["underlyingType"]
            extInfo["underlyingSubType"] = item["underlyingSubType"]
            extInfo["orderTypes"] = item["orderTypes"]
            extInfo["timeInForce"] = item["timeInForce"]
            extInfo["deliveryDate"] = item["deliveryDate"]
            extInfo["onboardDate"] = item["onboardDate"]
            extInfo["contractType"] = item["contractType"]
            cInfo["extras"] = extInfo

            ruleInfo = dict()
            ruleInfo["session"] = "ALLDAY"
            ruleInfo["holiday"] = ""

            ruleInfo["covermode"] = 3       #0-开平, 1-区分平今, 3-不分开平
            ruleInfo["pricemode"] = 0       #0-支持限价市价, 1-只支持限价, 2-只支持市价  
            ruleInfo["category"] = wrap_category(iType)      #20-币币SPOT, 21-永续SWAP, 22-期货Future, 23-币币杠杆Margin
            ruleInfo["trademode"] = tMode   #0-多空, 1-做多, 2-做多T+1

            for fItem in item["filters"]:
                if fItem["filterType"] == "PRICE_FILTER":
                    ruleInfo["pricetick"] = float(fItem["tickSize"])
                if fItem["filterType"] == "LOT_SIZE":
                    ruleInfo["lotstick"] = float(fItem["stepSize"])
                    ruleInfo["minlots"] = float(fItem["minQty"])
                ruleInfo["volscale"] = 1

            cInfo["rules"] = ruleInfo

            contracts[cInfo['code']] = cInfo
            

        # 这里将下载到的合约列表落地
        f = open(filename, "w")
        f.write(json.dumps({"BINANCE":contracts}, indent=4, ensure_ascii=False))
        f.close()

    @staticmethod
    def load_dpairs_from_binance(filename:str, proxy:str = None) -> bool:

        contracts = dict()

        content  = httpGet('https://dapi.binance.com/dapi/v1/exchangeInfo', proxy=proxy, headers={
            "Accept":"application/json"
        })
        if len(content) == 0:
            return False

        try:
            root = json.loads(content)
        except:
            print("加载合约列表出错")
            return False

        for item in root["symbols"]:
            cInfo = dict()
            cInfo["name"] = item["symbol"]
            cInfo["code"] = item["symbol"]
            cInfo["exchg"] = "BINANCE"

            iType = item["contractType"]
            if len(iType.strip()) == 0:
                continue

            if iType == "PERPETUAL":
                iType = "SWAP"
            else:
                iType = "FUTURES"
            tMode = 0 #0-多空, 1-做多, 2-做多T+1

            #这些是wt不用的额外信息，做一个保存
            extInfo = dict()
            extInfo["instType"] = iType
            extInfo["baseAsset"] = item["baseAsset"]    
            extInfo["quoteAsset"] = item["quoteAsset"]
            extInfo["marginAsset"] = item["marginAsset"]
            extInfo["pricePrecision"] = item["pricePrecision"]
            extInfo["quantityPrecision"] = item["quantityPrecision"]
            extInfo["baseAssetPrecision"] = item["baseAssetPrecision"]
            extInfo["quotePrecision"] = item["quotePrecision"]
            extInfo["underlyingType"] = item["underlyingType"]
            extInfo["underlyingSubType"] = item["underlyingSubType"]
            extInfo["orderTypes"] = item["orderTypes"]
            extInfo["timeInForce"] = item["timeInForce"]
            extInfo["deliveryDate"] = item["deliveryDate"]
            extInfo["onboardDate"] = item["onboardDate"]
            extInfo["contractType"] = item["contractType"]
            cInfo["extras"] = extInfo

            ruleInfo = dict()
            ruleInfo["session"] = "ALLDAY"
            ruleInfo["holiday"] = ""

            ruleInfo["covermode"] = 3       #0-开平, 1-区分平今, 3-不分开平
            ruleInfo["pricemode"] = 0       #0-支持限价市价, 1-只支持限价, 2-只支持市价  
            ruleInfo["category"] = wrap_category(iType)      #20-币币SPOT, 21-永续SWAP, 22-期货Future, 23-币币杠杆Margin
            ruleInfo["trademode"] = tMode   #0-多空, 1-做多, 2-做多T+1

            for fItem in item["filters"]:
                if fItem["filterType"] == "PRICE_FILTER":
                    ruleInfo["pricetick"] = float(fItem["tickSize"])
                if fItem["filterType"] == "LOT_SIZE":
                    ruleInfo["lotstick"] = float(fItem["stepSize"])
                    ruleInfo["minlots"] = float(fItem["minQty"])
                ruleInfo["volscale"] = 1

            cInfo["rules"] = ruleInfo

            contracts[cInfo['code']] = cInfo
            

        # 这里将下载到的合约列表落地
        f = open(filename, "w")
        f.write(json.dumps({"BINANCE":contracts}, indent=4, ensure_ascii=False))
        f.close()


    @staticmethod
    def load_from_ftx(filename:str, instTypes:list = ["SPOT"], proxy:str = None) -> bool:

        contracts = dict()

        content  = httpGet('https://ftx.com/api/markets', proxy=proxy, headers={
            "Accept":"application/json"
        })
        if len(content) == 0:
            return False

        try:
            root = json.loads(content)
        except:
            print("加载合约列表出错")
            return False

        if not root["success"]:
            print("加载合约列表失败")
            return False

        all_types = list()

        for item in root["result"]:
            cInfo = dict()
            cInfo["name"] = item["name"]
            cInfo["code"] = item["name"]
            cInfo["exchg"] = "FTX"

            iType = item["type"].upper()
            if iType == "FUTURE":
                iType += "S"

            if iType not in all_types:
                all_types.append(iType)

            if iType not in instTypes:
                continue

            tMode = 1 if iType=='SPOT' else 0 #0-多空, 1-做多, 2-做多T+1

            #这些是wt不用的额外信息，做一个保存
            extInfo = dict()
            extInfo["instType"] = iType
            extInfo["baseCurrency"] = item["baseCurrency"]    
            extInfo["quoteCurrency"] = item["quoteCurrency"]
            extInfo["underlying"] = item["underlying"]
            extInfo["postOnly"] = item["postOnly"]
            extInfo["highLeverageFeeExempt"] = item["highLeverageFeeExempt"]
            cInfo["extras"] = extInfo

            ruleInfo = dict()
            ruleInfo["session"] = "ALLDAY"
            ruleInfo["holiday"] = ""

            ruleInfo["covermode"] = 3       #0-开平, 1-区分平今, 3-不分开平
            ruleInfo["pricemode"] = 0       #0-支持限价市价, 1-只支持限价, 2-只支持市价  
            ruleInfo["category"] = wrap_category(iType)      #20-币币SPOT, 21-永续SWAP, 22-期货Future, 23-币币杠杆Margin
            ruleInfo["trademode"] = tMode   #0-多空, 1-做多, 2-做多T+1

            ruleInfo["pricetick"] = item["priceIncrement"]
            ruleInfo["lotstick"] = item["sizeIncrement"]
            ruleInfo["minlots"] = item["minProvideSize"]
            ruleInfo["volscale"] = 1

            cInfo["rules"] = ruleInfo

            contracts[cInfo['code']] = cInfo
            
        print(all_types)
        # 这里将下载到的合约列表落地
        f = open(filename, "w")
        f.write(json.dumps({"FTX":contracts}, indent=4, ensure_ascii=False))
        f.close()

