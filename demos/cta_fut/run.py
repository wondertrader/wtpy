from wtpy import WtEngine,EngineType
from Strategies.DualThrust import StraDualThrust

from ConsoleIdxWriter import ConsoleIdxWriter

if __name__ == "__main__":
    #创建一个运行环境，并加入策略
    env = WtEngine(EngineType.ET_CTA)
    env.init('../common/', "config.yaml")
    
    straInfo = StraDualThrust(name='pydt_au', code="SHFE.au.HOT", barCnt=50, period="m5", days=30, k1=0.2, k2=0.2, isForStk=False)
    env.add_cta_strategy(straInfo)
    
    idxWriter = ConsoleIdxWriter()
    env.set_writer(idxWriter)

    env.run()

    kw = input('press any key to exit\n')