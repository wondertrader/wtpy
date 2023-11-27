import time
from wtpy import WtDtEngine

from wtpy.ExtModuleDefs import BaseExtDataDumper

class MyDataDumper(BaseExtDataDumper):
    def __init__(self, id:str):
        BaseExtDataDumper.__init__(self, id)

    def dump_his_bars(self, stdCode:str, period:str, bars, count:int) -> bool:
        '''
        加载历史K线（回测、实盘）
        @stdCode    合约代码，格式如CFFEX.IF.2106
        @period     周期，m1/m5/d1
        @bars       回调函数，WTSBarStruct的指针
        @count      数据条数
        '''
        print("dumping %s bars of %s via extended dumper" % (period, stdCode))
        return True

    def dump_his_ticks(self, stdCode:str, uDate:int, ticks, count:int) -> bool:
        '''
        加载历史K线（只在回测有效，实盘只提供当日落地的）
        @stdCode    合约代码，格式如CFFEX.IF.2106
        @uDate      日期，格式如yyyymmdd
        @ticks      回调函数，WTSTickStruct的指针
        @count      数据条数
        '''
        print("dumping ticks on %d of %s via extended dumper" % (uDate, stdCode))
        return True

def test_ext_dumper():
    #创建一个运行环境，并加入策略
    engine = WtDtEngine()
    engine.add_extended_data_dumper(MyDataDumper("dumper"))
    engine.initialize("dtcfg.yaml", "logcfgdt.yaml")
    
    engine.run(True)

    print('press ctrl-c to exit')
    try:
    	while True:
            time.sleep(1)
    except KeyboardInterrupt as e:
    	exit(0)

test_ext_dumper()