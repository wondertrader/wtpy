from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from .WtLogger import WtLogger
import asyncio
import json
import threading
import time

class PushServer:

    def __init__(self, app:FastAPI, dataMgr, logger:WtLogger = None):
        self.app = app
        self.dataMgr = dataMgr
        self.logger = logger
        self.ready = False

        self.active_connections = list()

        self.lock = threading.Lock()

        self.mutex = threading.Lock()
        self.messages = list()
        self.worker:threading.Thread = None
        self.stopped = False

    async def connect(self, ws: WebSocket):
        # 等待连接
        await ws.accept()

        if "tokeninfo" in ws.session:
            tInfo = ws.session["tokeninfo"]
            if tInfo is not None:
                self.logger.info(f"{tInfo['loginid']} connected")
            # 存储ws连接对象
            self.active_connections.append(ws)

    def disconnect(self, ws: WebSocket):
        # 关闭时 移除ws对象
        self.active_connections.remove(ws)
        if "tokeninfo" in ws.session:
            tInfo = ws.session["tokeninfo"]
            if tInfo is not None:
                self.logger.info(f"{tInfo['loginid']} disconnected")

    @staticmethod
    async def send_personal_message(data: dict, ws: WebSocket):
        # 发送个人消息
        await ws.send_json(data)

    def broadcast(self, data: dict, groupid:str=""):
        self.lock.acquire()

        loop = None
        try:
            loop = asyncio.get_event_loop()
        except:
            loop = None
        
        if loop is None or loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        tasks = []
        # 广播消息
        for ws in self.active_connections:
            if len(groupid)!=0 and "groupid" in ws.session and ws.session["groupid"]!=groupid:
                continue
            tasks.append(asyncio.ensure_future(ws.send_json(data)))
        
        if len(tasks) > 0:            
            loop.run_until_complete(asyncio.gather(*tasks))

        loop.close()
        self.lock.release()

    def on_subscribe_group(self, ws:WebSocket, data:dict):
        if ws not in self.active_connections:
            return

        if "groupid" not in data:
            return

        tokenInfo = ws.session["tokeninfo"]
        ws.session["groupid"] = data["groupid"]
        self.logger.info("{}@{} subscribed group {}".format(tokenInfo["loginid"], tokenInfo["loginip"] , data["groupid"]))

    def run(self):
        app = self.app
        @app.websocket("/")
        async def ws_listen(ws:WebSocket):
            await self.connect(ws)
            try:
                while True:
                    data = await ws.receive_text()
                    try:
                        req = json.loads(data)
                        tp = req["type"]
                        if tp == 'subscribe':
                            self.on_subscribe_group(ws,req)
                            await self.send_personal_message(req, ws)
                        elif tp == 'heartbeat':
                            await self.send_personal_message({"type":"heartbeat", "message":"pong"}, ws)
                    except:
                        continue

            except WebSocketDisconnect:
                self.disconnect(ws)
        self.ready = True

        self.worker = threading.Thread(target=self.loop, daemon=True)
        self.worker.start()

    def loop(self):
        while not self.stopped:
            if len(self.messages) == 0:
                time.sleep(1)
                continue
            
            self.mutex.acquire()
            messages = self.messages.copy()
            self.messages = []
            self.mutex.release()

            for msg in messages:
                if msg["type"] == "gplog":
                    self.broadcast(msg, msg["groupid"])
                else:
                    self.broadcast(msg)

    def notifyGrpLog(self, groupid, tag:str, time:int, message):
        if not self.ready:
            return

        self.mutex.acquire()
        self.messages.append({"type":"gplog", "groupid":groupid, "tag":tag, "time":time, "message":message})
        self.mutex.release()

    def notifyGrpEvt(self, groupid, evttype):
        if not self.ready:
            return

        self.mutex.acquire()
        self.messages.append({"type":"gpevt", "groupid":groupid, "evttype":evttype})
        self.mutex.release()

    def notifyGrpChnlEvt(self, groupid, chnlid, evttype, data):
        if not self.ready:
            return

        self.mutex.acquire()
        self.messages.append({"type":"chnlevt", "groupid":groupid, "channel":chnlid, "data":data, "evttype":evttype})
        self.mutex.release()