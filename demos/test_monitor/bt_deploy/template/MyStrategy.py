from wtpy import BaseCtaStrategy
from wtpy import CtaContext

class MyStrategy(BaseCtaStrategy):
    
    def __init__(self, name:str, code:str):
        BaseCtaStrategy.__init__(self, name)
        self.__code__ = code

    def on_init(self, context:CtaContext):
        context.stra_log_text("My strategy inited")
    
    def on_calculate(self, context:CtaContext):
        pass

    def on_tick(self, context:CtaContext, stdCode:str, newTick:dict):
        pass