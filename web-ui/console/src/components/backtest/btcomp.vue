<template>
    <div style="height:100%;width:100%;display:flex;flex-direction:column;">
        <div style="flex:0 44px;">
            <el-tabs :value="selCat" tab-position="top" style="height:100%;margin:0;" @tab-click="onCatSel">
                <el-tab-pane label="绩效概览" name="summary">
                </el-tab-pane>
                <el-tab-pane label="信号分析" name="kline">
                </el-tab-pane>
                <el-tab-pane label="成交明细" name="trd">
                </el-tab-pane>
                <el-tab-pane label="信号明细" name="sig">
                </el-tab-pane>
                <el-tab-pane label="回合明细" name="rnd">
                </el-tab-pane>
                <el-tab-pane label="每日绩效" name="fnd">
                </el-tab-pane>
            </el-tabs>
        </div>
        <div style="flex: 1;overflow:auto;width:100%;">
            <div style="height:100%;width:100%;overflow:auto;" v-show="selCat=='kline'">
                <div id="bt_kline" style="height:100%;width:100%;" >
                    <p>这里绘制K线和信号列表</p>
                </div>
            </div>
            <div style="height:100%;width:100%;display:flex;flex-direction:column;" v-show="selCat=='summary'">
                <div style="flex:0 200px;width:100%;">
                    <el-row>
                        <el-col :span="4">
                            <div class="panel">
                                <p class="panel-tag">回测天数</p>
                                <p class="panel-val text-info">{{btInfo?btInfo.perform.days:0}}天</p>
                            </div>
                        </el-col>
                        <el-col :span="4">
                            <div class="panel">
                                <p class="panel-tag">开始时间</p>
                                <p class="panel-val text-info">{{btInfo?fmtBtTime(btInfo.state.stime):"-"}}</p>
                            </div>
                        </el-col>
                        <el-col :span="4">
                            <div class="panel">
                                <p class="panel-tag">结束时间</p>
                                <p class="panel-val text-info">{{btInfo?fmtBtTime(btInfo.state.etime):"-"}}</p>
                            </div>
                        </el-col>
                        <el-col :span="4">
                            <div class="panel">
                                <p class="panel-tag">初始资金</p>
                                <p class="panel-val text-info">{{btInfo?btInfo.capital.toFixed(1):0}}</p>
                            </div>
                        </el-col>
                        <el-col :span="4">
                            <div class="panel">
                                <p class="panel-tag">总收益率</p>
                                <p class="panel-val" :class="getClass(btInfo?btInfo.perform.total_return:0)">{{btInfo?btInfo.perform.total_return.toFixed(2):"0.00"}}%</p>
                            </div>
                        </el-col>
                        <el-col :span="4">
                            <div class="panel">
                                <p class="panel-tag">胜率</p>
                                <p class="panel-val text-danger">{{btInfo?btInfo.perform.win_rate.toFixed(2):"0.00"}}%</p>
                            </div>
                        </el-col>
                    </el-row>
                    <div class="divider"></div>
                    <el-row>
                        <el-col :span="4">
                            <div class="panel">
                                <p class="panel-tag">年化收益率</p>
                                <p class="panel-val" :class="getClass(btInfo?btInfo.perform.annual_return:0)">{{btInfo?btInfo.perform.annual_return.toFixed(2):"0.00"}}%</p>
                            </div>
                        </el-col>
                        <el-col :span="4">
                            <div class="panel">
                                <p class="panel-tag">最大回撤</p>
                                <p class="panel-val text-success">{{btInfo?btInfo.perform.max_falldown.toFixed(2):"0.00"}}%</p>
                            </div>
                        </el-col>
                        <el-col :span="4">
                            <div class="panel">
                                <p class="panel-tag">最大盈利</p>
                                <p class="panel-val text-danger">{{btInfo?btInfo.perform.max_profratio.toFixed(2):"0.00"}}%</p>
                            </div>
                        </el-col>
                        <el-col :span="4">
                            <div class="panel">
                                <p class="panel-tag">夏普率</p>
                                <p class="panel-val text-info">{{btInfo?btInfo.perform.sharpe_ratio.toFixed(2):"0.00"}}</p>
                            </div>
                        </el-col>
                        <el-col :span="4">
                            <div class="panel">
                                <p class="panel-tag">索提诺比率</p>
                                <p class="panel-val text-info">{{btInfo?btInfo.perform.sortino_ratio.toFixed(2):"0.00"}}</p>
                            </div>
                        </el-col>
                        <el-col :span="4">
                            <div class="panel">
                                <p class="panel-tag">卡尔玛比率</p>
                                <p class="panel-val text-info">{{btInfo?btInfo.perform.calmar_ratio.toFixed(2):"0.00"}}</p>
                            </div>
                        </el-col>
                    </el-row>
                </div>
                <div class="divider"></div>
                <div style="flex:1;width:100%;">
                    <div style="height:100%;width:100%;">
                    <div id="bt_fund" style="height:100%;width:100%;" >
                        <p>这里绘制每日收益曲线</p>
                    </div>
                    </div>
                </div>
            </div>
            <div style="max-height:100%;overflow:auto;"  v-show="selCat=='sig'" v-loading="loading.signal">
                <el-table
                    border
                    stripe
                    :data="signals"
                    class="table">
                    <el-table-column
                        prop="code"
                        label="品种"
                        width="120"
                        sortable>
                    </el-table-column>
                    <el-table-column
                        prop="target"
                        label="目标数量"
                        width="80">
                        <template slot-scope="scope">
                            <span :class="fmtProfit(scope.row.target)">{{scope.row.target}}</span>
                        </template>
                    </el-table-column>
                    <el-table-column
                        label="触发价格"
                        width="100">
                        <template slot-scope="scope">
                            <span>{{fmtPrice(scope.row.sigprice)}}</span>
                        </template>
                    </el-table-column>
                    <el-table-column
                        label="触发时间"
                        width="180">
                        <template slot-scope="scope">
                            <span>{{fmtTime(scope.row.gentime, true)}}</span>
                        </template>
                    </el-table-column>
                    <el-table-column
                        prop="tag"
                        label="标记"
                        sortable
                        width="180">
                    </el-table-column>
                </el-table>
            </div>
            <div style="max-height:100%;overflow:auto;"  v-show="selCat=='rnd'" v-loading="loading.round">
                <el-table
                    border
                    stripe
                    :data="rounds"
                    class="table">
                    <el-table-column
                        prop="code"
                        label="品种"
                        width="120"
                        sortable>
                    </el-table-column>
                    <el-table-column
                        label="方向"
                        width="64">
                        <template slot-scope="scope">
                            <span :class="scope.row.direct=='LONG'?'text-danger':'text-success'">{{scope.row.direct=='LONG'?'多':'空'}}</span>
                        </template>
                    </el-table-column>
                    <el-table-column
                        label="开仓时间"
                        width="120">
                        <template slot-scope="scope">
                            <span>{{fmtTime(scope.row.opentime)}}</span>
                        </template>
                    </el-table-column>
                    <el-table-column
                        label="开仓价格"
                        width="80">
                        <template slot-scope="scope">
                            <span>{{fmtPrice(scope.row.openprice)}}</span>
                        </template>
                    </el-table-column>
                    <el-table-column
                        label="平仓时间"
                        width="120">
                        <template slot-scope="scope">
                            <span>{{fmtTime(scope.row.closetime)}}</span>
                        </template>
                    </el-table-column>
                    <el-table-column
                        label="平仓价格"
                        width="80">
                        <template slot-scope="scope">
                            <span>{{fmtPrice(scope.row.closeprice)}}</span>
                        </template>
                    </el-table-column>
                    <el-table-column
                        prop="qty"
                        label="数量"
                        width="64">
                    </el-table-column>
                    <el-table-column
                        label="盈亏"
                        width="100">
                        <template slot-scope="scope">
                            <span :class="scope.row.profit>=0?'text-danger':'text-success'">{{scope.row.profit.toFixed(1)}}</span>
                        </template>
                    </el-table-column>
                    <el-table-column
                        label="潜在盈利"
                        width="100">
                        <template slot-scope="scope">
                            <span class="text-danger">{{scope.row.maxprofit.toFixed(1)}}</span>
                        </template>
                    </el-table-column>
                    <el-table-column
                        label="潜在亏损"
                        width="100">
                        <template slot-scope="scope">
                            <span class="text-success">{{scope.row.maxloss.toFixed(1)}}</span>
                        </template>
                    </el-table-column>
                    <el-table-column
                        prop="entertag"
                        label="进场标记"
                        width="100">
                    </el-table-column>
                    <el-table-column
                        prop="exittag"
                        label="出场标记"
                        width="100">
                    </el-table-column>
                </el-table>
            </div>
            <div style="max-height:100%;overflow:auto;"  v-show="selCat=='fnd'" v-loading="loading.fund">
                <el-table
                    border
                    stripe
                    :data="funds"
                    class="table">
                    <el-table-column
                        label="日期"
                        width="120">
                        <template slot-scope="scope">
                            <span>{{fmtDate(scope.row.date)}}</span>
                        </template>
                    </el-table-column>
                    <el-table-column
                        label="平仓盈亏"
                        width="100">
                        <template slot-scope="scope">
                            <span :class="scope.row.closeprofit>=0?'text-danger':'text-success'">{{scope.row.closeprofit.toFixed(1)}}</span>
                        </template>
                    </el-table-column>
                    <el-table-column
                        label="浮动盈亏"
                        width="100">
                        <template slot-scope="scope">
                            <span :class="scope.row.dynprofit>=0?'text-danger':'text-success'">{{scope.row.dynprofit.toFixed(1)}}</span>
                        </template>
                    </el-table-column>
                    <el-table-column
                        prop="fee"
                        label="手续费"
                        width="120">
                    </el-table-column>
                    <el-table-column
                        prop="dynbalance"
                        label="动态权益"
                        width="120">
                        <template slot-scope="scope">
                            <span :class="scope.row.dynbalance>=0?'text-danger':'text-success'">{{scope.row.dynbalance.toFixed(1)}}</span>
                        </template>
                    </el-table-column>
                </el-table>
            </div>
            <div style="max-height:100%;overflow:auto;" v-show="selCat=='trd'" v-loading="loading.trade">
                <el-table
                    border
                    stripe
                    :data="trades"
                    :summary-method="getTrdSum"
                    show-summary
                    class="table">
                    <el-table-column
                        prop="code"
                        label="品种"
                        width="120"
                        sortable>
                    </el-table-column>
                    <el-table-column
                        label="时间"
                        width="120">
                        <template slot-scope="scope">
                            <span>{{fmtTime(scope.row.time)}}</span>
                        </template>
                    </el-table-column>
                    <el-table-column
                        label="动作"
                        width="80">
                        <template slot-scope="scope">
                            <span :class="(scope.row.action=='开多'||scope.row.action=='平空')?'text-danger':'text-success'">{{scope.row.action}}</span>
                        </template>
                    </el-table-column>
                    <el-table-column
                        label="价格"
                        width="80">
                        <template slot-scope="scope">
                            <span>{{fmtPrice(scope.row.price)}}</span>
                        </template>
                    </el-table-column>
                    <el-table-column
                        prop="volume"
                        label="数量"
                        width="80">
                    </el-table-column>
                    <el-table-column
                        prop="tag"
                        label="标记"
                        sortable>
                    </el-table-column>
                </el-table>
            </div>
        </div>
    </div>
