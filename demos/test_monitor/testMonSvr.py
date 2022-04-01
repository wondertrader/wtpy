'''
Descripttion: Automatically generated file comment
version: 
Author: Wesley
Date: 2020-08-26 14:36:49
LastEditors: Wesley
LastEditTime: 2021-08-31 17:18:07
'''
from wtpy.monitor import WtMonSvr, WtBtMon
from wtpy import WtDtServo

dtServo = WtDtServo()
# 设置基础文件路径
dtServo.setBasefiles(commfile="../common/commodities.json", 
                contractfile="../common/contracts.json", 
                holidayfile="../common/holidays.json", 
                sessionfile="../common/sessions.json", 
                hotfile="../common/hots.json")

# 设置行情数据存储路径，这个一定是datakit落地的目录
dtServo.setStorage("../storage/")
dtServo.commitConfig()

# 创建监控服务，deploy_dir是策略组合部署的根目录
svr = WtMonSvr(deploy_dir="./deploy")

# 创建回测管理器
btMon = WtBtMon(deploy_folder="./bt_deploy", logger=svr.logger)

# 设置回测管理器
svr.set_bt_mon(btMon)

# 设置dtservo
svr.set_dt_servo(dtServo)

# 启动服务
svr.run(port=8099, bSync=False)
input("press enter key to exit\n")