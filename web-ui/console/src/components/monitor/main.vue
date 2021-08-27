<template>
    <div style="height:100%;">
        <el-container style="height:100%;">
            <el-header style="height:44px !important;">
                <div style="float:left; height:100%;margin-top: 7px;">
                    <el-menu :default-active="selectedIdx" class="el-menu-demo" mode="horizontal" @select="handleTabSel">
                        <el-menu-item v-for="(item,idx) in groups" :key="idx" :index="item.id">
                            {{item.name}}
                            <i :class="item.datmod=='auto'?'el-icon-monitor':'el-icon-thumb'"/>
                        </el-menu-item>
                    </el-menu>
                </div>
                <div style="float:right; margin:6px 0px;">
                    <el-row>
                        <el-tooltip class="item" effect="dark" content="手动停止组合" placement="top-start" v-show="selectedIdx!='' && curGroup.running">
                            <el-button type="danger" icon="el-icon-magic-stick" size="mini" @click="handleStopGroup" plain>停止</el-button>
                        </el-tooltip>
                        <el-tooltip class="item" effect="dark" content="手动启动组合" placement="top-start" v-show="selectedIdx!='' && !curGroup.running">
                            <el-button type="success" icon="el-icon-magic-stick" size="mini" @click="handleStartGroup" plain>启动</el-button>
                        </el-tooltip>
                        <el-tooltip class="item" effect="dark" content="查看策略组合的基本信息" placement="top-start" v-show="selectedIdx!=''">
                            <el-button type="primary" icon="el-icon-magic-stick" size="mini" @click="handleViewGrop" plain>查看</el-button>
                        </el-tooltip>
                        <el-tooltip class="item" effect="dark" content="配置策略组合的自动调度" placement="top-start" v-show="selectedIdx!=''" v-if="isAdmin">
                            <el-button type="primary" icon="el-icon-time" size="mini" @click="handleClickSchedule" plain>调度</el-button>
                        </el-tooltip>
                        <el-divider direction="vertical"></el-divider>
                        <el-tooltip class="item" effect="dark" content="管理策略组合" placement="top-start">
                            <el-dropdown split-button type="danger" size="mini" trigger="click" @command="handleGrpCmd">
                                组合管理
                                <el-dropdown-menu slot="dropdown">
                                    <el-dropdown-item command="addgrp">
                                        <i class="el-icon-plus"/>
                                        <span>添加组合</span>
                                    </el-dropdown-item>
                                    <el-dropdown-item command="delgrp" v-show="curGroup!=null">
                                        <i class="el-icon-delete"/>
                                        <span>删除组合</span>
                                    </el-dropdown-item>
                                </el-dropdown-menu>
                            </el-dropdown>
                        </el-tooltip>
                    </el-row>
                </div> 
            </el-header>
            <el-main>
                <div style="height:100%;width:100%;">
                    <Empty v-show="groups.length==0" style="height:100%;width:100%;"/>
                    <Group ref="group" v-show="groups.length!=0" style="height:100%;width:100%;" :groupinfo="curGroup"/>
                </div>
            </el-main>
        </el-container>
        <el-drawer
            title="计划任务"
            :with-header="false"
            :visible.sync="schedule"
            direction="rtl"
            size="500px">
            <Schedule :config="curMonCfg" :fixinfo="true"/>
        </el-drawer>
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
        <el-dialog
            :title="addGroup?'添加组合':'修改组合'"
            :visible.sync="showgrpdlg"
            width="25%"
            class="dialog-group"
            :before-close="onCloseGrpDlg">  
            <el-row>
                <el-col :span="6">
                    <a>组合ID：</a>
                </el-col>
                <el-col :span="18">
                    <el-input v-model="copyGroup.id" size="mini" :disabled="!editGroup"></el-input>
                </el-col>
            </el-row>
            <el-row>
                <el-col :span="6">
                    <a>组合名称：</a>
                </el-col>
                <el-col :span="18">
                    <el-input v-model="copyGroup.name" size="mini" :disabled="!editGroup"></el-input>
                </el-col>
            </el-row>
            <el-row>
                <el-col :span="6">
                    <a>组合路径：</a>
                </el-col>
                <el-col :span="18">
                    <el-input v-model="copyGroup.path" size="mini" :disabled="!editGroup">
                        <el-tooltip slot="append"  effect="dark" content="选择组合所在的目录" placement="top">
                            <el-button icon="el-icon-folder" @click="handlePickFolder" :disabled="!editGroup"></el-button>
                        </el-tooltip>
                    </el-input>
                 </el-col>
            </el-row>
            <el-row>
                <el-col :span="6">
                    <a>组合类型：</a>
                </el-col>
                <el-col :span="18">
                    <el-radio v-model="copyGroup.gtype" label="cta" :disabled="!editGroup">CTA组合</el-radio>
                    <el-radio v-model="copyGroup.gtype" label="hft" :disabled="!editGroup">HFT组合</el-radio>
                    <el-radio v-model="copyGroup.gtype" label="sel" :disabled="!editGroup">SEL组合</el-radio>
                </el-col>
            </el-row>
            <el-row>
                <el-col :span="6">
                    <a>数据模式：</a>
                </el-col>
                <el-col :span="18">
                    <el-tooltip class="item" effect="dark" content="组合会自动向监控服务推送数据" placement="top">
                        <el-radio v-model="copyGroup.datmod" label="auto" :disabled="!editGroup">自动</el-radio>
                    </el-tooltip>
                    <el-tooltip class="item" effect="dark" content="监控服务只在有请求的时候去读取数据" placement="top">
                        <el-radio v-model="copyGroup.datmod" label="mannual" :disabled="!editGroup">手动</el-radio>
                    </el-tooltip>
                </el-col>
            </el-row>
            <el-row>
                <el-col :span="6">
                    <a>消息地址：</a>
                </el-col>
                <el-col :span="18">
                    <el-tooltip class="item" effect="dark" content="消息订阅地址要和配置文件中的notifier一致" placement="top">
                        <el-input v-model="copyGroup.mqurl" size="mini" :disabled="!editGroup || copyGroup.datmod!='auto'" placeholder="请输入消息队列的订阅地址"></el-input>
                    </el-tooltip>
                </el-col>
            </el-row>
            <el-row>
                <el-col :span="6">
                    <a>组合环境：</a>
                </el-col>
                <el-col :span="18">
                    <el-radio v-model="copyGroup.env" label="product" :disabled="!editGroup">生产环境</el-radio>
                    <el-radio v-model="copyGroup.env" label="backtest" :disabled="!editGroup">回测环境</el-radio>
                </el-col>
            </el-row>
            <el-row style="height:60px;">
                <el-col :span="6">
                    <a>组合介绍：</a>
                </el-col>
                <el-col :span="18">
                    <el-input type="textarea" v-model="copyGroup.info" style="min-height:80px;" :disabled="!editGroup"></el-input>
                </el-col>
            </el-row>
            <span slot="footer" class="dialog-footer">
                <el-button type="primary" plain size="mini" icon="el-icon-edit" v-show="!addGroup && !editGroup" @click="editGroup=true">编辑</el-button>
                <el-button type="primary" @click="onCommitGroup()" plain size="mini" icon="el-icon-thumb" >提交</el-button>
            </span>
        </el-dialog>
        <el-dialog
            title="选择目录"
            :visible.sync="showfolders"
            width="25%">
            <div style="width:100%;height:300px;overflow:auto;border:1px solid #E4E7ED;">
                <el-tree :data="folders" @node-click="handleFolderClick"></el-tree>
            </div>
            <span slot="footer" class="dialog-footer">
                <el-button @click="showfolders = false" size='mini'>取 消</el-button>
                <el-button type="primary" @click="handleFolderPicked" plain size='mini'>确 定</el-button>
            </span>
        </el-dialog>
    </div>    
