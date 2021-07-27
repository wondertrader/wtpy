<template>
    <div style="height:100%;width:100%;display:flex;flex-direction:row;">
        <div style="flex:0 320px;min-width:320px;border:1px solid #DCDFE6;border-radius:2px;margin:4px;">
            <div style="height:100%;overflow:auto;">
                <el-tree :data="folders" @node-click="handleFileClick"></el-tree>
            </div>
        </div>
        <div style="flex:1;margin:4px;display:flex;flex-direction:column;overflow:auto;">
            <div style="flex:1;height:100%;overflow:auto;border:1px solid #DCDFE6;border-radius:2px;" v-loading="fileOnway">
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

export default {
    name: 'editor',
    props:{
        groupid:{
            type:String,
            default(){
                return "";
            }
        }
    },
    computed:{
        curFilePath(){
            if(this.curFile == null)
                return '';
            else
                return this.curFile.path;
        }
    },
    components:{
        codemirror
    },
    watch:{
        groupid: function(newVal, oldVal){
            newVal = newVal || "";
            oldVal = oldVal || "";

            if(newVal.length == 0 || newVal == oldVal)
                return;
            
            this.queryFiles();
        }
    },
    data () {
        return {
            folders:[],
            edit: false,
            filename:'',
            content_s:"",
            content_backup:"",
            curFile:null,
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
        }
    },
    methods: {
        queryFiles: function(){
            let self = this;
            self.$api.getGroupDir(self.groupid, (resObj)=>{
                if(resObj.result < 0){
                    self.$notify.error('获取组合目录结构失败：' + resObj.message);
                } else {
                    this.folders = [resObj.tree];
                }
            });
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
    mounted(){
        
    }
}
</script>
<style>
.CodeMirror{
    height:100% !important;
}
</style>