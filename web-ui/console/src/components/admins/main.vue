<template>
	<div style="height:100%;width:100%;">
        <el-row style="height:100%;">
            <el-col :span="12" style="height:100%;">
                <div style="height:100%;display:flex;flex-direction:column;">
                    <div style="flex:0;margin:2px 4px 0px 4px;min-height:39px;display:flex;flex-direction:row;">
                        <div style="flex:0;" class="simtab">
                            <span>用户列表</span>
                        </div> 
                        <div style="flex:1;border-bottom: 1px solid #E4E7ED;margin-top:6px;">
                            <el-dropdown split-button type="danger" size="mini" style="float:right;" @command="handleUserCmd" trigger="click">
                                <i class="el-icon-edit-outline"></i>管理
                                <el-dropdown-menu slot="dropdown">
                                    <el-dropdown-item command="add"><i class="el-icon-circle-plus-outline"></i>添加用户</el-dropdown-item>
                                    <el-dropdown-item command="mod"><i class="el-icon-edit-outline"></i>修改用户</el-dropdown-item>
                                    <el-dropdown-item command="del"><i class="el-icon-delete"></i>删除用户</el-dropdown-item>
                                    <el-dropdown-item command="reset"><i class="el-icon-switch-button"></i>重置密码</el-dropdown-item>
                                    <el-dropdown-item divided  command="refresh"><i class="el-icon-refresh"></i>刷新数据</el-dropdown-item>
                                </el-dropdown-menu>
                            </el-dropdown>
                        </div> 
                    </div>
                    <div style="flex:1;margin:10px 4px;height:100%;">
                        <div style="max-height:100%;overflow:auto;">
                            <el-table
                                border
                                stripe
                                :data.sync="users"
                                class="table"
                                v-loading="loading_user"
                                highlight-current-row
                                @current-change="handleSelectUser">
                                <el-table-column
                                    prop="loginid"
                                    label="登录名"
                                    width="100">
                                </el-table-column>
                                <el-table-column
                                    prop="name"
                                    label="姓名"
                                    width="80">
                                </el-table-column>
                                <el-table-column
                                    prop="createtime"
                                    label="创建时间"
                                    width="100">
                                </el-table-column>
                                <el-table-column
                                    prop="createby"
                                    label="创建人"
                                    width="100">
                                </el-table-column>
                                <el-table-column
                                    prop="modifytime"
                                    label="修改时间"
                                    width="100">
                                </el-table-column>
                                <el-table-column
                                    prop="modifyby"
                                    label="修改人"
                                    width="100">
                                </el-table-column>
                                <el-table-column
                                    prop="remark"
                                    label="备注">
                                </el-table-column>
                            </el-table>
                        </div>
                    </div>
                </div>
            </el-col>
            <el-col :span="12" style="height:100%;border-left: 1px solid #E4E7ED;">
                <div style="height:100%;display:flex;flex-direction:column;">
                    <div style="flex:0;margin:2px 4px 0px 4px;min-height:39px;display:flex;flex-direction:row;">
                        <div style="flex:0;" class="simtab">
                            <span>操作日志</span>
                        </div> 
                        <div style="flex:1;border-bottom: 1px solid #E4E7ED;margin-top:6px;">
                            <el-row style="height:100%;">
                                <el-col :span="12" :offset="9">
                                    <el-date-picker
                                        v-model="daterange"
                                        type="daterange"
                                        align="right"
                                        size="mini"
                                        style="float:right;"
                                        unlink-panels
                                        range-separator="至"
                                        start-placeholder="开始日期"
                                        end-placeholder="结束日期"
                                        @change="handleDtRangeChange">
                                    </el-date-picker>
                                </el-col>
                                <el-col :span="3">
                                    <el-button type="primary" icon="el-icon-refresh" size="mini" plain style="float:right;" @click="onClickQryActions">刷新</el-button>
                                </el-col>
                            </el-row>                            
                        </div> 
                    </div>
                    <div style="flex:1;margin:10px 4px;height:100%;">
                        <div style="max-height:100%;overflow:auto;">
                            <el-table
                                border
                                stripe
                                :data="actions"
                                class="table">
                                <el-table-column
                                    prop="loginid"
                                    label="登录名"
                                    width="100">
                                </el-table-column>
                                <el-table-column
                                    prop="actiontime"
                                    label="操作时间"
                                    width="100">
                                </el-table-column>
                                <el-table-column
                                    prop="actionip"
                                    label="来源IP"
                                    width="120">
                                </el-table-column>
                                <el-table-column
                                    prop="action"
                                    label="类型"
                                    width="80">
                                </el-table-column>
                                 <el-table-column
                                    prop="remark"
                                    label="备注">
                                </el-table-column>
                            </el-table>
                        </div>
                    </div>
                </div>
            </el-col>
        </el-row>
        <el-dialog
            :title="addUser?'添加用户':'修改用户'"
            :visible.sync="showUserDlg"
            class="dialog-user"
            width="25%">
            <el-row>
                <el-col :span="6">
                    <a>登录名：</a>
                </el-col>
                <el-col :span="18">
                    <el-input v-model="curUser.loginid" size="mini" :disabled="!addUser"></el-input>
                </el-col>
            </el-row>
            <el-row>
                <el-col :span="6">
                    <a>用户姓名：</a>
                </el-col>
                <el-col :span="18">
                    <el-input v-model="curUser.name" size="mini"></el-input>
                </el-col>
            </el-row>
            <el-row>
                <el-col :span="6">
                    <a>用户类型：</a>
                </el-col>
                <el-col :span="18">
                    <el-tooltip effect="dark" content="拥有全部的管理权限" placement="top-start">
                        <el-radio v-model="curUser.role" label="admin">管理员</el-radio>
                    </el-tooltip>
                    <el-tooltip effect="dark" content="拥有风控权限" placement="top-start">
                        <el-radio v-model="curUser.role" label="risker">风控员</el-radio>
                    </el-tooltip>
                </el-col>
            </el-row>
            <el-row>
                <el-col :span="6">
                    <a>登录密码：</a>
                </el-col>
                <el-col :span="18">
                    <el-input v-model="curUser.passwd" size="mini" type="password" show-password :disabled="!addUser"></el-input>
                </el-col>
            </el-row>
            <el-row style="height:60px;">
                <el-col :span="6">
                    <a>IP限制：</a>
                </el-col>
                <el-col :span="18">
                    <el-input type="textarea" v-model="curUser.iplist" size="mini"></el-input>
                </el-col>
            </el-row>
            <el-row style="height:60px;">
                <el-col :span="6">
                    <a>备注信息：</a>
                </el-col>
                <el-col :span="18">
                    <el-input type="textarea" v-model="curUser.remark" style="min-height:80px;"></el-input>
                </el-col>
            </el-row>
            <span slot="footer" class="dialog-footer">
                <el-button type="primary" plain size="mini" @click="onCommitUser">提交数据</el-button>
            </span>
        </el-dialog>
    </div>
