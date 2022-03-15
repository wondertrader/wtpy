import json
from wtpy import BaseIndexWriter

class ConsoleIdxWriter(BaseIndexWriter):
    '''
    Mysql指标数据写入器
    '''

    def __init__(self):
        pass

    def write_indicator(self, id, tag, time, data):
        print('策略%s的指标输出，标记：%s，时间：%d，数据：%s' % (id, tag, time, json.dumps(data)))