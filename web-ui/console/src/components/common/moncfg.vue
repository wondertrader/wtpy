<template>
    <div style="display:flex;flex-direction:column;margin:4px 20px;">
        <div style="padding-bottom: 12px;">
            <h4>调度设置</h4>
        </div>
        <el-divider content-position="left">任务信息</el-divider>
        <div class="config-label">
            <el-row>
                <el-col :span="4">
                    <a>任务ID：</a>
                </el-col>
                <el-col :span="7">
                    <el-input size="mini" :disabled="fixinfo" v-model="config.id"></el-input>
                </el-col>
                <el-col :span="4" :offset="2">
                    <a>启动参数：</a>
                </el-col>
                <el-col :span="7">
                    <el-input size="mini" v-model="config.param" placeholder="run.py"></el-input>
                </el-col>
            </el-row>
            <el-row>
                <el-col :span="4">
                    <a>执行程序：</a>
                </el-col>
                <el-col :span="20">
                    <el-input size="mini" v-model="config.path" placeholder="python执行程序所在目录，请上服务器查询">
                        <el-tooltip slot="append"  effect="dark" content="直接获取python路径" placement="top">
                            <el-button icon="el-icon-link" @click="onLinkPython"></el-button>
                        </el-tooltip>
                    </el-input>
                </el-col>
            </el-row>
            <el-row>
                <el-col :span="4">
                    <a>工作目录：</a>
                </el-col>
                <el-col :span="20">
                    <el-input size="mini" :disabled="fixinfo" v-model="config.folder">
                        <el-tooltip slot="append"  effect="dark" content="选择组合所在的目录" placement="top">
                            <el-button icon="el-icon-folder" :disabled="fixinfo" @click="handlePickFolder"></el-button>
                        </el-tooltip>
                    </el-input>
                </el-col>
            </el-row>
            <el-row>
                <el-col :span="4">
                    <a>消息地址：</a>
                </el-col>
                <el-col :span="20">
                    <el-input size="mini" v-model="config.mqurl" placeholder="请输入消息队列的URL" :disabled="forapp"></el-input>
                </el-col>
            </el-row>
        </div>
        <el-divider content-position="left">监控设置</el-divider>
        <div class="config-row">
            <div style="flex:0;margin-top:6px;padding-right:16px;">
                <el-checkbox v-model="config.guard">进程守护</el-checkbox>
            </div>
            <div style="flex:0:display:inline">
                <span class="config-label">检测间隔</span>
                <el-input-number size="mini" :min="1" :max="100" label="检测间隔" v-model="config.span"></el-input-number>
                <span class="config-label">s</span>
            </div>
            <div style="flex:1">
                
            </div>
            <div style="flex:0;margin-top:6px;">
                <el-checkbox v-model="config.schedule.active">计划任务</el-checkbox>
            </div>
        </div>
        <el-divider content-position="left">计划任务</el-divider>
        <div class="config-row">
            <div class="week-marker">
                <el-checkbox v-model="config.schedule.weekmask[0]" :disabled="!config.schedule.active">周日</el-checkbox>
            </div>
            <div class="week-marker">
                <el-checkbox v-model="config.schedule.weekmask[1]" :disabled="!config.schedule.active">周一</el-checkbox>
            </div>
            <div class="week-marker">
                <el-checkbox v-model="config.schedule.weekmask[2]" :disabled="!config.schedule.active">周二</el-checkbox>
            </div>
            <div class="week-marker">
                <el-checkbox v-model="config.schedule.weekmask[3]" :disabled="!config.schedule.active">周三</el-checkbox>
            </div>
            <div class="week-marker">
                <el-checkbox v-model="config.schedule.weekmask[4]" :disabled="!config.schedule.active">周四</el-checkbox>
            </div>
            <div class="week-marker">
                <el-checkbox v-model="config.schedule.weekmask[5]" :disabled="!config.schedule.active">周五</el-checkbox>
            </div>
            <div class="week-marker">
                <el-checkbox v-model="config.schedule.weekmask[6]" :disabled="!config.schedule.active">周六</el-checkbox>
            </div>
        </div>
        <el-row>
            <el-col :span="5">
                <el-checkbox v-model="config.schedule.tasks[0].active" :disabled="!config.schedule.active">任务一</el-checkbox>
            </el-col>
            <el-col :span="6">
                <el-input
                    placeholder="请输入时间"
                    suffix-icon="el-icon-time"
                    size="mini"
                    type="time"
                    :disabled="!config.schedule.tasks[0].active || !config.schedule.active"
                    v-model="config.schedule.tasks[0].time">
                </el-input>
            </el-col>
            <el-col :span="5" :offset="1">
                <el-select v-model="config.schedule.tasks[0].action" placeholder="请选择" size="mini" :disabled="!config.schedule.tasks[0].active || !config.schedule.active">
                    <el-option
                        v-for="(item,idx) in actions"
                        :key="idx"
                        :label="item"
                        :value="idx">
                    </el-option>
                </el-select>
            </el-col>
        </el-row>
        <el-row>
            <el-col :span="5">
                <el-checkbox v-model="config.schedule.tasks[1].active" :disabled="!config.schedule.active">任务二</el-checkbox>
            </el-col>
            <el-col :span="6">
                <el-input
                    placeholder="请输入时间"
                    suffix-icon="el-icon-time"
                    size="mini"
                    type="time"
                    :disabled="!config.schedule.tasks[1].active || !config.schedule.active"
                    v-model="config.schedule.tasks[1].time">
                </el-input>
            </el-col>
            <el-col :span="5" :offset="1">
                <el-select v-model="config.schedule.tasks[1].action" placeholder="请选择" size="mini" :disabled="!config.schedule.tasks[1].active || !config.schedule.active">
                    <el-option
                        v-for="(item,idx) in actions"
                        :key="idx"
                        :label="item"
                        :value="idx">
                    </el-option>
                </el-select>
            </el-col>
        </el-row>
        <el-row>
            <el-col :span="5">
                <el-checkbox v-model="config.schedule.tasks[2].active" :disabled="!config.schedule.active">任务三</el-checkbox>
            </el-col>
            <el-col :span="6">
                <el-input
                    placeholder="请输入时间"
                    suffix-icon="el-icon-time"
                    size="mini"
                    type="time"
                    :disabled="!config.schedule.tasks[2].active || !config.schedule.active"
                    v-model="config.schedule.tasks[2].time">
                </el-input>
            </el-col>
            <el-col :span="5" :offset="1">
                <el-select v-model="config.schedule.tasks[2].action" placeholder="请选择" size="mini" :disabled="!config.schedule.tasks[2].active || !config.schedule.active">
                    <el-option
                        v-for="(item,idx) in actions"
                        :key="idx"
                        :label="item"
                        :value="idx">
                    </el-option>
                </el-select>
            </el-col>
        </el-row>
        <el-row>
            <el-col :span="5">
                <el-checkbox v-model="config.schedule.tasks[3].active" :disabled="!config.schedule.active">任务四</el-checkbox>
            </el-col>
            <el-col :span="6">
                <el-input
                    placeholder="请输入时间"
                    suffix-icon="el-icon-time"
                    size="mini"
                    type="time"
                    :disabled="!config.schedule.tasks[3].active || !config.schedule.active"
                    v-model="config.schedule.tasks[3].time">
                </el-input>
            </el-col>
            <el-col :span="5" :offset="1">
                <el-select v-model="config.schedule.tasks[3].action" placeholder="请选择" size="mini" :disabled="!config.schedule.tasks[3].active || !config.schedule.active">
                    <el-option
                        v-for="(item,idx) in actions"
                        :key="idx"
                        :label="item"
                        :value="idx">
                    </el-option>
                </el-select>
            </el-col>
        </el-row>
        <el-row>
            <el-col :span="5">
                <el-checkbox v-model="config.schedule.tasks[4].active" :disabled="!config.schedule.active">任务五</el-checkbox>
            </el-col>
            <el-col :span="6">
                <el-input
                    placeholder="请输入时间"
                    suffix-icon="el-icon-time"
                    size="mini"
                    type="time"
                    :disabled="!config.schedule.tasks[4].active || !config.schedule.active"
                    v-model="config.schedule.tasks[4].time">
                </el-input>
            </el-col>
            <el-col :span="5" :offset="1">
                <el-select v-model="config.schedule.tasks[4].action" placeholder="请选择" size="mini" :disabled="!config.schedule.tasks[4].active || !config.schedule.active">
                    <el-option
                        v-for="(item,idx) in actions"
                        :key="idx"
                        :label="item"
                        :value="idx">
                    </el-option>
                </el-select>
            </el-col>
        </el-row>
        <el-row>
            <el-col :span="5">
                <el-checkbox v-model="config.schedule.tasks[5].active" :disabled="!config.schedule.active">任务六</el-checkbox>
            </el-col>
            <el-col :span="6">
                <el-input
                    placeholder="请输入时间"
                    suffix-icon="el-icon-time"
                    size="mini"
                    type="time"
                    :disabled="!config.schedule.tasks[5].active || !config.schedule.active"
                    v-model="config.schedule.tasks[5].time">
                </el-input>
            </el-col>
            <el-col :span="5" :offset="1">
                <el-select v-model="config.schedule.tasks[5].action" placeholder="请选择" size="mini" :disabled="!config.schedule.tasks[5].active || !config.schedule.active">
                    <el-option
                        v-for="(item,idx) in actions"
                        :key="idx"
                        :label="item"
                        :value="idx">
                    </el-option>
                </el-select>
            </el-col>
        </el-row>
        <div style="padding:8px 4px;">
            <div style="flex:1:display:inline;float:right">
                <el-button type="primary" size="mini" style="float:right;" plain @click="onConfigCommit()">提交设置</el-button>
            </div>
        </div>
        <el-dialog
            title="选择目录"
            :visible.sync="showfolders"
            width="25%">
            <div style="width:100%;height:300px;overflow:auto;border:1px solid #E4E7ED;">
                <el-tree :data="folders" @node-click="handleFolderClick"></el-tree>
            </div>
            <span slot="footer" class="dialog-footer">
                <el-button @click="showfolders = false">取 消</el-button>
                <el-button type="primary" @click="handleFolderPicked" plain>确 定</el-button>
            </span>
        </el-dialog>
    </div>   
