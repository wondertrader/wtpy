from wtpy import ContractLoader,LoaderType
import os

os.chdir('d:\\aa')
loader = ContractLoader(lType = LoaderType.LT_CTP)
loader.start(cfgfile="config.ini")
input("press enter key to exit\n")