import numpy as np

# from gym import Env
# from gym.spaces import Box

from wtpy.CtaContext import CtaContext
from wtpy.StrategyDefs import BaseCtaStrategy
from wtpy.WtBtEngine import WtBtEngine, EngineType

class EnvStrategy(BaseCtaStrategy):
    def __init__(self, name:str, code:str, period:str, count:int):
        super().__init__(name=name)

        self.__code__:str = code
        self.__period__:str = period
        self.__count__:int = count

        self.obs = 1
        self.reward = 1
        self.action = 0

    def on_init(self, context:CtaContext):
        #先订阅实时数据
        context.stra_get_bars(self.__code__, self.__period__, self.__count__, True)

    def on_calculate(self, context: CtaContext):
        print('on_calculate action%s'%self.action)

        # todo 输出 obs和reward 给外部
        self.obs += 1
        self.reward += 1

    def on_calculate_done(self, context: CtaContext):
        print('on_calculate_done action%s'%self.action)

    def on_backtest_end(self, context: CtaContext):
        print('on_backtest_end')



class WtEnv():
    def __init__(self) -> None:
        super().__init__()

        self._iter_ = 0
        self._strategy = None

        #创建一个运行环境
        self._engine_:WtBtEngine = WtBtEngine(EngineType.ET_CTA)
        self._engine_.init('../common/', "configbt.yaml")
        self._engine_.configBacktest(201909100930,201912011500)
        self._engine_.configBTStorage(mode="csv", path="../storage/")
        self._engine_.commitBTConfig()

    def reset(self) -> np.ndarray:
        self.close()
        self._iter_ += 1

        #创建一个策略，并加入运行环境
        self._strategy = EnvStrategy(name='EnvStrategy_%s'%self._iter_, code='CFFEX.IF.HOT', period='m5', count=60)
        # 设置策略的时候，一定要安装钩子
        self._engine_.set_cta_strategy(self._strategy, slippage=1, hook=True)
        # 回测一定要异步运行，不然这里不会返回，回测结束了才会返回
        self._engine_.run_backtest(bAsync=True)

        self._strategy.action = 0
        self._engine_.cta_step()

        #todo 怎么从on_calc里拿到obs和reward
        return self._strategy.obs

    def step(self, action:np.ndarray) -> tuple:
        # 单步触发oncalc
        bSucc = self._engine_.cta_step()

        obs = self._strategy.obs # todo 怎么从取得oncalc里的obs数据
        reward = self._strategy.reward # todo 怎么从取得reward里的obs数据
        done = True if np.random.randint(1, 100)==99 else False #是否结束
        done = not bSucc
        return obs, reward, done, {}
        print("state updated")

         #todo  怎么把action传入oncalc里
        self._strategy.action = action
        print("action updated, Go!")
        
        bSucc = self._engine_.cta_step()
        print("action executed")

        return obs, reward, done, {}
    
    def close(self) -> None:
        self._engine_.stop_backtest()

    def __del__(self):
        self._engine_.release_backtest()

if __name__ == '__main__':
    # env = DemoEnv()
    # done = False
    # obs = env.reset()
    # while not done:
    #     obs, reward, done, info = env.step(1)
    #     print(obs, reward, done, info)
    # env.close()

    env = WtEnv()
    for i in range(10): #模拟训练10次
        print('第%s次训练'%i)
        obs = env.reset()
        done = False
        action = 0
        while not done:
            action += 1 #模拟智能体产生动作
            obs, reward, done, info = env.step(action)
            print('obs%s'%obs, 'reward%s'%reward, done, info)
    env.close()