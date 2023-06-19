from wtpy import WtBtEngine,EngineType
from wtpy.apps import WtBtAnalyst

import sys
sys.path.append('../Strategies')
from DualThrust import StraDualThrust

def analyze_with_pyfolio(fund_filename:str, capital:float=500000):
    import pyfolio as pf
    import pandas as pd
    from datetime import datetime
    import matplotlib.pyplot as plt

    # 读取每日资金
    df = pd.read_csv(fund_filename)
    df['date'] = df['date'].apply(lambda x : datetime.strptime(str(x), '%Y%m%d'))
    df = df.set_index(df["date"])

    # 将资金转换成收益率
    ay = df['dynbalance'] + capital
    rets = ay.pct_change().fillna(0).tz_localize('UTC')

    # 调用pyfolio进行分析
    pf.create_full_tear_sheet(rets)

    # 如果在jupyter，不需要执行该语句
    plt.show()

if __name__ == "__main__":
    #创建一个运行环境，并加入策略
    engine = WtBtEngine(EngineType.ET_CTA)
    engine.init('../common/', "configbt.yaml")
    engine.configBacktest(201909100930,201912011500)
    engine.configBTStorage(mode="csv", path="../storage/")

    # 注册自定义连续合约规则
    # engine.registerCustomRule(ruleTag="0001", filename="../common/hots.json")
    
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
    # 主力合约回测
    straInfo = StraDualThrust(name='pydt_IF', code="CFFEX.IF.HOT", barCnt=50, period="m5", days=30, k1=0.1, k2=0.1, isForStk=False)
     
    # 自定义连续合约回测
    # 测试的时候把storage中的CFFEX.IF.HOT_m5.csv复制一份，改名为CFFEX.IF.0001_m5.csv即可
    # straInfo = StraDualThrust(name='pydt_IF', code="CFFEX.IF.0001", barCnt=50, period="m5", days=30, k1=0.1, k2=0.1, isForStk=False)
    # 
    
    '''
    @slippage       滑点大小
    @incremental    是否增量回测, 默认为False, 如果为True, 则会自动根据策略ID到output_bt目录下加载对应的数据
    @isRatioSlp     滑点是否是比例, 默认为False, 如果为True, 则slippage为万分比
    '''
    engine.set_cta_strategy(straInfo, slippage=0, isRatioSlp=False, incremental=False)

    #开始运行回测
    engine.run_backtest(bAsync=False)

    if True:
        #创建绩效分析模块
        analyst = WtBtAnalyst()
        #将回测的输出数据目录传递给绩效分析模块
        analyst.add_strategy("pydt_IF", folder="./outputs_bt/", init_capital=500000, rf=0.02, annual_trading_days=240)
        #运行绩效模块
        analyst.run_new()
    else:
        #使用pyfolio进行绩效分析
        analyze_with_pyfolio("./outputs_bt/pydt_IF/funds.csv")

    kw = input('press any key to exit\n')
    engine.release_backtest()