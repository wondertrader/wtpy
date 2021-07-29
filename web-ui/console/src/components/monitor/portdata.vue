<template>
    <div style="height:100%;overflow:auto;">
        <el-container style="height:100%;overflow:auto;">
            <el-header style="height:40px; overflow-y:hidden;">
                <div style="height:100%;display:flex;flex-direction:row;">
                    <div style="flex:0;height:100%;">
                        <el-tabs :value="selCat" tab-position="top" @tab-click="handleCatChange" style="height:100%;margin:0;">
                            <el-tab-pane label="持仓数据" name="pos">
                            </el-tab-pane>
                            <el-tab-pane label="组合风控" name="rsk">
                            </el-tab-pane>
                            <el-tab-pane label="每日绩效" name="fnd" v-if="isAdmin">
                            </el-tab-pane>
                        </el-tabs>
                    </div>
                    <div style="flex:1;border-bottom:2px solid #E4E7ED;margin-top: 4px;">
                        <div style="float:right">
                            <el-row>
                                <el-col :offset="7" :span="4">
                                    <el-tooltip class="item" effect="dark" content="每隔30秒刷新一次" placement="top" v-show="selCat=='pos'">
                                        <el-checkbox v-model="autoData" style="float:right;margin-top:6px;" @change="handleCheckAutoData">自动刷新</el-checkbox>
                                    </el-tooltip>
                                </el-col>
                                <el-col :offset="1" :span="4">
                                    <el-button type="primary" icon="el-icon-refresh" size="mini" plain @click="queryData()">刷新</el-button>
                                </el-col>
                            </el-row>
                        </div>
                    </div> 
                </div>
            </el-header>
            <el-main style="overflow:auto;border-bottom:1px solid #E4E7ED;">
                <div style="height:100%;display:flex;flex-direction:row;" v-show="selCat=='pos'" v-loading="loading.position" >
                    <div style="flex:1;height:100%;overflow:auto;border-right:1px solid #E4E7ED;width:100%;">
                        <div>
                            <el-table
                                border
                                stripe
                                :data="positions"
                                :summary-method="getPosSum"
                                show-summary
                                class="table">
                                <el-table-column
                                    prop="code"
                                    label="品种"
                                    width="120"
                                    sortable>
                                </el-table-column>
                                <el-table-column
                                    label="数量"
                                    width="100">
                                    <template slot-scope="scope">
                                        <span :class="scope.row.qty>=0?'text-danger':'text-success'">{{scope.row.qty}}</span>
                                    </template>
                                </el-table-column>
                                <el-table-column
                                    label="浮盈"
                                    width="100"
                                    sortable>
                                    <template slot-scope="scope">
                                        <span :class="scope.row.profit>=0?'text-danger':'text-success'">{{scope.row.profit.toFixed(1)}}</span>
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
                                    width="100">
                                    <template slot-scope="scope">
                                        <span>{{fmtPrice(scope.row.price)}}</span>
                                    </template>
                                </el-table-column>
                            </el-table>
                        </div>
                    </div>
                    <div style="flex:1;height:100%;overflow:auto;width:100%;display:flex;flex-direction:column;" v-if="isAdmin">
                        <div style="flex:1;width:100%;height:100%;">
                            <div id="pie" style="width:100%;height:100%;">
                            </div>
                        </div>
                    </div>
                </div>
                <div style="height:100%;overflow:auto;"  v-show="selCat=='rsk'" v-loading="loading.risk">
                    <div style="height:100%;display:flex;flex-direction:column;">
                        <div style="flex:1;display:flex;flex-direction:row;">
                            <div class="filter-pane el-card is-always-shadow">
                                <div style="height:100%;display:flex;flex-direction:column;">
                                    <div style="flex:0 1 44px;padding: 18px 20px;border-bottom: 1px solid #EBEEF5;box-sizing: border-box;">
                                        <span class="filter">策略过滤器</span>
                                        <el-button style="float: right; margin-left:1px;" 
                                            type="danger" size="mini" plain 
                                            @click="checkAllFilters('strategy_filters',true)">一键过滤</el-button>
                                        <el-button style="float: right; margin-right:1px;" 
                                            type="success" size="mini" plain
                                            @click="checkAllFilters('strategy_filters',false)">一键通过</el-button>
                                    </div>
                                    <div style="flex:1 0 0; overflow:auto;padding:20px;">
                                        <el-row v-for="val,id in filters['strategy_filters']" :key="id" class="filter-row">
                                            <el-col :span="12">
                                                <i class="el-icon-cpu"/><span class="filter-strategy">{{id}}</span>
                                            </el-col>
                                            <el-col :span="12">
                                                <el-switch
                                                    v-model="filters['strategy_filters'][id]"
                                                    active-text="过滤"
                                                    inactive-text="通过"
                                                    inactive-color="#13ce66"
                                                    active-color="#ff4949">
                                                </el-switch>
                                            </el-col>
                                        </el-row>
                                    </div>
                                </div>
                            </div>
                            <div class="filter-pane el-card is-always-shadow">
                                <div style="height:100%;display:flex;flex-direction:column;">
                                    <div style="flex:0 1 44px;padding: 18px 20px;border-bottom: 1px solid #EBEEF5;box-sizing: border-box;">
                                        <span class="filter">代码过滤器</span>
                                        <el-button style="float: right; margin-left:1px;" 
                                            type="danger" size="mini" plain
                                            @click="checkAllFilters('code_filters',true)">一键过滤</el-button>
                                        <el-button style="float: right; margin-right:1px;" 
                                            type="success" size="mini" plain
                                            @click="checkAllFilters('code_filters',false)">一键通过</el-button>
                                    </div>
                                    <div style="flex:1 0 0; overflow:auto;padding:20px;">
                                        <el-row v-for="val,id in filters['code_filters']" :key="id" class="filter-row">
                                            <el-col :span="10" style="margin-top:4px;">
                                                <i class="el-icon-collection"/><span class="filter-code">{{id}}</span>
                                            </el-col>
                                            <el-col :span="10" style="margin-top:4px;">
                                                <el-switch
                                                    v-model="filters['code_filters'][id]"
                                                    active-text="过滤"
                                                    inactive-text="通过"
                                                    inactive-color="#13ce66"
                                                    active-color="#ff4949"
                                                    style="float:right;">
                                                </el-switch>
                                            </el-col>
                                            <el-col :span="4">
                                                <el-tooltip placement="top">
                                                    <div slot="content">删除代码过滤器</div>
                                                    <el-button size="mini" circle icon="el-icon-delete" style="float:right;" @click="onDelCodeFilter(id)"></el-button>
                                                </el-tooltip>
                                            </el-col>
                                        </el-row>
                                        <el-row class="filter-row">
                                            <el-tooltip placement="top">
                                                <div slot="content">添加代码过滤器</div>
                                                <el-button style="width:100%;" type="primary" plain @click="onAddCodeFilter()" icon="el-icon-plus"></el-button>
                                            </el-tooltip>
                                        </el-row>
                                    </div>
                                </div>
                            </div>
                            <div class="filter-pane el-card is-always-shadow">
                                <div style="height:100%;display:flex;flex-direction:column;">
                                    <div style="flex:0 1 44px;padding: 18px 20px;border-bottom: 1px solid #EBEEF5;box-sizing: border-box;">
                                        <span class="filter">通道过滤器</span>
                                        <el-button style="float: right; margin-left:1px;" 
                                            type="danger" size="mini" plain
                                            @click="checkAllFilters('channel_filters',true)">一键过滤</el-button>
                                        <el-button style="float: right; margin-right:1px;" 
                                            type="success" size="mini" plain
                                            @click="checkAllFilters('channel_filters',false)">一键通过</el-button>
                                    </div>
                                    <div style="flex:1 0 0; overflow:auto;padding:20px;">
                                        <el-row v-for="val,id in filters['channel_filters']" :key="id" class="filter-row">
                                            <el-col :span="12">
                                                <i class="el-icon-link"/><span class="filter-channel">{{id}}</span>
                                            </el-col>
                                            <el-col :span="12">
                                                <el-switch
                                                    v-model="filters['channel_filters'][id]"
                                                    active-text="过滤"
                                                    inactive-text="通过"
                                                    inactive-color="#13ce66"
                                                    active-color="#ff4949">
                                                </el-switch>
                                            </el-col>
                                        </el-row>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div style="flex:0 28px; margin:2px 0;">
                            <span style="font-size:12px;color:gray;line-height:24px;">
                                当过滤器生效时，相关的信号都会被过滤掉！修改完过滤器，一定要记得<strong>提交</strong>！提交以后会在<strong>1分钟内</strong>生效！
                            </span>
                            <el-button type="danger" icon="el-icon-finished" style="float:right;" @click="onCommitFilters()">提交</el-button>
                        </div>
                    </div>
                </div>
                <div style="height:100%;display:flex;flex-direction:column;"  v-show="selCat=='fnd'" v-loading="loading.fund"  v-if="isAdmin">
                    <div style="height:40px;display:inline-block;flex:0;margin:4px;">
                        <el-row>
                            <el-col :span="2" style="margin-top:2px;">
                                <i class="el-icon-money"></i>
                                <a>资金规模</a>
                            </el-col>
                            <el-col :span="3" >
                                <el-input v-model="capital" placeholder="请输入资金规模" size="mini" type="number" min="1000000" step="1000000"></el-input>
                            </el-col>
                            <el-col :span="2" style="margin-left:2px;">
                                <el-button size="mini" plain type="danger" @click="onClickResetCapital">刷新数据</el-button>
                            </el-col>
                        </el-row>
                    </div>
                    <div style="flex:1;width:100%;overflow:auto;height:50%;border-bottom:1px solid #E4E7ED;">
                        <div style="max-height:100%;">
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
                                    width="90">
                                    <template slot-scope="scope">
                                        <span :class="scope.row.closeprofit>=0?'text-danger':'text-success'">{{scope.row.closeprofit.toFixed(1)}}</span>
                                    </template>
                                </el-table-column>
                                <el-table-column
                                    label="浮动盈亏"
                                    width="90">
                                    <template slot-scope="scope">
                                        <span :class="scope.row.dynprofit>=0?'text-danger':'text-success'">{{scope.row.dynprofit.toFixed(1)}}</span>
                                    </template>
                                </el-table-column>
                                <el-table-column
                                    prop="fee"
                                    label="佣金"
                                    width="80"
                                    :formatter="formatAmount">
                                </el-table-column>
                                <el-table-column
                                    label="动态权益"
                                    width="110">
                                    <template slot-scope="scope">
                                        <span :class="(scope.row.dynbalance+scope.row.capital)>=0?'text-danger':'text-success'">{{(scope.row.dynbalance+scope.row.capital).toFixed(1)}}</span>
                                    </template>
                                </el-table-column>
                                <el-table-column
                                    label="日内最大市值"
                                    width="140">
                                    <template slot-scope="scope">
                                        <span class="text-danger">{{(scope.row.maxdynbalance+scope.row.capital).toFixed(1) + "(" + fmtFundTime(scope.row.maxtime) + ")"}}</span>
                                    </template>
                                </el-table-column>
                                <el-table-column
                                    label="日内最小市值"
                                    width="140">
                                    <template slot-scope="scope">
                                        <span class="text-success">{{(scope.row.mindynbalance+scope.row.capital).toFixed(1) + "(" + fmtFundTime(scope.row.mintime) + ")"}}</span>
                                    </template>
                                </el-table-column>
                                <el-table-column
                                    label="多日最大市值"
                                    width="160">
                                    <template slot-scope="scope">
                                        <span class="text-danger">{{(scope.row.mdmaxbalance+scope.row.capital).toFixed(1) + "(" + fmtFundDate(scope.row.mdmaxdate) + ")"}}</span>
                                    </template>
                                </el-table-column>
                                <el-table-column
                                    label="多日最小市值"
                                    width="160">
                                    <template slot-scope="scope">
                                        <span class="text-success">{{(scope.row.mdminbalance+scope.row.capital).toFixed(1) + "(" + fmtFundDate(scope.row.mdmindate) + ")"}}</span>
                                    </template>
                                </el-table-column>
                            </el-table>
                        </div>
                    </div>
                    <div style="flex:1;width:100%;overflow:auto;display:flex;flex-direction:column;margin:4px;">
                        <div style="flex:1;width:100%;border-top:1px solid #E4E7ED;">
                            <div id="grptrend" style="width:100%;height:100%;">
                            </div>
                        </div>                        
                    </div>
                </div>
            </el-main>
            <el-footer style="height:24px;">
                <span style="font-size:12px;color:gray;line-height:24px;">数据刷新时间: {{refreshTime}}</span>
            </el-footer>
        </el-container>
    </div>    
