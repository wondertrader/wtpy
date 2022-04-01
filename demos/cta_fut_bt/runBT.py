from wtpy import WtBtEngine,EngineType
from wtpy.apps import WtBtAnalyst

from Strategies.DualThrust import StraDualThrust

if __name__ == "__main__":
    #创建一个运行环境，并加入策略
    engine = WtBtEngine(EngineType.ET_CTA)
    engine.init('../common/', "configbt.yaml")
    engine.configBacktest(201909100930,201912011500)
    engine.configBTStorage(mode="csv", path="../storage/")
    engine.commitBTConfig()

    '''
    创建DualThrust策略的一个实例
    name    策略实例名称
    code    回测使用的合约代码
    barCnt  要拉取的K线条数
    period  要使用的K线周期，m表示分钟线
    days    策略算法参数，算法引用的历史数据条数
    k1      策略算法参数，上边界系数
    k2      策略算法参数，下边界系数
    isForStk    DualThrust策略用于控制交易品种的代码
    '''
    straInfo = StraDualThrust(name='pydt_IF', code="CFFEX.IF.HOT", barCnt=50, period="m5", days=30, k1=0.1, k2=0.1, isForStk=False)
    engine.set_cta_strategy(straInfo)

    #开始运行回测
    engine.run_backtest(bAsync=False)

    #创建绩效分析模块
    analyst = WtBtAnalyst()
    #将回测的输出数据目录传递给绩效分析模块
    analyst.add_strategy("pydt_IF", folder="./outputs_bt/pydt_IF/", init_capital=500000, rf=0.02, annual_trading_days=240)
    #运行绩效模块
    analyst.run_new()

    kw = input('press any key to exit\n')
    engine.release_backtest()