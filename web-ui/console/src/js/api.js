import $ from 'jquery'
import md5 from 'js-md5'

Date.prototype.format = function (fmt) { // author: meizz
	var o = {
		"M+": this.getMonth() + 1, // 月份
		"d+": this.getDate(), // 日
		"h+": this.getHours(), // 小时
		"m+": this.getMinutes(), // 分
		"s+": this.getSeconds(), // 秒
		"q+": Math.floor((this.getMonth() + 3) / 3), // 季度
		"S": this.getMilliseconds()
		// 毫秒
	};
	if (/(y+)/.test(fmt))
		fmt = fmt.replace(RegExp.$1, (this.getFullYear() + "")
			.substr(4 - RegExp.$1.length));
	for (var k in o)
		if (new RegExp("(" + k + ")").test(fmt))
			fmt = fmt.replace(RegExp.$1, (RegExp.$1.length == 1) ? (o[k]) :
				(("00" + o[k]).substr(("" + o[k]).length)));
	return fmt;
};

Date.prototype.addDays = function (days) {
	var d = this.valueOf();
	d += 24 * 60 * 60 * 1000 * days;
	return new Date(d);
};


export default function () {

	var self = this;

	///////////////////////////////////////////////////////
	//本地存储
	/*
	 * 存储本地数据
	 */
	self.setItem = function (key, val) {
		return window.localStorage.setItem(key, val);
	};

	/*
	 * 获取本地数据
	 */
	self.getItem = function (key) {
		return window.localStorage.getItem(key) || "";
	};

	self.token = self.getItem('token');

	/*
	 * 删除本地数据
	 */
	self.removeItem = function (key) {
		return window.localStorage.removeItem(key);
	};

	///////////////////////////////////////////////////////
	//接口相关

	self.login = function (loginid, pwd, cb) {
		let reqInfo = {
			loginid: loginid,
			passwd: md5(pwd)
		};

		$.post("/mgr/login",
			JSON.stringify(reqInfo),
			function (data, textStatus) {
				if (textStatus != 'success') {
					cb({
						result: -9999,
						message: textStatus
					});
				} else {
					cb(data);
				}
			}, 'json');
	};

	self.getGroups = function(cb){
		let reqInfo = {	};

		$.post("/mgr/qrygrp",
			JSON.stringify(reqInfo),
			function (data, textStatus) {
				if (textStatus != 'success') {
					cb({
						result: -9999,
						message: textStatus
					});
				} else {
					cb(data);
				}
			}, 'json');
	};

	self.startGroup = function(grpid, cb){
		let reqInfo = {
			groupid: grpid||""
		};

		$.post("/mgr/startgrp",
			JSON.stringify(reqInfo),
			function (data, textStatus) {
				if (textStatus != 'success') {
					cb({
						result: -9999,
						message: textStatus
					});
				} else {
					cb(data);
				}
			}, 'json');
	};

	self.stopGroup = function(grpid, cb){
		let reqInfo = {
			groupid: grpid||""
		};

		$.post("/mgr/stopgrp",
			JSON.stringify(reqInfo),
			function (data, textStatus) {
				if (textStatus != 'success') {
					cb({
						result: -9999,
						message: textStatus
					});
				} else {
					cb(data);
				}
			}, 'json');
	};

	self.delGroup = function(grpid, cb){
		let reqInfo = {
			groupid: grpid||""
		};

		$.post("/mgr/delgrp",
			JSON.stringify(reqInfo),
			function (data, textStatus) {
				if (textStatus != 'success') {
					cb({
						result: -9999,
						message: textStatus
					});
				} else {
					cb(data);
				}
			}, 'json');
	};


	self.getFolders = function(cb){
		let reqInfo = {	};

		$.post("/mgr/qrydir",
			JSON.stringify(reqInfo),
			function (data, textStatus) {
				if (textStatus != 'success') {
					cb({
						result: -9999,
						message: textStatus
					});
				} else {
					cb(data);
				}
			}, 'json');
	};

	self.commitGroup = function(grpInfo, action, cb){
		let reqInfo = JSON.parse(JSON.stringify(grpInfo));
		reqInfo.groupid = grpInfo.id;
		reqInfo.action = action;

		$.post("/mgr/addgrp",
			JSON.stringify(reqInfo),
			function (data, textStatus) {
				if (textStatus != 'success') {
					cb({
						result: -9999,
						message: textStatus
					});
				} else {
					cb(data);
				}
			}, 'json');
	};

	self.getGroupCfg = function(grpid, cb){
		let reqInfo = {
			groupid: grpid
		}

		$.post("/mgr/qrygrpcfg",
			JSON.stringify(reqInfo),
			function (data, textStatus) {
				if (textStatus != 'success') {
					cb({
						result: -9999,
						message: textStatus
					});
				} else {
					cb(data);
				}
			}, 'json');
	};

	self.commitGroupCfg = function(grpid, config, cb){
		let reqInfo = {
			groupid: grpid,
			config: config
		}

		$.post("/mgr/cmtgrpcfg",
			JSON.stringify(reqInfo),
			function (data, textStatus) {
				if (textStatus != 'success') {
					cb({
						result: -9999,
						message: textStatus
					});
				} else {
					cb(data);
				}
			}, 'json');
	};

    self.getGroupEntry = function(grpid, cb){
		let reqInfo = {
			groupid: grpid
		}

		$.post("/mgr/qrygrpentry",
			JSON.stringify(reqInfo),
			function (data, textStatus) {
				if (textStatus != 'success') {
					cb({
						result: -9999,
						message: textStatus
					});
				} else {
					cb(data);
				}
			}, 'json');
	};

    self.getGroupDir = function(grpid, cb){
		let reqInfo = {
			groupid: grpid
		}

		$.post("/mgr/qrygrpdir",
			JSON.stringify(reqInfo),
			function (data, textStatus) {
				if (textStatus != 'success') {
					cb({
						result: -9999,
						message: textStatus
					});
				} else {
					cb(data);
				}
			}, 'json');
	};

    self.getGroupFile = function(grpid, path, cb){
		let reqInfo = {
			groupid: grpid,
            path: path
		}

		$.post("/mgr/qrygrpfile",
			JSON.stringify(reqInfo),
			function (data, textStatus) {
				if (textStatus != 'success') {
					cb({
						result: -9999,
						message: textStatus
					});
				} else {
					cb(data);
				}
			}, 'json');
	};

    self.commitGroupFile = function(grpid, path, content, cb){
		let reqInfo = {
			groupid: grpid,
            path: path,
            content:content
		}

		$.post("/mgr/cmtgrpfile",
			JSON.stringify(reqInfo),
			function (data, textStatus) {
				if (textStatus != 'success') {
					cb({
						result: -9999,
						message: textStatus
					});
				} else {
					cb(data);
				}
			}, 'json');
	};

	self.commitGroupEntry = function(grpid, content, cb){
		let reqInfo = {
			groupid: grpid,
			content: content
		}

		$.post("/mgr/cmtgrpentry",
			JSON.stringify(reqInfo),
			function (data, textStatus) {
				if (textStatus != 'success') {
					cb({
						result: -9999,
						message: textStatus
					});
				} else {
					cb(data);
				}
			}, 'json');
	};

	self.getLogs = function(grpid, logtype, cb){
		if(typeof(logtype) == 'function'){
			cb = logtype;
			logtype = "";
		}

		let reqInfo = {
			id: grpid,
			type:logtype
		};


		$.post("/mgr/qrylogs",
			JSON.stringify(reqInfo),
			function (data, textStatus) {
				if (textStatus != 'success') {
					cb({
						result: -9999,
						message: textStatus
					});
				} else {
					cb(data);
				}
			}, 'json');
	};

	self.getMonCfg = function(grpid, cb){
		let reqInfo = {
			groupid: grpid
		};


		$.post("/mgr/qrymon",
			JSON.stringify(reqInfo),
			function (data, textStatus) {
				if (textStatus != 'success') {
					cb({
						result: -9999,
						message: textStatus
					});
				} else {
					cb(data);
				}
			}, 'json');
	};

	self.commitMonCfg = function(monCfg, cb){
		let reqInfo = monCfg;

		$.post("/mgr/cfgmon",
			JSON.stringify(reqInfo),
			function (data, textStatus) {
				if (textStatus != 'success') {
					cb({
						result: -9999,
						message: textStatus
					});
				} else {
					cb(data);
				}
			}, 'json');
	};

	self.getStrategies = function(grpid, stype, cb){
		if(typeof(stype) == 'function'){
			cb = stype;
			stype = "";
		}

		let reqInfo = {
			groupid: grpid,
			type:stype
		};


		$.post("/mgr/qrystras",
			JSON.stringify(reqInfo),
			function (data, textStatus) {
				if (textStatus != 'success') {
					cb({
						result: -9999,
						message: textStatus
					});
				} else {
					cb(data);
				}
			}, 'json');
	};

	self.getChannels = function(grpid, cb){
		let reqInfo = {
			groupid: grpid
		};

		$.post("/mgr/qrychnls",
			JSON.stringify(reqInfo),
			function (data, textStatus) {
				if (textStatus != 'success') {
					cb({
						result: -9999,
						message: textStatus
					});
				} else {
					cb(data);
				}
			}, 'json');
	};

	self.getTrades = function(gid, sid, cb){
		if(typeof(sid) == 'function'){
			cb = sid;
			sid = "";
		}

		let reqInfo = {
			groupid: gid,
			strategyid:sid
		};


		$.post("/mgr/qrytrds",
			JSON.stringify(reqInfo),
			function (data, textStatus) {
				if (textStatus != 'success') {
					cb({
						result: -9999,
						message: textStatus
					});
				} else {
					cb(data);
				}
			}, 'json');
	};

	self.getSignals = function(gid, sid, cb){
		if(typeof(sid) == 'function'){
			cb = sid;
			sid = "";
		}

		let reqInfo = {
			groupid: gid,
			strategyid:sid
		};


		$.post("/mgr/qrysigs",
			JSON.stringify(reqInfo),
			function (data, textStatus) {
				if (textStatus != 'success') {
					cb({
						result: -9999,
						message: textStatus
					});
				} else {
					cb(data);
				}
			}, 'json');
	};

	self.getRounds = function(gid, sid, cb){
		if(typeof(sid) == 'function'){
			cb = sid;
			sid = "";
		}

		let reqInfo = {
			groupid: gid,
			strategyid:sid
		};


		$.post("/mgr/qryrnds",
			JSON.stringify(reqInfo),
			function (data, textStatus) {
				if (textStatus != 'success') {
					cb({
						result: -9999,
						message: textStatus
					});
				} else {
					cb(data);
				}
			}, 'json');
	};

	self.getPositions = function(gid, sid, cb){
		if(typeof(sid) == 'function'){
			cb = sid;
			sid = "";
		}

		let reqInfo = {
			groupid: gid,
			strategyid:sid
		};


		$.post("/mgr/qrypos",
			JSON.stringify(reqInfo),
			function (data, textStatus) {
				if (textStatus != 'success') {
					cb({
						result: -9999,
						message: textStatus
					});
				} else {
					cb(data);
				}
			}, 'json');
	};

	self.getFunds = function(gid, sid, cb){
		if(typeof(sid) == 'function'){
			cb = sid;
			sid = "";
		}

		let reqInfo = {
			groupid: gid,
			strategyid:sid
		};


		$.post("/mgr/qryfunds",
			JSON.stringify(reqInfo),
			function (data, textStatus) {
				if (textStatus != 'success') {
					cb({
						result: -9999,
						message: textStatus
					});
				} else {
					cb(data);
				}
			}, 'json');
	};

	self.getChnlOrders = function(gid, cid, cb){
		if(typeof(cid) == 'function'){
			cb = cid;
			cid = "";
		}

		let reqInfo = {
			groupid: gid,
			channelid:cid
		};


		$.post("/mgr/qrychnlords",
			JSON.stringify(reqInfo),
			function (data, textStatus) {
				if (textStatus != 'success') {
					cb({
						result: -9999,
						message: textStatus
					});
				} else {
					cb(data);
				}
			}, 'json');
	};

	self.getChnlTrades = function(gid, cid, cb){
		if(typeof(cid) == 'function'){
			cb = cid;
			cid = "";
		}

		let reqInfo = {
			groupid: gid,
			channelid:cid
		};


		$.post("/mgr/qrychnltrds",
			JSON.stringify(reqInfo),
			function (data, textStatus) {
				if (textStatus != 'success') {
					cb({
						result: -9999,
						message: textStatus
					});
				} else {
					cb(data);
				}
			}, 'json');
	};

	self.getChnlPositions = function(gid, cid, cb){
		if(typeof(cid) == 'function'){
			cb = cid;
			cid = "";
		}

		let reqInfo = {
			groupid: gid,
			channelid:cid
		};


		$.post("/mgr/qrychnlpos",
			JSON.stringify(reqInfo),
			function (data, textStatus) {
				if (textStatus != 'success') {
					cb({
						result: -9999,
						message: textStatus
					});
				} else {
					cb(data);
				}
			}, 'json');
	};

    self.getChnlFunds = function(gid, cid, cb){
		if(typeof(cid) == 'function'){
			cb = cid;
			cid = "";
		}

		let reqInfo = {
			groupid: gid,
			channelid:cid
		};


		$.post("/mgr/qrychnlfund",
			JSON.stringify(reqInfo),
			function (data, textStatus) {
				if (textStatus != 'success') {
					cb({
						result: -9999,
						message: textStatus
					});
				} else {
					cb(data);
				}
			}, 'json');
	};

	self.getUsers = function(cb){
		let reqInfo = {
		};

		$.post("/mgr/qryusers",
			JSON.stringify(reqInfo),
			function (data, textStatus) {
				if (textStatus != 'success') {
					cb({
						result: -9999,
						message: textStatus
					});
				} else {
					cb(data);
				}
			}, 'json');
	};

	self.commitUser = function(usrInfo, action, cb){
		let reqInfo = Object.assign({}, usrInfo);
		reqInfo.action = action||"add";
		if(reqInfo.passwd != "********")
			reqInfo.passwd = md5(reqInfo.passwd);

		$.post("/mgr/cmtuser",
			JSON.stringify(reqInfo),
			function (data, textStatus) {
				if (textStatus != 'success') {
					cb({
						result: -9999,
						message: textStatus
					});
				} else {
					cb(data);
				}
			}, 'json');
	};

	self.delUser = function(loginid, cb){
		let reqInfo = {
			loginid: loginid
		};

		$.post("/mgr/deluser",
			JSON.stringify(reqInfo),
			function (data, textStatus) {
				if (textStatus != 'success') {
					cb({
						result: -9999,
						message: textStatus
					});
				} else {
					cb(data);
				}
			}, 'json');
	};

	self.getActions = function(beginDt, endDt, cb){
		let reqInfo = {
			sdate: beginDt,
			edate: endDt
		};

		$.post("/mgr/qryacts",
			JSON.stringify(reqInfo),
			function (data, textStatus) {
				if (textStatus != 'success') {
					cb({
						result: -9999,
						message: textStatus
					});
				} else {
					cb(data);
				}
			}, 'json');
	};

	self.getPythonPath = function(cb){
		let reqInfo = {};

		$.post("/mgr/qryexec",
			JSON.stringify(reqInfo),
			function (data, textStatus) {
				if (textStatus != 'success') {
					cb({
						result: -9999,
						message: textStatus
					});
				} else {
					cb(data);
				}
			}, 'json');
	};

	self.getMonApps = function(cb){
		let reqInfo = {};

		$.post("/mgr/qrymons",
			JSON.stringify(reqInfo),
			function (data, textStatus) {
				if (textStatus != 'success') {
					cb({
						result: -9999,
						message: textStatus
					});
				} else {
					cb(data);
				}
			}, 'json');
	};

	self.startApp = function(appid, cb){
		let reqInfo = {
			appid: appid||""
		};

		$.post("/mgr/startapp",
			JSON.stringify(reqInfo),
			function (data, textStatus) {
				if (textStatus != 'success') {
					cb({
						result: -9999,
						message: textStatus
					});
				} else {
					cb(data);
				}
			}, 'json');
	};

	self.stopApp = function(appid, cb){
		let reqInfo = {
			appid: appid||""
		};

		$.post("/mgr/stopapp",
			JSON.stringify(reqInfo),
			function (data, textStatus) {
				if (textStatus != 'success') {
					cb({
						result: -9999,
						message: textStatus
					});
				} else {
					cb(data);
				}
			}, 'json');
	};

	self.getMonLogs = function(cb){
		let reqInfo = {
		};

		$.post("/mgr/qrymonlog",
			JSON.stringify(reqInfo),
			function (data, textStatus) {
				if (textStatus != 'success') {
					cb({
						result: -9999,
						message: textStatus
					});
				} else {
					cb(data);
				}
			}, 'json');
	};

	self.delApp = function(appid, cb){
		let reqInfo = {
			appid: appid||""
		};

		$.post("/mgr/delapp",
			JSON.stringify(reqInfo),
			function (data, textStatus) {
				if (textStatus != 'success') {
					cb({
						result: -9999,
						message: textStatus
					});
				} else {
					cb(data);
				}
			}, 'json');
	};

    self.getPortPositions = function(gid, cb){
		let reqInfo = {
			groupid: gid
		};


		$.post("/mgr/qryportpos",
			JSON.stringify(reqInfo),
			function (data, textStatus) {
				if (textStatus != 'success') {
					cb({
						result: -9999,
						message: textStatus
					});
				} else {
					cb(data);
				}
			}, 'json');
	};

    self.getPortFunds = function(gid, cb){
		let reqInfo = {
			groupid: gid
		};


		$.post("/mgr/qryportfunds",
			JSON.stringify(reqInfo),
			function (data, textStatus) {
				if (textStatus != 'success') {
					cb({
						result: -9999,
						message: textStatus
					});
				} else {
					cb(data);
				}
			}, 'json');
	};

    self.getPortPerfs = function(gid, cb){
		let reqInfo = {
			groupid: gid
		};


		$.post("/mgr/qryportperfs",
			JSON.stringify(reqInfo),
			function (data, textStatus) {
				if (textStatus != 'success') {
					cb({
						result: -9999,
						message: textStatus
					});
				} else {
					cb(data);
				}
			}, 'json');
	};
};
