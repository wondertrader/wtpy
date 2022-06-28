from wtpy import TraderDumper,DumperSink

class MySink(DumperSink):

    def on_account(self, channelid, curTDate:int, currency, prebalance:float, balance:float, dynbalance:float, 
	        closeprofit:float, dynprofit:float, fee:float, margin:float, deposit:float, withdraw:float, isLast:bool):
        print("account", channelid, dynbalance)

    def on_order(self, channelid, exchg, code, curTDate:int, orderid, direct:int, offset:int, 
            volume:float, leftover:float, traded:float, price:float, ordertype:int, pricetype:int, ordertime:int, state:int, statemsg, isLast:bool):
        print("order", channelid, exchg, code)

    def on_trade(self, channelid, exchg, code, curTDate:int, tradeid, orderid, direct:int, 
            offset:int, volume:float, price:float, amount:float, ordertype:int, tradetype:int, tradetime:int, isLast:bool):
        print("trade", channelid, exchg, code)

    def on_position(self, channelid, exchg, code, curTDate:int, direct:int, volume:float, 
            cost:float, margin:float, avgpx:float, dynprofit:float, volscale:int, isLast:bool):
        print("positions", channelid, exchg, code)

def run_dumper():
    dumper = TraderDumper(MySink(), "logcfg.yaml")
    dumper.init("./", "config.yaml")

    #配置文件中也可以配置
    trader = {
        "active":True,
        "channelid":"simnow",
        "user":"youraccount",
        "pass":"yourpasswd",
        "module": "TraderCTP",#可以是其他支持的交易模块
        "broker":"9999",
        "front": 'tcp://180.168.146.187:10201',
        "appid": 'simnow_client_test',
        "authcode": '0000000000000000'
    }
    dumper.add_trader(trader)
    
    dumper.run(bOnce=True)

run_dumper()