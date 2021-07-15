<template>
    <div style="height:100%;width:100%;display:flex;flex-direction:column;" v-loading="loading">
        <div style="flex:1;overflow:auto;border: 1px solid #DCDFE6;border-radius:4px;">
            <codemirror
                ref="mycode"
                v-model="content_s"
                :options="cmOptions"
                style="height:100%;">
            </codemirror>
        </div>
        <div style="flex:0;min-height:32px; margin-top:8px;">
            <el-button size="mini" style="float:right;" v-show="!edit" @click="onClickEdit()">
                <i class="el-icon-edit"/>修改
            </el-button>
            <el-button size="mini" style="float:right;" v-show="edit" @click="onClickCommit()">
                <i class="el-icon-set-up"/>提交
            </el-button>
            <el-button size="mini" style="float:right;" v-show="edit" @click="edit=false;">
                <i class="el-icon-refresh-left"/>取消
            </el-button>
        </div>
    </div>  
</template>

<script>
import {codemirror } from 'vue-codemirror'
import "codemirror/mode/python/python.js";

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
    name: 'setting',
    props:{
        groupid:{
            type:String,
            default(){
                return "";
            }
        }
    },
    components:{
        codemirror
    },
    data () {
        return {
            content:"",
            content_s:"",
            edit: false,
            loading: false,
            cmOptions:{
                mode:"python",
                lineNumbers: true, //是否显示行号
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
    watch:{
        groupid: function(newVal, oldVal){
            newVal = newVal || "";
            oldVal = oldVal || "";

            if(newVal.length == 0 || newVal == oldVal)
                return;
            
            this.queryEntry();
        }
    },
    methods: {
        queryEntry: function(){
            let self = this;
            this.edit=false;
            this.loading = true;                
            setTimeout(()=>{
                self.$api.getGroupEntry(self.groupid, (resObj)=>{
                    if(resObj.result < 0){
                        self.$notify.error('拉取入口文件失败：' + resObj.message);
                    } else {

                        self.content = resObj.content;
                        self.content_s = resObj.content;
                        self.cmOptions.readOnly = true;
                    }
                    self.loading = false;
                });
            }, 300);
        },
        onClickEdit: function(){
            this.content_s = self.content;
            this.cmOptions.readOnly = false;
            this.edit = true;
        },
        onClickCommit: function(){
            this.loading = true;
            this.$api.commitGroupEntry(this.groupid, this.content_s, (resObj)=>{
                if(resObj.result < 0){
                    this.$message.error("入口文件提交失败:" + resObj.message);
                } else {
                    this.$message({
                        message:"入口文件提交成功",
                        type:"success"
                    });
                    this.content = this.content_s;
                }
                this.edit = false;
                this.cmOptions.readOnly = true;
                this.loading = false;
            });
        }
    }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style>
.CodeMirror {
	width: 100%;
    height: 100% !important;
    min-height: 500px;
}

.CodeMirror-scroll {
	overflow-y: hidden;
	overflow-x: auto;
}
</style>
