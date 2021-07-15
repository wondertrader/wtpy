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
                            <el-row >
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
                    <div style="flex:0 24px;align-items:right;">
                        <span style="font-size:12px;color:gray;">日志刷新时间: {{logTime}}</span>
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
                            <el-tab-pane label="组合数据" name="pdata">
                            </el-tab-pane>
                            <el-tab-pane label="文件管理" name="editor" v-if="isAdmin">
                            </el-tab-pane>
                            <el-tab-pane label="组合配置" name="setting" v-if="isAdmin">
                            </el-tab-pane>
                            <el-tab-pane label="执行入口" name="entry" v-if="isAdmin">
                            </el-tab-pane>
                        </el-tabs>
                    </div>
                    <div style="flex:1;margin:2px;overflow:auto;">
                        <StrategyData v-show="selData=='sdata'" :groupid="groupid"/>
                        <ChannelData v-show="selData=='tdata'" :groupid="groupid"/>
                        <PorfolioData v-show="selData=='pdata'" :groupid="groupid"/>
                        <Editor v-show="selData=='editor'" :groupid="groupid" v-if="isAdmin"/>
                        <Setting v-show="selData=='setting'" :groupid="groupid" v-if="isAdmin"/>
                        <Entry v-show="selData=='entry'" :groupid="groupid" v-if="isAdmin"/>
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
import Setting from './setting'
import Entry from './entry'
import Editor from './editor'
export default {
    name: 'empty',
    components: {
        StrategyData, ChannelData, PorfolioData, Setting, Entry, Editor
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
                this.queryLogs(true);
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
