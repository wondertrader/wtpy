<template>
    <div style="height:100%;">
        <el-container style="height:100%;">
            <el-header style="height:40px; overflow-y:hidden;">
                <div style="height:100%;display:flex;flex-direction:row;">
                    <div style="flex:0;height:100%;">
                        <el-tabs :value="selCat" tab-position="top" @tab-click="handleCatChange">
                            <el-tab-pane label="持仓明细" name="pos">
                            </el-tab-pane>
                            <el-tab-pane label="成交明细" name="trd">
                            </el-tab-pane>
                            <el-tab-pane label="订单明细" name="ord">
                            </el-tab-pane>
                            <el-tab-pane label="资金明细" name="fnd">
                            </el-tab-pane>
                        </el-tabs>
                    </div>
                    <div style="flex:1;border-bottom:2px solid #E4E7ED;margin-top: 4px;">
                        <div style="float:right">
                            <el-row>
                                <el-col :span="4">
                                    <el-tooltip class="item" effect="dark" content="每隔30秒刷新一次" placement="top">
                                        <el-checkbox v-model="autoData" style="float:right;margin-top:6px;" @change="handleCheckAutoData">自动刷新</el-checkbox>
                                    </el-tooltip>
                                </el-col>
                                <el-col :offset="1" :span="12">
                                    <el-select v-model="chnlfilter" placeholder="请选择" size="mini" @change="onChnlSwitch">
                                        <el-option label="全部通道" value="all" v-show="showAllChannels(selCat)">
                                            <i class="el-icon-tickets"/>
                                            <span>全部通道</span>
                                        </el-option>
                                        <el-option :label="cid" :value="cid" :key="cid" v-for="cid in channels">
                                            <i class="el-icon-tickets"/>
                                            <span>{{cid}}</span>
                                        </el-option>
                                    </el-select>
                                </el-col>
                                <el-col :span="4">
                                    <el-button type="primary" icon="el-icon-refresh" size="mini" plain @click="queryData()">刷新</el-button>
                                </el-col>
                            </el-row>                            
                        </div>
                    </div> 
                </div>
            </el-header>
            <el-main style="overflow:auto;border-bottom: 1px solid #E4E7ED;">
                <div style="max-height:100%;overflow:auto;" v-show="selCat=='pos'" v-loading="loading.position">
                    <el-table
                        border
                        stripe
                        :data="positions"
                        :summary-method="getPosSum"
                        show-summary
                        class="table">
                        <el-table-column
                            prop="channel"
                            label="通道"
                            width="120">
                        </el-table-column>
                        <el-table-column
                            prop="code"
                            label="品种"
                            width="120"
                            sortable>
                        </el-table-column>
                        <el-table-column
                            prop="long"
                            label="多头"
                            width="140">
                            <template slot-scope="scope">
                                <a class="text-danger">
                                    <span>昨{{scope.row.long.prevol}}[{{ scope.row.long.preavail}}]</span>
                                    <span>|</span>
                                    <span>今{{scope.row.long.newvol}}[{{ scope.row.long.newavail}}]</span>
                                </a>
                            </template>
                        </el-table-column>
                        <el-table-column
                            prop="short"
                            label="空头"
                            width="140">
                            <template slot-scope="scope">
                                <a class="text-success">
                                    <span>昨{{scope.row.short.prevol}}[{{ scope.row.short.preavail}}]</span>
                                    <span>|</span>
                                    <span>今{{scope.row.short.newvol}}[{{ scope.row.short.newavail}}]</span>
                                </a>
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
                            prop="channel"
                            label="通道"
                            width="120">
                        </el-table-column>
                        <el-table-column
                            prop="code"
                            label="品种"
                            width="120"
                            sortable>
                        </el-table-column>
                        <el-table-column
                            prop="time"
                            label="时间"
                            width="150"
                            sortable
                            :formatter="formatTime">
                        </el-table-column>
                        <el-table-column
                            prop="localid"
                            label="本地单号"
                            width="120">
                        </el-table-column>
                        <el-table-column
                            label="动作"
                            width="80">
                            <template slot-scope="scope">
                                <span :class="getActClr(scope.row.action)">{{scope.row.action}}</span>
                            </template>
                        </el-table-column>
                        <el-table-column
                            prop="price"
                            label="价格"
                            width="80"
                            :formatter="fmtPrice">
                        </el-table-column>
                        <el-table-column
                            prop="volume"
                            label="数量"
                            width="80">
                        </el-table-column>
                        <el-table-column
                            prop="tradeid"
                            label="成交单号"
                            width="100">
                        </el-table-column>
                        <el-table-column
                            prop="orderid"
                            label="委托单号"
                            width="100">
                        </el-table-column>
                    </el-table>
                </div>
                <div style="max-height:100%;overflow:auto;"  v-show="selCat=='ord'" v-loading="loading.order">
                    <el-table
                        border
                        stripe
                        :data="orders"
                        :summary-method="getOrdSum"
                        show-summary
                        class="table">
                        <el-table-column
                            prop="channel"
                            label="通道"
                            width="120">
                        </el-table-column>
                        <el-table-column
                            prop="code"
                            label="品种"
                            width="120"
                            sortable>
                        </el-table-column>
                        <el-table-column
                            prop="time"
                            label="委托时间"
                            width="150"
                            sortable
                            :formatter="formatTime">
                        </el-table-column>
                        <el-table-column
                            prop="localid"
                            label="本地单号"
                            width="120">
                        </el-table-column>
                        <el-table-column
                            label="动作"
                            width="80">
                            <template slot-scope="scope">
                                <span :class="getActClr(scope.row.action)">{{scope.row.action}}</span>
                            </template>
                        </el-table-column>
                        <el-table-column
                            prop="price"
                            label="价格"
                            width="80"
                            :formatter="fmtPrice">
                        </el-table-column>
                        <el-table-column
                            prop="total"
                            label="数量"
                            width="80">
                        </el-table-column>
                        <el-table-column
                            prop="traded"
                            label="成交"
                            width="80">
                        </el-table-column>
                        <el-table-column
                            prop="orderid"
                            label="委托单号"
                            width="100">
                        </el-table-column>
                        <el-table-column
                            label="撤销"
                            width="80">
                            <template slot-scope="scope">
                                <span :class="scope.row.canceled=='TRUE'?'text-danger':'text-info'">{{scope.row.canceled=='TRUE'?'是':'否'}}</span>
                            </template>
                        </el-table-column>
                    </el-table>
                </div>
                <div style="max-height:100%;overflow:auto;"  v-show="selCat=='fnd'" v-loading="loading.fund">
                    <el-table
                        border
                        stripe
                        :data="funds"
                        :summary-method="getFndSum"
                        show-summary
                        class="table">
                        <el-table-column
                            prop="channel"
                            label="通道"
                            width="120"
                            sortable>
                        </el-table-column>
                        <el-table-column
                            prop="currency"
                            label="币种"
                            width="64">
                        </el-table-column>
                        <el-table-column
                            prop="prebalance"
                            label="上日结存"
                            width="120"
                            sortable
                            :formatter="fmtAmount">
                        </el-table-column>
                        <el-table-column
                            prop="balance"
                            label="静态权益"
                            width="120"
                            sortable
                            :formatter="fmtAmount">
                        </el-table-column>
                        <el-table-column
                            label="平仓盈亏"
                            width="110"
                            sortable>
                            <template slot-scope="scope">
                                <span :class="scope.row.closeprofit>=0?'text-danger':'text-success'">{{scope.row.closeprofit.toFixed(2)}}</span>
                            </template>
                        </el-table-column>
                        <el-table-column
                            label="浮动盈亏"
                            width="110"
                            sortable>
                            <template slot-scope="scope">
                                <span :class="scope.row.dynprofit>=0?'text-danger':'text-success'">{{scope.row.dynprofit.toFixed(2)}}</span>
                            </template>
                        </el-table-column>
                        <el-table-column
                            prop="margin"
                            label="保证金"
                            width="120"
                            sortable
                            :formatter="fmtAmount">
                        </el-table-column>
                        <el-table-column
                            prop="fee"
                            label="手续费"
                            width="100"
                            sortable
                            :formatter="fmtAmount">
                        </el-table-column>
                        <el-table-column
                            prop="available"
                            label="可用资金"
                            width="120"
                            sortable
                            :formatter="fmtAmount">
                        </el-table-column>
                        <el-table-column
                            label="出入金"
                            width="100"
                            sortable>
                            <template slot-scope="scope">
                                <span :class="scope.row.moneyio>=0?'text-danger':'text-success'">{{scope.row.moneyio.toFixed(2)}}</span>
                            </template>
                        </el-table-column>
                    </el-table>
                </div>
            </el-main>
            <el-footer style="height:24px;">
                <span style="font-size:12px;color:gray;line-height:24px;">数据刷新时间: {{refreshTime}}</span>
            </el-footer>
        </el-container>
    </div>    
