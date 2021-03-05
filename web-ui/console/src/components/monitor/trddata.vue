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
                        </el-tabs>
                    </div>
                    <div style="flex:1;border-bottom:2px solid #E4E7ED;margin-top: 4px;">
                        <div style="float:right">
                            <el-button type="primary" icon="el-icon-refresh" size="mini" plain @click="queryData()">刷新</el-button>
                            <el-select v-model="chnlfilter" placeholder="请选择" size="mini" @change="onChnlSwitch">
                                <el-option :label="cid" :value="cid" :key="cid" v-for="cid in channels">
                                    <i class="el-icon-tickets"/>
                                    <span>{{cid}}</span>
                                </el-option>
                            </el-select>
                        </div>
                    </div> 
                </div>
            </el-header>
            <el-main>
                <div style="max-height:100%;overflow:auto;" v-show="selCat=='pos'" v-loading="loading.position">
                    <el-table
                        border
                        stripe
                        :data="positions"
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
                        class="table">
                        <el-table-column
                            prop="channel"
                            label="通道"
                            width="100">
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
                        class="table">
                        <el-table-column
                            prop="channel"
                            label="通道"
                            width="100">
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
            </el-main>
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
                        this.$alert(resObj.message);
                    } else {
                        this.channels = resObj.channels;
                        this.chnlfilter = this.channels[0];

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
            chnlfilter:"",
            channels:[],
            loading:{
                trade: false,
                order: false,
                position: false,
                fund: false
            },
            trades:[],
            orders:[],
            positions:[]
        }
    },
    methods: {
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
        queryData: function(){
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
                            self.$alert("查询成交出错：" + resObj.message, "查询失败");
                        } else {
                            self.trades = resObj.trades;
                            self.trades.reverse();
                        }

                        self.loading.trade = false;
                    });
                }, 300);                
            } else if(curCat == "ord"){
                self.loading.order = true;
                setTimeout(()=>{
                    this.$api.getChnlOrders(groupid, chnlid, (resObj)=>{
                        if (resObj.result < 0) {
                            self.$alert("查询委托出错：" + resObj.message, "查询失败");
                        } else {
                            self.orders = resObj.orders;
                            self.orders.reverse();
                        }

                        self.loading.order = false;
                    });
                }, 300);   
            } else if(curCat == "pos"){
                self.loading.position = true;
                setTimeout(()=>{
                    this.$api.getChnlPositions(groupid, chnlid, (resObj)=>{
                        if (resObj.result < 0) {
                            self.$alert("查询持仓出错：" + resObj.message, "查询失败");
                        } else {
                            self.positions = resObj.positions;
                        }

                        self.loading.position = false;
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
