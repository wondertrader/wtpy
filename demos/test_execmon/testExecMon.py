from wtpy import WtExecApi
import time

def test_exec_mon():
    api = WtExecApi()
    api.initialize(logCfg = "logcfgexec.yaml")
    api.config(cfgfile = 'cfgexec.yaml')
    api.run()

    time.sleep(10)
    api.set_position("CFFEX.IF.HOT", 1)

test_exec_mon()