</template>

<script>
export default {
    name: 'tradedata',
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

            setTimeout(()=>{
                this.$api.getChannels(newVal, (resObj)=>{
                    //console.log(resObj);
                    if(resObj.result < 0){
                        this.$notify.error('拉取组合交易通道出错：' + resObj.message);
                    } else {
                        this.channels = resObj.channels;
                        
                        let needShowAll = this.showAllChannels(this.selCat);

                        if( !needShowAll)
                            this.chnlfilter = this.channels[0];
                        else
                            this.chnlfilter = 'all';

                        setTimeout(()=>{
                            this.queryData();
                        }, 300);
                    }
                });
            }, 300);
        }
    },
    data () {
        return {
            selCat:"pos",
            chnlfilter:"all",
            channels:[],
            loading:{
                trade: false,
                order: false,
                position: false,
                fund: false
            },
            trades:[],
            orders:[],
            positions:[],
            funds:[],
            autoData: false,
            dataInterval: 0,
            refreshTime:new Date().format('yyyy.MM.dd hh:mm:ss')
        }
    },
    methods: {
        showAllChannels: function(catid){
            if(catid == 'fnd' || catid == 'pos')
                return true;
            return false;
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
                    sums[index] = data.length + "笔";
                } else if (index == 2){
                    const values = data.map(item => Number(item.long.newvol));
                    const values_Pre = data.map(item => Number(item.long.prevol));
                    sums[index] = '昨' + values_Pre.reduce((prev, curr) => {
                            const value = Number(curr);
                            if (!isNaN(value)) {
                                return prev + curr;
                            } else {
                                return prev;
                            }
                        }, 0) + '手' +
                        ' | 今' + values.reduce((prev, curr) => {
                            const value = Number(curr);
                            if (!isNaN(value)) {
                                return prev + curr;
                            } else {
                                return prev;
                            }
                        }, 0) + '手';
                } else if (index == 3){
                    const values = data.map(item => Number(item.short.newvol));
                    const values_Pre = data.map(item => Number(item.short.prevol));
                    sums[index] = '昨' + values_Pre.reduce((prev, curr) => {
                            const value = Number(curr);
                            if (!isNaN(value)) {
                                return prev + curr;
                            } else {
                                return prev;
                            }
                        }, 0) + '手' +
                        ' | 今' + values.reduce((prev, curr) => {
                            const value = Number(curr);
                            if (!isNaN(value)) {
                                return prev + curr;
                            } else {
                                return prev;
                            }
                        }, 0) + '手';
                }
                
            });

            return sums;
        },
        getTrdSum: function(param){
            const { columns, data } = param;
            const sums = [];
            columns.forEach((column, index) => {
                if (index < 4 || index > 6) {
                    sums[index] = '';
                    return;
                } else if (index == 4){
                    sums[index] = '总计';
                    return;
                } else if (index == 5){
                    sums[index] = data.length + "笔";
                } else if (index == 6){
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
        getOrdSum: function(param){
            const { columns, data } = param;
            const sums = [];
            columns.forEach((column, index) => {
                if (index < 4 || index > 7) {
                    sums[index] = '';
                    return;
                } else if (index == 4){
                    sums[index] = '总计';
                    return;
                } else if (index == 5){
                    sums[index] = data.length + "笔";
                } else if (index == 6){
                    const values = data.map(item => Number(item.total));
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
                } else if (index == 7){
                    const values = data.map(item => Number(item.traded));
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
        getFndSum: function(param){
            const { columns, data } = param;
            const sums = [];
            columns.forEach((column, index) => {
                if (index == 0){
                    sums[index] = '总计';
                    return;
                } else if (index == 1){
                    sums[index] = data.length + "条";
                } else if (index == 2){
                    const values = data.map(item => Number(item.prebalance));
                    if (!values.every(value => isNaN(value))) {
                        sums[index] = values.reduce((prev, curr) => {
                            const value = Number(curr);
                            if (!isNaN(value)) {
                                return prev + curr;
                            } else {
                                return prev;
                            }
                            }, 0).toFixed(2);
                    } else {
                        sums[index] = 'N/A';
                    }
                } else if (index == 3){
                    const values = data.map(item => Number(item.balance));
                    if (!values.every(value => isNaN(value))) {
                        sums[index] = values.reduce((prev, curr) => {
                            const value = Number(curr);
                            if (!isNaN(value)) {
                                return prev + curr;
                            } else {
                                return prev;
                            }
                            }, 0).toFixed(2);
                    } else {
                        sums[index] = 'N/A';
                    }
                } else if (index == 4){
                    const values = data.map(item => Number(item.closeprofit));
                    if (!values.every(value => isNaN(value))) {
                        sums[index] = values.reduce((prev, curr) => {
                            const value = Number(curr);
                            if (!isNaN(value)) {
                                return prev + curr;
                            } else {
                                return prev;
                            }
                            }, 0).toFixed(2);
                    } else {
                        sums[index] = 'N/A';
                    }
                } else if (index == 5){
                    const values = data.map(item => Number(item.dynprofit));
                    if (!values.every(value => isNaN(value))) {
                        sums[index] = values.reduce((prev, curr) => {
                            const value = Number(curr);
                            if (!isNaN(value)) {
                                return prev + curr;
                            } else {
                                return prev;
                            }
                            }, 0).toFixed(2);
                    } else {
                        sums[index] = 'N/A';
                    }
                } else if (index == 6){
                    const values = data.map(item => Number(item.margin));
                    if (!values.every(value => isNaN(value))) {
                        sums[index] = values.reduce((prev, curr) => {
                            const value = Number(curr);
                            if (!isNaN(value)) {
                                return prev + curr;
                            } else {
                                return prev;
                            }
                            }, 0).toFixed(2);
                    } else {
                        sums[index] = 'N/A';
                    }
                } else if (index == 7){
                    const values = data.map(item => Number(item.fee));
                    if (!values.every(value => isNaN(value))) {
                        sums[index] = values.reduce((prev, curr) => {
                            const value = Number(curr);
                            if (!isNaN(value)) {
                                return prev + curr;
                            } else {
                                return prev;
                            }
                            }, 0).toFixed(2);
                    } else {
                        sums[index] = 'N/A';
                    }
                } else if (index == 8){
                    const values = data.map(item => Number(item.available));
                    if (!values.every(value => isNaN(value))) {
                        sums[index] = values.reduce((prev, curr) => {
                            const value = Number(curr);
                            if (!isNaN(value)) {
                                return prev + curr;
                            } else {
                                return prev;
                            }
                            }, 0).toFixed(2);
                    } else {
                        sums[index] = 'N/A';
                    }
                } else if (index == 9){
                    const values = data.map(item => Number(item.moneyio));
                    if (!values.every(value => isNaN(value))) {
                        sums[index] = values.reduce((prev, curr) => {
                            const value = Number(curr);
                            if (!isNaN(value)) {
                                return prev + curr;
                            } else {
                                return prev;
                            }
                            }, 0).toFixed(2);
                    } else {
                        sums[index] = 'N/A';
                    }
                }   
            });

            return sums;
        },
        handleCheckAutoData: function(val){
            this.resetDataInterval();
        },
        resetDataInterval: function(){
            if(this.autoData){
                if(this.dataInterval != 0){
                    clearInterval(this.dataInterval);
                }

                this.dataInterval = setInterval(()=>{
                    this.queryData();
                }, 30000);
            } else if(this.dataInterval != 0){
                clearInterval(this.dataInterval);
            }
        },
        getActClr: function(act){
            if(act == "开多" || act == "平空" || act == "平今空")
                return 'text-danger';
            else
                return 'text-success';
        },
        handleCatChange: function(tab, event){
            if(this.selCat == tab.name)
                return;

            this.selCat = tab.name;

            let needShowAll = this.showAllChannels(this.selCat);

            if( !needShowAll && this.chnlfilter=='all')
                this.chnlfilter = this.channels[0];
            else if(needShowAll)
                this.chnlfilter = 'all';

            this.queryData();
        },
        onChnlSwitch: function(){
            this.queryData();
        },
        formatTime: function(row,col){
            let time = row[col.property];
            let dt = new Date();
            dt.setTime(time);
            return dt.format("yyyy/MM/dd hh:mm:ss");
        },
        fmtPrice:function(row,col){
            let val = row[col.property];
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
        fmtAmount:function(row,col){
            let val = row[col.property];
            return val.toFixed(2);
        },
        queryData: function(needReset){
            needReset = needReset || false;
            var self = this;
            let curCat = this.selCat;
            let groupid = this.groupid || "";
            let chnlid = this.chnlfilter || "";

            if(groupid.length == 0){
                this.$notify.error("组合ID不能为空");
                return;
            }

            if(chnlid.length == 0){
                this.$notify.error("通道ID不能为空");
                return;
            }

            if(curCat == "trd"){
                self.loading.trade = true;
                setTimeout(()=>{
                    this.$api.getChnlTrades(groupid, chnlid, (resObj)=>{
                        if (resObj.result < 0) {
                            this.$notify.error("查询成交出错：" + resObj.message);
                        } else {
                            resObj.trades.forEach((item)=>{
                                item.action = (function(act){
                                    if(act == "OL") return "开多";
                                    if(act == "OS") return "开空";
                                    if(act == "CL") return "平多";
                                    if(act == "CS") return "平空";
                                    return act;
                                })(item.action);
                            });
                            self.trades = resObj.trades;
                            self.trades.reverse();
                        }

                        self.loading.trade = false;
                        self.refreshTime = new Date().format('yyyy.MM.dd hh:mm:ss');
                        if(needReset)
                            self.resetDataInterval();
                    });
                }, 300);                
            } else if(curCat == "ord"){
                self.loading.order = true;
                setTimeout(()=>{
                    this.$api.getChnlOrders(groupid, chnlid, (resObj)=>{
                        if (resObj.result < 0) {
                            this.$notify.error("查询订单出错：" + resObj.message);
                        } else {
                            resObj.orders.forEach((item)=>{
                                item.action = (function(act){
                                    if(act == "OL") return "开多";
                                    if(act == "OS") return "开空";
                                    if(act == "CL") return "平多";
                                    if(act == "CS") return "平空";
                                    return act;
                                })(item.action);
                            });

                            self.orders = resObj.orders;
                            self.orders.reverse();
                        }

                        self.loading.order = false;
                        self.refreshTime = new Date().format('yyyy.MM.dd hh:mm:ss');
                        if(needReset)
                            self.resetDataInterval();
                    });
                }, 300);   
            } else if(curCat == "pos"){
                self.loading.position = true;
                setTimeout(()=>{
                    this.$api.getChnlPositions(groupid, chnlid, (resObj)=>{
                        if (resObj.result < 0) {
                            this.$notify.error("查询持仓出错：" + resObj.message);
                        } else {
                            self.positions = resObj.positions;
                        }

                        self.loading.position = false;
                        self.refreshTime = new Date().format('yyyy.MM.dd hh:mm:ss');
                        if(needReset)
                            self.resetDataInterval();
                    });
                }, 300);   
            } else if(curCat == "fnd"){
                self.loading.fund = true;
                setTimeout(()=>{
                    this.$api.getChnlFunds(groupid, chnlid, (resObj)=>{
                        if (resObj.result < 0) {
                            this.$notify.error("查询资金出错：" + resObj.message);
                        } else {
                            let funds = [];
                            for(let cid in resObj.funds){
                                let chnlfunds = resObj.funds[cid];
                                for(let cur in chnlfunds){
                                    let item = chnlfunds[cur];
                                    item.channel = cid;
                                    item.currency = cur;
                                    item.moneyio = item.deposit - item.withdraw;
                                    item.dynprofit = item.dynprofit || 0;
                                    funds.push(item);
                                }
                            }
                            self.funds = funds;
                        }

                        self.loading.fund = false;
                        self.refreshTime = new Date().format('yyyy.MM.dd hh:mm:ss');
                        if(needReset)
                            self.resetDataInterval();
                    });
                }, 300);   
            } 
        }
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
