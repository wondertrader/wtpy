from wtpy import WtDtEngine

if __name__ == "__main__":
    #创建一个运行环境，并加入策略
    engine = WtDtEngine()
    engine.initialize("dtcfg.yaml", "logcfgdt.yaml")
    
    engine.run(True)

    kw = input('press any key to exit\n')