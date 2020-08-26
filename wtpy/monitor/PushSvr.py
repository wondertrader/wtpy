from flask_socketio import SocketIO, emit
from flask import session, sessions

def parse_data(data):
    try:
        json_data = json.loads(data.decode("utf-8"))
        return True,json_data
    except:
        return False, {
            "result": -998,
            "message": "请求数据解析失败"
        }

def get_param(json_data, key:str, type=str, defVal = ""):
    if key not in json_data:
        return defVal
    else:
        return type(json_data[key])

class PushServer:

    def __init__(self, app, dataMgr):
        sockio = SocketIO(app)
        self.sockio = sockio
        self.app = app
        self.dataMgr = dataMgr

        @sockio.on('connect', namespace='/')
        def on_connect():
            # emit('my response', {'data': 'Connected'})
            usrInfo = session.get("userinfo")

        @sockio.on('disconnect', namespace='/')
        def on_disconnect():
            print('Client disconnected')

        @sockio.on('setgroup', namespace='/')
        def set_group(data):
            groupid = get_param(data, "groupid")
            if len(groupid) == 0:
                emit('setgroup', {"result":-2, "message":"组合ID不能为空"})
            else:
                session["groupid"] = groupid
                

    def run(self, port:int, host:str):
        self.sockio.run(self.app, host, port)

    def notifyGrpLog(self, groupid, message):
        self.sockio.emit("notify", {"type":"gplog", "groupid":groupid, "message":message}, broadcast=True)

    def notifyGrpEvt(self, groupid, evttype):
        self.sockio.emit("notify", {"type":"gpevt", "groupid":groupid, "evttype":evttype}, broadcast=True)

    def notifyGrpChnlEvt(self, groupid, chnlid, evttype, data):
        self.sockio.emit("notify", {"type":"gpevt", "groupid":groupid, "channel":chnlid, "data":data, "evttype":evttype}, broadcast=True)