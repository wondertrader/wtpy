<template>
    <div style="height:100%;width:100%;">
        <div style="height:100%;display:flex;flex-direction:row;">
            <div style="height:100%;flex:0 320px;">
                <div style="display:flex;flex-direction:column;">
                    <div style="flex:0 40px;display:flex;flex-direction:row;">
                        <div style="flex:0;" class="simtab">
                            <span>我的策略</span>
                        </div> 
                        <div style="flex:1;border-bottom: 1px solid #E4E7ED;margin-top:10px;margin-right:6px;">
                            <el-tooltip placement="top" style="float:right;">
                                <div slot="content">刷新列表</div>
                                <i class="el-icon-refresh button" @click="onRefreshStrategy" style="float:right;"/>
                            </el-tooltip>
                            <el-tooltip placement="top" style="float:right;">
                                <div slot="content">新建策略</div>
                                <i class="el-icon-plus button" @click="onAddStrategy" style="float:right;"/>
                            </el-tooltip>
                        </div>
                    </div>
                    <div style="flex:1 1;">
                        <div style="overflow:auto;" class="stra-list" v-loading="strasOnWay">
                            <div class="stra-item" v-for="(item,idx) in strategies" :key="idx">
                                <el-row class="stra-line">
                                    <i class="el-icon-cpu"/>
                                    <span class="stra-title">{{item.name}}</span>
                                    <el-tooltip placement="top" style="float:right;">
                                        <div slot="content">删除策略</div>
                                        <i class="el-icon-delete button" @click="onDelStrategy(item.id)" style="float:right;"/>
                                    </el-tooltip>
                                    <el-tooltip placement="top" style="float:right;">
                                        <div slot="content">查看策略</div>
                                        <i class="el-icon-view button" @click="onOpenStrategy(item)" style="float:right;"/>
                                    </el-tooltip>
                                </el-row>
                                <el-row  class="stra-line">
                                    <el-col :span="12">
                                        <span class="stra-label">年化：</span>
                                        <span class="stra-return">{{item.perform.return.toFixed(2)}}%</span>
                                    </el-col>
                                    <el-col :span="12">
                                        <span class="stra-label">最大回撤：</span>
                                        <span class="stra-mdd">{{item.perform.mdd.toFixed(2)}}%</span>
                                    </el-col>
                                </el-row>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div style="height:100%;border-left: 1px solid #E4E7ED;flex: 1 0;">
                <div style="height:100%;display:flex;flex-direction:column;">
                    <div style="flex:0 0 44px;margin:2px 4px 0px 4px;">
                        <el-tabs :value="selData" type="card" style="height:100%;" @tab-click="handleClickTab">
                            <el-tab-pane label="策略查看" name="editor">
                            </el-tab-pane>
                            <el-tab-pane label="回测详情" name="backtest">
                            </el-tab-pane>
                        </el-tabs>
                    </div>
                    <div style="flex:1 0;overflow:auto;margin:4px;">
                        <div style="height:100%;display:flex;flex-direction:column;" v-show="selData=='editor'">
                            <div style="flex:2;display:flex;flex-direction:column;">
                                <div style="flex:0;">
                                    <span style="color:gray;">快捷操作：</span>
                                    <el-tooltip placement="top">
                                        <div slot="content">提交代码</div>
                                        <i class="el-icon-upload2 toolbar" @click="onClickCommit()"/>
                                    </el-tooltip>
                                    <el-tooltip placement="top">
                                        <div slot="content">放弃修改</div>
                                        <i class="el-icon-refresh-left toolbar" @click="onClickCancel()"/>
                                    </el-tooltip>
                                    <el-tooltip placement="top">
                                        <div slot="content">启动回测</div>
                                        <i class="el-icon-video-play toolbar"/>
                                    </el-tooltip>
                                    <span style="color:gray;float:right;">当前策略:{{curStra?curStra.name:""}}</span>
                                </div>
                                <div style="flex:1 1;overflow:auto;border:1px solid #DCDFE6;border-radius:2px;">
                                    <div style="height:100%">
                                        <codemirror
                                            ref="mycode"
                                            v-model="content"
                                            :options="cmOptions"
                                            style="height:100% !important;">
                                        </codemirror>
                                    </div>
                                </div>
                            </div>
                            <div class="divider"></div>
                            <div style="flex:1;">
                                <el-table
                                    border
                                    stripe
                                    :data="backtests"
                                    class="table">
                                    <el-table-column
                                        prop="time"
                                        label="回测时间"
                                        width="150">
                                    </el-table-column>
                                    <el-table-column
                                        prop="stime"
                                        label="开始时间"
                                        width="130">
                                    </el-table-column>
                                    <el-table-column
                                        prop="etime"
                                        label="结束时间"
                                        width="130">
                                    </el-table-column>
                                    <el-table-column
                                        prop="return"
                                        label="累计收益率%"
                                        width="110">
                                    </el-table-column>
                                    <el-table-column
                                        prop="ar"
                                        label="年化收益率%"
                                        width="110">
                                    </el-table-column>
                                    <el-table-column
                                        prop="mdd"
                                        label="最大回撤%"
                                        width="90">
                                    </el-table-column>
                                    <el-table-column
                                        prop="sharpe"
                                        label="夏普率"
                                        width="72">
                                    </el-table-column>
                                    <el-table-column
                                        prop="calma"
                                        label="卡尔玛比率"
                                        width="100">
                                    </el-table-column>
                                    <el-table-column
                                        label="回测进度">
                                         <template slot-scope="scope">
                                            <el-progress :percentage="scope.row.progress" color="#409eff"></el-progress>
                                        </template>
                                    </el-table-column>
                                    <el-table-column
                                        prop="elapse"
                                        label="耗时s"
                                        width="60">
                                    </el-table-column>
                                    <el-table-column
                                        label="操作"
                                        width="60">
                                        <template>
                                            <el-tooltip placement="top">
                                                <div slot="content">删除该回测记录</div>
                                                <i class="el-icon-delete btopt-btn"></i>
                                            </el-tooltip>
                                            <el-tooltip placement="top">
                                                <div slot="content">查看回测详情</div>
                                                <i class="el-icon-view btopt-btn"></i>
                                            </el-tooltip>
                                        </template>
                                    </el-table-column>
                                </el-table>
                            </div>
                        </div>
                        <BTComp style="height:100%;" v-show="selData=='backtest'">
                        </BTComp>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import {codemirror } from 'vue-codemirror'
