import threading
import struct
import json

from wtpy import WtMsgQue, WtMQClient

mq = WtMsgQue()

TOPIC_RT_TRADE = "TRD_TRADE"    # 生产环境下的成交通知
TOPIC_RT_ORDER = "TRD_ORDER"    # 生产环境下的订单通知
TOPIC_RT_NOTIFY = "TRD_NOTIFY"  # 生产环境下的普通通知
TOPIC_RT_LOG = "LOG"            # 生产环境下的日志通知

class EventSink:
    def __init__(self):
        pass

    def on_order(self, chnl:str, ordInfo:dict):
        pass

    def on_trade(self, chnl:str, trdInfo:dict):
        pass
    
    def on_notify(self, chnl:str, message:str):
        pass

    def on_log(self, tag:str, time:int, message:str):
        pass

class EventReceiver(WtMQClient):

    def __init__(self, url:str, topics:list = [], sink:EventSink = None):
        self.url = url
        mq.add_mq_client(url, self)
        for topic in topics:
            self.subscribe(topic)

        self._stopped = False
        self._worker = None
        self._sink = sink

    def on_mq_message(self, topic:str, message:str, dataLen:int):
        topic = topic.decode()
        message = message[:dataLen].decode()
        if self._sink is not None:
            if topic == TOPIC_RT_TRADE:
                msgObj = json.loads(message)
                trader = msgObj["trader"]
                msgObj.pop("trader")
                self._sink.on_trade(trader, trader)
            elif topic == TOPIC_RT_ORDER:
                msgObj = json.loads(message)
                trader = msgObj["trader"]
                msgObj.pop("trader")
                self._sink.on_order(trader, trader)
            elif topic == TOPIC_RT_TRADE:
                msgObj = json.loads(message)
                trader = msgObj["trader"]
                msgObj.pop("trader")
                self._sink.on_notify(trader, msgObj)
            elif topic == TOPIC_RT_LOG:
                msgObj = json.loads(message)
                self._sink.on_log(msgObj["tag"], msgObj["time"], msgObj["message"])

    def run(self):
        self.start()

    def release(self):
        mq.destroy_mq_client(self)
