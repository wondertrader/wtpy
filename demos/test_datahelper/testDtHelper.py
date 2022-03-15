from wtpy.wrapper import WtDataHelper
from wtpy.WtCoreDefs import WTSBarStruct, WTSTickStruct
from ctypes import POINTER
from wtpy.SessionMgr import SessionMgr
import pandas as pd

dtHelper = WtDataHelper()

def test_store_bars():
    print("loading %s bars of %s from extended loader" % (period, stdCode))

    df = pd.read_csv('../storage/csv/CFFEX.IF.HOT_m5.csv')
    df = df.rename(columns={
        '<Date>':'date',
        ' <Time>':'time',
        ' <Open>':'open',
        ' <High>':'high',
        ' <Low>':'low',
        ' <Close>':'close',
        ' <Volume>':'vol',
        })
    df['date'] = df['date'].astype('datetime64').dt.strftime('%Y%m%d').astype('int64')
    df['time'] = (df['date']-19900000)*10000 + df['time'].str.replace(':', '').str[:-2].astype('int')

    BUFFER = WTSBarStruct*len(df)
    buffer = BUFFER()

    def assign(procession, buffer):
        tuple(map(lambda x: setattr(buffer[x[0]], procession.name, x[1]), enumerate(procession)))


    df.apply(assign, buffer=buffer)
    print(df)
    print(buffer[0].to_dict)
    print(buffer[-1].to_dict)

    dtHelper.store_bars(barFile="./CFFEX.IF.HOT_m5.bin", firstBar=buffer, count=len(df), period="m5")

def test_resample():
    # 测试重采样
    sessMgr = SessionMgr()
    sessMgr.load("sessions.json")
    sInfo = sessMgr.getSession("SD0930")
    ret = dtHelper.resample_bars("IC2009.dsb",'m1',5,202001010931,202009181500,sInfo)
    print(ret)