</template>

<script>
import { mapGetters } from 'vuex';

export default {
    name: 'schedule',
    computed: {
        ...mapGetters([
            'folders'
        ])
    },
    props:{
        fixinfo:{
            type:Boolean,
            default(){
                return false;
            }
        },
        forapp:{
            type:Boolean,
            default(){
                return false;
            }
        },
        config:{
            type:Object,
            default(){
                return {
                    "id": "",
                    "folder": "",
                    "path": "",
                    "param": "",
                    "mqurl":"",
                    "span":3,
                    "guard":false,
                    "redirect":false,
                    "schedule":{
                        "active": true,
                        "weekflag":"0111110",
                        "weekmask":[false, true, true, true, true, true, false],
                        "tasks":[
                            {
                                "active":false,
                                "time":"00:00",
                                "action": 0
                            },
                            {
                                "active":false,
                                "time":"00:00",
                                "action": 0
                            },
                            {
                                "active":false,
                                "time":"00:00",
                                "action": 0
                            },
                            {
                                "active":false,
                                "time":"00:00",
                                "action": 0
                            },
                            {
                                "active":false,
                                "time":"00:00",
                                "action": 0
                            },
                            {
                                "active":false,
                                "time":"00:00",
                                "action": 0
                            }
                        ]
                    }
                }
            }
        }
    },
    data () {
        return {
            showfolders:false,
            selfolder:"",
            actions:["启动","停止","重启"]
        }
    },
    methods: {
        onLinkPython: function(){
            this.$api.getPythonPath((resObj)=>{
                if(resObj.result < 0){
                    this.$alert(resObj.message);
                } else {
                    this.config.path = resObj.path;
                }
            })
        },
        handlePickFolder: function(e){
            let self = this;
            self.selfolder = "";
            if(self.folders.length == 0){
                this.$api.getFolders((resObj)=>{
                    if(resObj.result < 0){
                        self.$alert(resObj.message);
                    } else {
                        this.$store.commit("setfolders", {
                            folders: [resObj.tree]
                        });
                        self.showfolders = true;
                    }
                })
            } else {
                self.showfolders = true;
            }
        },
        handleFolderPicked: function(){
            let self = this;
            if(self.selfolder == ''){
                self.$alert("请选择目录");
            } else {
                self.config.folder = self.selfolder;
                self.showfolders = false;
            }
        },
        handleFolderClick: function(data){
            this.selfolder = data.path;
        },
        onConfigCommit: function(){
            let self = this;
            let config = JSON.parse(JSON.stringify(this.config));
            if(config.path.length == 0){
                this.$alert("执行程序路径不能为空");
                return;
            }

            if(config.id.length == 0){
                this.$alert("应用ID不能为空");
                return;
            }

            if(config.folder.length == 0){
                this.$alert("执行目录不能为空");
                return;
            }

            //转换日期掩码
            config.schedule.weekflag = "";
            for(let idx = 0; idx < 7; idx++){
                config.schedule.weekflag += config.schedule.weekmask[idx]?"1":"0";
            }

            //转换时间
            for(let idx = 0; idx < 6; idx++){
                let timestr = config.schedule.tasks[idx].time;
                timestr = timestr.replace(":","");
                config.schedule.tasks[idx].time = parseInt(timestr);
            }

            config.redirect = !self.forapp;
            config.isapp = self.forapp;

            this.$confirm('确定要提交该调度配置?', '自动调度', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning'
            }).then(() => {
                delete config.schedule.weekmask;
                this.$api.commitMonCfg(config, (resObj)=>{
                    if(resObj.result < 0){
                        this.$message.error(resObj.message);
                    } else {
                        this.$message({
                            message: "监控配置已提交成功",
                            type:"success"
                        });

                        this.$emit('cfgudt');
                    }
                });
            });
        }
    }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.week-marker{
    flex: 0;
    padding-right: 12px;
}

.config-row{
    display:flex;
    flex-direction:row;
    padding:8px 4px;
}

.el-row{
    padding: 8px 4px;
}

.task-item{
    width: 100%;
    flex: 1;
    display: inline;
}

.config-label{
    color:#606266;
    font-weight: 500;
    font-size: 14px;
}
</style>
