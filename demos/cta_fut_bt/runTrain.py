import numpy as np

from gym import Env
from gym.spaces import Box

from wtpy.CtaContext import CtaContext
from wtpy.StrategyDefs import BaseCtaStrategy
from wtpy.WtBtEngine import WtBtEngine, EngineType

class EnvStrategy(BaseCtaStrategy):
    def __init__(self, name:str, code:str, period:str, count:int):
        super().__init__(name=name)

        self.__code__:str = code
        self.__period__:str = period
        self.__count__:int = count

    def on_init(self, context:CtaContext):
        #先订阅实时数据
        context.stra_get_bars(self.__code__, self.__period__, self.__count__, True)

    def on_calculate(self, context: CtaContext):
        # 输出 obs和reward
        # 获得 action
        pass

class DemoEnv(Env):
    def __init__(self) -> None:
        #这是必须定义的，否则大部分rl框架会检测不通过
        self.observation_space:Box = Box(low=-np.inf, high=np.inf, shape=(4, ), dtype=np.float64)
        self.action_space:Box = Box(low=-1, high=1, shape=(1, ), dtype=np.float64)
        self._iter_ = 0

    def reset(self) -> np.ndarray:
        self._iter_ += 1
        return self.observation_space.sample() #随机模拟

    def step(self, action:np.ndarray) -> tuple:
        obs = self.observation_space.sample() #随机模拟
        reward = 1 #奖励
        done = True if np.random.randint(1, 100)==99 else False #是否结束
        return obs, reward, done, {}

    def close(self) -> None:
        pass

class WtEnv(DemoEnv):
    def __init__(self) -> None:
        super().__init__()

        #创建一个运行环境
        self._engine_:WtBtEngine = WtBtEngine(EngineType.ET_CTA)
        self._engine_.init('./common/', "configbt.json")
        self._engine_.configBacktest(201909100930,201912011500)
        self._engine_.configBTStorage(mode="csv", path="./storage/")
        self._engine_.commitBTConfig()

    def reset(self) -> np.ndarray:
        self._iter_ += 1
        #创建一个策略，并加入运行环境
        strategy = EnvStrategy(name='EnvStrategy_%s'%self._iter_, code='CFFEX.IF.HOT', period='m5', count=60)
        self._engine_.set_cta_strategy(strategy, slippage=1)
        self._engine_.run_backtest()

        #todo 怎么从on_calc里拿到obs和reward

    def step(self, action:np.ndarray) -> tuple:
        #todo 怎么把action传给on_calc并拿到下次obs和reward

        obs = self.observation_space.sample() #随机模拟
        reward = 1 #奖励
        done = True if np.random.randint(1, 100)==99 else False #是否结束
        return obs, reward, done, {}
    
    def close(self) -> None:
        self._engine_.stop_backtest()

    def __del__(self):
        self._engine_.release_backtest()

if __name__ == '__main__':
    env = DemoEnv()
    done = False
    obs = env.reset()
    while not done:
        obs, reward, done, info = env.step(env.action_space.sample)
        print(obs, reward, done, info)
    env.close()

    env = WtEnv()
    done = False
    obs = env.reset()
    # while not done:
    #     obs, reward, done, info = env.step(env.action_space.sample)
    #     print(obs, reward, done, info)
    env.close()