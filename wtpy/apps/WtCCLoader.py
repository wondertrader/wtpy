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

class WtCCLoader:

    @staticmethod
    def load_from_okex(filename:str, instTypes:list = ["SPOT"], proxy:str = None) -> bool:

        contracts = dict()

        def wrap_category(iType:str):
            #20-币币SPOT, 21-永续SWAP, 22-期货Future, 23-杠杆Margin
            if iType == "SPOT":
                return 20
            elif iType == "SWAP":
                return 21
            elif iType == "FUTURES":
                return 22
            elif iType == "MARGIN":
                return 23
            else:
                return 24

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

