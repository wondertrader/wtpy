# 1、配置04_DataKit/config.ini
# 2、python 04_DataKit.py
# 3、程序自动生成Common/commodities.json  Common/contracts.json
# 4、请注意simnow只能在开盘时间运行
# todo:  statemonitor.json 硬编码无法移到配置文件目录中，等群主发功

from wtpy import WtDtEngine

if __name__ == "__main__":
    #创建一个运行环境，并加入策略
    env = WtDtEngine()
    env.initialize("./04_DataKit/dtcfg.json", "./04_DataKit/logcfgdt.json")
    
    env.run()

    kw = input('press any key to exit\n')