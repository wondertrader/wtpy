<template>
    <div style="height:100%;overflow:auto;">
        <el-container style="height:100%;overflow:auto;">
            <el-header style="height:40px; overflow-y:hidden;">
                <div style="height:100%;display:flex;flex-direction:row;">
                    <div style="flex:0;height:100%;">
                        <el-tabs :value="selCat" tab-position="top" @tab-click="handleCatChange" style="height:100%;margin:0;">
                            <el-tab-pane label="持仓明细" name="pos">
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
                    <div style="flex:1;border-bottom:2px solid #E4E7ED;margin-top: 4px;">
                        <div style="float:right">
                            <el-button type="primary" icon="el-icon-refresh" size="mini" plain @click="queryData()">刷新</el-button>
                            <el-select v-model="strafilter" placeholder="请选择" size="mini" @change="onStraSwitch">
                                <el-option label="全部策略" value="all" v-show="selCat=='pos'">
                                    <i class="el-icon-collection"/>
                                    <span>全部策略</span>
                                </el-option>
                                <el-option :label="sid" :value="sid" :key="sid" v-for="sid in strategies">
                                    <i class="el-icon-tickets"/>
                                    <span>{{sid}}</span>
                                </el-option>
                            </el-select>
                        </div>
                    </div> 
                </div>
            </el-header>
            <el-main style="overflow:auto;">
                <div style="max-height:100%;overflow:auto;" v-show="selCat=='pos'" v-loading="loading.position">
                    <el-table
                        border
                        stripe
                        :data="positions"
                        class="table">
                        <el-table-column
                            prop="strategy"
                            label="策略"
                            width="120">
                        </el-table-column>
                        <el-table-column
                            prop="code"
                            label="品种"
                            width="120">
                        </el-table-column>
                        <el-table-column
                            prop="qty"
                            label="数量"
                            width="64">
                        </el-table-column>
                        <el-table-column
                            prop="profit"
                            label="浮盈"
                            :formatter="formatAmount"
                            width="80">
                        </el-table-column>
                        <el-table-column
                            prop="opentime"
                            label="开仓时间"
                            width="120">
                        </el-table-column>
                        <el-table-column
                            prop="price"
                            label="开仓价格"
                            width="100">
                        </el-table-column>
                        <el-table-column
                            prop="maxprofit"
                            label="最大浮盈"
                            :formatter="formatAmount"
                            width="100">
                        </el-table-column>
                        <el-table-column
                            prop="maxloss"
                            label="最大浮亏"
                            :formatter="formatAmount"
                            width="100">
                        </el-table-column>
                        <el-table-column
                            prop="opentag"
                            label="标记">
                        </el-table-column>
                    </el-table>
                </div>
                <div style="max-height:100%;overflow:auto;" v-show="selCat=='trd'" v-loading="loading.trade">
                    <el-table
                        border
                        stripe
                        :data="trades"
                        class="table">
                        <el-table-column
                            prop="strategy"
                            label="策略"
                            width="120">
                        </el-table-column>
                        <el-table-column
                            prop="code"
                            label="品种"
                            width="120">
                        </el-table-column>
                        <el-table-column
                            prop="time"
                            label="时间"
                            width="120">
                        </el-table-column>
                        <el-table-column
                            prop="action"
                            label="动作"
                            width="80">
                        </el-table-column>
                        <el-table-column
                            prop="price"
                            label="价格"
                            width="80">
                        </el-table-column>
                        <el-table-column
                            prop="volumn"
                            label="数量"
                            width="80">
                        </el-table-column>
                        <el-table-column
                            prop="tag"
                            label="标记">
                        </el-table-column>
                    </el-table>
                </div>
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
                            width="120">
                        </el-table-column>
                        <el-table-column
                            prop="target"
                            label="目标数量"
                            width="80">
                        </el-table-column>
                        <el-table-column
                            prop="sigprice"
                            label="触发价格"
                            width="100">
                        </el-table-column>
                        <el-table-column
                            prop="gentime"
                            label="触发时间"
                            width="160">
                        </el-table-column>
                        <el-table-column
                            prop="tag"
                            label="标记">
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
                            width="120">
                        </el-table-column>
                        <el-table-column
                            prop="direct"
                            label="方向"
                            width="80">
                        </el-table-column>
                        <el-table-column
                            prop="opentime"
                            label="开仓时间"
                            width="120">
                        </el-table-column>
                        <el-table-column
                            prop="openprice"
                            label="开仓价格"
                            width="80">
                        </el-table-column>
                        <el-table-column
                            prop="closetime"
                            label="平仓时间"
                            width="120">
                        </el-table-column>
                        <el-table-column
                            prop="closeprice"
                            label="平仓价格"
                            width="80">
                        </el-table-column>
                        <el-table-column
                            prop="qty"
                            label="数量"
                            width="64">
                        </el-table-column>
                        <el-table-column
                            prop="profit"
                            label="盈亏"
                            width="80">
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
                <div style="height:100%;display:flex;flex-direction:column;"  v-show="selCat=='fnd'" v-loading="loading.fund">
                    <div style="flex:1;width:100%;overflow:auto;height:50%;border-bottom:1px solid #E4E7ED;">
                        <div style="max-height:100%; margin:4px;">
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
                                    prop="date"
                                    label="日期"
                                    width="120">
                                </el-table-column>
                                <el-table-column
                                    prop="closeprofit"
                                    label="平仓盈亏"
                                    width="80">
                                </el-table-column>
                                <el-table-column
                                    prop="dynprofit"
                                    label="浮动盈亏"
                                    width="100">
                                </el-table-column>
                                <el-table-column
                                    prop="fee"
                                    label="手续费"
                                    width="120">
                                </el-table-column>
                                <el-table-column
                                    prop="dynbalance"
                                    label="动态权益">
                                </el-table-column>
                            </el-table>
                        </div>
                    </div>
                    <div style="flex:1;width:100%;overflow:auto;">
                        <div id="trend" style="width:100%;height:100%;">
                        </div>
                    </div>
                </div>
            </el-main>
        </el-container>
    </div>    
