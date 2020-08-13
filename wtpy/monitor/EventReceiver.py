import socket
import threading
import struct
import json

UDP_MSG_PUSHTRADE = 0x301
UDP_MSG_PUSHORDER = 0x302
UDP_MSG_PUSHEVENT = 0x303

class EventSink:
    def __init__(self):
        pass

    def on_order(self, grpid:str, chnl:str, ordInfo:dict):
        pass

    def on_trade(self, grpid:str, chnl:str, trdInfo:dict):
        pass
    
    def on_message(self, grpid:str, chnl:str, message:str):
        pass

class EventReceiver:

    def __init__(self, port:int = 8096, host:str = '0.0.0.0', sink:EventSink = None):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((host, port))  # 为服务器绑定一个固定的地址，ip和端口
        self.sock.settimeout(10)

        self._stopped = False
        self._worker = None
        self._sink = sink

    def run(self):
        self._worker = threading.Thread(target=self.__loop__, daemon=True)
        self._worker.start()

    def stop(self):
        self._stopped = True
        self.sock.close()

    def __loop__(self):
        while not self._stopped:
            try:
                data, remote = self.sock.recvfrom(10240)
                json_str = data[40:]
                grpid, trader, mtype, length = struct.unpack('=16s16s2I', data[:40])

                grpid = grpid.decode("gbk")
                trader = trader.decode("gbk")

                json_str = json_str.decode("gbk")

                if mtype == UDP_MSG_PUSHTRADE:
                    if self._sink is not None:
                        self._sink.on_trade(grpid, trader, json.loads(json_str))
                elif mtype == UDP_MSG_PUSHORDER:
                    if self._sink is not None:
                        self._sink.on_order(grpid, trader, json.loads(json_str))
                elif mtype == UDP_MSG_PUSHEVENT:
                    if self._sink is not None:
                        self._sink.on_message(grpid, trader, json_str)
            except:
                print("timeout")
