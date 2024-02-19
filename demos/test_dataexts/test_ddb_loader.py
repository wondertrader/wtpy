import time
from wtpy.ExtModuleDefs import BaseExtDataLoader
from ctypes import POINTER
from wtpy.WtCoreDefs import WTSBarStruct, WTSTickStruct

import pandas as pd

import dolphindb as ddb

from wtpy import WtEngine,WtBtEngine,EngineType
from wtpy.apps import WtBtAnalyst
from Strategies.DualThrust import StraDualThrust

class DDBDataLoader(BaseExtDataLoader):
    def __init__(self, host:str, port:int, user:str, pwd:str):
        BaseExtDataLoader.__init__(self)
        self.ddb_params = dict(
            host=host, 
            port=port, 
            userid=user, 
            password=pwd
            )

        self._check_table()

    def _check_table(self):

        pool = ddb.DBConnectionPool(threadNum=3, **self.ddb_params)

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
    
    def load_final_his_bars(self, stdCode:str, period:str, feeder) -> bool:
        '''
        加载历史K线（回测、实盘）
        @stdCode    合约代码，格式如CFFEX.IF.2106
        @period     周期，m1/m5/d1
        @feeder     回调函数，feed_raw_bars(bars:POINTER(WTSBarStruct), count:int, factor:double)
        '''
        print(f"loading {period} bars of {stdCode} from extended dolphindb loader")

        ay = stdCode.split('.')
        exchg = ay[0]
        if len(ay) > 2:
            pid = ay[1]
            month = ay[2]
            if month in ['HOT','2ND']:
                code = f"{pid}.{month}" # 这里主要针对主力合约
            else:
                code = f"{pid}{month}"  #郑商所的月份是少一位的，但是我们要在数据库里处理成4位，不然时间长了就会有问题            
        else:
            code = ay[1]    # 如果只有两段，那么就直接使用

        period = 0 if period=='d1' else 1 if period=='m1' else 2

        s = ddb.session()
        s.connect(**self.ddb_params)
        script = f'''
        db = database( "dfs://FUT_KLINES");
        tb = loadTable(db, `Klines);
        select * from tb where exchange='{exchg}' and code='{code}' and period={period};
        '''
        df = s.run(script)
        df['date'] = df['trading_date'].astype('datetime64[ns]').dt.strftime('%Y%m%d').astype('int64')
        df['time'] = df['bartime'].astype('datetime64[ns]').dt.strftime('%Y%m%d%H%M').astype('int64')-199000000000
        df.rename(columns={
            'diff_interest':'diff'
            }, inplace=True)
        df.drop(columns=['trading_date','bartime','period','exchange','code'], inplace=True)

        BUFFER = WTSBarStruct*len(df)
        buffer = BUFFER()

        def assign(procession, buffer):
            tuple(map(lambda x: setattr(buffer[x[0]], procession.name, x[1]), enumerate(procession)))

        df.apply(assign, buffer=buffer)
        print(df)
        print(buffer[0].to_dict())

        feeder(buffer, len(df))
        return True

    def load_his_ticks(self, stdCode:str, uDate:int, feeder) -> bool:
        '''
        加载历史K线（只在回测有效，实盘只提供当日落地的）
        @stdCode    合约代码，格式如CFFEX.IF.2106
        @uDate      日期，格式如yyyymmdd
        @feeder     回调函数，feed_raw_ticks(ticks:POINTER(WTSTickStruct), count:int)
        '''
        print(f"loading ticks on {uDate} of {stdCode} from extended dolphindb loader")

        ay = stdCode.split('.')
        exchg = ay[0]
        if len(ay) > 2:
            pid = ay[1]
            month = ay[2]
            if month in ['HOT','2ND']:
                code = f"{pid}.{month}" # 这里主要针对主力合约
            else:
                code = f"{pid}{month}"  #郑商所的月份是少一位的，但是我们要在数据库里处理成4位，不然时间长了就会有问题            
        else:
            code = ay[1]    # 如果只有两段，那么就直接使用

        uDate = str(uDate)

        s = ddb.session()
        s.connect(**self.ddb_params)

        script = f'''
        db = database( "dfs://FUT_TICKS");
        tb = loadTable(db, `Ticks);
        select * from tb where trading_date={uDate[:4]}.{uDate[4:6]}.{uDate[6:]} and exchange='{exchg}' and code='{code}';
        '''
        df = s.run(script)
        df.rename(columns={
            "exchange":"exchg",
            "volume":"total_volume",
            "turnover":"total_turnover",
            "bp1":"bid_price_0",
            "bp2":"bid_price_1",
            "bp3":"bid_price_2",
            "bp4":"bid_price_3",
            "bp5":"bid_price_4",

            "ap1":"ask_price_0",
            "ap2":"ask_price_1",
            "ap3":"ask_price_2",
            "ap4":"ask_price_3",
            "ap5":"ask_price_4",

            "bq1":"bid_qty_0",
            "bq2":"bid_qty_1",
            "bq3":"bid_qty_2",
            "bq4":"bid_qty_3",
            "bq5":"bid_qty_4",

            "aq1":"ask_qty_0",
            "aq2":"ask_qty_1",
            "aq3":"ask_qty_2",
            "aq4":"ask_qty_3",
            "aq5":"ask_qty_4"
        }, inplace=True)

        df['exchg'] = df['exchg'].apply(lambda x: x.encode('utf-8'))
        df['code'] = df['code'].apply(lambda x: x.encode('utf-8'))
        df['trading_date'] = df['trading_date'].astype('datetime64[ns]').dt.strftime('%Y%m%d').astype('int64')
        df['action_date'] = df['action_time'].astype('datetime64[ns]').dt.strftime('%Y%m%d').astype('int64')
        df['action_time'] = df['action_time'].astype('datetime64[ns]').dt.strftime('%H%M%S%f').astype('int64')//1000
        print(df)

        BUFFER = WTSTickStruct*len(df)
        buffer = BUFFER()

        def assign(procession, buffer):
            tuple(map(lambda x: setattr(buffer[x[0]], procession.name, x[1]), enumerate(procession)))

        df.apply(assign, buffer=buffer)
        print(buffer[0].to_dict())

        feeder(buffer, len(df))
        return True

