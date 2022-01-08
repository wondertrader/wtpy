from wtpy import ContractLoader,LoaderType

loader = ContractLoader(lType = LoaderType.LT_CTP)
loader.start(cfgfile="config.ini")
input("press enter key to exit\n")