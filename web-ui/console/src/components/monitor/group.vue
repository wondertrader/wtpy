<template>
    <div style="height:100vh;width:100%;">
        <el-row style="height:100%">
            <el-col :span="8" style="height:100%;">
                <div style="height:100%;display:flex;flex-direction:column;">
                    <div style="flex:0;margin:2px 4px 0px 4px;min-height:39px;display:flex;flex-direction:row;">
                        <div style="flex:0;" class="simtab">
                            <span>滚动日志</span>
                        </div> 
                        <div style="flex:1;border-bottom: 1px solid #E4E7ED;margin-top:6px;"></div>
                        <div style="flex:0 160px;border-bottom: 1px solid #E4E7ED;margin-top:6px;display:inline-block;">
                            <el-row v-show="!logScroll">
                                <el-col :span="11">
                                    <el-tooltip class="item" effect="dark" content="每个15秒刷新一次" placement="top">
                                        <el-checkbox v-model="autoLog" style="float:right;margin-top:6px;" @change="handleCheckAutoLog">自动刷新</el-checkbox>
                                    </el-tooltip>
                                </el-col>
                                <el-col :offset="1" :span="12">
                                    <el-button type="primary" style="" icon="el-icon-refresh" size="mini" plain @click="handleClickQryLog()">刷新</el-button>
                                </el-col>
                            </el-row>                   
                        </div> 
                    </div>
                    <div style="flex:1;margin:10px 4px;" v-loading="logOnway">
                        <textarea readonly="readonly" ref="logs" autocomplete="off" placeholder="这里是日志内容" class="el-textarea__inner" :value="logs"></textarea>
                    </div>
                    <div style="flex:0 24px;align-items:right;" v-show="!logScroll">
                        <span style="font-size:12px;color:gray;">日志刷新时间: {{logTime}}</span>
                    </div>
                </div>
            </el-col>
            <el-col :span="16" style="height:100%;border-left: 1px solid #E4E7ED;">
                <div style="height:100%;display:flex;flex-direction:column;">
                    <div style="flex:0;margin:2px 4px 0px 4px;min-height:44px;">
                        <el-tabs :value="selData" type="card" style="height:100%;" @tab-click="handleClickTab">
                            <el-tab-pane label="策略管理" name="sdata">
                            </el-tab-pane>
                            <el-tab-pane label="组合管理" name="pdata">
                            </el-tab-pane>
                            <el-tab-pane label="通道管理" name="tdata">
                            </el-tab-pane>                            
                            <el-tab-pane label="配置管理" name="editor">
                            </el-tab-pane>
                        </el-tabs>
                    </div>
                    <div style="flex:1;margin:2px;overflow:auto;">
                        <StrategyData v-show="selData=='sdata'" :groupid="groupid"/>
                        <ChannelData v-show="selData=='tdata'" :groupid="groupid"/>
                        <PorfolioData v-show="selData=='pdata'" :groupid="groupid" ref="portfolio"/>
                        <Editor v-show="selData=='editor'" :groupid="groupid"/>
                    </div>
                </div>
            </el-col>
        </el-row>
    </div>    
</template>

