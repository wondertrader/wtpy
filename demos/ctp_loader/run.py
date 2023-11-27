import time
from wtpy import ContractLoader,LoaderType

loader = ContractLoader(lType = LoaderType.LT_CTP)
print('press ctrl-c to exit')
try:
    loader.start(cfgfile="config.ini")
    while True:
        time.sleep(1)
except KeyboardInterrupt as e:
    exit(0)