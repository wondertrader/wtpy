<template>
    <div style="height:100%;display:flex;flex-direction:column;">
        <div style="flex:1 40%;overflow:auto;border-bottom:1px solid #E4E7ED;">
            <div id="kline" style="width:100%;height:100%;">
            </div>
        </div>
        <div style="flex:1 60%;overflow:auto;display:flex;flex-direction:column;margin:4px;">
            <div style="flex:0 44px;">
                <el-tabs :value="selCat" tab-position="top" style="height:100%;margin:0;" @tab-click="handleCatChange">
                    <el-tab-pane label="信号明细" name="sig">
                    </el-tab-pane>
                    <el-tab-pane label="回合明细" name="rnd">
                    </el-tab-pane>
                    <el-tab-pane label="每日绩效" name="fnd" v-if="isAdmin">
                    </el-tab-pane>
                </el-tabs>
            </div>
            <div style="flex: 1; margin:4px;">
                <div style="max-height:100%;overflow:auto;"  v-show="selCat=='sig'" v-loading="loading.signal">
                    <el-table
                        border
                        stripe
                        :data="signals"
                        :summary-method="getSigSum"
                        show-summary
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
                        :summary-method="getRndSum"
                        show-summary
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
                <div style="height:100%;display:flex;flex-direction:column;"  v-show="selCat=='fnd'" v-loading="loading.fund"  v-if="isAdmin">
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
                            label="动态权益">
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
            selCat:"rnd",
            signals:[],
            rounds:[],
            funds:[],
            nvChart:null,
        };
    },
    methods: {
        handleCatChange: function(tab, event){
            if(this.selCat == tab.name)
                return;

            this.selCat = tab.name;
        },
       
    },
    mounted() {
        
    },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