def test_in_bt():
    engine = WtBtEngine(EngineType.ET_CTA)

    # 初始化之前，向回测框架注册加载器
    engine.set_extended_data_loader(loader=DDBDataLoader(host="127.0.0.1", port=8900, user='admin', pwd='123456'), bAutoTrans=False)

    engine.init('../common/', "configbt.yaml")

    engine.configBacktest(201909100930,201912011500)
    engine.configBTStorage(mode="csv", path="../storage/")
    engine.commitBTConfig()

    straInfo = StraDualThrust(name='pydt_IF', code="CFFEX.IF.HOT", barCnt=50, period="m5", days=30, k1=0.1, k2=0.1, isForStk=False)
    engine.set_cta_strategy(straInfo)

    engine.run_backtest()

    analyst = WtBtAnalyst()
    analyst.add_strategy("pydt_IF", folder="./outputs_bt/pydt_IF/", init_capital=500000, rf=0.02, annual_trading_days=240)
    analyst.run()

    kw = input('press any key to exit\n')
    engine.release_backtest()

def test_in_rt():
    engine = WtEngine(EngineType.ET_CTA)

    # 初始化之前，向实盘框架注册加载器
    engine.set_extended_data_loader(DDBDataLoader(host="127.0.0.1", port=8900, user='admin', pwd='123456'))

    engine.init('../common/', "config.yaml")
    
    straInfo = StraDualThrust(name='pydt_au', code="SHFE.au.HOT", barCnt=50, period="m5", days=30, k1=0.2, k2=0.2, isForStk=False)
    engine.add_cta_strategy(straInfo)

    engine.run()

    print('press ctrl-c to exit')
    try:
    	while True:
            time.sleep(1)
    except KeyboardInterrupt as e:
    	exit(0)

test_in_bt()