</template>

<script>
export default {
    name: 'stradata',
    props:{
        groupid:{
            type:String,
            default(){
                return "";
            }
        }
    },
    components: {
    },
    watch:{
        groupid: function(newVal, oldVal){
            newVal = newVal || "";
            oldVal = oldVal || "";

            if(newVal.length == 0 || newVal == oldVal)
                return;

            //console.log(oldVal, newVal);

            setTimeout(()=>{
                //this.queryData();
                this.$api.getStrategies(newVal, (resObj)=>{
                    //console.log(resObj);
                    if(resObj.result < 0){
                        this.$alert(resObj.message);
                    } else {
                        this.strategies = resObj.strategies;
                        this.strafilter = this.strategies[0];

                        this.queryData();
                    }
                });
            }, 300);
        }
    },
    data () {
        return {
            selCat:"pos",
            strafilter:"",
            strategies:[],
            loading:{
                trade: false,
                signal: false,
                round: false,
                position: false,
                fund: false
            },
            trades:[],
            positions:[],
            signals:[],
            rounds:[],
            strategies:[],
            funds:[],
            nvChart:null
        }
    },
    methods: {
        handleCatChange: function(tab, event){
            if(this.selCat == tab.name)
                return;

            this.selCat = tab.name;

            if(this.selCat != 'pos' && this.strafilter=='all')
                this.strafilter = this.strategies[0];

            this.queryData();
        },
        onStraSwitch: function(){
            this.queryData();
        },
        formatAmount: function(row,col){
            return row[col.property].toFixed(2);
        },
        queryData: function(){
            let self = this;
            let curCat = this.selCat;
            let groupid = this.groupid || "";
            let straid = this.strafilter || "";

            if(groupid.length == 0){
                this.$notify.error("组合ID不能为空");
                return;
            }

            if(straid.length == 0){
                this.$notify.error("策略ID不能为空");
                return;
            }

            if(curCat == "trd"){
                self.loading.trade = true;
                setTimeout(()=>{
                    this.$api.getTrades(groupid, straid, (resObj)=>{
                        if (resObj.result < 0) {
                            self.$alert("查询成交出错：" + resObj.message, "查询失败");
                        } else {
                            resObj.trades.forEach((tItem)=>{
                                let action = "";
                                if(tItem.offset == "OPEN")
                                    action += "开";
                                else 
                                    action += "平";

                                if(tItem.offset == "LONG")
                                    action += "多";
                                else 
                                    action += "空";

                                tItem.action = action;
                            });
                            self.trades = resObj.trades;
                            self.trades.reverse();
                        }

                        self.loading.trade = false;
                    });
                }, 300);                
            } else if(curCat == "sig"){
                self.loading.signal = true;
                setTimeout(()=>{
                    this.$api.getSignals(groupid, straid, (resObj)=>{
                        if (resObj.result < 0) {
                            self.$alert("查询信号出错：" + resObj.message, "查询失败");
                        } else {
                            self.signals = resObj.signals;
                            self.signals.reverse();
                        }

                        self.loading.signal = false;
                    });
                }, 300);   
            } else if(curCat == "rnd"){
                self.loading.round = true;
                setTimeout(()=>{
                    this.$api.getRounds(groupid, straid, (resObj)=>{
                        if (resObj.result < 0) {
                            self.$alert("查询回合出错：" + resObj.message, "查询失败");
                        } else {
                            self.rounds = resObj.rounds;
                            self.rounds.reverse();
                        }

                        self.loading.round = false;
                    });
                }, 300);   
            } else if(curCat == "pos"){
                self.loading.position = true;
                setTimeout(()=>{
                    this.$api.getPositions(groupid, straid, (resObj)=>{
                        if (resObj.result < 0) {
                            self.$alert("查询持仓出错：" + resObj.message, "查询失败");
                        } else {
                            resObj.positions.forEach((pItem)=>{
                                pItem.qty = pItem.volumn*(pItem.long?1:-1);
                            })
                            self.positions = resObj.positions;
                        }

                        self.loading.position = false;
                    });
                }, 300);   
            } else if(curCat == "fnd"){
                self.loading.fund = true;
                setTimeout(()=>{
                    this.$api.getFunds(groupid, straid, (resObj)=>{
                        if (resObj.result < 0) {
                            self.$alert("查询绩效出错：" + resObj.message, "查询失败");
                        } else {
                            self.funds = resObj.funds;
                            
                            if(this.nvChart == null) 
                                this.nvChart = this.$echarts.init(document.getElementById('trend'));

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
                                    smooth: true,
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
                                                    color: 'rgba(250,183,8,0.5)' // 0% 处的颜色
                                                }, {
                                                    offset: 1,
                                                    color: 'rgba(0,0,0,0.3)' // 100% 处的颜色
                                                }],
                                                globalCoord: false // 缺省为 false
                                            }
                                        }
                                    },
                                    data: [],
                                    lineStyle: {
                                        normal: {
                                            color: 'rgb(250,183,8)',
                                            width: 2
                                        }
                                    },
                                    itemStyle: {
                                        normal: {
                                            color: 'rgb(250,183,8)',
                                            borderWidth: 1
                                        }
                                    }
                                }]
                            };

                            let dates = [],
                                prices = [];
                            
                            let baseamt = 5000000;
                            for(let idx in resObj.funds) {
                                let item = resObj.funds[idx];
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

                            this.nvChart.setOption(options);

                            self.funds.reverse();
                        }

                        self.loading.fund = false;
                    });
                }, 300);   
            }
        }
    },
    mounted(){
        
    }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.el-header{
    padding: 0px 4px;
}

.table{
    width:100%;
    height:100%;
}

.el-select{
    width: 120px;
}
</style>
