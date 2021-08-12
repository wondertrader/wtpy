<template>
    <div style="height:100%;width:100%;">
        <div style="height:100%;display:flex;flex-direction:row;">
            <div style="height:100%;flex:0 320px;">
                <div style="display:flex;flex-direction:column;">
                    <div style="flex:0 40px;display:flex;flex-direction:row;">
                        <div style="flex:0;" class="simtab">
                            <span>我的策略</span>
                        </div> 
                        <div style="flex:1;border-bottom: 1px solid #E4E7ED;margin-top:6px;"></div>
                    </div>
                    <div style="flex:1 1;" v-loading="fileOnway">
                        <div style="overflow:auto;">
                            <el-tree :data="folders" @node-click="handleFileClick"></el-tree>
                        </div>
                    </div>
                </div>
            </div>
            <div style="height:100%;border-left: 1px solid #E4E7ED;flex: 1 0;">
                <div style="height:100%;display:flex;flex-direction:column;">
                    <div style="flex:0 0 44px;margin:2px 4px 0px 4px;">
                        <el-tabs :value="selData" type="card" style="height:100%;" @tab-click="handleClickTab">
                            <el-tab-pane label="策略编辑" name="editor">
                            </el-tab-pane>
                            <el-tab-pane label="回测详情" name="backtest">
                            </el-tab-pane>
                        </el-tabs>
                    </div>
                    <div style="flex:1 0;overflow:auto;margin:4px;">
                        <div style="height:100%;display:flex;flex-direction:column;" v-show="selData=='editor'">
                            <div style="flex:2;display:flex;flex-direction:column;">
                                <div style="flex:1 1;overflow:auto;border:1px solid #DCDFE6;border-radius:2px;">
                                    <div style="height:100%">
                                        <codemirror
                                            ref="mycode"
                                            v-model="content_s"
                                            :options="cmOptions"
                                            style="height:100% !important;">
                                        </codemirror>
                                    </div>
                                </div>
                                <div style="flex:0 32px;margin-top:8px;">
                                    <span style="font-size:12px;color:gray;float:left;">当前文件:{{curFilePath}}</span>
                                    <el-button size="mini" style="float:right;" v-show="!edit" @click="onClickEdit()">
                                        <i class="el-icon-edit"/>修改
                                    </el-button>
                                    <el-button size="mini" style="float:right;" v-show="edit" @click="onClickCommit()">
                                        <i class="el-icon-set-up"/>提交
                                    </el-button>
                                    <el-button size="mini" style="float:right;" v-show="edit" @click="onClickCancel()">
                                        <i class="el-icon-refresh-left"/>取消
                                    </el-button>
                                </div>
                            </div>
                            <el-divider></el-divider>
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
                                                <i class="el-icon-delete delete-btn"></i>
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
import "codemirror/mode/python/python.js";
import "codemirror/mode/javascript/javascript.js"

import 'codemirror/lib/codemirror.css'
import 'codemirror/addon/fold/foldgutter.css'
import 'codemirror/addon/lint/lint.css'

import "codemirror/addon/comment/comment.js";
import "codemirror/addon/selection/active-line.js";
import "codemirror/keymap/sublime.js";
import "codemirror/addon/fold/foldcode.js";
import "codemirror/addon/fold/foldgutter.js";
import "codemirror/addon/fold/brace-fold.js";
import "codemirror/addon/fold/indent-fold.js";
import "codemirror/addon/fold/comment-fold.js";

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
            folders:[],
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
            filename:'',
            content_s:"",
            content_backup:"",
            curFile:null,
            curFilePath:"",
            fileOnway: false,
            cmOptions:{
                mode:"python",
                keyMap: "sublime", // 快键键风格
                lineNumbers: true, // 显示行号
                smartIndent: true, // 智能缩进
                indentUnit: 4, // 智能缩进单位为4个空格长度
                indentWithTabs: true, // 使用制表符进行智能缩进
                lineWrapping: true, // 
                // 在行槽中添加行号显示器、折叠器、语法检测器
                gutters: ["CodeMirror-linenumbers", "CodeMirror-foldgutter", "CodeMirror-lint-markers"], 
                foldGutter: true, // 启用行槽中的代码折叠
                autofocus: true, // 自动聚焦
                matchBrackets: true, // 匹配结束符号，比如"]、}"
                autoCloseBrackets: true, // 自动闭合符号
                styleActiveLine: true, // 显示选中行的样式
                readOnly:true
            }
        };
    },
    methods: {
       handleClickTab: function(tab, event){
            this.selData = tab.name;
        },
        handleFileClick: function(data){
            let self = this;
            if(data.isfile){
                let ay = data.path.split('.');
                let ext = ay[ay.length-1].toLowerCase()
                let exts = ['py','json','js','csv']
                if(exts.indexOf(ext) == -1){
                    this.$toast("该文件不可查看");
                    return;
                }
                self.fileOnway = true;
                self.curFile = data;
                self.$api.getGroupFile(this.groupid, data.path, (resObj)=>{
                    if(resObj.result < 0){
                        self.$notify.error('获取文件内容失败' + resObj.message);
                    } else {
                        self.content_s = resObj.content;

                        self.cmOptions.mode = (function(ext){
                            if(ext == 'py')
                                return 'python';
                            else if(ext == 'json')
                                return {name:"javascript", json: true};
                            else if(ext == 'js')
                                return "javascript";
                            else
                                return 'text/plain';
                        })(ext);
                        self.fileOnway = false;
                    }
                });
            }
        },
        onClickEdit: function(){
            this.content_backup = this.content_s;
            this.cmOptions.readOnly = false;
            this.edit = true;
        },
        onClickCancel: function(){
            if(this.content_s != this.content_backup){
                this.$confirm('内容已被修改，确定要放弃修改吗?', '提示', {
                        confirmButtonText: '确定',
                        cancelButtonText: '取消',
                        type: 'warning'
                    })
                    .then(() => {
                        this.content_s = this.content_backup;
                        this.cmOptions.readOnly = true;
                        this.edit = false;
                    })
                    .catch(() => {       
                    });
            } else {
                this.content_s = this.content_backup;
                this.cmOptions.readOnly = true;
                this.edit = false;
            }            
        },
        onClickCommit: function(){

            this.loading = true;
            this.$api.commitGroupFile(this.groupid, this.curFile.path, this.content_s, (resObj)=>{
                if(resObj.result < 0){
                    this.$message.error("文件提交失败:" + resObj.message);
                } else {
                    this.$message({
                        message:"文件提交成功",
                        type:"success"
                    });
                }
                this.edit = false;
                this.cmOptions.readOnly = true;
                this.loading = false;
            });
        }
    },
    mounted() {
        
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

.delete-btn:hover{
    cursor: pointer;
    color: #F56C6C;
}
</style>
