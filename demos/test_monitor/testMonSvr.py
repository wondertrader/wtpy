from wtpy.monitor import WtMonSvr

# 如果要配置在线回测，则必须要配置WtDtServo
# from wtpy import WtDtServo
# dtServo = WtDtServo()
# dtServo.setBasefiles(commfile="../common/commodities.json", 
#                 contractfile="../common/contracts.json", 
#                 holidayfile="../common/holidays.json", 
#                 sessionfile="../common/sessions.json", 
#                 hotfile="../common/hots.json")
# dtServo.setStorage("../storage/")
# dtServo.commitConfig()

# 创建监控服务，deploy_dir是策略组合部署的根目录
svr = WtMonSvr(deploy_dir="./deploy")

# 将回测管理模块提交给WtMonSvr
# from wtpy.monitor import WtBtMon
# btMon = WtBtMon(deploy_folder="./bt_deploy", logger=svr.logger) # 创建回测管理器
# svr.set_bt_mon(btMon) # 设置回测管理器
# svr.set_dt_servo(dtServo) # 设置dtservo

# 启动服务
svr.run(port=8099, bSync=False)
input("press enter key to exit\n")

# PC版控制台入口地址： http://127.0.0.1:8099/console
# 移动版控制台入口地址： http://127.0.0.1:8099/mobile