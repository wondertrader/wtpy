<template>
    <div style="height:100%;width:100%;display:flex;flex-direction:column;">
        <div style="flex:1;overflow:auto;border: 1px solid #DCDFE6;border-radius:4px;">
            <json-viewer
                :value="setting"
                :expand-depth=5
                copyable
                v-show="!edit"
                class="setting">
            </json-viewer>
            <textarea
                v-show="edit"
                v-model="setting_s"
                class="setting el-textarea__inner">
            </textarea>
        </div>
        <div style="flex:0;min-height:32px; margin-top:8px;">
            <el-button size="mini" style="float:right;" v-show="!edit" @click="onClickEdit()">
                <i class="el-icon-edit"/>修改
            </el-button>
            <el-button size="mini" style="float:right;" v-show="edit" @click="edit=false;">
                <i class="el-icon-set-up"/>提交
            </el-button>
            <el-button size="mini" style="float:right;" v-show="edit" @click="edit=false;">
                <i class="el-icon-refresh-left"/>取消
            </el-button>
        </div>
    </div>  
</template>

<script>
export default {
    name: 'empty',
    components: {
    },
    data () {
        return {
            setting_s:"",
            setting:{
                "basefiles":{
                    "session":"D:/WFP/common/sessions.json",
                    "commodity":"D:/WFP/common/commodities.json",
                    "contract":"D:/WFP/common/contracts.json",
                    "holiday":"D:/WFP/common/holidays.json",
                    "hot":"D:/WFP/common/hots.json"
                },
                "env":{
                    "name":"cta",
                    "mode": "product",
                    "product":{
                        "session":"TRADING"
                    },
                    "filters":"filters.json",
                    "fees":"fees.json",
                    "riskmon":{
                        "active":true,
                        "module":"WtRiskMonFact.dll",
                        "name":"SimpleRiskMon",
                        "calc_span":5,
                        "risk_span": 30,
                        "risk_scale": 0.3,
                        "basic_ratio": 101,
                        "inner_day_fd":20.0,
                        "inner_day_active":true,
                        "multi_day_fd":60.0,
                        "multi_day_active":false,
                        "base_amount": 5000000
                    }
                },
                "data":{
                    "store":{
                        "module":"WtDataReader.dll",
                        "path":"E:\\WTP_Data\\"
                    }
                },
                "executers":[
                    {
                        "active":true,
                        "id":"exe3",
                        "scale": 1,
                        "policy":
                        {
                            "default":{
                                "name":"WtExeFact.WtSimpExeUnit",
                                "offset": 0,
                                "expire": 40,
                                "opposite": true
                            }
                        },
                        "trader":"simnow"
                    }
                ],
                "traders":[
                    {
                        "active":true,
                        "id":"simnow",
                        "module":"TraderCTP.dll",
                        "front":"tcp://180.168.146.187:10101",
                        "broker":"9999",
                        "user":"153498",
                        "pass":"hx2019",
                        "appid":"simnow_client_test",
                        "authcode":"0000000000000000",
                        "quick":true,
                        "riskmon":
                        {
                            "active":true,
                            "policy":
                            {
                                "default":
                                {
                                    "order_times_boundary": 20,
                                    "order_stat_timespan": 10,
                                    
                                    "cancel_times_boundary": 20,
                                    "cancel_stat_timespan": 10,
                                    "cancel_total_limits": 470
                                }
                            }
                        }
                    }
                ],
                "parsers":[
                    {
                        "active":true,
                        "id":"parser1",
                        "module":"ParserUDP.dll",
                        "host":"127.0.0.1",
                        "bport":9001,
                        "sport":3997,
                        "filter":""
                    }
                ],
                "bspolicy":"actpolicy.json"
            },
            edit: false
        }
    },
    methods: {
        onClickEdit: function(){
            this.setting_s = JSON.stringify(this.setting, null, 2);
            this.edit=true;
        }
    }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.setting{
    height: 100%;
    width: 100%;
}
</style>