<script>
import { mapGetters } from 'vuex';
import StrategyData from './stradata'
import ChannelData from './trddata'
import PorfolioData from './portdata'
import Editor from './editor'
export default {
    name: 'empty',
    components: {
        StrategyData, ChannelData, PorfolioData, Editor
    },
    computed: {
        ...mapGetters([
            'cache'
        ]),
        isAdmin(){
            let uInfo = this.cache.userinfo;
            if(uInfo)
                return (uInfo.role == 'admin' || uInfo.role == 'superman');
            else
                return false;        
        },
        groupid(){
            if(this.groupinfo == null)
                return "";
            else
                return this.groupinfo.id;
        }
    },
    props:{
        groupinfo:{
            type: Object,
            default() {
                return {
                    id:"",
                    name:"",
                    path:"",
                    info:"",
                    gtype:"cta",
                    datmod:"auto"
                }
            }
        }
    },
    watch:{
        groupinfo(newGrp, oldVal){
            let self = this;

            if(newGrp == null)
                return;

            if(oldVal != null && newGrp.id == oldVal.id)
                return;

            //只有手动模式的组合才需要请求日志数据
            self.logScroll = (newGrp.datmod == 'auto');
            setTimeout(()=>{
                this.queryLogs(true);
            }, 300);
        }
    },
    data () {
        return {
            selData: "sdata",
            logs:"",
            logfilter:"total",
            logCache:"",
            logLines:0,
            logScroll: true,
            logOnway: false,
            autoLog: false,
            logInterval: 0,
            logTime:new Date().format('yyyy.MM.dd hh:mm:ss')
        }
    },
    methods: {
        handleClickTab: function(tab, event){
            this.selData = tab.name;
            if(tab.name == 'pdata'){
                setTimeout(()=>{
                    this.$refs.portfolio.$emit("resize");
                },150);
            }
        },
        handleClickQryLog: function(){
            setTimeout(()=>{
                this.queryLogs(true);
            }, 300);
        },
        handleCheckAutoLog: function(val){
            this.resetLogInterval();
        },
        resetLogInterval: function(){
            if(this.autoLog){
                if(this.logInterval != 0){
                    clearInterval(this.logInterval);
                }

                this.logInterval = setInterval(()=>{
                    this.queryLogs();
                }, 15000);
            } else if(this.logInterval != 0){
                clearInterval(this.logInterval);
            }
        },
        queryLogs: function(needReset){
            needReset = needReset || false;
            let self = this;
            if(this.groupinfo.id == "")
                return;

            self.logOnway = true;
            this.$api.getLogs(this.groupinfo.id, this.logfilter, (resObj)=>{
                if(resObj.result < 0){
                    this.logs = '';
                    this.logLines = 0;
                    this.$notify.error('组合日志拉取失败：' + resObj.message);
                    self.$nextTick(()=>{
                        self.$refs.logs.scrollTo(0,0);
                    });
                } else {
                    this.logs = resObj.content;
                    this.logLines = resObj.lines||0;
                    self.$nextTick(()=>{
                        let height = self.$refs.logs.scrollHeight;
                        self.$refs.logs.scrollTo(0,height);
                    });
                }
                self.logTime = new Date().format('yyyy.MM.dd hh:mm:ss');
                self.logOnway = false;

                if(needReset)
                    self.resetLogInterval();
            });
        },
        processLog: function(data){
            let self = this;
            let message = data.message || "";
            if(message.length > 0){
                let isEmpty = self.logCache.length == 0;
                let date = new Date(data.time);
                let line = "[" + date.format("yyyy.MM.dd hh:mm:ss") + " - " + data.tag + "] " + message + "\n";
                self.logCache += line;
                self.logLines ++;
                if(isEmpty){
                    self.$nextTick(()=>{
                        if(self.logLines >= 200){
                            self.logs = "";
                            self.logLines = 0;
                        }

                        self.logs += self.logCache;
                        self.logCache = "";
                        self.$nextTick(()=>{
                            let height = self.$refs.logs.scrollHeight;
                            self.$refs.logs.scrollTo(0,height);
                        });
                    });
                }
            }
        },
        processEvent: function(data){
            let self = this;
            let evttype = data.evttype || "";
            if(evttype == '')
                return;

            if(evttype == 'notify'){
                self.$notify({
                    title:"订单回报",
                    type:"error",
                    message: "交易通道{0}错误：{1}".format(data.channel,data.message),
                    duration: 0
                });
            } else if(evttype == 'order'){
                if(!data.data.canceled)
                    return;

                self.$notify({
                    title:"订单回报",
                    type:"error",
                    message: "交易通道{0}订单已撤销，本地订单号：{1}".format(data.channel,data.data.localid),
                    duration: 0
                });
            } else if(evttype == 'trade'){
                let action = (data.data.isopen?"开":"平") + (data.data.islong?"多":"空");
                self.$notify({
                    title:"成交回报",
                    type:"success",
                    message: "交易通道：{0}，操作：{1}，代码：{2}，数量：{3}，成交价：{4}，本地订单号：{5}".format(
                        data.channel, action, data.data.code, data.data.volume, data.data.price, data.data.localid)
                });
            }
        }
    },
    mounted() {
        let self = this;
        self.$on('notify', (data) => {
            if(data.groupid != self.groupinfo.id)
                return;

            if(data.type == "gplog"){
                if(!self.logScroll)
                    return;

                self.processLog(data);
            } else if(data.type == "chnlevt"){
                self.processEvent(data);
            }
        });
    }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.simtab{
    padding: 0px 20px;
    height:100%;
    line-height:39px; 
    border: 1px solid #E4E7ED;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    min-width:56px;
    font-size:14px;
}

.el-textarea__inner{
    height: 100% !important;
}

.el-select{
    width: 120px;
}
</style>
