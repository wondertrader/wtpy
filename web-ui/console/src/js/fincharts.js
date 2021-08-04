/*
 * 金融图表
 */
export default function() {

    let self = this;

	//根据id获取对象
	function $id(id) {
		return document.getElementById(id);
	}

	/*
	 * 向下取整
	 * val		要变换的数，number
	 * offset	是否要针对canvas偏移，bool
	 */
	function $floor(val, offset) {
		if(offset)
			return Math.floor(val) + 0.5;
		else
			return Math.floor(val);
	}

	/*
	 * 四舍五入
	 * val		要变换的数，number
	 * offset	是否要针对canvas偏移，bool
	 */
	function $round(val, offset) {
		if(offset)
			return Math.round(val) + 0.5;
		else
			return Math.round(val);
	}

	/*
	 * 是否是触摸设备
	 */
	function isTouchDevice() {
		return !!('ontouchstart' in window);
	}

	function preventEvent(e) {
		if(e.preventDefault)
			e.preventDefault();
		e.cancelBubble = true;
	}

	/*
	 * 金额格式化
	 */
	function toMoney(val, prec) {
		prec = prec || 2;
		return val.toFixed(prec);
	}

	function getPageCoord(element) {
		var coord = {
			x: 0,
			y: 0
		};
		while(element) {
			coord.x += element.offsetLeft;
			coord.y += element.offsetTop;
			element = element.offsetParent;
		}
		return coord;
	}

	function offsetEvtPts(e, relativePoint) {
		e = e || event;
		if(e.touches && e.touches.length) {
			e = e.touches[0];
		} else if(e.changedTouches && e.changedTouches.length) {
			e = e.changedTouches[0];
		}

		var offsetX, offsetY;
		offsetX = e.pageX - relativePoint.x;
		offsetY = e.pageY - relativePoint.y;
		return {
			x: offsetX,
			y: offsetY
		};
	}

	/*
	 * 画线函数
	 */
	function line(ctx, x0, y0, x1, y1, color, width, dashes) {
		dashes = dashes || [];
		ctx.beginPath();
		ctx.setLineDash(dashes);
		ctx.moveTo(x0, y0);
		ctx.lineTo(x1, y1);
		ctx.strokeStyle = color;
		ctx.lineWidth = width || 1;
		ctx.stroke();
	}

	/*
	 * 添加事件
	 */
	function addEvent(canvas, evtName, callback) {
		if(!canvas)
			return;

		canvas.addEventListener(evtName, callback, false);
	}

	/*
	 * 获取事件位置
	 * 主要为了兼容不同浏览器
	 */
	function getEventPosition(ev) {
		var x, y;
		if(ev.layerX || ev.layerX == 0) {
			x = ev.layerX;
			y = ev.layerY;
		} else if(ev.offsetX || ev.offsetX == 0) { // Opera   
			x = ev.offsetX;
			y = ev.offsetY;
		}
		return {
			x: x,
			y: y
		};
	}

	/*
	 * 判断某个点是否在区域内
	 */
	function isPointInRegion(region, pt) {
		if(!pt || !region)
			return false;

		if(region.x <= pt.x && pt.x <= region.x + region.width &&
			region.y <= pt.y && pt.y <= region.y + region.height)
			return true;

		return false;
	}

	/*
	 * 格式化时间
	 */
	function fmtBarTime(curTime, isForMin, isSplitter) {
		var s = curTime + '';
		if(isForMin) {
			if(isSplitter)
				return s.substr(4, 2) + "/" + s.substr(6, 2);
			else
				return s.substr(8, 2) + ":" + s.substr(10, 2);
		} else {
			if(isSplitter)
				return s.substr(0, 4);
			else
				return s.substr(4, 2) + "/" + s.substr(6, 2);
		}
	}

	function paddingStr(str, length, isLeft, pattern) {
		
		if(typeof(str) != "string")
			str = str + '';
		
		if(str.length >= length)
			return str;

		while(str.length < length) {
			if(isLeft)
				str = pattern + str;
			else
				str = str + pattern;
		}

		return str;
	}

	/*
	 * 将分时图的主题转换成对应的样式
	 */
	function wrapTrendTheme(options) {
		var theme = options.theme || "default";

		var defStyles = {
			colors: {
				backgroundColor: 'white', //背景色
				gridLineColor: '#303540', //网格线颜色
				borderColor: 'gray', //边框线颜色
				fallColor: '#28C773', //下跌颜色
				riseColor: '#F55555', //上涨颜色
				normalColor: 'black', //普通颜色
				titleColor: 'black', //标题文字颜色
				xAxisColor: 'black', //x坐标文字颜色
				yAxisColor: 'black', //y坐标文字颜色
				priceLineColor: 'rgb(36,143,207)', //走势线颜色
				avgPriceLineColor: 'gold', //均线颜色
				middleLineColor: 'red', //基准线颜色
				gradientColors: [ //填充渐变色
					[0.0, 'rgb(220,231,249)'],
					[1.0, 'rgb(145,185,245)']
				]
			},
			fonts: { //各个字体
				title: '12px Arial',
				yAxis: '11px Arial',
				xAxis: '11px Arial'
			}
		};

		var blkStyles = {
			colors: {
				backgroundColor: '#20222A', //背景色
				gridLineColor: '#303540', //网格线颜色
				borderColor: '#8392A5', //边框线颜色
				fallColor: '#28C773', //'#00FFFF', //下跌颜色
				riseColor: '#F55555', //上涨颜色
				normalColor: '#fff', //普通颜色
				titleColor: '#fff', //标题文字颜色
				xAxisColor: '#fff', //x坐标文字颜色
				yAxisColor: '#fff', //y坐标文字颜色
				priceLineColor: 'rgb(36,143,207)', //走势线颜色
				avgPriceLineColor: 'gold', //均线颜色
				middleLineColor: '#fff', //基准线颜色
				gradientColors: [ //填充渐变色
					[0.0, 'rgb(220,231,249)'],
					[1.0, 'rgb(145,185,245)']
				]
			},
			fonts: { //各个字体
				title: '12px Arial',
				yAxis: '11px Arial',
				xAxis: '11px Arial'
			}
		};

		var styles = {
			"default": defStyles,
			"black": blkStyles
		};

		//options.styles = styles[theme] || defStyles;
		options.styles = blkStyles;
	}

	/*
	 * 将K线图的主题转换成对应的样式
	 */
	function wrapKlineTheme(options) {
		let theme = options.theme || 'default';

		var defStyles = {
			colors: {
				backgroundColor: 'white', //背景色
				gridLineColor: '#303540', //网格线颜色
				borderColor: 'gray', //边框颜色
				vlineColor: 'white',//光标颜色
				fallColor: 'rgb(35,188,0)', //上涨颜色
				riseColor: 'rgb(241,18,0)', //下跌颜色
				titleColor: '#fff', //标题文字颜色
				yAxisColor: 'black', //纵坐标字体颜色
				xAxisColor: 'black', //横坐标字体颜色
				slider: { //滑动条
					lineColor: 'lightgray', //滑动条线条颜色
					gradient: [ //渐变填充设置
						[0.0, 'rgb(220,231,249)'],
						[1.0, 'rgb(145,185,245)']
					],
				},
				gripper: { //滑动块颜色设置
					borderColor: 'gray', //边框颜色
					fillColor: 'blue' //填充色
				},
				express: ['red', 'yellow', 'purple'] //指标线颜色
			},
			fonts: {
				title: '12px Arial',
				yAxis: '11px Arial', //纵坐标字体
				xAxis: '11px Arial' //横坐标字体
			}
		};

		var blkStyles = {
			colors: {
				backgroundColor: '#20222A', //背景色
				gridLineColor: '#303540', //网格线颜色
				borderColor: '#8392A5', //边框颜色
				fallColor: '#0DEE97', //下跌颜色
				riseColor: '#F0114E', //上涨颜色
				titleColor: '#fff', //标题文字颜色
				yAxisColor: '#fff', //纵坐标字体颜色
				xAxisColor: '#fff', //横坐标字体颜色
				slider: { //滑动条
					lineColor: 'lightgray', //滑动条线条颜色
					gradient: [ //渐变填充设置
						[0.0, 'rgb(220,231,249)'],
						[1.0, 'rgb(145,185,245)']
					],
				},
				gripper: { //滑动块颜色设置
					borderColor: '#DDDDDD', //边框颜色
					fillColor: '#687182' //填充色
				},
				express: ['#598E97', '#2E414F', '#B5725C'] //指标线颜色
			},
			fonts: {
				title: '12px Arial',
				yAxis: '11px Arial', //纵坐标字体
				xAxis: '11px Arial' //横坐标字体
			}
		};

		options.styles = blkStyles;
	}

	function getPixelRatio(ctx) {
		var devicePixelRatio = window.devicePixelRatio || 1;
		var backingStoreRatio = ctx.webkitBackingStorePixelRatio ||
			ctx.mozBackingStorePixelRatio ||
			ctx.msBackingStorePixelRatio ||
			ctx.oBackingStorePixelRatio ||
			ctx.backingStorePixelRatio || 1;

		return devicePixelRatio / backingStoreRatio;
	}

	//格式化时间
	function fmtTimeByIdx(sections, idx, both) {
		var left = idx;
		for(var i in sections) {
			i = parseInt(i);
			var totalMins = sections[i].close - sections[i].open;
			if(sections[i].close < sections[i].open)
				totalMins += 1440;
			if(left == totalMins && both) {
				var mins = sections[i].open + left;
				var right = -1;
				if(sections[i + 1] != undefined && left == totalMins)
					right = sections[i + 1].open;

				var h = Math.floor(mins / 60) + '';
				var m = mins % 60 + '';
				var rh = Math.floor(right / 60) + '';
				var rm = right % 60 + '';

				if(h >= 24) h -= 24;
				if(rh >= 24) rh -= 24;

				if(right != -1) {
					return paddingStr(h, 2, true, '0') + ":" + paddingStr(m, 2, true, '0') + "/" + paddingStr(rh, 2, true, '0') + ":" + paddingStr(rm, 2, true, '0');
				} else {
					return paddingStr(h, 2, true, '0') + ":" + paddingStr(m, 2, true, '0');
				}
			} else if(left <= totalMins) {
				var mins = sections[i].open + left;
				var h = Math.floor(mins / 60) ;
				if(h >= 24) h -= 24;
				var m = mins % 60;
				
				return paddingStr(h, 2, true, '0') + ":" + paddingStr(m, 2, true, '0');
			}

			left -= totalMins;
		}
		return "";
	}

	//是否是一个小节结束
	function isSectionEnd(sections, idx) {
		var totalMins = 0;
		for(var i in sections) {
			totalMins += sections[i].close - sections[i].open;
			if(sections[i].close < sections[i].open)
				totalMins += 1440;
			if(totalMins == idx)
				return true;
		}

		return false;
	}

	function getSectionBounds(sections, idx) {
		var totalMins = 0;
		for(var i in sections) {
			var thisMins = sections[i].close - sections[i].open;
			if(thisMins < 0) thisMins += 1440;
			if(totalMins <= idx && (totalMins + thisMins) > idx)
				return [totalMins, totalMins + thisMins];
		}

		return [0, 0];
	}

	var EventEmitter = function() {};
	EventEmitter.prototype = {
		on: function(etype, handler) {
			this.handlers = this.handlers || {};

			this.handlers[etype] = handler;
		},
		emit: function(etype) {
			this.handlers = this.handlers || {};
			var handler = this.handlers[etype];
			if(!handler)
				return;

			var args = [];
			for(var idx = 1; idx < arguments.length; idx++) {
				args.push(arguments[idx]);
			}
			handler.apply(this, args);
		}
	};

	/*
	 * 分时图
	 */
	var trendChart = function(canvasId, options) {

		var canvas = $id(canvasId);
		if(canvas.chart)
			return;

		this.canvas = canvas;
		canvas.chart = this;

		this.ctx = this.canvas.getContext('2d');

		var ratio = getPixelRatio(this.ctx);
		this.totalWidth = this.canvas.width;
		this.totalHeight = this.canvas.height;

		//缩放画布改变css宽和高来变成高分辨率
		this.canvas.style.width = this.canvas.width + 'px'; //确定分辨率
		this.canvas.style.height = this.canvas.height + 'px';
		this.canvas.width *= ratio; //确定物理分辨率
		this.canvas.height *= ratio;

		this.ctx.scale(ratio, ratio);
		this.decimal = options.decimal || 0;

		var totalWidth = this.totalWidth;
		var totalHeight = this.totalHeight;

		this.options = options;
		//转换样式
		wrapTrendTheme(this.options);

		//先把各个区域划分出来
		this.regions = {
			title: {
				x: 8,
				y: 0,
				width: totalWidth - 16,
				height: 24
			},
			trendLeftAxis: {
				x: 8,
				y: 24,
				width: 52,
				height: $floor((totalHeight - 48) * 2 / 3)
			},
			trendRightAxis: {
				x: totalWidth - 60,
				y: 24,
				width: 52,
				height: $floor((totalHeight - 48) * 2 / 3)
			},
			volLeftAxis: {
				x: 0,
				y: 24 + $floor((totalHeight - 48) * 2 / 3),
				width: 60,
				height: $floor((totalHeight - 48) / 3)
			},
			xAxis: {
				x: 8,
				y: totalHeight - 24,
				width: totalWidth - 16,
				height: 24
			},
			trend: {
				x: 8,
				y: 24,
				width: totalWidth - 16,
				height: $floor((totalHeight - 48) * 2 / 3)
			}, //分时柱线
			vol: {
				x: 8,
				y: 24 + $floor((totalHeight - 48) * 2 / 3),
				width: totalWidth - 16,
				height: $floor((totalHeight - 48) / 3)
			}
		}
		for(var key in this.regions) {
			this.regions[key].x += 0.5;
			this.regions[key].y += 0.5;
		}

		var tHours = Math.floor(this.options.maxDotsCount / 60);
		this.xSpan = Math.floor(Math.log(tHours) / Math.LN2);
		//console.log(this.xSpan);
	};

	trendChart.prototype = new EventEmitter;

	let trendProtoType = {
		setData: function(datas, totalMins, prec) {

			totalMins = totalMins || 0;
			if(totalMins != 0) {
				this.options.maxDotsCount = totalMins;
				var tHours = Math.floor(this.options.maxDotsCount / 60);
				this.xSpan = Math.floor(Math.log(tHours) / Math.LN2);
			}

			this.data = datas;
			
			this.decimal = prec || this.decimal || 0;

			var preclose = datas.quote.preClose;
			var maxDiff = 0;
			var maxVol = 0;
			var totalAmt = 0,
				totalVol = 0;
			var avgPx = [];
			for(var idx in datas.mins) {
				var curPx = datas.mins[idx].price;
				if(curPx == 0) curPx = preclose;
				maxDiff = Math.max(maxDiff, Math.abs(curPx - preclose));
				maxVol = Math.max(maxVol, datas.mins[idx].volume);
				totalVol += datas.mins[idx].volume;
				totalAmt += datas.mins[idx].volume * curPx;
				avgPx.push(totalAmt / totalVol);
			}
			this.maxDiff = maxDiff + 0.05 * maxDiff;
			this.maxVol = maxVol;
			this.avgPx = avgPx;
		},
		updateData: function(tick) {
			this.data.quote = tick;
			this.paint();
		},
		getXAxisLabel: function(idx) {
			var sections = this.data.sections;

			var bounds = getSectionBounds(sections, idx);
			var preSecEnd = bounds[0];
			var nxtSecEnd = bounds[1];

			if(isSectionEnd(sections, idx)) {
				return fmtTimeByIdx(sections, idx, true);
			} else if(idx % (60 * this.xSpan) == 0 && (nxtSecEnd - idx) >= (this.xSpan * 30) && (idx - preSecEnd) >= (this.xSpan * 30)) {
				return fmtTimeByIdx(sections, idx, false);
			} else if(idx == 0) {
				return fmtTimeByIdx(sections, idx, false);
			}

			return "";
		},
		isDrawVLine: function(idx) {
			var sections = this.data.sections;

			if(isSectionEnd(sections, idx)) {
				return true;
			} else if(idx % (60 * this.xSpan) == 0) {
				return true;
			}

			return false;
		},
		paint: function() {

			var ctx = this.ctx;
			ctx.clearRect(0, 0, this.totalWidth, this.totalHeight);

			this.paintBackground();

			this.paintTitle();
			this.paintXAxis();
			this.paintMinYAxis();
			//this.paintVolYAxis();
			this.paintChart();
			this.paintVolume();
		},

		paintBackground: function() {
			var region = {
				x: 0,
				y: 0,
				width: this.totalWidth,
				height: this.totalHeight
			};
			var ctx = this.ctx;
			ctx.beginPath();
			ctx.fillStyle = this.options.styles.colors.backgroundColor;
			ctx.fillRect(region.x, region.y, region.width, region.height);
		},

		paintTitle: function(dataIdx) {
			dataIdx = dataIdx || this.data.mins.length - 1;

			var styles = this.options.styles;
			var ctx = this.ctx;
			var region = this.regions.title;
			ctx.clearRect(region.x, region.y, region.width, region.height);

			ctx.beginPath();
			ctx.fillStyle = this.options.styles.colors.backgroundColor;
			ctx.fillRect(region.x, region.y, region.width, region.height);

			ctx.font = styles.fonts.title;
			ctx.fillStyle = styles.colors.titleColor;
			ctx.textBaseline = "bottom";

			var y = region.y + region.height - 6;

			var price = this.data.quote.price;
			var preclose = this.data.quote.preClose;
			if(price == 0) price = preclose;

			var x = region.x;
			var txt = '最新: ' + price.toFixed(this.decimal);
			var width = ctx.measureText(txt).width;
			ctx.fillText(txt, x, y);

			var isRise = price > preclose;
			var isEqual = price == preclose;
			var isFall = price < preclose;
			var diff = toMoney(price - preclose, this.decimal);
			var txtRiseFall = (isRise ? '↑  ' : (isFall ? '↓  ' : '  ')) + diff +
				('(') +
				toMoney(diff * 100 / preclose) +
				'%)';

			var x = region.x + width;
			ctx.fillStyle = isRise ? styles.colors.riseColor : (isFall ? styles.colors.fallColor : styles.colors.normalColor);
			ctx.fillText(txtRiseFall, x, y);

			var actiontm = this.data.quote.actiontm;
			if(actiontm) {
				var temp = actiontm + '';
				while(temp.length < 9)
					temp = '0' + temp;
				var txtTime = temp.substr(0, 2) + ":" + temp.substr(2, 2) + ":" + temp.substr(4, 2);
				ctx.fillStyle = styles.colors.titleColor;
				var timeWidth = ctx.measureText(txtTime).width;
				ctx.fillText(txtTime, region.x + region.width - timeWidth, y);
			}

		},
		paintXAxis: function() {
			var ctx = this.ctx;
			var xOpts = this.options.xAxis;
			var region = this.regions.xAxis;
			var styles = this.options.styles;

			ctx.textBaseline = "top";
			ctx.font = styles.fonts.xAxis;
			ctx.fillStyle = styles.colors.xAxisColor;

			var totalPts = this.options.maxDotsCount;
			var totalWidth = region.width - 2;
			var stepVal = totalWidth / (totalPts - 1);

			var labels = {};
			for(var idx = 0; idx < totalPts; idx++) {
				var pos = parseInt(idx);
				var label = this.getXAxisLabel(pos);
				//如果没有拿到横坐标标签，或者当前的位置离收盘只差45分钟以内
				//那么这个也不显示
				if(label.length == 0 || (totalPts - idx > 1 && totalPts - idx <= (0.75 * 60 * this.xSpan)))
					continue;

				var x = region.x + stepVal * pos + 1;
				var y = region.y + 2;
				var width = ctx.measureText(label).width;
				x -= $round(width / 2);
				if(x < region.x)
					x = region.x;
				else if(x + width > region.x + region.width)
					x = region.x + region.width - width;
				ctx.fillText(label, x, y);
			}
		},

		paintMinYAxis: function() {
			var ctx = this.ctx;
			var cOptions = this.options.minsChart;
			var styles = this.options.styles;

			var axisOpts = this.options.yAxis;
			var regionL = this.regions.trendLeftAxis;
			var regionR = this.regions.trendRightAxis;

			var preclose = this.data.quote.preClose;

			var middleIndex = (cOptions.horizontalLineCount + cOptions.horizontalLineCount % 2) / 2;
			var splitCount = 1;
			var maxVal = this.data.quote.preClose + this.maxDiff;
			var minVal = this.data.quote.preClose - this.maxDiff;
			var stepVal = (maxVal - minVal) / splitCount;

			ctx.font = styles.fonts.yAxis;
			for(var i = 0; i < 2; i++) {

				//左侧
				var yVal = maxVal - stepVal * i;
				if(i == middleIndex) yVal = this.data.quote.preClose;
				var color = i == 0 ? styles.colors.riseColor : styles.colors.fallColor;
				var pt = {
					x: regionL.x,
					y: regionL.y + regionL.height / splitCount * i
				}
				var txt = yVal.toFixed(this.decimal);
				var width = ctx.measureText(txt).width;
				ctx.fillStyle = color;
				ctx.textBaseline = i == 0 ? "top" : "bottom";
				ctx.fillText(txt, pt.x + 2, pt.y);

				//右侧
				var yVal = ((maxVal - stepVal * i) - preclose) * 100 / preclose;
				if(i == middleIndex) yVal = 0.0;

				var pt = {
					x: regionR.x + regionR.width,
					y: regionR.y + regionL.height / splitCount * i
				}
				var txt = yVal.toFixed(2) + "%";
				var width = ctx.measureText(txt).width;
				ctx.textBaseline = i == 0 ? "top" : "bottom";
				ctx.fillText(txt, pt.x - width - 2, pt.y);
			}
		},

		paintVolYAxis: function() {
			var ctx = this.ctx;
			var cOptions = this.options.volume;
			var styles = this.options.styles;
			var regionL = this.regions.volLeftAxis;
			var regionR = this.regions.volRightAxis;

			var splitCount = cOptions.horizontalLineCount + 1;
			var maxVal = this.maxVol;
			var stepVal = maxVal / splitCount;

			ctx.textBaseline = "middle";
			ctx.fillStyle = styles.colors.normalColor;
			ctx.font = styles.fonts.yAxis;
			for(var i = 1; i < cOptions.horizontalLineCount + 1; i++) {

				//左侧
				var yVal = maxVal - stepVal * i;
				var pt = {
					x: regionL.x + regionL.width,
					y: regionL.y + regionL.height / splitCount * i
				}
				var txt = yVal.toFixed(0);
				var width = ctx.measureText(txt).width;
				ctx.fillText(txt, pt.x - width - 6, pt.y);
			}
		},

		paintChart: function() {
			var cOptions = this.options.minsChart;
			var styles = this.options.styles;

			var region = this.regions.trend;
			var ctx = this.ctx;
			ctx.beginPath();
			ctx.strokeStyle = styles.colors.borderColor;
			ctx.rect(region.x, region.y, region.width, region.height);
			ctx.stroke();
			ctx.closePath();

			//水平线
			var middleIndex = (cOptions.horizontalLineCount + cOptions.horizontalLineCount % 2) / 2;
			var splitCount = cOptions.horizontalLineCount + 1;
			for(var i = 1; i <= cOptions.horizontalLineCount; i++) {
				var color = (i == middleIndex ? styles.colors.middleLineColor : styles.colors.gridLineColor);
				var y = $floor(region.y + region.height * i / splitCount, true);
				line(ctx, region.x + 1, y, region.x + region.width - 1, y, color);
			}

			//走势图
			var totalPts = this.options.maxDotsCount;
			var totalWidth = region.width - 2;
			var totalHeight = region.height;
			var stepVal = totalWidth / (totalPts - 1);
			var maxVal = this.data.quote.preClose + this.maxDiff;
			var minVal = this.data.quote.preClose - this.maxDiff;

			//垂直线 
			for(var idx = 1; idx < totalPts - 1; idx++) {
				if(!this.isDrawVLine(idx))
					continue;

				var x = region.x + 1 + $floor(stepVal * idx);
				line(ctx, x, region.y, x, region.y + region.height, styles.colors.gridLineColor);
			}

			//先画均线
			if(this.options.showAvgPriceLine) {
				ctx.beginPath();
				ctx.strokeStyle = styles.colors.avgPriceLineColor;
				var x = 0;
				var lastPx = this.data.quote.preClose;
				for(var idx in this.avgPx) {
					x = 1 + region.x + $round(stepVal * idx);
					var price = this.avgPx[idx];
					if(price == 0) price = lastPx;
					var y = region.y + (maxVal - price) / (maxVal - minVal) * totalHeight;
					ctx.lineTo(x, y);
					lastPx = price;
				}
				ctx.stroke();
			}

			//再画走势图
			ctx.beginPath();
			ctx.strokeStyle = styles.colors.priceLineColor;
			var x = 0;
			var lastPx = this.data.quote.preClose;
			for(var idx in this.data.mins) {
				x = 1 + region.x + $round(stepVal * idx);
				var price = this.data.mins[idx].price;
				if(price == 0) price = lastPx;
				var y = region.y + (maxVal - price) / (maxVal - minVal) * totalHeight;
				ctx.lineTo(x, y);
				lastPx = price;
			}
			ctx.stroke();
			ctx.lineTo(x, region.y + region.height);
			ctx.lineTo(region.x + 1, region.y + region.height);
			ctx.closePath();
			var g1 = ctx.createLinearGradient(0, 0, 0, region.height);
			for(var idx in styles.colors.gradientColors) {
				var curItem = styles.colors.gradientColors[idx];
				g1.addColorStop(curItem[0], curItem[1]);
			}
			ctx.fillStyle = g1;
			ctx.globalAlpha = 0.3;
			ctx.fill();
			ctx.globalAlpha = 1.0;
		},

		paintVolume: function() {
			var cOptions = this.options.volume;
			var styles = this.options.styles;

			var region = this.regions.vol;
			var ctx = this.ctx;
			ctx.beginPath();
			ctx.strokeStyle = styles.colors.borderColor;
			ctx.rect(region.x, region.y, region.width, region.height);
			ctx.stroke();

			//水平线
			var middleIndex = (cOptions.horizontalLineCount + cOptions.horizontalLineCount % 2) / 2;
			var splitCount = cOptions.horizontalLineCount + 1;
			for(var i = 1; i <= cOptions.horizontalLineCount; i++) {
				var color = styles.colors.gridLineColor;
				var y = $floor(region.y + region.height * i / splitCount, true);
				line(ctx, region.x + 1, y, region.x + region.width - 1, y, color);
			}

			//成交量线
			var totalPts = this.options.maxDotsCount;
			var totalWidth = region.width - 2;
			var totalHeight = region.height;
			var stepVal = totalWidth / (totalPts - 1);

			//垂直线 
			for(var idx = 1; idx < totalPts - 1; idx++) {
				if(!this.isDrawVLine(idx))
					continue;

				var x = region.x + 1 + $floor(stepVal * idx);
				line(ctx, x, region.y, x, region.y + region.height, styles.colors.gridLineColor);
			}

			var maxVal = this.maxVol;

			var prePrice = this.data.quote.preclose;

			//ctx.lineWidth=0.5;
			for(var idx in this.data.mins) {
				//var x = $round(1 + region.x + stepVal*idx, true);
				var x = 1 + region.x + stepVal * idx;
				var vol = this.data.mins[idx].volume;
				var y = region.y + $round((maxVal - vol) / maxVal * totalHeight);
				var curPrice = this.data.mins[idx].price;
				if(curPrice >= prePrice) {
					ctx.strokeStyle = styles.colors.riseColor;
				} else
					ctx.strokeStyle = styles.colors.fallColor;

				line(ctx, x, region.y + region.height - 1, x, y, ctx.strokeStyle);
				prePrice = curPrice;
			}

		},
	}

	Object.assign(trendChart.prototype, trendProtoType);

	/*
	 * K线图
	 */
	var klineChart = function(canvasId, options) {

		var canvas = $id(canvasId);
		if(canvas.chart)
			return;

		this.canvas = canvas;
		canvas.chart = this;

		this.ctx = this.canvas.getContext('2d');

		this.options = options;
		wrapKlineTheme(this.options);
		this.styles = options.styles;
		this.decimal = options.decimal || 0;

		this.barWidth = 5;
		this.barGap = 2;
		this.evtReg = false;

        this.datas = [];

		this.resize();
	};

	let klineProtoType = {
		setData: function(datas, isMins, isMore, prec) {
			datas = datas || [];
			if(datas.length == 0)
				return;
			
			isMore = isMore || false;
			var newCnt = 0;
			if(isMore){
				newCnt = datas.length - 1;
				this.datas = this.datas || [];
				if(this.datas.length == 0){
					this.datas = datas;
				} else {
					datas.push.apply(datas, this.datas.slice(1));
					this.datas = datas;
				}	
			} else {
				this.datas = datas;
			}
			
			
			this.isMins = isMins || false;
			this.decimal = prec || this.decimal || 0;

			//计算全局最高价和最低价
			var maxVal = 0;
			var minVal = 9999999;
			var maxVol = 0;
			for(var idx in datas) {
				maxVal = Math.max(maxVal, datas[idx].high);
				minVal = Math.min(minVal, datas[idx].low);
				maxVol = Math.max(maxVol, datas[idx].volumn);
			}
			this.totalMaxVal = maxVal + 0.05 * (maxVal - minVal);
			this.totalMinVal = minVal - 0.05 * (maxVal - minVal);
			
			//估算左侧纵坐标宽度
			var ctx = this.ctx;
			ctx.font = this.styles.fonts.yAxis;
			var txt = this.totalMaxVal.toFixed(this.decimal);
			var width = ctx.measureText(txt).width;
			txt = maxVol + '';
			width = Math.max(width, ctx.measureText(txt).width);
			this.yAxisWidth = width + 8;
			this.resize();
			
			if(isMore){
				this.viewHead = this.viewHead + newCnt;
			} else {
				this.viewHead = Math.max(0, datas.length - this.viewSize);
			}

			var region = this.regions.slider;
			var totalPts = this.datas.length;
			var totalWidth = region.width - 2;

			this.stepVal = totalWidth / (totalPts - 1);
			
			this.showVLine = false;

			this.calcExps();

			this.recalcLayout();
		},
		calcExps: function() {

			//计算主图指标
			if(this.options.innerExps) {
				var expHelper = window.expHelper;
				this.innerExps = {};
				for(var key in this.options.innerExps) {
					var expData = expHelper.calcExpress(
						this.datas, key, this.options.innerExps[key]);
					if(expData) {
						this.innerExps[key] = expData;
					}
				}
				//console.log(JSON.stringify(this.innerExps));
			}
		},

		resize: function() {
            var ratio = getPixelRatio(this.ctx);
            this.totalWidth = this.canvas.width;
            this.totalHeight = this.canvas.height;

            //缩放画布改变css宽和高来变成高分辨率
            this.canvas.style.width = this.canvas.width + 'px'; //确定分辨率
            this.canvas.style.height = this.canvas.height + 'px';
            this.canvas.width *= ratio; //确定物理分辨率
            this.canvas.height *= ratio;

            this.ctx.scale(ratio, ratio);

			var gap = this.options.chartGap;
			var totalWidth = this.totalWidth;
			var totalHeight = this.totalHeight;
			var sliderHeight = 36;
			var axisHeight = 24;
			var titleHeight = 24;

			var chartHeight = totalHeight - sliderHeight - axisHeight - titleHeight;
			var mainHeight = $floor(chartHeight * 2 / 3);
			
			var yAxisWidth = this.yAxisWidth || 60;

			//先把各个区域划分出来
			this.regions = {
				title: {
					x: yAxisWidth,
					y: 0,
					width: totalWidth - yAxisWidth - 4,
					height: 24
				},
				sliderYAxis: {
					x: 0,
					y: totalHeight - sliderHeight,
					width: yAxisWidth,
					height: sliderHeight - 4
				},
				slider: {
					x: yAxisWidth,
					y: totalHeight - sliderHeight,
					width: totalWidth - yAxisWidth - 4,
					height: sliderHeight - 4
				},
				barsYAxis: {
					x: 0,
					y: titleHeight,
					width: yAxisWidth,
					height: mainHeight
				},
				volYAxis: {
					x: 0,
					y: gap + titleHeight + mainHeight,
					width: yAxisWidth,
					height: chartHeight - mainHeight - gap
				},

				bars: {
					x: yAxisWidth,
					y: titleHeight,
					width: totalWidth - yAxisWidth - 4,
					height: mainHeight
				},
				vol: {
					x: yAxisWidth,
					y: gap + titleHeight + mainHeight,
					width: totalWidth - yAxisWidth - 4,
					height: chartHeight - mainHeight - gap
				},
				xAxis: {
					x: yAxisWidth,
					y: totalHeight - sliderHeight - axisHeight,
					width: totalWidth - yAxisWidth - 4,
					height: 24
				}
			}
			for(var key in this.regions) {
				this.regions[key].x += 0.5;
				this.regions[key].y += 0.5;
			}

			this.viewSize = $floor((this.regions.bars.width - this.barGap) / (this.barWidth + this.barGap));
			//this.viewHead = 0;
		},

		recalcLayout: function() {

			if(!this.datas || this.datas.length <= 0)
				return;

			var maxVal = 0;
			var minVal = 9999999;
			var maxVol = 0;
			for(var idx = 0; idx < this.viewSize; idx++) {

				var pos = idx + this.viewHead;
				if(pos >= this.datas.length)
					break;

				var bar = this.datas[pos];

				maxVal = Math.max(maxVal, bar.high);
				minVal = Math.min(minVal, bar.low);
				maxVol = Math.max(maxVol, bar.volume);

				for(var key in this.innerExps) {
					//console.log(this.innerExps[key]);
					var curExp = this.innerExps[key];
					for(var i in curExp) {
						var curLineData = curExp[i];
						var curVal = curLineData[pos];
						if(!isNaN(curVal)) {
							maxVal = Math.max(maxVal, curVal);
							minVal = Math.min(minVal, curVal);
						}
					}
				}
			}

			this.maxVal = maxVal + 0.05 * (maxVal - minVal);
			this.minVal = minVal - 0.05 * (maxVal - minVal);
			this.maxVol = Math.floor(maxVol * 1.05);

			var region = this.regions.slider;
			var stepVal = this.stepVal;

			var left = region.x + $round(stepVal * this.viewHead, true);
			var length = $round(stepVal * this.viewSize);
			this.regions.gripper = {
				x: left,
				y: region.y,
				width: Math.min(length, region.width + region.x - left),
				height: region.height
			};
		},

		paint: function() {

			var ctx = this.ctx;
			ctx.clearRect(0, 0, this.totalWidth, this.totalHeight);

			this.paintBackground();
			
			this.paintTitle();
			
			this.paintXAxis();
			this.paintBarYAxis();
			this.paintVolYAxis();
			this.paintSliderYAxis();
			this.paintBars();
			this.paintInnerExps();
			this.paintVol();
			this.paintSlider();
			this.paintGripper();
			this.paintVLine();

			this.registerEvents();
		},

		paintVLine: function() {
			var self = this;
			if(!self.showVLine || self.vlineIdx == -1)
				return;

			var idx = self.vlineIdx - this.viewHead;
			var region = this.regions.bars;
			var startX = region.x + this.barGap;
			var x = startX + $round((this.barWidth + this.barGap) * idx + this.barWidth / 2);
			var top = this.regions.bars.y;
			var bottom = this.regions.vol.y + this.regions.vol.height;
			
			var ctx = this.ctx;
			line(this.ctx, x, top, x, bottom, this.ctx.vlineColor, 1, [2,2]);
		},

		paintBackground: function() {
			var region = {
				x: 0,
				y: 0,
				width: this.totalWidth,
				height: this.totalHeight
			};
			var ctx = this.ctx;
			ctx.beginPath();
			ctx.fillStyle = this.styles.colors.backgroundColor;
			ctx.fillRect(region.x, region.y, region.width, region.height);
		},

		paintInnerExps: function() {
			var cOptions = this.options.bars;
			var region = this.regions.bars;

			var ctx = this.ctx;

			var totalHeight = region.height;
			var maxVal = this.maxVal;
			var minVal = this.minVal;

			var startX = region.x + this.barGap;

			if(!this.innerExps)
				return;

			for(var key in this.innerExps) {
				var curExp = this.innerExps[key];
				for(var idx in curExp) {
					var curLineData = curExp[idx];
					ctx.strokeStyle = this.styles.colors.express[idx];
					ctx.beginPath();
					for(var i = 0; i < this.viewSize; i++) {
						var pos = i + this.viewHead;
						if(pos >= this.datas.length)
							break;

						var curVal = curLineData[pos];
						if(isNaN(curVal))
							continue;

						var x = startX + $round((this.barWidth + this.barGap) * i + this.barWidth / 2);
						var y = region.y + $round((maxVal - curVal) / (maxVal - minVal) * totalHeight);
						if(i == 0)
							ctx.moveTo(x, y);
						else
							ctx.lineTo(x, y);
					}
					ctx.stroke();
				}

			}
		},

		paintBars: function() {
			var cOptions = this.options.bars;

			var region = this.regions.bars;
			var ctx = this.ctx;
			ctx.beginPath();
			ctx.strokeStyle = this.styles.colors.borderColor;
			ctx.rect(region.x, region.y, region.width, region.height);
			ctx.stroke();

			var middleIndex = (cOptions.horizontalLineCount + cOptions.horizontalLineCount % 2) / 2;
			var splitCount = cOptions.horizontalLineCount + 1;
			for(var i = 1; i <= cOptions.horizontalLineCount; i++) {
				var color = this.styles.colors.gridLineColor;
				var y = $floor(region.y + region.height * i / splitCount, true);
				line(ctx, region.x + 1, y, region.x + region.width - 1, y, color);
			}

			var totalHeight = region.height;
			var maxVal = this.maxVal;
			var minVal = this.minVal;

			if(!this.datas || this.datas.length == 0)
				return;

			var startX = region.x + this.barGap;
			var x = startX;
			for(var idx = 0; idx < this.viewSize; idx++) {

				var pos = idx + this.viewHead;
				if(pos >= this.datas.length)
					break;

				var bar = this.datas[idx + this.viewHead];
				x = startX + $round((this.barWidth + this.barGap) * idx + this.barWidth / 2);
				var high = region.y + $round((maxVal - bar.high) / (maxVal - minVal) * totalHeight);
				var low = region.y + $round((maxVal - bar.low) / (maxVal - minVal) * totalHeight);
				var open = region.y + $round((maxVal - bar.open) / (maxVal - minVal) * totalHeight);
				var close = region.y + $round((maxVal - bar.close) / (maxVal - minVal) * totalHeight);

				ctx.beginPath();
				if(bar.close >= bar.open) {
					ctx.strokeStyle = this.styles.colors.riseColor;
					ctx.strokeRect(x - $floor(this.barWidth / 2),
						Math.min(open, close),
						this.barWidth - 1,
						Math.abs(close - open));
					line(ctx, x, high, x, Math.min(open, close), this.styles.colors.riseColor);
					line(ctx, x, low, x, Math.max(open, close), this.styles.colors.riseColor);
				} else {
					ctx.fillStyle = this.styles.colors.fallColor;
					ctx.fillRect(x - this.barWidth / 2,
						Math.min(open, close) + 0.5,
						this.barWidth,
						Math.abs(close - open));
					line(ctx, x, high, x, low, this.styles.colors.fallColor);
				}
			}
		},

		paintVol: function() {
			var cOptions = this.options.volume;

			var region = this.regions.vol;
			var ctx = this.ctx;
			ctx.beginPath();
			ctx.strokeStyle = this.styles.colors.borderColor;
			ctx.rect(region.x, region.y, region.width, region.height);
			ctx.stroke();

			var middleIndex = (cOptions.horizontalLineCount + cOptions.horizontalLineCount % 2) / 2;
			var splitCount = cOptions.horizontalLineCount + 1;
			for(var i = 1; i <= cOptions.horizontalLineCount; i++) {
				var color = this.styles.colors.gridLineColor;
				var y = $floor(region.y + region.height * i / splitCount, true);
				line(ctx, region.x + 1, y, region.x + region.width - 1, y, color);
			}

			if(!this.datas || this.datas.length == 0)
				return;

			var totalHeight = region.height;
			var maxVal = this.maxVol;

			var startX = region.x + this.barGap;
			var baseY = region.y + totalHeight - 0.5;
			var x = startX;
			for(var idx = 0; idx < this.viewSize; idx++) {

				var pos = idx + this.viewHead;
				if(pos >= this.datas.length)
					break;

				var bar = this.datas[idx + this.viewHead];
				x = startX + $round((this.barWidth + this.barGap) * idx + this.barWidth / 2);
				var y = region.y + $floor((maxVal - bar.volume) / maxVal * totalHeight, true);

				ctx.beginPath();
				if(bar.close >= bar.open) {
					ctx.fillStyle = this.styles.colors.riseColor;
				} else {
					ctx.fillStyle = this.styles.colors.fallColor;
				}
				ctx.fillRect(x - this.barWidth / 2, y, this.barWidth, baseY - y);
			}
		},
		paintXAxis: function() {

			if(!this.datas || this.datas.length == 0)
				return;

			var ctx = this.ctx;
			var cOptions = this.options.xAxis;
			var region = this.regions.xAxis;

			var count = cOptions.visibleCount;
			var stepNum = Math.floor(this.viewSize / (count - 1));
			var lastMark = '';
			for(var i = 0; i < count; i++) {
				var offset = i * stepNum;
				if(offset >= this.viewSize)
					offset = this.viewSize-1;
					
				var idx = this.viewHead + offset;
				if(idx >= this.datas.length)
					return;

				if(idx < 0)
					return;

				var bar = this.datas[idx];
				var isSplitter = false;
				if(this.isMins) {
					var curMark = (bar.quoteTime + '').substr(4, 4);
					if(curMark != lastMark) {
						isSplitter = true;
						lastMark = curMark;
					}
				} else {
					var curMark = (bar.quoteTime + '').substr(0, 4);
					if(curMark != lastMark) {
						isSplitter = true;
						lastMark = curMark;
					}
				}
				var time = fmtBarTime(bar.quoteTime, this.isMins, isSplitter);

				var x = region.x + this.barGap + $round((this.barWidth + this.barGap) * offset + this.barWidth / 2);
				ctx.strokeStyle = this.styles.colors.xAxisColor;
				line(ctx, x, region.y, x, region.y+3, ctx.strokeStyle);
				
				ctx.textBaseline = "top";
				ctx.fillStyle = this.styles.colors.xAxisColor;
				ctx.font = this.styles.fonts.xAxis;
				var y = region.y + 3;
				var width = ctx.measureText(time).width;
				if(i == 0) {

				} else if(i == count - 1) {
					x = x - width;
				} else {
					x = x - width / 2;
				}
				ctx.fillText(time, x, y);
			}
		},

		paintBarYAxis: function() {

			var ctx = this.ctx;
			var cOptions = this.options.bars;
			var region = this.regions.barsYAxis;

			var splitCount = cOptions.horizontalLineCount + 1;
			var maxVal = this.maxVal || 0;
			var minVal = this.minVal || 0;
			var stepVal = (maxVal - minVal) / splitCount;

			ctx.textBaseline = "middle";
			ctx.fillStyle = this.styles.colors.yAxisColor;
			ctx.font = this.styles.fonts.yAxis;
			for(var i = 0; i < cOptions.horizontalLineCount + 1; i++) {

				//左侧
				var yVal = maxVal - stepVal * i;
				var pt = {
					x: region.x + region.width,
					y: region.y + region.height / splitCount * i
				}
				var txt = yVal.toFixed(this.decimal);
				var width = ctx.measureText(txt).width;
				ctx.fillText(txt, pt.x - width - 6, pt.y);
			}
		},

		paintVolYAxis: function() {

			var ctx = this.ctx;
			var cOptions = this.options.volume;
			var region = this.regions.volYAxis;

			var splitCount = cOptions.horizontalLineCount + 1;
			var maxVal = this.maxVol || 0;
			var stepVal = maxVal / splitCount;

			ctx.textBaseline = "middle";
			ctx.fillStyle = this.styles.colors.xAxisColor;
			ctx.font = this.styles.fonts.yAxis;
			for(var i = 0; i < cOptions.horizontalLineCount + 1; i++) {

				//左侧
				var yVal = maxVal - stepVal * i;
				var pt = {
					x: region.x + region.width,
					y: region.y + region.height / splitCount * i
				}
				var txt = (yVal / 100).toFixed(0);
				var width = ctx.measureText(txt).width;
				ctx.fillText(txt, pt.x - width - 6, pt.y);
			}
		},

		paintSliderYAxis: function() {

			var ctx = this.ctx;
			var cOptions = this.options.slider;
			var region = this.regions.sliderYAxis;

			var splitCount = cOptions.horizontalLineCount + 1;
			var maxVal = this.totalMaxVal || 0;
			var minVal = this.totalMinVal || 0;

			ctx.textBaseline = "middle";
			ctx.fillStyle = this.styles.colors.yAxis;
			ctx.font = this.styles.fonts.yAxis;

			var txt = maxVal.toFixed(this.decimal);
			var width = ctx.measureText(txt).width;
			ctx.fillText(txt, region.x + region.width - width - 6, region.y);

			txt = minVal.toFixed(this.decimal);
			width = ctx.measureText(txt).width;
			ctx.fillText(txt, region.x + region.width - width - 6, region.y + region.height);
		},
		
		paintTitle: function(){
			if(this.datas.length == 0)
				return;
			
			var idx = this.viewHead + this.viewSize - 1;
			if(idx >= this.datas.length)
				idx = this.datas.length - 1;
				
			if(this.showVLine && this.vlineIdx != -1)
				idx = this.vlineIdx;
				
			var prec = this.decimal || 0;
			
			var styles = this.styles;
			var ctx = this.ctx;
			var region = this.regions.title;
			ctx.clearRect(region.x, region.y, region.width, region.height);

			ctx.beginPath();
			ctx.fillStyle = styles.colors.backgroundColor;
			ctx.fillRect(region.x, region.y, region.width, region.height);

			ctx.font = styles.fonts.title;
			ctx.fillStyle = styles.colors.titleColor;
			ctx.textBaseline = "bottom";

			var y = region.y + region.height - 6;
			var curBar = this.datas[idx];
			
			var x = region.x;
			var txt = fmtBarTime(curBar.quoteTime, this.isMins, false);
			var width = ctx.measureText(txt).width;
			ctx.fillText(txt, x, y);
			
			x += width + 6; 
			txt = "开:" + curBar.open.toFixed(prec);
			var width = ctx.measureText(txt).width;
			ctx.fillText(txt, x, y);
			
			x += width + 6; 
			txt = "高:" + curBar.high.toFixed(prec);
			var width = ctx.measureText(txt).width;
			var ticks = curBar.high - curBar.open;
			ctx.fillText(txt, x, y);
			
			x += width + 6; 
			txt = "低:" + curBar.low.toFixed(prec);
			var width = ctx.measureText(txt).width;
			ctx.fillText(txt, x, y);
			
			x += width + 6; 
			txt = "收:" + curBar.close.toFixed(prec);
			var width = ctx.measureText(txt).width;
			ctx.fillText(txt, x, y);
		},

		paintSlider: function() {
			var cOptions = this.options.slider;

			var region = this.regions.slider;
			var ctx = this.ctx;
			ctx.beginPath();
			ctx.strokeStyle = cOptions.borderColor;
			ctx.rect(region.x, region.y, region.width, region.height);
			ctx.stroke();

			//水平线
			/*
			var splitCount = cOptions.horizontalLineCount + 1;
			for(var i = 1; i <= cOptions.horizontalLineCount; i++) {
				var color = cOptions.splitLineColor;
				var y = $floor(region.y + region.height * i / splitCount, true);
				line(ctx, region.x + 1, y, region.x + region.width - 1, y, color);
			}
			*/

			if(!this.datas)
				return;

			var klines = this.datas;
			var totalPts = klines.length;
			var totalWidth = region.width - 2;
			var totalHeight = region.height;
			var stepVal = this.stepVal;

			var maxVal = this.totalMaxVal;
			var minVal = this.totalMinVal;

			ctx.globalAlpha = 0.3;
			ctx.beginPath();
			ctx.strokeStyle = this.styles.colors.sliderColor;
			var x = 0;
			for(var idx in klines) {
				x = 1 + region.x + $round(stepVal * idx);
				var price = klines[idx].close;
				var y = region.y + (maxVal - price) / (maxVal - minVal) * totalHeight;
				ctx.lineTo(x, y);
			}
			ctx.stroke();
			ctx.lineTo(x, region.y + region.height);
			ctx.lineTo(region.x + 1, region.y + region.height);
			ctx.closePath();
			var g1 = ctx.createLinearGradient(0, 0, 0, region.height);
			for(var idx in this.styles.colors.slider.gradient) {
				var curItem = this.styles.colors.slider.gradient[idx];
				g1.addColorStop(curItem[0], curItem[1]);
			}
			ctx.fillStyle = g1;
			ctx.fill();
			ctx.globalAlpha = 1.0;
		},

		paintGripper: function() {

			var region = this.regions.gripper;
			if(!region)
				return;

			var ctx = this.ctx;
			ctx.beginPath();

			ctx.fillStyle = this.styles.colors.gripper.fillColor;
			ctx.globalAlpha = 0.7;
			ctx.fillRect(region.x, region.y - 0.5, region.width, region.height);
			ctx.strokeStyle = this.styles.colors.gripper.borderColor;
			ctx.strokeRect(region.x + 0.5, region.y, region.width, region.height);

			ctx.globalAlpha = 1.0;
		},

		registerEvents: function() {
			if(this.evtReg)
				return;

			var self = this;

			var canvas = this.canvas;

			var touchable = isTouchDevice();
			if(touchable) {

				addEvent(canvas, 'touchstart', function(ev) {
					//console.log('touchstart');
					ev = ev || event;
					preventEvent(ev);

					var relativePoint = getPageCoord(canvas);
					var src = ev.srcElement || ev.target || ev.relatedTarget;
					var fixedEvt = offsetEvtPts(ev, relativePoint);

					self.onDragStart(fixedEvt);
				});

				addEvent(canvas, 'touchmove', function(ev) {
					//console.log('touchmove');
					ev = ev || event;
					preventEvent(ev);

					var relativePoint = getPageCoord(canvas);
					var src = ev.srcElement || ev.target || ev.relatedTarget;
					var fixedEvt = offsetEvtPts(ev, relativePoint);

					self.onDrag(fixedEvt)
				});

				addEvent(canvas, 'touchend', function(ev) {
					//console.log('touchend');
					ev = ev || event;
					preventEvent(ev);

					var relativePoint = getPageCoord(canvas);
					var src = ev.srcElement || ev.target || ev.relatedTarget;
					var fixedEvt = offsetEvtPts(ev, relativePoint);

					self.onDragEnd(fixedEvt);
				});
			} else {
				addEvent(canvas, 'mouseout', function(ev) {
					self.onDragEnd(ev);
				});

				addEvent(canvas, 'mousemove', function(ev) {
					self.onDrag(ev);
				});

				addEvent(canvas, 'mousedown', function(ev) {
					self.onDragStart(ev);
				});

				addEvent(canvas, 'mouseup', function(ev) {
					self.onDragEnd(ev);
				});
			}

			this.evtReg = true;
		},

		onHitTest: function(curPt) {
			var region = this.regions.bars;
			var dist = curPt.x - region.x - this.barGap - Math.floor(this.barWidth / 2);
			var idx = $round(dist / (this.barGap + this.barWidth));
			if(idx < 0) {
				this.showVLine = false;
			} else {
				if(idx >= this.viewSize)
					idx = this.viewSize - 1;
					
				this.vlineIdx = idx + this.viewHead;
				if(this.vlineIdx >= this.datas.length)
					this.vlineIdx = this.datas.length - 1;

				this.emit("barsel", {
					index: this.vlineIdx,
					value: this.datas[this.vlineIdx],
					ismin: this.isMins
				});
			}

			this.paint();
		},

		onDragStart: function(ev) {
			if(this.isDragging)
				return;

			var region = this.regions.slider;
			var curPt = ev;
			if(isPointInRegion(region, curPt)) {
				this.startPt = ev;
				this.isDragging = true;
				this.showVLine = false;
			} else if(!isPointInRegion(this.regions.title, curPt)){
				this.showVLine = true;

				this.onHitTest(curPt);
			}
		},

		onDragEnd: function(evt) {
			if(!this.isDragging)
				return;

			this.isDragging = false;
		},

		onDrag: function(evt) {
			var curPt = evt;
			if(this.isDragging) {
				var region = this.regions.slider;
				if(isPointInRegion(region, curPt)) {
					var dist = curPt.x - this.startPt.x;
					var steps = $round(dist / this.stepVal);
					if(steps == 0)
						return;

					if(this.datas.length <= this.viewSize)
						return;
					
					if(viewHead == 0 && steps<0)
						return;
						
					var viewHead = this.viewHead + steps;
					if(viewHead > this.datas.length - this.viewSize)
						viewHead = this.datas.length - this.viewSize;
					else if(viewHead < 0)
						viewHead = 0;
					
					if(viewHead == 0 && this.datas.length < 500){
						//触发事件
						this.emit("moredata", {
							index: 0,
							curTime: this.datas[0].quoteTime,
							isMins: this.isMins
						});
					}
						
					this.viewHead = viewHead;
					this.recalcLayout();
					this.paint();

					this.startPt = curPt;
				}
			} else if(this.showVLine) {
				this.onHitTest(curPt);
			}
		}
	};

	klineChart.prototype = new EventEmitter;
	Object.assign(klineChart.prototype, klineProtoType);

	self.klineChart = klineChart;
	self.trendChart = trendChart;
};