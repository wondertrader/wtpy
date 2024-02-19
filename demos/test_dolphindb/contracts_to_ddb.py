import dolphindb as ddb
import json
import datetime
import pandas as pd

def check_table(pool:ddb.DBConnectionPool):
    script_kline = '''
    tbName = "CodeInfos"
    dbName = "dfs://BASIC_INFOS"

    if( not existsTable(dbName, tbName)){
        if(not existsDatabase(dbName)){
            db = database(dbName, RANGE, date(datetimeAdd(1980.01M,0..80*12,'M')), engine = 'TSDB')
        } else {
            db = database(dbName)
        }
        
        sch = table(1:0, `name`type, [STRING, INT])

        sch.tableInsert('exchange', SYMBOL)
        sch.tableInsert('code', SYMBOL)
        sch.tableInsert('name', SYMBOL)
        sch.tableInsert('product', SYMBOL)
        
        sch.tableInsert('opendate',DATE)
        sch.tableInsert('expiredate',DATE)
        
        sch.tableInsert('option',BOOL)
        sch.tableInsert('call',BOOL)
        sch.tableInsert('underlying',SYMBOL)
        sch.tableInsert('strikeprice',DOUBLE)
        sch.tableInsert('underlyingscale',DOUBLE)
        
        ft = table(1:0, sch.name, sch.type)

        db.createPartitionedTable(
            table=ft, tableName=tbName, 
            partitionColumns=['opendate'],
            sortColumns=['exchange','code','opendate'],
            keepDuplicates=LAST)
    }
    '''
    pool.runTaskAsync(script=script_kline)

def trans_contracts(filename:str, pool:ddb.DBConnectionPool, ctype=0):
    total_contracts = None
    with open(filename, mode="r", encoding="utf-8") as f:
        content = f.read()
        total_contracts = json.loads(content)

    data = list()
    for exchg in total_contracts:
        for code in total_contracts[exchg]:
            item = total_contracts[exchg][code]
            dataItem = dict(
                exchange = exchg,
                code = code,
                name = item["name"],
                product = item["product"]
            )

            if "opendate" in item:
                dataItem["opendate"] = datetime.datetime.strptime(str(item["opendate"]), "%Y%m%d")
                dataItem["expiredate"] = datetime.datetime.strptime(str(item["expiredate"]), "%Y%m%d")
            else:
                dataItem["opendate"] = datetime.datetime(1990, 1, 1)
                dataItem["expiredate"] = datetime.datetime(2060, 12, 31)

            dataItem["ctype"] = ctype

            if "option" in item:
                dataItem["call"] = item['option']['optiontype']==49
                dataItem["underlying"] = item['option']['underlying']
                dataItem["strikeprice"] = item['option']['strikeprice']
                dataItem["underlyingscale"] = item['option']['underlyingscale']
            else:
                dataItem["call"] = True
                dataItem["underlying"] = ""
                dataItem["strikeprice"] = 0.0
                dataItem["underlyingscale"] = 0.0

            data.append(dataItem)

    df_data = pd.DataFrame(data)
    print(df_data)

    appender = ddb.PartitionedTableAppender(dbPath="dfs://BASIC_INFOS", tableName="CodeInfos", partitionColName="opendate", dbConnectionPool=pool)
    appender.append(df_data)

if __name__ == "__main__":

    host="127.0.0.1"
    port=8900
    user='admin'
    pwd='123456'

    pool = ddb.DBConnectionPool(host=host, port=port, userid=user, password=pwd, threadNum=3)

    #ctype，合约类型，0-股票，1-期货，2-商品股指期权，3-ETF， 4-ETF期权, 5-股票指数
    trans_contracts("./stocks.json", pool, ctype=0)
    trans_contracts("./contracts.json", pool, ctype=1)
    trans_contracts("./fut_options.json", pool, ctype=2)
    trans_contracts("./etfs.json", pool, ctype=3)
    trans_contracts("./stk_options.json", pool, ctype=4)