<template>
    <div style="height:100vh;width:100%;">
        <el-row style="height:100%">
            <el-col :span="8" style="height:100%;">
                <div style="height:100%;display:flex;flex-direction:column;">
                    <div style="flex:0;margin:2px 4px 0px 4px;min-height:39px;display:flex;flex-direction:row;">
                        <div style="flex:0;" class="simtab">
                            <span>滚动日志</span>
                        </div> 
                        <div style="flex:1;border-bottom: 1px solid #E4E7ED;margin-top:6px;">
                            <el-switch
                                v-model="logScroll"
                                active-text="自动滚动"
                                inactive-text="暂停滚动" 
                                active-color="#13ce66"
                                inactive-color="#ff4949"
                                display="block"
                                style="float:right;"
                                v-show="isLogAuto">
                            </el-switch>
                            <el-button type="primary" icon="el-icon-refresh" size="mini" plain style="float:right;" v-show="!isLogAuto" @click="handleClickQryLog()">刷新</el-button>
                        </div> 
                    </div>
                    <div style="flex:1;margin:10px 4px;" v-loading="logOnway">
                        <textarea readonly="readonly" ref="logs" autocomplete="off" placeholder="这里是日志内容" class="el-textarea__inner" :value="logs"></textarea>
                    </div>
                </div>
            </el-col>
            <el-col :span="16" style="height:100%;border-left: 1px solid #E4E7ED;">
                <div style="height:100%;display:flex;flex-direction:column;">
                    <div style="flex:0;margin:2px 4px 0px 4px;min-height:44px;">
                        <el-tabs :value="selData" type="card" style="height:100%;" @tab-click="handleClickTab">
                            <el-tab-pane label="策略数据" name="sdata">
                            </el-tab-pane>
                            <el-tab-pane label="交易数据" name="tdata">
                            </el-tab-pane>
                            <el-tab-pane label="组合配置" name="setting">
                            </el-tab-pane>
                        </el-tabs>
                    </div>
                    <div style="flex:1;margin:2px;overflow:auto;">
                        <StrategyData v-show="selData=='sdata'" :groupid="groupid"/>
                        <ChannelData v-show="selData=='tdata'" :groupid="groupid"/>
                        <Setting v-show="selData=='setting'" :groupid="groupid"/>
                    </div>
                </div>
            </el-col>
        </el-row>
    </div>    
</template>

<script>
import StrategyData from './stradata'
import ChannelData from './trddata'
import Setting from './setting'
export default {
    name: 'empty',
    components: {
        StrategyData, ChannelData, Setting
    },
    computed: {
        groupid(){
            if(this.groupinfo == null)
                return "";
            else
                return this.groupinfo.id;
        },
        isLogAuto(){
            if(this.groupinfo == null)
                return false;
            else
                return this.groupinfo.datmod=="auto";
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
    data () {
        return {
            selData: "sdata",
            logs:"",
            logfilter:"total",
            logCache:"",
            logLines:0,
            logScroll: true,
            logOnway: false
        }
    },
    methods: {
        handleClickTab: function(tab, event){
            this.selData = tab.name;
        },
        handleClickQryLog: function(){
            setTimeout(()=>{
                this.queryLogs();
            }, 300);
        },
        queryLogs: function(){
            let self = this;
            if(this.groupinfo.id == "")
                return;

            self.logOnway = true;
            this.$api.getLogs(this.groupinfo.id, this.logfilter, (resObj)=>{
                if(resObj.result < 0){
                    this.$alert(resObj.message);
                } else {
                    this.logs = resObj.content;
                    this.logLines = resObj.lines||0;
                    self.$nextTick(()=>{
                        let height = self.$refs.logs.scrollHeight;
                        self.$refs.logs.scrollTo(0,height);
                    });
                }
                self.logOnway = false;
            });
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
            setTimeout(()=>{
                this.queryLogs();
            }, 300);
        }
    },
    mounted() {
        let self = this;
        self.$on('notify', (data) => {
            if(data.type == "gplog" && data.groupid == self.groupinfo.id){
                if(!self.logScroll)
                    return;

                let message = data.message || "";
                if(message.length > 0){
                    let isEmpty = self.logCache.length == 0;
                    self.logCache += message;
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