</template>

<script>
import { mapGetters } from 'vuex';
export default {
    name: 'portdata',
    props:{
        groupid:{
            type:String,
            default(){
                return "";
            }
        }
    },
    computed:{
        ...mapGetters([
            'cache'
        ]),
        isAdmin(){
            let uInfo = this.cache.userinfo;
            if(uInfo)
                return (uInfo.role == 'admin' || uInfo.role == 'superman');
            else
                return false;        
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


            setTimeout(()=>{
                this.queryData();
            }, 300);
        }
    },
    data () {
        return {
            selCat: "pos",
            loading:{
                risk: false,
                performance: false,
                position: false,
                fund: false
            },
            capital:5000000,
            performances:[],
            positions:[],
            filters:{},
            funds:[],
            nvChart:null,
            pieChart:null,
            autoData: false,
            dataInterval: 0,
            refreshTime:new Date().format('yyyy.MM.dd hh:mm:ss')
        }
    },
    methods: {
        handleCheckAutoData: function(val){
            this.resetDataInterval();
        },
        resetDataInterval: function(){
            if(this.autoData){
                if(this.dataInterval != 0){
                    clearInterval(this.dataInterval);
                }

                this.dataInterval = setInterval(()=>{
                    if(this.selCat == 'pos')
                        this.queryData();
                }, 30000);
            } else if(this.dataInterval != 0){
                clearInterval(this.dataInterval);
            }
        },
        getPosSum: function(param){
            const { columns, data } = param;
            const sums = [];
            columns.forEach((column, index) => {
                if (index != 0 && index != 1 && index != 2 && index != 3) {
                    sums[index] = '';
                    return;
                } else if (index == 0){
                    sums[index] = '总计';
                    return;
                } else if (index == 1){
                    const values = data.map(item => Number(item.qty));
                    if (!values.every(value => isNaN(value))) {
                        sums[index] = data.length + "笔 | " + values.reduce((prev, curr) => {
                            const value = Number(curr);
                            if (!isNaN(value)) {
                                return prev + Math.abs(curr);
                            } else {
                                return prev;
                            }
                            }, 0) + '手';
                    } else {
                        sums[index] = 'N/A';
                    }
                } else if (index == 2){
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
        handleCatChange: function(tab, event){
            if(this.selCat == tab.name)
                return;

            this.selCat = tab.name;

            this.queryData();
        },
        formatAmount: function(row,col){
            return row[col.property].toFixed(2);
        },
        fmtFundTime:function(val){
            let ret = Math.floor(val/1000) + "";
            if(ret.length < 6)
                ret = "0" + ret;

            return ret.substr(0,2) + ":" + ret.substr(2,2);
        },
        fmtFundDate:function(val){
            let ret = val + "";
            return ret.substr(2,2) + "." + ret.substr(4,2) + "." + ret.substr(6,2);
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
        onClickResetCapital: function(){
            let self = this;
            let capital = parseInt(self.capital);
            self.funds.forEach((item)=>{
                item.capital = capital;
            });
            this.paintChart();
        },
        paintChart: function(){
            let self = this;
            if(this.nvChart == null) 
                this.nvChart = this.$echarts.init(document.getElementById('grptrend'));

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

            let baseamt = parseInt(self.capital);
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

            this.nvChart.setOption(options);
        },
        paintPie: function(){
            if(!this.isAdmin)
                return;
            let self = this;
            if(this.pieChart == null) 
                this.pieChart = this.$echarts.init(document.getElementById('pie'));

            let datas = [];
            for(let pid in self.performances){
                let item  = self.performances[pid];
                let profit = item.closeprofit+item.dynprofit;
                datas.push({
                    value: Math.abs(profit),
                    truevalue: profit,
                    name:pid
                });
            }

            let options = {
                title: {
                    text: '组合绩效归因',
                    subtext: '按品种',
                    left: 'center'
                },
                tooltip: {
                    trigger: 'item',
                    formatter1: '{a} <br/>{b} : {c} ({d}%)',
                    formatter: function(params) {
                        return params.name + ": " + (params.data.truevalue/10000).toFixed(2) + "万(" + params.percent.toFixed(1) + "%)";
                    }
                },
                legend: {
                    orient: 'horizontal',
                    left: 'center',
                    top: 'bottom'
                },
                series: [
                    {
                        name: '分品种绩效',
                        type: 'pie',
                        radius: '50%',
                        emphasis: {
                            itemStyle: {
                                shadowBlur: 10,
                                shadowOffsetX: 0,
                                shadowColor: 'rgba(0, 0, 0, 0.5)'
                            }
                        },
                        data: datas
                    }
                ]
            };

            this.pieChart.setOption(options);
        },
        queryPerf: function(){
            let self = this;
            let groupid = this.groupid || "";
            this.$api.getPortPerfs(groupid, (resObj)=>{
                if (resObj.result < 0) {
                    self.$notify.error("查询绩效归因出错：" + resObj.message, "查询失败");
                } else {
                    self.performances = resObj.performance;
                    setTimeout(()=>{
                        self.paintPie();
                    }, 300);                    
                }
            });
        },
        checkAllFilters: function(fid, bCheck){
            for(let id in this.filters[fid]){
                this.filters[fid][id] = bCheck;
            }
        },
        onAddCodeFilter: function(){
            let self = this;
            self.$prompt('请输入品种代码，格式如CFFEX.IF', '新增代码过滤器', {
                confirmButtonText: '确定',
                cancelButtonText: '取消'
            }).then(({ value }) => {
                if(self.filters["code_filters"][value] != undefined){
                    self.$alert("该品种代码已存在");
                    return true;
                } else {
                    self.filters["code_filters"][value] = true;
                    self.$forceUpdate();
                }
            }).catch(() => {
                         
            });
        },
        onDelCodeFilter: function(code){
            let self = this;
            this.$confirm('确定要删除该代码过滤器吗?', '删除代码过滤器', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning'
            }).then(() => {
                delete self.filters["code_filters"][code];
                self.$forceUpdate();
            }).catch(() => {
                         
            });
        },
        onCommitFilters: function(){
            let self = this;
            this.$confirm('确定要提交最新的过滤器配置吗?', '提交过滤器', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning'
            }).then(() => {
                let groupid = this.groupid || "";
                self.$api.commitPortFilters(groupid, self.filters, (resObj)=>{
                    if(resObj.result < 0){
                        this.$notify.error("提交过滤器出错：" + resObj.message);
                    } else {
                        this.$notify({
                            message: "过滤器提交成功"
                        });
                    }
                });
            }).catch(() => {
                         
            });
        },
        queryData: function(needReset){
            needReset = needReset || false;
            let self = this;
            let curCat = this.selCat;
            let groupid = this.groupid || "";

            if(groupid.length == 0){
                this.$notify.error("组合ID不能为空");
                return;
            }


            if(curCat == "pos"){
                self.loading.position = true;
                setTimeout(()=>{
                    this.$api.getPortPositions(groupid, (resObj)=>{
                        if (resObj.result < 0) {
                            this.$notify.error("查询持仓出错：" + resObj.message);
                        } else {
                            resObj.positions.forEach((pItem)=>{
                                pItem.qty = pItem.volume*(pItem.long?1:-1);
                            })
                            self.positions = resObj.positions;
                        }

                        self.loading.position = false;
                        self.refreshTime = new Date().format('yyyy.MM.dd hh:mm:ss');
                        if(needReset)
                            self.resetDataInterval();
                    });

                    this.queryPerf();
                }, 300);   
            } else if(curCat == "fnd"){
                self.loading.fund = true;
                setTimeout(()=>{
                    let capital = parseInt(self.capital);
                    this.$api.getPortFunds(groupid, (resObj)=>{
                        if (resObj.result < 0) {
                            this.$notify.error("查询绩效出错：" + resObj.message);
                        } else {
                            resObj.funds.forEach((item)=>{
                                item.dynbalance = item.balance + item.dynprofit;
                                item.capital = capital;
                            });
                            self.funds = resObj.funds;                            
                            self.funds.reverse();
                            
                            self.paintChart();
                        }
                        self.loading.fund = false;
                        self.refreshTime = new Date().format('yyyy.MM.dd hh:mm:ss');
                        if(needReset)
                            self.resetDataInterval();
                    });
                }, 300);   
            } else if(curCat == "rsk"){
                self.loading.risk = true;
                setTimeout(()=>{
                    let capital = parseInt(self.capital);
                    this.$api.getPortFilters(groupid, (resObj)=>{
                        if (resObj.result < 0) {
                            this.$notify.error("查询过滤器出错：" + resObj.message);
                        } else {
                            resObj.filters["strategy_filters"] = resObj.filters["strategy_filters"] || {};
                            resObj.filters["code_filters"] = resObj.filters["code_filters"] || {};
                            resObj.filters["channel_filters"] = resObj.filters["executer_filters"] || {};

                            self.filters = resObj.filters;
                        }
                        self.loading.risk = false;
                        self.refreshTime = new Date().format('yyyy.MM.dd hh:mm:ss');
                        if(needReset)
                            self.resetDataInterval();
                    });
                }, 300);   
            }
        }
    },
    mounted(){
        let self = this;
        window.onresize = function(){
            if (!self.zooming) {
                self.zooming = true
                setTimeout(function () {
                    if(self.myChart) self.nvChart.resize();
                    if(self.pieChart) self.pieChart.resize();
                    self.zooming = false;
                }, 300);
            }
        };

        self.$nextTick(()=>{
            self.$on("resize", ()=>{
                if (!self.zooming) {
                    self.zooming = true
                    setTimeout(function () {
                        if(self.myChart) self.nvChart.resize();
                        if(self.pieChart) self.pieChart.resize();
                        self.zooming = false;
                    }, 150);
                }
            });
        });
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

.filter{
    font-size: 24px;
    font-weight: bold;
}

.filter-row{
    padding-top: 4px;
    padding-bottom: 4px;
}

.filter-strategy{
    padding-left: 4px;
}

.filter-code{
    padding-left: 4px;
}

.filter-channel{
    padding-left: 4px;
}

.filter-pane{
    flex:1;
    margin:2px;
}

.delete-btn{
    float:right;
    color:#ff4949;
}

.delete-btn i{
    color:#ff4949;
}
</style>
