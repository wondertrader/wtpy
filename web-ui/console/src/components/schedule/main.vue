<template>
	<div style="height:100%;width:100%;">
        <el-row style="height:100%">
            <el-col :span="16" style="height:100%;">
                <div style="height:100%;display:flex;flex-direction:column;">
                    <div style="flex:0;margin:2px 4px 0px 4px;min-height:39px;display:flex;flex-direction:row;">
                        <div style="flex:0;" class="simtab">
                            <span>应用列表</span>
                        </div> 
                        <div style="flex:1;border-bottom: 1px solid #E4E7ED;margin-top:6px;">
                            <el-dropdown split-button type="danger" size="mini" style="float:right;" trigger="click" @command="handleAppCommand">
                                <i class="el-icon-edit-outline"></i>管理
                                <el-dropdown-menu slot="dropdown">
                                    <el-dropdown-item command="add"><i class="el-icon-circle-plus-outline"></i>添加应用</el-dropdown-item>
                                    <el-dropdown-item command="del"><i class="el-icon-delete"></i>删除应用</el-dropdown-item>
                                    <el-dropdown-item divided  command="refresh"><i class="el-icon-refresh"></i>刷新列表</el-dropdown-item>
                                    <el-dropdown-item divided  command="start"><i class="el-icon-refresh"></i>启动应用</el-dropdown-item>
                                    <el-dropdown-item command="stop"><i class="el-icon-delete"></i>停止应用</el-dropdown-item>
                                </el-dropdown-menu>
                            </el-dropdown>
                        </div> 
                    </div>
                    <div style="flex:1;margin:10px 4px;height:100%;">
                        <div style="max-height:100%;overflow:auto;">
                            <el-table
                                border
                                stripe
                                v-loading="loading"
                                :data="monitors"
                                highlight-current-row
                                @current-change="handleSelectApp"
                                class="table">
                                <el-table-column
                                    label="名称"
                                    width="120">
                                    <template slot-scope="scope">
                                        <i :class="scope.row.group?'el-icon-data-analysis':'el-icon-monitor'"></i>
                                        <a style="padding-left:8px;">{{scope.row.id}}</a>
                                    </template>
                                </el-table-column>
                                <el-table-column
                                    prop="state"
                                    label="状态"
                                    width="80">
                                </el-table-column>
                                <el-table-column
                                    prop="guard"
                                    label="守护"
                                    width="80">
                                </el-table-column>
                                <el-table-column
                                    prop="task"
                                    label="任务"
                                    width="80">
                                </el-table-column>
                                <el-table-column
                                    prop="param"
                                    label="参数"
                                    width="80">
                                </el-table-column>
                                <el-table-column
                                    prop="span"
                                    label="间隔(s)"
                                    width="80">
                                </el-table-column>
                                <el-table-column
                                    prop="path"
                                    label="路径">
                                </el-table-column>
                                <el-table-column
                                    prop="folder"
                                    label="目录">
                                </el-table-column>
                            </el-table>
                        </div>
                    </div>
                </div>
            </el-col>
            <el-col :span="8" style="height:100%;border-left: 1px solid #E4E7ED;">
                <MoniforCfg :config="curMonCfg" :fixinfo="!addApp" :forapp="true" @cfgudt="onCfgUpdated"/>
            </el-col>
        </el-row>
    </div>
    
</template>

<script>
import MoniforCfg from '../common/moncfg'
export default {
    name: 'Schedule',
    components: {
        MoniforCfg
    },
    data() {
        return {
            showfolders:false,
            selfolder:"",
            loading: false,
            committing: false,
            addApp: false,
            monitors:[],
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
    methods:{
        onCfgUpdated: function(){
            this.queryData();
        },
        handleSelectApp: function(appInfo){
            console.log(appInfo);
            let config = JSON.parse(JSON.stringify(appInfo));
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

            this.curMonCfg = config;
        },
        resetConf: function(){
            this.curMonCfg = {
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
            };
        },
        queryData: function(){
            let self = this;

            self.resetConf();
            
            self.loading = true;
            setTimeout(()=>{
                self.$api.getMonApps((resObj)=>{
                    if(resObj.result < 0){
                        self.$message.error(resObj.message);
                    } else {
                        let monitors = [];
                        let keys = Object.keys(resObj.schedules);
                        for(let idx = 0; idx < keys.length; idx++){
                            let key = keys[idx];
                            let appInfo = resObj.schedules[key];
                            appInfo.state = appInfo.running?"运行中":"未启动";
                            appInfo.guard = appInfo.gurad?"是":"否";
                            appInfo.task = appInfo.schedule.active?"是":"否";
                            monitors.push(appInfo);
                        }
                        self.monitors = monitors;
                    }
                    self.loading = false;
                })
            }, 300);
        },
        handleAppCommand: function(command){
            if(command == 'add'){
                this.resetConf();
                this.addApp = true;
            } else if(command == "del"){

            } else if(command == 'refresh'){
                this.queryData();
            } else if(command == 'start'){
                this.$api.startApp(this.curMonCfg.id, (resObj)=>{
                    if(resObj.result < 0){
                        this.$message.error(resObj.message);
                    } 
                });
            } else if(command == 'stop'){
                
            }
        }
    },
    mounted (){
        this.$nextTick(()=>{
            this.queryData();
        });
    }
}

</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.table{
    width:100%;
    height:100%;
}

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

</style>
