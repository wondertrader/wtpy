import dolphindb as ddb
import datetime
from wtpy.wrapper import WtDataHelper

import os
import logging

logging.basicConfig(filename='dsb_to_ddb.log', level=logging.INFO, filemode="a", 
    format='[%(asctime)s - %(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

console = logging.StreamHandler()
console.setLevel(logging.INFO)
# 设置日志打印格式
formatter = logging.Formatter(fmt="[%(asctime)s - %(levelname)s] %(message)s", datefmt='%m-%d %H:%M:%S')
console.setFormatter(formatter)
# 将定义好的console日志handler添加到root logger
logging.getLogger('').addHandler(console)

dtHelper = WtDataHelper()

ddb_kline_order = ["exchange","code", "trading_date", "bartime", "period", "open", "high", "low", "close", "settle", "volume", "turnover", "open_interest", "diff_interest"]
ddb_tick_order = ['exchange', 'code', 'trading_date', 'action_time',  'price', 'open', 'high', 'low', 'settle',
       'upper_limit', 'lower_limit', 'volume', 'turnover', 'open_interest',
        'bp1', 'bp2', 'bp3', 'bp4', 'bp5', 'ap1', 'ap2', 'ap3',
       'ap4', 'ap5', 'bq1', 'bq2', 'bq3', 'bq4', 'bq5', 'aq1', 'aq2', 'aq3',
       'aq4', 'aq5']

def check_table(pool:ddb.DBConnectionPool):
    script_kline = '''
    dbName = "dfs://FUT_KLINES"
    tbName = "Klines"

    if( not existsTable(dbName, tbName)){
        if(not existsDatabase(dbName)){
            db1 = database("", RANGE, date(datetimeAdd(1980.01M,0..80*12,'M')))//
            db2 = database("", HASH, [SYMBOL, 20])//hash20
            db = database(dbName, COMPO, [db1,db2], engine='TSDB')//
        } else {
            db = database(dbName)
        }
        
        sch = table(1:0, `name`type, [STRING, INT])

        sch.tableInsert('exchange', SYMBOL)
        sch.tableInsert('code', SYMBOL)
        
        sch.tableInsert('trading_date',DATE)
        sch.tableInsert('bartime',DATETIME)
        sch.tableInsert('period',INT)
        
        sch.tableInsert('open',DOUBLE)
        sch.tableInsert('high',DOUBLE)
        sch.tableInsert('low',DOUBLE)
        sch.tableInsert('close',DOUBLE)
        sch.tableInsert('settle',DOUBLE)
        
        sch.tableInsert('volume',DOUBLE)
        sch.tableInsert('turnover',DOUBLE)
        sch.tableInsert('open_interest',DOUBLE)
        sch.tableInsert('diff_interest',DOUBLE)
        
        ft = table(1:0, sch.name, sch.type)
        db.createPartitionedTable(table=ft, tableName=tbName, partitionColumns=
            ["trading_date", "code"], sortColumns=
            ["exchange","code", "period","bartime"], keepDuplicates=LAST)
    }
    '''
    pool.runTaskAsync(script=script_kline)

    script_tick = '''
    tbName = "Ticks"
    dbName = "dfs://FUT_TICKS"

    if( not existsTable(dbName, tbName)){
        if(not existsDatabase(dbName)){
            db1 = database("", VALUE, 2023.01.01..2024.01.01)//
            db2 = database("", HASH, [SYMBOL, 20])//hash20
            db = database(dbName, COMPO, [db1,db2], engine='TSDB')//
        } else {
            db = database(dbName)
        }
        
        sch = table(1:0, `name`type, [STRING, INT])

        sch.tableInsert('exchange', SYMBOL)
        sch.tableInsert('code', SYMBOL)
        
        sch.tableInsert('trading_date',DATE)
        sch.tableInsert('action_time',DATETIME)
        
        sch.tableInsert('price',DOUBLE)
        sch.tableInsert('open',DOUBLE)
        sch.tableInsert('high',DOUBLE)
        sch.tableInsert('low',DOUBLE)
        sch.tableInsert('settle',DOUBLE)
        
        sch.tableInsert('upper_limit',DOUBLE)
        sch.tableInsert('lower_limit',DOUBLE)
        
        sch.tableInsert('volume',DOUBLE)
        sch.tableInsert('turnover',DOUBLE)
        sch.tableInsert('open_interest',DOUBLE)
        
        sch.tableInsert('bp1',DOUBLE)
        sch.tableInsert('bp2',DOUBLE)
        sch.tableInsert('bp3',DOUBLE)
        sch.tableInsert('bp4',DOUBLE)
        sch.tableInsert('bp5',DOUBLE)
        
        sch.tableInsert('ap1',DOUBLE)
        sch.tableInsert('ap2',DOUBLE)
        sch.tableInsert('ap3',DOUBLE)
        sch.tableInsert('ap4',DOUBLE)
        sch.tableInsert('ap5',DOUBLE)
        
        sch.tableInsert('bq1',DOUBLE)
        sch.tableInsert('bq2',DOUBLE)
        sch.tableInsert('bq3',DOUBLE)
        sch.tableInsert('bq4',DOUBLE)
        sch.tableInsert('bq5',DOUBLE)
        
        sch.tableInsert('aq1',DOUBLE)
        sch.tableInsert('aq2',DOUBLE)
        sch.tableInsert('aq3',DOUBLE)
        sch.tableInsert('aq4',DOUBLE)
        sch.tableInsert('aq5',DOUBLE)
        
        ft = table(1:0, sch.name, sch.type)

        db.createPartitionedTable(table=ft, tableName=tbName, partitionColumns=
        ["trading_date", "code"], sortColumns=
        ["exchange","code","action_time"], keepDuplicates=LAST)
    }
    '''
    pool.runTaskAsync(script_tick)

def trans_dsb_bars(exchg:str, code:str, filename:str, period:str, pool:ddb.DBConnectionPool):
    npBars = dtHelper.read_dsb_bars(filename, period=='d1')
    df_bars = npBars.to_df()
    df_bars.rename(columns={
        "date":"trading_date",
        "diff":"diff_interest"
    }, inplace=True)
    df_bars["exchange"] = exchg
    df_bars["code"] = code
    df_bars["period"] = 0 if period=='d1' else 1 if period=='m1' else 2
    df_bars = df_bars[ddb_kline_order]

    df_bars["trading_date"] = df_bars["trading_date"].apply(lambda x : datetime.datetime.strptime(str(x), "%Y%m%d"))
    if period=='d1':
        df_bars["bartime"] = df_bars["trading_date"].copy()
    else:
        df_bars["bartime"] = df_bars["bartime"].apply(lambda x : datetime.datetime.strptime(str(x), "%Y%m%d%H%M"))

    appender = ddb.PartitionedTableAppender(dbPath="dfs://FUT_KLINES", tableName="Klines", partitionColName="trading_date", dbConnectionPool=pool)
    appender.append(df_bars)

def trans_dsb_ticks(exchg:str, code:str, filename:str, pool:ddb.DBConnectionPool):
    npTicks = dtHelper.read_dsb_ticks(filename)
    df_ticks = npTicks.to_df()
    df_ticks.drop(columns = [
        "bid_price_5",
        "bid_price_6",
        "bid_price_7",
        "bid_price_8",
        "bid_price_9",
        "ask_price_5",
        "ask_price_6",
        "ask_price_7",
        "ask_price_8",
        "ask_price_9",
        "bid_qty_5",
        "bid_qty_6",
        "bid_qty_7",
        "bid_qty_8",
        "bid_qty_9",
        "ask_qty_5",
        "ask_qty_6",
        "ask_qty_7",
        "ask_qty_8",
        "ask_qty_9",
        "volume",
        "turn_over",
        "diff_interest"
        ], inplace=True)
    df_ticks.rename(columns={
        "bid_price_0":"bp1",
        "bid_price_1":"bp2",
        "bid_price_2":"bp3",
        "bid_price_3":"bp4",
        "bid_price_4":"bp5",
        "ask_price_0":"ap1",
        "ask_price_1":"ap2",
        "ask_price_2":"ap3",
        "ask_price_3":"ap4",
        "ask_price_4":"ap5",
        "bid_qty_0":"bq1",
        "bid_qty_1":"bq2",
        "bid_qty_2":"bq3",
        "bid_qty_3":"bq4",
        "bid_qty_4":"bq5",
        "ask_qty_0":"aq1",
        "ask_qty_1":"aq2",
        "ask_qty_2":"aq3",
        "ask_qty_3":"aq4",
        "ask_qty_4":"aq5",
        "exchg":"exchange",
        "total_volume":"volume",
        "total_turnover":"turnover",
        "settle_price":"settle"
    }, inplace=True)
    df_ticks["exchange"] = exchg
    df_ticks["code"] = code
    df_ticks["action_time"] = df_ticks["time"].apply(lambda x : datetime.datetime(x//10000000000000, x%10000000000000//100000000000, x%100000000000//1000000000,
                                                                                  x%1000000000//10000000, x%10000000//100000, x%100000//1000, x%1000*1000))
    df_ticks["trading_date"] = df_ticks["trading_date"].apply(lambda x : datetime.datetime.strptime(str(x), "%Y%m%d"))
    df_ticks.drop(columns=["time","action_date","pre_close","pre_settle","pre_interest"], inplace=True)

    appender = ddb.PartitionedTableAppender(dbPath="dfs://FUT_TICKS", tableName="Ticks", partitionColName="trading_date", dbConnectionPool=pool)
    appender.append(df_ticks[ddb_tick_order])

# test_dsb_bars()
def trans_his_ddb(his_root:str, host:str, port:int, user:str, pwd:str):
    pool = ddb.DBConnectionPool(host, port, 3, user, pwd)

    # 历史K线
    kline_tasks = []
    subdirs = ["day","min1", "min5"]
    for subdir in subdirs:
        subpath = os.path.abspath(os.path.join(his_root, subdir))
        if not os.path.exists(subpath):
            continue
        exchgs = os.listdir(subpath)
        for exchg in exchgs:
            exchgpath = os.path.abspath(os.path.join(subpath, exchg))
            files = os.listdir(exchgpath)
            for fname in files:
                if fname[-4:] != '.dsb':
                    continue

                filepath = os.path.abspath(os.path.join(exchgpath, fname))
                code = fname[:-4]
                kline_tasks.append(dict(
                    exchg = exchg,
                    code = code,
                    period = "d1" if subdir=='day' else 'm1' if subdir=='min1' else 'min5',
                    filepath = filepath
                ))

    logging.info(f"一共扫描出{len(kline_tasks)}个历史K线文件，开始迁移...")
    proced = 0
    for item in kline_tasks:
        trans_dsb_bars(item["exchg"], item["code"], item["filepath"], item["period"], pool)
        proced += 1
        logging.info(f"历史K线迁移进度{proced}/{len(kline_tasks)}")


    tick_tasks = []
    subpath = os.path.join(his_root, "ticks")
    if os.path.exists(subpath):
        exchgs = os.listdir(subpath)
        for exchg in exchgs:
            exchgpath = os.path.abspath(os.path.join(subpath, exchg))
            tdates = os.listdir(exchgpath)
            for tdate in tdates:
                tdatepath = os.path.abspath(os.path.join(exchgpath, tdate))
                files = os.listdir(tdatepath)
                for fname in files:
                    if fname[-4:] != '.dsb':
                        continue

                    filepath = os.path.abspath(os.path.join(tdatepath, fname))
                    code = fname[:-4]
                    tick_tasks.append(dict(
                        exchg = exchg,
                        code = code,
                        filepath = filepath,
                        tdate = tdate
                    ))

        logging.info(f"一共扫描出{len(tick_tasks)}个历史Tick文件，开始迁移...")
        proced = 0
        for item in tick_tasks:
            trans_dsb_ticks(item["exchg"], item["code"], item["filepath"], pool)
            proced += 1
            logging.info(f"历史Tick迁移进度{proced}/{len(kline_tasks)}")

if __name__ == "__main__":
    trans_his_ddb("../storage/his", host="127.0.0.1", port=8900, user='admin', pwd='123456')