</template>

<script>
import { mapGetters } from 'vuex';

import Group from './group'
import Empty from './empty'
import Schedule from '../common/moncfg'

export default {
    name: 'monitor',
    computed: {
        ...mapGetters([
            'folders',
            'cache'
        ]),
        grpname(){
            if(this.curGroup == null)
                return "组合基本信息";
            else
                return this.curGroup.name;
        },
        isAdmin(){
            let uInfo = this.cache.userinfo;
            if(uInfo)
                return (uInfo.role == 'admin' || uInfo.role == 'superman');
            else
                return false;        
        }
    },
    components: {
        Group, Empty, Schedule
    },
    data () {
        return {
            groups:[
            ],
            selectedIdx: "",
            schedule: false,
            baseinfo: false,
            showgrpdlg: false,
            curGroup: null,
            addGroup: false,
            editGroup: false,
            copyGroup:{
                id:"",
                name:"",
                path:"",
                info:"",
                gtype:"cta",
                datmod:"mannual",
                env:"product",
                mqurl:""
            },
            showfolders:false,
            selfolder:"",
            monitors:{},
            curMonCfg:{
                "id": "",
                "folder": "",
                "path": "",
                "param": "",
                "span":3,
                "guard":false,
                "redirect":false,
                "schedule":{
                    "active": false,
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
    },
    methods: {
        handlePickFolder: function(e){
            let self = this;
            self.selfolder = "";
            if(self.folders.length == 0){
                this.$api.getFolders((resObj)=>{
                    if(resObj.result < 0){
                        self.$notify.error('查询目录结构出错：' + resObj.message);
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
                self.copyGroup.path = self.selfolder;
                self.showfolders = false;
            }
        },
        handleFolderClick: function(data){
            this.selfolder = data.path;
        },
        handleTabSel: function(key, keypath){
            //console.log(key,keypath);
            let self = this;
            self.selectedIdx = key;

            self.groups.forEach((grpInfo)=>{
                if(grpInfo.id == key){
                    self.curGroup = grpInfo;
                    return true;
                }
            });
        },
        handleClickSchedule: function(){
            let self = this;
            let grpid = self.curGroup.id;
            if(!self.monitors[grpid]){
                self.$api.getMonCfg(grpid, (resObj)=>{
                    if(resObj.result < 0){
                        self.$notify.error(resObj.message);
                    } else if(resObj.config) {
                        let config = resObj.config;
                        config.schedule.weekmask = [];
                        for(let idx = 0; idx < config.schedule.weekflag.length; idx++){
                            config.schedule.weekmask.push(config.schedule.weekflag[idx]=='1');
                        }

                        for(let idx = 0; idx < 6; idx++){
                            let curTime = config.schedule.tasks[idx].time + '';
                            if(curTime.length == 1)
                                config.schedule.tasks[idx].time = "00:0" + curTime;
                            else if(curTime.length == 2)
                                config.schedule.tasks[idx].time = "00:" + curTime;
                            else if(curTime.length == 3)
                                config.schedule.tasks[idx].time = '0' + curTime[0] + ":" + curTime.substr(1);
                            else
                                config.schedule.tasks[idx].time = curTime.substr(0,2) + ":" + curTime.substr(2);
                        }
                        self.monitors[grpid] = config;
                        self.curMonCfg = config;
                        self.schedule = true;
                    } else {
                        //新建调度任务
                        this.$confirm('该组合尚未配置自动调度，马上去配置?', '自动调度', {
                            confirmButtonText: '确定',
                            cancelButtonText: '取消',
                            type: 'warning'
                        }).then(() => {
                            let config = {
                                "id": "",
                                "folder": "",
                                "path": "",
                                "param": "",
                                "span":3,
                                "guard":false,
                                "redirect":false,
                                "mqurl":"",
                                "schedule":{
                                    "active": false,
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
                            config.id = self.curGroup.id;
                            config.folder = self.curGroup.path;
                            config.redirect = true;
                            config.mqurl = self.curGroup.mqurl;
                            self.curMonCfg = config;
                            self.schedule = true;
                        });
                    }
                })
            } else {
                self.curMonCfg = self.monitors[grpid];
                self.schedule = true;
            }
        },
        handleGrpCmd: function(cmdid){
            let self = this;
            if(cmdid == "addgrp"){
                this.copyGroup = {
                    id:"",
                    name:"",
                    path:"",
                    info:"",
                    gtype:"cta",
                    datmod:"mannual",
                    env:"product",
                    mqurl:""
                };
                this.addGroup = true;
                this.showgrpdlg = true;
                this.editGroup = true;
            } else if(cmdid == "delgrp"){
                this.addGroup = false;
                this.showgrpdlg = false;

                let grpInfo = self.curGroup;

                this.$confirm('确定要删除该组合?', '组合管理', {
                    confirmButtonText: '确定',
                    cancelButtonText: '取消',
                    type: 'warning'
                }).then(() => {
                    this.$api.delGroup(grpInfo.id, (resObj)=>{
                        if(resObj.result < 0){
                            self.$notify.error('删除组合失败：' + resObj.message);
                        } else {
                            let nextIdx = 0;
                            for(let i = 0; i < self.groups.length; i++){
                                if(self.groups[i].id == grpInfo.id){
                                    self.groups.splice(i, 1);
                                    nextIdx = i;
                                    break;
                                }
                            }

                        }
                    });
                });
                
            }
        },
        onCommitGroup: function(){
            let self = this;
            let grpInfo = this.copyGroup;
            this.$api.commitGroup(grpInfo, this.addGroup?"add":"mod", (resObj)=>{
                if(resObj.result < 0){
                    self.$notify.error('提交组合信息失败：' + resObj.message);
                } else {
                    if(this.addGroup)
                        self.groups.push(grpInfo);
                    self.showgrpdlg = false;
                    if(self.curGroup == null){
                        self.selectedIdx = grpInfo.id;
                        self.curGroup = grpInfo;
                    }                    
                }
            });
        },
        onCloseGrpDlg: function(done){
            done();
        },
        handleViewGrop: function(){
            if(this.curGroup == null || this.curGroup.id == "")
                return;

            this.copyGroup = JSON.parse(JSON.stringify(this.curGroup));
            this.copyGroup.datmod = this.copyGroup.datmod || "mannual";

            this.addGroup = false;
            this.editGroup = false;
            this.showgrpdlg = true;            
        },
        handleStartGroup: function(){
            if(this.curGroup == null || this.curGroup.id == "")
                return;

            if(this.curGroup.running){
                this.$notify("组合正在运行");
                return;
            }

            let self = this;
            let grpid = self.curGroup.id;
            if(!self.monitors[grpid]){
                self.$api.getMonCfg(grpid, (resObj)=>{
                    if(resObj.result < 0){
                        self.$notify.error(resObj.message);
                    } else if(resObj.config) {
                        let config = resObj.config;
                        config.schedule.weekmask = [];
                        for(let idx = 0; idx < config.schedule.weekflag.length; idx++){
                            config.schedule.weekmask.push(config.schedule.weekflag[idx]=='1');
                        }

                        for(let idx = 0; idx < 6; idx++){
                            let curTime = config.schedule.tasks[idx].time + '';
                            if(curTime.length == 1)
                                config.schedule.tasks[idx].time = "00:0" + curTime;
                            else if(curTime.length == 2)
                                config.schedule.tasks[idx].time = "00:" + curTime;
                            else if(curTime.length == 3)
                                config.schedule.tasks[idx].time = '0' + curTime[0] + ":" + curTime.substr(1);
                            else
                                config.schedule.tasks[idx].time = curTime.substr(0,2) + ":" + curTime.substr(2);
                        }
                        self.monitors[grpid] = config;

                        this.$api.startGroup(this.curGroup.id, (resObj)=>{
                            if(resObj.result < 0){
                                this.$notify.error(resObj.message);
                            } 
                        });
                    } else {
                        self.$alert("该组合尚未配置调度，不能启动");
                    }
                });
            } else {
                this.$api.startGroup(this.curGroup.id, (resObj)=>{
                    if(resObj.result < 0){
                        this.$notify.error('启动组合失败：' + resObj.message);
                    } 
                });
            }
        },
        handleStopGroup: function(){
            if(this.curGroup == null || this.curGroup.id == "")
                return;

            if(!this.curGroup.running){
                this.$notify("组合已经处于停止状态"); 
                return;
            }

            this.$confirm('确定要停止该组合吗?', '手动停止', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning'
            }).then(() => {
                this.$api.stopGroup(this.curGroup.id, (resObj)=>{
                    if(resObj.result < 0){
                        this.$notify.error(resObj.message);
                    } 
                });
            });
        }
    },
    mounted() {
        let self = this;
        self.$nextTick(()=>{
            self.$api.getGroups((resObj) => {
                //console.log(resObj);
                if (resObj.result < 0) {
                    self.$notify.error("查询组合出错：" + resObj.message);
                } else {
                    self.groups = resObj.groups;
                    if(self.groups.length > 0){
                        self.selectedIdx = self.groups[0].id;
                        self.curGroup = self.groups[0];
                    }

                    self.sockets.subscribe('notify', (data) => {
                        if(data.type == 'gpevt'){
                            if(data.evttype == "start"){
                                setTimeout(()=>{
                                    self.$notify({message:"组合"+data.groupid+"已启动",type:"success"});
                                }, 300);
                                
                            } else if(data.evttype == "stop") {
                                setTimeout(()=>{
                                    self.$notify.error("组合"+data.groupid+"已停止");
                                }, 300);
                            }
                        }

                        if(data.type == 'chnlevt'){
                            let obj = null;
                            let evttype = data.evttype || "";

                            let thisGrp = null;
                            self.groups.forEach((grpInfo)=>{
                                if(grpInfo.id == data.groupid)
                                    thisGrp = grpInfo;
                            });

                            if(thisGrp != null){
                                if(evttype == 'notify'){
                                    obj = {
                                        time:new Date(),
                                        group: thisGrp.name,
                                        channel: data.channel,
                                        title:"事件通知",
                                        type:"error",
                                        message: "错误：{1}".format(data.channel,data.message)
                                    };
                                } else if(evttype == 'order'){
                                    if(data.data.canceled){
                                        obj = {
                                            time:new Date(),
                                            group: thisGrp.name,
                                            channel: data.channel,
                                            title:"订单回报",
                                            type:"danger",
                                            message: "订单已撤销，本地订单号：{1}".format(data.channel,data.data.localid)
                                        };
                                    }
                                    
                                } else if(evttype == 'trade'){
                                    let action = (data.data.isopen?"开":"平") + (data.data.islong?"多":"空");

                                    obj = {
                                        time:new Date(),
                                        group: thisGrp.name,
                                        channel: data.channel,
                                        title:"成交回报",
                                        type:"success",
                                        message: "操作：{1}，代码：{2}，数量：{3}，成交价：{4}，本地订单号：{5}".format(
                                            data.channel, action, data.data.code, data.data.volume, data.data.price, data.data.localid)
                                    };
                                }

                                if(obj != null){
                                    self.$emit("notify", obj);
                                }
                            }
                        }

                        if(self.curGroup == null || data.groupid != self.curGroup.id)
                            return;

                        if(data.type == 'gplog' || data.type == 'chnlevt'){
                            if(self.$refs.group)
                                self.$refs.group.$emit('notify', data);
                        } else if(data.type == 'gpevt') {
                            if(data.evttype == "start"){
                                self.curGroup.running = true;
                            } else if(data.evttype == "stop") {
                                self.curGroup.running = false;
                            }
                        }
                    }); 
                }
            });
        })
    }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.el-menu--horizontal>.el-menu-item {
    float: left;
    height: 36px;
    line-height: 36px;
    margin: 0;
    border-bottom: 2px solid transparent;
    color: #909399;
}

.el-menu--horizontal>.el-menu-item.is-active {
    border-bottom: 2px solid #000000;
    color: #303133;
}

.el-menu.el-menu--horizontal {
    border-bottom: solid 0px #e6e6e6;
}

.el-header {
    border-bottom: solid 1px #e6e6e6;
}

.dialog-group .el-row{
    margin: 4px 8px;
    padding: 4px 0px;
    align-items: center;
    align-content: center;
    vertical-align: middle;
    height: 36px;
}
</style>