//基础库
import 'codemirror/lib/codemirror.css'

//python语言库
import "codemirror/mode/python/python.js";

//代码提示插件
import "codemirror/addon/hint/show-hint.js"

//代码折叠插件
import 'codemirror/addon/fold/foldgutter.css'
import "codemirror/addon/fold/foldcode.js";
import "codemirror/addon/fold/brace-fold.js";
import "codemirror/addon/fold/indent-fold.js";
import "codemirror/addon/fold/comment-fold.js";

import 'codemirror/addon/lint/lint.css'
import "codemirror/addon/comment/comment.js";
import "codemirror/addon/selection/active-line.js";

//查找插件
import "codemirror/addon/search/search.js";
import "codemirror/addon/search/searchcursor.js";
import "codemirror/addon/search/jump-to-line.js";
import "codemirror/addon/dialog/dialog.js";
import "codemirror/addon/dialog/dialog.css";

//sublime风格快捷键插件
import "codemirror/keymap/sublime.js";

import "codemirror/addon/edit/closebrackets.js";
import "codemirror/addon/edit/matchbrackets.js";

import BTComp from './btcomp.vue'

export default {
    name: "Backtest",
    components:{
        codemirror,BTComp
    },
    data() {
        return {
            selData:"editor",
            strategies:[],
            strasOnWay:false,
            curStra:null,
            curBT:null,
            backtests:[{
                time:"2021.08.12 17:03:45",
                stime:"2021.07.01 09:00",
                etime:"2021.08.12 15:00",
                return:9.46,
                ar:16.83,
                mdd:3.17,
                sharpe:3.2795,
                calma:3.5946,
                progress: 100,
                elapse:48
            }],
            edit: false,
            content:"",
            content_bak:"",
            cmOptions:{
                mode:"python",
                keyMap: "sublime", // 快键键风格
                lineNumbers: true, // 显示行号
                smartIndent: true, // 智能缩进
                indentUnit: 4, // 智能缩进单位为4个空格长度
                indentWithTabs: false, // 使用制表符进行智能缩进
                lineWrapping: true, // 
                // 在行槽中添加行号显示器、折叠器、语法检测器
                gutters: ["CodeMirror-linenumbers", "CodeMirror-foldgutter", "CodeMirror-lint-markers"], 
                foldGutter: true, // 启用行槽中的代码折叠
                autofocus: true, // 自动聚焦
                matchBrackets: true, // 匹配结束符号，比如"]、}"
                autoCloseBrackets: true, // 自动闭合符号
                styleActiveLine: true, // 显示选中行的样式
                extraKeys:{
                    "Ctrl-S":()=>{
                        this.onSaveCode();
                    }
                }
            }
        };
    },
    methods: {
        onAddStrategy: function(){
            this.$prompt('请输入策略名称', '新建策略', {
                confirmButtonText: '确定',
                cancelButtonText: '取消'
            }).then(( val ) => {
                this.$api.addBtStrategy(val.value, (resObj)=>{
                    if(resObj.result < 0){
                        this.$message.error("新建策略失败:" + resObj.message);
                    } else {
                        this.strategies.push(resObj.strategy)
                    }
                })
            }).catch(() => {
                        
            });
        },
        onSaveCode: function(e){
            if(this.curStra == null || this.content == this.content_bak)
                return;

            this.$api.commitBtStraCode(this.curStra.id, this.content, (resObj)=>{
                if(resObj.result < 0){
                    this.$message.error("策略代码提交失败:" + resObj.message);
                } else {
                    this.$message({
                        message:"策略代码保存成功",
                        type:"success"
                    });
                    this.content_bak = this.content;
                }
            });
        },
        onDelStrategy: function(straid){
            this.$confirm('确定要删除该策略吗', '删除策略', {
                confirmButtonText: '确定',
                cancelButtonText: '取消'
            }).then(( val ) => {
                this.$api.delBtStrategy(straid, (resObj)=>{
                    if(resObj.result < 0){
                        this.$message.error("删除策略失败:" + resObj.message);
                    } else {
                        this.$message.success("删除策略成功");
                        this.refreshStras();
                    }
                });
            }).catch(() => {
                        
            });
        },
        onRefreshStrategy: function(){
            this.refreshStras();
        },
        onOpenStrategy: function(strInfo){
            this.curStra = strInfo;

            this.$api.getBtStraCode(strInfo.id, (resObj)=>{
                if(resObj.result < 0){
                    this.$message.error("拉取策略代码失败:" + resObj.message);
                } else {
                    this.content_bak = resObj.content;
                    this.content = resObj.content;
                }
            });
        },
        handleClickTab: function(tab, event){
            this.selData = tab.name;
        },
        onClickCancel: function(){
            if(this.content != this.content_bak){
                this.$confirm('内容已被修改，确定要放弃修改吗?', '提示', {
                        confirmButtonText: '确定',
                        cancelButtonText: '取消',
                        type: 'warning'
                    })
                    .then(() => {
                        this.content = this.content_bak;
                        this.cmOptions.readOnly = true;
                        this.edit = false;
                    })
                    .catch(() => {       
                    });
            } else {
                this.content = this.content_bak;
                this.cmOptions.readOnly = true;
                this.edit = false;
            }            
        },
        onClickCommit: function(){
            if(this.curStra == null || this.content == this.content_bak)
                return;
                
            this.loading = true;
            this.$api.commitBtStraCode(this.curStra.id, this.content, (resObj)=>{
                if(resObj.result < 0){
                    this.$message.error("策略代码提交失败:" + resObj.message);
                } else {
                    this.$message({
                        message:"策略代码提交成功",
                        type:"success"
                    });
                }
                this.edit = false;
                this.cmOptions.readOnly = true;
                this.loading = false;
            });
        },
        refreshStras: function(){
            this.strasOnWay = true;
            this.$api.getBtStrategies((resObj)=>{
                if(resObj.result < 0){
                    this.$message.error("拉取策略列表失败:" + resObj.message);
                } else {
                    this.strategies = resObj.strategies;
                }
                this.strasOnWay = false;
            });
        }
    },
    mounted() {
        this.$nextTick(()=>{
            setTimeout(()=>{
                this.refreshStras();
            },300);
        });

    },
};
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
.CodeMirror{
    height:100% !important;
}

.btopt-btn:hover{
    cursor: pointer;
    color: #F56C6C;
}

.stra-item{
    padding: 8px 16px;
    border-bottom: 1px solid #E4E7ED;
}

.stra-item:hover{
    background-color: #f5f7fa;
    cursor: pointer;
}

.stra-list:nth-child(odd){
    background-color: #fafafa;
}

.stra-list{
    padding: 4px 0px;
}

.stra-title{
    font-size: 16px;
}

.stra-label{
    color:#707070;
    font-size: 14px;
}

.stra-return{
    color:#707070;
    font-size: 14px;
}

.stra-mdd{
    color:#707070;
    font-size: 14px;
}

.button{
    padding: 4px;
    font-weight: bold;
    color: #909399;
}

.toolbar{
    padding: 4px;
    color: #909399;
}

.toolbar:hover{
    cursor:pointer;
    color: #F56C6C;
}

.button:hover{
    cursor:pointer;
    color: #F56C6C;
}

.divider{
    display: block;
    height: 1px;
    width: 100%;
    margin: 4px 0;
    background-color: #DCDFE6;
}
</style>

<style>
.el-tabs__header{
    margin:0px;
}
</style>