</template>

<script>
export default {
    name: 'Login',
    data() {
        return {
            users:[],
            actions:[],
            curUser:{
                loginid:"",
                name:"",
                remark:"",
                role:"admin",
                passwd:"",
                iplist:""
            },
            daterange:[],
            showUserDlg: false,
            addUser: true,
            loading_user:false
        }
    },
    methods:{
        handleSelectUser: function(usrInfo){
            this.curUser = JSON.parse(JSON.stringify(usrInfo));
        },
        handleDtRangeChange: function(){
        },
        onClickQryActions: function(){
            if(this.daterange.length == 0){
                this.$alert("请选选择日期范围");
            }

            let sdate = this.daterange[0].format("yyyy-MM-dd 00:00:00");
            let edate = this.daterange[1].format("yyyy-MM-dd 23:59:59");
            this.$api.getActions(sdate, edate, (resObj)=>{
                if(resObj.result >= 0){
                    this.actions = resObj.actions;
                }
            });
        },
        onCommitUser: function(){
            this.$api.commitUser(this.curUser, this.addUser?"add":"mod", (resObj)=>{
                if(resObj.result < 0){
                    this.$notify.error(resObj.message);
                } else {
                    this.$notify({
                        message:"用户信息提交成功",
                        type:"success"
                    });
                    this.showUserDlg = false;
                    this.queryUsers();
                }
            });
        },
        queryUsers: function(){
            this.loading_user = true;
            this.$api.getUsers((resObj)=>{
                if(resObj.result >= 0){
                    this.users = resObj.users;
                } else {
                    this.$notify.error(resObj.message);
                }
                this.loading_user = false;
            });
        },
        handleUserCmd: function(command){
            if(command == 'add'){
                this.curUser = {
                    loginid:"",
                    name:"",
                    remark:"",
                    role:"admin",
                    passwd:"",
                    iplist:""
                };
                this.addUser = true;
                this.showUserDlg = true;
            } else if(command == 'mod'){
                if(this.curUser.loginid == ""){
                    this.$alert("请选择要修改的用户");
                    return;
                }
                this.curUser.passwd = "********";
                this.addUser = false;
                this.showUserDlg = true;
            } else if(command == 'del'){
                if(this.curUser.loginid == ""){
                    this.$alert("请选择要删除的用户");
                    return;
                }
                
                this.$confirm('确定要删除用户' + this.curUser.loginid + '吗?', '删除用户', {
                    confirmButtonText: '确定',
                    cancelButtonText: '取消',
                    type: 'danger'
                }).then(() => {
                    this.$api.delUser(this.curUser.loginid, (resObj)=>{
                        if(resObj.result < 0){
                            this.$notify.error(resObj.message);
                        } else {
                            this.$notify({
                                message: "用户已删除",
                                type:"success"
                            });
                            this.queryUsers();
                        }
                    });
                });
            } else if(command == 'reset'){
                if(this.curUser.loginid == ""){
                    this.$alert("请选择要重置密码的用户");
                    return;
                }

                this.$prompt('请输入新的密码', '重置密码', {
                    confirmButtonText: '确定',
                    cancelButtonText: '取消',
                    inputType: 'password'
                }).then(({ value }) => {
                    this.$confirm('确定要重置用户' + this.curUser.loginid + '的密码吗?', '重置密码', {
                        confirmButtonText: '确定',
                        cancelButtonText: '取消',
                        type: 'danger'
                    }).then(() => {
                        this.$api.resetpwd(this.curUser.loginid, value, (resObj)=>{
                            if(resObj.result < 0){
                                this.$notify.error(resObj.message);
                            } else {
                                this.$notify({
                                    message: "密码重置成功",
                                    type:"success"
                                });
                            }
                        });
                    });
                }).catch(() => {
                           
                });
                
                
            } else if(command == "refresh"){
                this.queryUsers();
            }

        }
    },
    mounted (){
        this.$nextTick(()=>{
            this.queryUsers();
        })       
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

.dialog-user .el-row{
    margin: 4px 8px;
    padding: 4px 0px;
    align-items: center;
    align-content: center;
    vertical-align: middle;
    height: 36px;
}
</style>
