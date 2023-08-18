from wtpy.monitor import WtBtSnooper
from wtpy import WtDtServo

def testBtSnooper():    

    dtServo = WtDtServo()
    # 这里配置的是基础数据文件目录
    dtServo.setBasefiles(folder="E:\\gitlocal\\MyStras\\CTA\\common\\")

    # 这里配置的是datakit落地的数据目录
    dtServo.setStorage(path='E:/storage/')

    snooper = WtBtSnooper(dtServo)
    snooper.run_as_server(port=8081, host="0.0.0.0")

testBtSnooper()
# 运行了服务以后，在浏览器打开以下网址即可使用
# http://127.0.0.1:8081/backtest/backtest.html
