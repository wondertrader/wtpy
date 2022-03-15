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
dtServo.setBasefiles(commfile="../common/commodities.json", 
                contractfile="../common/contracts.json", 
                holidayfile="../common/holidays.json", 
                sessionfile="../common/sessions.json", 
                hotfile="../common/hots.json")
dtServo.setStorage("../storage/")
dtServo.commitConfig()

svr = WtMonSvr(deploy_dir="./deploy")
btMon = WtBtMon(deploy_folder="./bt_deploy", logger=svr.logger)
svr.set_bt_mon(btMon)
svr.set_dt_servo(dtServo)
svr.run(port=8099, bSync=False)
input("press enter key to exit\n")