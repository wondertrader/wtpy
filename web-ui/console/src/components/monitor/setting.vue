<template>
    <div style="height:100%;width:100%;display:flex;flex-direction:column;" v-loading="loading">
        <div style="flex:1;overflow:auto;border: 1px solid #DCDFE6;border-radius:4px;">
            <codemirror
                ref="mycode"
                v-model="setting_s"
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
import 'codemirror/lib/codemirror.css'
import "codemirror/mode/javascript/javascript.js";
import 'codemirror/addon/lint/json-lint'

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
            setting_s:"",
            setting:{},
            edit: false,
            loading: false,
            cmOptions:{
                mode: 'text/x-python',
                gutters: ['CodeMirror-lint-markers'],
                lineNumbers: true, //是否显示行号
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
            
            this.queryCfg();
        }
    },
    methods: {
        queryCfg: function(){
            let self = this;
            this.edit=false;
            this.loading = true;                
            setTimeout(()=>{
                self.$api.getGroupCfg(self.groupid, (resObj)=>{
                    if(resObj.result < 0){
                        self.$alert(resObj.message);
                    } else {
                        self.setting = resObj.config;
                        self.setting_s = JSON.stringify(self.setting, null, 2);
                        self.cmOptions.readOnly = true;
                    }
                    self.loading = false;
                });
            }, 300);
        },
        onClickEdit: function(){
            this.setting_s = JSON.stringify(this.setting, null, 2);
            this.cmOptions.readOnly = false;
            this.edit = true;
        },
        onClickCommit: function(){
            let config = null;
            try{
                config = JSON.parse(this.setting_s);
            } catch(e){
                this.$message.error("设置项解析失败:" + e.message);
                return;
            }

            this.loading = true;
            this.$api.commitGroupCfg(this.groupid, config, (resObj)=>{
                if(resObj.result < 0){
                    this.$message.error("组合配置提交失败:" + resObj.message);
                } else {
                    this.$message({
                        message:"组合配置提交成功",
                        type:"success"
                    });
                    this.setting = config;
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