</template>

<script>

export default {
    name: "BTComp",
    props:{
        btInfo:{
            type: Object,
            default() {
                return null;
            }
        },
        straInfo:{
            type: Object,
            default() {
                return null;
            }
        }
    },
    watch:{
        btInfo(newVal, oldVal){
            let self = this;

            if(newVal == null)
                return;

            if(oldVal != null && newVal.id == oldVal.id)
                return;

            setTimeout(()=>{
                self.queryTrades();
                self.queryRounds();
                self.queryFunds();
                self.querySignals();
            }, 300);
        }
    },
    data() {
        return {
            loading:{
                signal: false,
                round: false,
                fund: false,
                trade: false
            },
            selCat:"summary",
            signals:[],
            rounds:[],
            funds:[],
            trades:[],
            kChart:null,
            tChart:null,
            bars:[]
        };
    },
    methods: {
        fmtBtTime: function(t){
            t = t+''
            return t.substr(0,4)+"."+t.substr(4,2)+"."+t.substr(6,2)+" "+t.substr(8,2)+":"+t.substr(10,2);
        },
        onCatSel: function(tab, event){
            if(this.selCat == tab.name)
                return;

            this.selCat = tab.name;

            if(tab.name == "kline" && this.kChart){
                setTimeout(()=>{
                    this.kChart.resize();
                }, 300);
            } else if(tab.name == "summary" && this.tChart){
                setTimeout(()=>{
                    this.tChart.resize();
                }, 300);
            }
                
        },
        queryBars: function(){
            if(this.btInfo == null)
                return;

            let code = this.btInfo.state.code;
            let stime = this.btInfo.state.stime;
            let etime = this.btInfo.state.etime;
            let period = this.btInfo.state.period;

            this.$api.getBtBars(code, period, stime, etime, (resObj)=>{
                if (resObj.result < 0) {
                    this.$notify.error("拉取K线出错：" + resObj.message);
                } else {
                    this.bars = resObj.bars;
                    this.paintChart(false);
                }
            });
        },
        querySignals: function(){
            let straid = this.straInfo.id;
            let btid = this.btInfo.id;
            this.loading.signal = true;
            this.$api.getBtSignals(straid, btid, (resObj)=>{
                if (resObj.result < 0) {
                    this.$notify.error("查询信号出错：" + resObj.message);
                } else {
                    this.signals = resObj.signals;
                    this.signals.reverse();
                }

                this.loading.signal = false;
            });
        },
        queryTrades: function(){
            let straid = this.straInfo.id;
            let btid = this.btInfo.id;
            this.loading.trade = true;
            this.$api.getBtTrades(straid, btid, (resObj)=>{
                if (resObj.result < 0) {
                    this.$notify.error("查询成交出错：" + resObj.message);
                } else {
                    resObj.trades.forEach((tItem)=>{
                        let action = "";
                        if(tItem.offset == "OPEN")
                            action += "开";
                        else 
                            action += "平";

                        if(tItem.direction == "LONG")
                            action += "多";
                        else 
                            action += "空";

                        tItem.action = action;
                    });
                    this.trades = resObj.trades;
                    this.trades.reverse();
                }

                this.loading.trade = false;

                setTimeout(()=>{
                    this.queryBars();
                }, 300);
            }); 
        },
        queryRounds: function(){
            let straid = this.straInfo.id;
            let btid = this.btInfo.id;
            this.loading.round = false;
            this.$api.getBtRounds(straid, btid, (resObj)=>{
                if (resObj.result < 0) {
                    this.$notify.error("查询回合出错：" + resObj.message);
                } else {
                    this.rounds = resObj.rounds;
                    this.rounds.reverse();
                }

                this.loading.round = false;
            });
        },
        queryFunds: function(){
            let straid = this.straInfo.id;
            let btid = this.btInfo.id;
            this.loading.fund = true;
            this.$api.getBtFunds(straid, btid, (resObj)=>{
                if (resObj.result < 0) {
                    this.$notify.error("查询绩效出错：" + resObj.message);
                } else {
                    this.funds = resObj.funds;                            
                    this.funds.reverse();
                    this.paintTrend();
                }
                this.loading.fund = false;
            });
        },
        getTrdSum: function(param){
            const { columns, data } = param;
            const sums = [];
            columns.forEach((column, index) => {
                if (index < 3 || index > 5) {
                    sums[index] = '';
                    return;
                } else if (index == 3){
                    sums[index] = '总计';
                    return;
                } else if (index == 4){
                    sums[index] = data.length + "笔";
                } else if (index == 5){
                    const values = data.map(item => Number(item.volume));
                    if (!values.every(value => isNaN(value))) {
                        sums[index] = values.reduce((prev, curr) => {
                            const value = Number(curr);
                            if (!isNaN(value)) {
                                return prev + curr;
                            } else {
                                return prev;
                            }
                            }, 0) + '手';
                    } else {
                        sums[index] = 'N/A';
                    }
                }                
            });

            return sums;
        },
        getSigSum: function(param){
            const { columns, data } = param;
            const sums = [];
            columns.forEach((column, index) => {
                if (index > 1) {
                    sums[index] = '';
                    return;
                } else if (index == 0){
                    sums[index] = '总计';
                    return;
                } else if (index == 1){
                    sums[index] = data.length + "笔";
                }                
            });

            return sums;
        },
        getRndSum: function(param){
            const { columns, data } = param;
            const sums = [];
            columns.forEach((column, index) => {
                if (index != 5 && index != 6 && index != 7 && index != 8) {
                    sums[index] = '';
                    return;
                } else if (index == 5){
                    sums[index] = '总计';
                    return;
                } else if (index == 6){
                    sums[index] = data.length + "笔";
                    return;
                }

                if(index == 7){
                    const values = data.map(item => Number(item.qty));
                    if (!values.every(value => isNaN(value))) {
                        sums[index] = values.reduce((prev, curr) => {
                            const value = Number(curr);
                            if (!isNaN(value)) {
                                return prev + curr;
                            } else {
                                return prev;
                            }
                            }, 0) + '手';
                    } else {
                        sums[index] = 'N/A';
                    }
                } else if(index == 8) {
                    const values = data.map(item => Number(item.profit));
                    if (!values.every(value => isNaN(value))) {
                        sums[index] = values.reduce((prev, curr) => {
                            const value = Number(curr);
                            if (!isNaN(value)) {
                                return prev + curr;
                            } else {
                                return prev;
                            }
                            }, 0).toFixed(1);
                    } else {
                        sums[index] = 'N/A';
                    }
                }
                
            });

            return sums;
        },
        paintChart: function(isDay){
            let bars = this.bars || [];
            isDay = isDay || false;
            let self = this;
            if(self.kChart == null) //K线图
                self.kChart = this.$echarts.init(document.getElementById("bt_kline"));

            let upColor = "#ec0000";
            let upBorderColor = "#8A0000";
            let downColor = "#00da3c";
            let downBorderColor = "#008F28";

            // 数据意义：开盘(open)，收盘(close)，最低(lowest)，最高(highest)
            let cats = [], vals = [];
            bars.forEach((bItem, idx)=>{
                let curDt = bItem.date + '';
                curDt = curDt.substr(0,4) + "/" + parseInt(curDt.substr(4,2)) + "/" + parseInt(curDt.substr(6,2));
                if(!isDay){
                    let curTm = bItem.time%10000 + '';
                    if(curTm.length == 3)
                        curTm = "0"+curTm;
                    curDt += " " + curTm.substr(0,2) + ":" + curTm.substr(2,2);
                }
                
                cats.push(curDt);
                vals.push([bItem.open, bItem.close, bItem.low, bItem.high]);
            });

            let trades = JSON.parse(JSON.stringify(this.trades)).reverse();
            let pts = [];
            let links = [];
            let lastDt = "";
            trades.forEach((item)=>{
                let curDt = item.time + "";
                curDt = curDt.substr(0,4) + "/" + parseInt(curDt.substr(4,2)) + "/" + parseInt(curDt.substr(6,2)) + " " + curDt.substr(8,2) + ":" + curDt.substr(10,2);
                let isBuy = (item.action == "开多" || item.action == "平空" || item.action == "OL" || item.action == "CS");
                let isEnter = (item.action[0] == "开" || item.action[0] == "O");
                if(lastDt == curDt){
                    let lastPt = pts[pts.length-1];
                    lastPt.data.volume += item.volume;
                    lastPt.data.flag += (isEnter?1:2);
                } else {
                    pts.push({
                        value:[curDt, item.price],
                        symbol:'triangle',
                        symbolRotate: isBuy?0:180,
                        symbolOffset: [0, isBuy?'50%':'-50%'],
                        itemStyle:{
                            color:isBuy?"#f00":"#0f0"
                        },            
                        data:{
                            isBuy: isBuy,
                            volume: item.volume,
                            price: item.price,
                            flag: (isEnter?1:2)
                        }
                    });
                }
                let lastPt = pts[pts.length-1];
                let prevPt = pts[pts.length-2];
                if(lastPt.data.flag >= 2){
                    let isProfit = (lastPt.data.price-prevPt.data.price)*(isBuy?-1:1) >= 0;
                    links.push({
                        source:pts.length-2,
                        target:pts.length-1,
                        lineStyle:{
                            color:isProfit?"#f00":"#0f0",
                            type:"solid",
                            width:1
                        }
                    });
                }
                                
                lastDt = curDt;
            });

            let title = this.btInfo.state.code + " " + this.btInfo.state.period;

            let option = {
                title: {
                    text: title
                },
                toolbox:{
                    show:true,
                    orient:'horizontal',
                    feature: {
                        saveAsImage: {},
                        restore:{}
                    }
                },
                tooltip: {
                    trigger: "axis",
                    axisPointer: {
                        type: "cross"
                    },
                    formatter: function(params){
                        params.sort((a,b)=>{
                            return a.seriesIndex - b.seriesIndex;
                        });

                        let date = params[0].axisValue;
                        let datas = params[0].data;
                        var tip = date + "<br/><br/>";
                        tip += params[0].marker + "开: " + datas[1].toFixed(2) + "<br/>";
                        tip += params[0].marker + "高: " + datas[4].toFixed(2) + "<br/>";
                        tip += params[0].marker + "低: " + datas[3].toFixed(2) + "<br/>";
                        tip += params[0].marker + "收: " + datas[2].toFixed(2) + "<br/>";

                        if(params.length > 1){
                            let data = params[1].data.data;

                            let action = (function(item){
                                if(item.isBuy){
                                    if(item.flag == 3){
                                        return "翻多: +";
                                    } else if(item.flag == 2){
                                        return "平空: +";
                                    } else {
                                        return "开多: +";
                                    }
                                } else {
                                    if(item.flag == 3){
                                        return "翻空: -";
                                    } else if(item.flag == 2){
                                        return "平多: -";
                                    } else {
                                        return "开空: -";
                                    }
                                }
                            })(data);
                            tip += params[1].marker + action + data.volume + "@" + data.price + "<br/>";
                        }

                        return tip;
                    }
                },
                axisPointer: {
                    link: {xAxisIndex: 'all'},
                    label: {
                        backgroundColor: '#777'
                    }
                },
                grid: {
                    left: "4%",
                    right: "4%",
                    bottom: "10%"
                },
                xAxis:{
                    type: "category",
                    data: cats,
                    scale: true,
                    boundaryGap: true,
                    axisLine: { onZero: false },
                    splitLine: { show: false },
                    splitNumber: 20,
                    min: "dataMin",
                    max: "dataMax"
                },
                yAxis:{
                    scale: true,
                    splitArea: {
                        show: true
                    }
                },
                dataZoom: [
                    {
                        type: "inside",
                        start: 90,
                        end: 100
                    },
                    {
                        show: true,
                        type: "slider",
                        y: "95%",
                        start: 90,
                        end: 100
                    }
                ],
                series: [
                    {
                        name: "K线",
                        type: "candlestick",
                        data: vals,
                        yAxisIndex : '0',
                        itemStyle: {
                            normal: {
                                color: upColor,
                                color0: downColor,
                                borderColor: upBorderColor,
                                borderColor0: downBorderColor
                            }
                        },
                        markLine: {
                            symbol: ['none', 'none'],
                            data: [
                                {
                                    name: 'min line on close',
                                    type: 'min',
                                    valueDim: 'close'
                                },
                                {
                                    name: 'max line on close',
                                    type: 'max',
                                    valueDim: 'close'
                                }
                            ]
                        }
                    },
                    {
                        type: 'graph',
                        layout: 'none',
                        coordinateSystem: 'cartesian2d',
                        data: pts,
                        links:links,
                        symbolSize:20,
                        zlevel:9
                    }
                ]
            };

            self.kChart.setOption(option);
        },
        fmtDate:function(val){
            let ret = val + "";
            return ret.substr(0,4) + "." + ret.substr(4,2) + "." + ret.substr(6,2);
        },
        fmtProfit:function(val){
            if(val > 0)
                return 'text-danger';
            else if(val < 0)
                return 'text-success';
            else
                return '';
        },
        fmtTime:function(val, bSignal){
            bSignal = bSignal || false;
            if(!bSignal){
                let ret = val + "";
                return ret.substr(2,2) + "." + ret.substr(4,2) + "." + ret.substr(6,2) + " " + ret.substr(8,2) + ":" + ret.substr(10,2);
            } else {
                let ret = val + "";
                return ret.substr(2,2) + "." + ret.substr(4,2) + "." + ret.substr(6,2) + " " + ret.substr(8,2) + ":" + ret.substr(10,2)+ ":" + ret.substr(12,2)+ "," + ret.substr(14,3);
            }
        },
        formatAmount: function(row,col){
            return row[col.property].toFixed(2);
        },
        fmtPrice:function(val){
            let ret = val.toFixed(4);
            let idx=0;
            for(; idx < ret.length; idx++){
                if(ret[ret.length-1-idx] != '0')
                    break;
            }
            if(ret[ret.length-1-idx] == ".")
                idx ++;

            let len = ret.length-idx;
            return ret.substr(0, len);
        },
        paintTrend: function(){
             let self = this;
            if(this.tChart == null) 
                this.tChart = this.$echarts.init(document.getElementById('bt_fund'));

            let options = {
                title: {
                    text: '净值走势'
                },
                tooltip: {
                    trigger: 'axis',
                    axisPointer: {
                        label: {
                            backgroundColor: '#6a7985',
                            formatter: function(params) {
                                var val = params.value + '';
                                return val.substr(0, 4) + '.' + val.substr(4, 2) + '.' + val.substr(6, 2);
                            }
                        }
                    },
                    formatter: function(params) {
                        if(params.length == 0)
                            return "收益曲线";

                        var ret = params[0].axisValueLabel;

                        for(var idx in params) {
                            if(params[idx].seriesName == '净值')
                                ret += '<br/>净值: ' + params[idx].value.toFixed(4);
                            else
                                ret += '<br/>' + params[idx].seriesName + ': ' + params[idx].value;
                        }

                        return ret;
                    }
                },
                grid: {
                    top: 42,
                    left: '8',
                    right: '8',
                    bottom: '8',
                    containLabel: true
                },
                xAxis: {
                    type: 'category',
                    data: [],
                    boundaryGap: false,
                    axisLabel: {
                        textStyle: {
                            color: '#000'
                        },
                        formatter: function(val, idx) {
                            val = val + '';
                            return val.substr(0, 4) + '.' + val.substr(4, 2) + '.' + val.substr(6, 2);
                        }
                    },
                    axisLine: {
                        lineStyle: {
                            color: '#000'
                        }
                    }
                },
                yAxis: [{
                    type: 'value',
                    axisLabel: {
                        textStyle: {
                            color: '#000'
                        },
                        formatter: function(val, idx) {
                            return val.toFixed(4);
                        }
                    },
                    axisLine: {
                        lineStyle: {
                            color: '#000'
                        }
                    },
                    scale: true
                }],
                series: [{
                    name: '净值',
                    type: 'line',
                    stack: '净值',
                    areaStyle: {
                        normal: {
                            color: {
                                type: 'linear',
                                x: 0,
                                y: 0,
                                x2: 0,
                                y2: 1,
                                colorStops: [{
                                    offset: 0,
                                    color: 'rgba(102,156,214,0.5)' // 0% 处的颜色
                                }, {
                                    offset: 1,
                                    color: 'rgba(242,242,242,0.3)' // 100% 处的颜色
                                }],
                                globalCoord: false // 缺省为 false
                            }
                        }
                    },
                    data: [],
                    lineStyle: {
                        normal: {
                            color: 'rgb(102,156,214)',
                            width: 2
                        }
                    },
                    itemStyle: {
                        normal: {
                            color: 'rgb(102,156,214)',
                            borderWidth: 1
                        }
                    }
                }]
            };

            let dates = [],
                prices = [];
            
            let baseamt = parseInt(self.btInfo.capital);
            for(let idx = self.funds.length-1; idx >= 0; idx--) {
                let item = self.funds[idx];
                dates.push(item.date);
                let dynbal = baseamt + item.dynbalance;
                prices.push(dynbal/baseamt);
            }

            let maxPx = Math.max.apply(null, prices);
            let minPx = Math.min.apply(null, prices);

            if(maxPx == minPx) {
                maxPx *= 1.05;
                minPx *= 0.95;
            } else {
                var diff = maxPx - minPx;
                maxPx += diff * 0.05;
                minPx = Math.max(0, minPx - diff * 0.05);
            }

            options.xAxis.data = dates;
            options.series[0].data = prices;
            options.yAxis[0].max = maxPx;
            options.yAxis[0].min = minPx;

            this.tChart.setOption(options);
        },
        getClass: function(v){
            if(v >= 0)
                return "text-danger";
            else
                return "text-success";
        }
    },
    mounted() {
        window.onresize = function(){
            let self = this;
            if (!self.zooming) {
                self.zooming = true
                setTimeout(function () {
                    if(self.kChart) 
                        self.kChart.resize();
                    if(self.tChart) 
                        self.tChart.resize();
                    self.zooming = false;
                }, 300);
            }
        };
    },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    .panel{
        align-items: center;
        height:100%;
        border-right: solid 1px #DCDFE6;
    }

    .panel-tag{
        text-align: center;
        font-weight: bold;
    }

    .panel-val{
        text-align: center;
    }

    .divider{
        display: block;
        height: 1px;
        width: 100%;
        margin: 4px 0;
        background-color: #DCDFE6;
    }

    .table{
        width:100%;
        height:100%;
    }
</style>
