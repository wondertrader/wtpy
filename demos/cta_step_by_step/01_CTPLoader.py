# 1、配置01_CTPLoader/config.ini
# 2、python 01_CTPLoader.py
# 3、程序自动生成common/commodities.json  common/contracts.json
# 4、请注意simnow只能在开盘时间运行
# 5、其实这一步不运行也没问题
# todo:  common/holidays.json common/hots.json common/sessions.json 三个文件的自动生成等群主发功

from wtpy import CTPLoader

loader = CTPLoader(folder='./01_CTPLoader', isMini=False)
loader.start()
input("press enter key to exit\n")