<template>
    <div style="height:100%;width:100%;display:flex;flex-direction:column;">
        <div style="flex:1 40%;overflow:auto;border-bottom:1px solid #E4E7ED;margin:2px;width:100%;display:flex;flex-direction:column;">
            <div style="flex:0 44px;">
                <el-tabs :value="selChart" tab-position="top" style="height:100%;margin:0;" @tab-click="onChartSel">
                    <el-tab-pane label="收益曲线" name="fund">
                    </el-tab-pane>
                    <el-tab-pane label="信号分析" name="kline">
                    </el-tab-pane>
                </el-tabs>
            </div>
            <div style="flex: 1; margin:4px;">
                <div id="bt_kline" style="width:100%;height:100%;" v-show="selChart=='kline'">
                </div>
                <div id="bt_fund" style="width:100%;height:100%;" v-show="selChart=='fund'">
                </div>
            </div>
        </div>
        <div style="flex:1 60%;overflow:auto;display:flex;flex-direction:column;margin:2px;width:100%;">
            <div style="flex:0 44px;">
                <el-tabs :value="selCat" tab-position="top" style="height:100%;margin:0;" @tab-click="onCatSel">
                    <el-tab-pane label="信号明细" name="sig">
                    </el-tab-pane>
                    <el-tab-pane label="回合明细" name="rnd">
                    </el-tab-pane>
                    <el-tab-pane label="每日绩效" name="fnd">
                    </el-tab-pane>
                </el-tabs>
            </div>
            <div style="flex: 1; margin:4px;">
                <div style="max-height:100%;overflow:auto;"  v-show="selCat=='sig'" v-loading="loading.signal">
                    <el-table
                        border
                        stripe
                        :data="signals"
                        class="table">
                        <el-table-column
                            prop="strategy"
                            label="策略"
                            width="120">
                        </el-table-column>
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
                            prop="strategy"
                            label="策略"
                            width="120">
                        </el-table-column>
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
                            prop="strategy"
                            label="策略"
                            width="120">
                        </el-table-column>
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
            </div>             
        </div>
    </div>
</template>

<script>

export default {
    name: "BTComp",
    data() {
        return {
            loading:{
                signal: false,
                round: false,
                fund: false
            },
            selChart:"fund",
            selCat:"rnd",
            signals:[],
            rounds:[],
            funds:[],
            nvChart:null,
        };
    },
    methods: {
        onChartSel: function(tab){
            this.selChart = tab.name;
        },
        onCatSel: function(tab, event){
            if(this.selCat == tab.name)
                return;

            this.selCat = tab.name;
        },
        paintChart: function(bars){
            bars = bars || [];
            let self = this;
            if(self.nvChart == null) //K线图
                self.nvChart = this.$echarts.init(document.getElementById("bt_kline"));

            let upColor = "#ec0000";
            let upBorderColor = "#8A0000";
            let downColor = "#00da3c";
            let downBorderColor = "#008F28";

            // 数据意义：开盘(open)，收盘(close)，最低(lowest)，最高(highest)
            let cats = [], vals = [], ma5 = [], ma10 = [], ma20 = [], closes = [];
            bars.forEach((bItem, idx)=>{
                let curDt = bItem.date + '';
                cats.push(curDt.substr(0,4) + "/" + parseInt(curDt.substr(4,2)) + "/" + parseInt(curDt.substr(6,2)))
                vals.push([bItem.open, bItem.close, bItem.low, bItem.high]);
                closes.push(bItem.close);

                let count = closes.length;

                if(count < 5)
                    ma5.push('-');
                    else{
                    var sum = 0;
                    for (var j = 0; j < 5; j++) {
                        sum += closes[count - 1 - j];
                    }
                    ma5.push(sum / 5);
                }

                if(closes.length < 10)
                    ma10.push('-');
                    else{
                    var sum = 0;
                    for (var j = 0; j < 10; j++) {
                        sum += closes[count - 1 - j];
                    }
                    ma10.push(sum / 10);
                }

                if(closes.length < 20)
                    ma20.push('-');
                    else{
                    var sum = 0;
                    for (var j = 0; j < 20; j++) {
                        sum += closes[count - 1 - j];
                    }
                    ma20.push(sum / 20);
                }
            });

            let option = {
                title: {
                    show: false
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

                        if(params[1].data != "-")
                            tip += params[1].marker + "MA5: " + params[1].data.toFixed(2) + "<br/>";

                        if(params[2].data != "-")
                            tip += params[2].marker + "MA10: " + params[2].data.toFixed(2) + "<br/>";

                        if(params[3].data != "-")
                            tip += params[3].marker + "MA20: " + params[3].data.toFixed(2) + "<br/>";

                        return tip;
                    }
                },
                axisPointer: {
                    link: {xAxisIndex: 'all'},
                    label: {
                        backgroundColor: '#777'
                    }
                },
                legend: {
                    data: ["K线", 'MA5', 'MA10', 'MA20']
                },
                grid: [
                    {
                        left: "4%",
                        right: "4%",
                        height: "50%"
                    },
                    {
                        left: "4%",
                        right: "4%",
                        top: "63%",
                        height: "25%"
                    }
                ],
                xAxis: [
                    {
                        type: "category",
                        data: cats,
                        scale: true,
                        boundaryGap: true,
                        axisLine: { onZero: false },
                        splitLine: { show: false },
                        splitNumber: 20,
                        min: "dataMin",
                        max: "dataMax",
                        show: false
                    }
                ],
                yAxis: [
                    {
                        scale: true,
                        splitArea: {
                            show: true
                        }
                    }
                ],
                dataZoom: [
                    {
                        type: "inside",
                        xAxisIndex: [0, 1],
                        start: 50,
                        end: 100
                    },
                    {
                        show: true,
                        xAxisIndex: [0, 1],
                        type: "slider",
                        y: "95%",
                        start: 50,
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
                        markPoint: {
                            label: {
                                normal: {
                                    formatter: function (param) {
                                        return param != null ? Math.round(param.value).toFixed(2) : '';
                                    }
                                }
                            },
                            data: [
                                {
                                    name: '最高价',
                                    type: 'max',
                                    valueDim: 'highest'
                                },
                                {
                                    name: '最低价',
                                    type: 'min',
                                    valueDim: 'lowest'
                                }
                            ],
                            tooltip: {
                                formatter: function (param) {
                                    return param.name + '<br>' + (param.data.coord || '');
                                }
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
                        name: 'MA5',
                        type: 'line',
                        yAxisIndex : '0',
                        data: ma5,
                        smooth: true,
                        showSymbol: false,
                        lineStyle: {
                            normal: {opacity: 0.5}
                        }
                    },
                    {
                        name: 'MA10',
                        type: 'line',
                        yAxisIndex : '0',
                        data: ma10,
                        smooth: true,
                        showSymbol: false,
                        lineStyle: {
                            normal: {opacity: 0.5}
                        }
                    },
                    {
                        name: 'MA20',
                        type: 'line',
                        yAxisIndex : '0',
                        data: ma20,
                        smooth: true,
                        showSymbol: false,
                        lineStyle: {
                            normal: {opacity: 0.5}
                        }
                    }
                ]
            };

            console.log(self.nvChart);
            self.nvchart.setOption(option);
        }
    },
    mounted() {
        this.$nextTick(()=>{
            //this.paintChart();
        });

        window.onresize = function(){
            if (!self.zooming) {
                self.zooming = true
                setTimeout(function () {
                    if(self.nvChart) self.nvChart.resize();                    
                    self.zooming = false;
                }, 300);
            }
        };
    },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
