<template>
    <div id="index" style="height:100%;" v-loading="loading">
        <el-container style="height:100%;">
            <el-aside width="230px" style="border-right:2px solid #E4E7ED;height:100%;">
                <div style="height:100%;display:flex;flex-direction:column;">
                    <div style="flex:0;height:44px !important;border-bottom: 1px solid #E4E7ED;">
                        <div style="display:flex;flex-direction:row;margin-left:12px;">
                            <div style="flex:0;margin-top:6px;padding-right: 12px;">
                                <img src="../assets/logo.png" height="28px" width="28px"/>
                            </div>
                            <div style="flex:1;margin-top:4px;overflow:hidden;">
                                <span style="font-size:24px;">WT控制台</span>
                            </div>
                        </div>
                    </div>
                    <div style="flex:1;">
                        <div style="display:flex;flex-direction:column;height:100%;">
                        <div style="flex:1;display:block;border-bottom: 1px solid #E4E7ED;">
                            <el-menu
                                default-active="1-1"
                                class="el-menu-vertical-demo"
                                style="height:100%;"
                                @select="handleItemSel"
                                router>
                                <el-submenu index="1">
                                    <template slot="title">
                                        <i class="el-icon-set-up"></i>
                                        <span>控制台</span>
                                    </template>
                                    <el-menu-item-group>
                                        <el-menu-item index="1-1" route="/monitor">
                                            <i class="el-icon-view"></i>
                                            <span>监控中心</span>
                                        </el-menu-item>
                                        <el-menu-item index="1-2" route="/schedule" v-if="isAdmin">
                                            <i class="el-icon-time"></i>
                                            <span>调度中心</span>
                                        </el-menu-item>
                                    </el-menu-item-group>
                                </el-submenu>
                                <el-submenu index="2" v-if="isAdmin">
                                    <template slot="title">
                                        <i class="el-icon-box"></i>
                                        <span>自动实施</span>
                                    </template>
                                    <el-menu-item-group>
                                        <el-menu-item index="2-1" route="/deploy">
                                            <i class="el-icon-thumb"></i>
                                            <span>策略部署</span>
                                        </el-menu-item>
                                        <el-menu-item index="2-2" route="/backtest">
                                            <i class="el-icon-data-line"></i>
                                            <span>在线回测</span>
                                        </el-menu-item>
                                    </el-menu-item-group>                           
                                </el-submenu>
                                <el-submenu index="3" v-if="isAdmin">
                                    <template slot="title">
                                        <i class="el-icon-setting"></i>
                                        <span>系统设置</span>
                                    </template>
                                    <el-menu-item-group>
                                        <el-menu-item index="3-1" route="/admins">
                                            <i class="el-icon-user"></i>
                                            <span>用户管理</span>
                                        </el-menu-item>
                                    </el-menu-item-group>                           
                                </el-submenu>
                            </el-menu>
                        </div>
                        <div style="flex:0;margin:8px;font-size:14px;display:flex;flex-direction:row;">
                            <div style="flex:0 0; margin-right:8px;">
                                <el-popover
                                    placement="top-start"
                                    width="240"
                                    trigger="hover">
                                    <div>
                                        <el-row style="font-size:20px; padding-bottom:4px;">
                                            <i class="el-icon-user" style="padding-right:4px;"/><strong>用户信息</strong>
                                        </el-row>
                                        <el-row>
                                            <el-col :span="8">账户：</el-col>
                                            <el-col :span="14">{{cache.loginid}}</el-col>
                                        </el-row>
                                        <el-row>
                                            <el-col :span="8">姓名：</el-col>
                                            <el-col :span="14">{{cache.userinfo.name}}</el-col>
                                        </el-row>
                                        <el-row>
                                            <el-col :span="8">用户类型：</el-col>
                                            <el-col :span="14">{{isAdmin?"管理员":"风控员"}}</el-col>
                                        </el-row>
                                        <el-row>
                                            <el-col :span="8">登录时间：</el-col>
                                            <el-col :span="14">{{cache.userinfo.logintime}}</el-col>
                                        </el-row>
                                        <el-row>
                                            <el-col :span="8">登录地址：</el-col>
                                            <el-col :span="14">{{cache.userinfo.loginip}}</el-col>
                                        </el-row>
                                    </div>
                                    <span slot="reference" ><i class="el-icon-user userhead"/></span>
                                </el-popover>
                            </div>
                            <div style="flex: 1 0;">
                                <el-row>
                                    <span class="user">{{cache.userinfo.name}}</span>
                                </el-row>
                                <el-row>
                                    <span class="user">{{cache.loginid}}</span>
                                </el-row>
                            </div>
                            <div style="flex: 0 0;">
                                <div>
                                    <el-tooltip placement="top">
                                        <div slot="content">修改密码</div>
                                        <i class="el-icon-setting button" @click="onModPwd"/>
                                    </el-tooltip>
                                </div>
                                <div>
                                    <el-tooltip placement="top">
                                        <div slot="content">注销登录</div>
                                        <i class="el-icon-switch-button button" @click="onLogout" style="color:#F56C6C;"/>
                                    </el-tooltip>
                                </div>
                            </div>
                        </div>
                        </div>
                    </div>
                </div>
            </el-aside>
            <el-container>
                <el-main style="border-bottom: 2px solid #E4E7ED;">
                    <keep-alive>
                        <router-view ref="main" @notify="handleNotify"></router-view>
                    </keep-alive>
                </el-main>
                <el-footer class="statusbar">
                    <div style="flex:1; margin:4px;">
                        <div class="scroller" @click="onClickScroller" v-show="lastNotify">
                            <marquee>
                                <i :class="getIconStyle(lastNotify?lastNotify.title:'')" style="padding-right:4px;"></i>
                                <span class="time">{{lastNotify?lastNotify.time.format("hh:mm:ss"):""}}</span>
                                <span class="group">{{lastNotify?lastNotify.group:""}}</span>
                                <span class="channel">{{lastNotify?lastNotify.channel:""}}</span>
                                <span :class="getTitleStyle(lastNotify?lastNotify.title:'')">{{lastNotify?lastNotify.title:""}}</span>
                                <span class="message">{{lastNotify?lastNotify.message:""}}</span>
                            </marquee>
                        </div>
                    </div>
                    <div style="flex:0;margin-top:4px; min-width:150px;">
                        <i class="el-icon-connection" style="color:green;padding-right:8px;"></i><a>推送通道已连接</a>
                    </div>  
                </el-footer>
            </el-container>
        </el-container>
        <el-dialog
            title="修改密码"
            :visible.sync="showDlgModPwd"
            width="360px">
            <el-row style="margin:8px 0;">
                <el-input placeholder="请输入旧密码" v-model="oldpwd" show-password></el-input>
            </el-row>
            <el-row style="margin:8px 0;">
                <el-input placeholder="请输入新密码" v-model="newpwd" show-password></el-input>
            </el-row>
            <el-row style="margin:8px 0;">
                <el-input placeholder="请确认新密码" v-model="confirmpwd" show-password></el-input>
            </el-row>
            <span slot="footer" class="dialog-footer">
                <el-button type="primary" @click="doModPwd()" plain>确 定</el-button>
            </span>
        </el-dialog>
        <el-dialog
            title="通知列表"
            :visible.sync="showNotifies"
            direction="btt"
            width="800px">
            <div style="height:400px;overflow-y:scroll;border:solid 1px #E4E7ED;padding:4px;">
                <el-table
                    :data="notifies"
                    stripe
                    :show-header="false">
                    <el-table-column>
                        <template slot-scope="scope">
                            <i :class="getIconStyle(scope.row.title)" style="padding-right:4px;"></i>
                            <span class="time">{{scope.row.time.format("hh:mm:ss")}}</span>
                            <span class="group">{{scope.row.group}}</span>
                            <span class="channel">{{scope.row.channel}}</span>
                            <span :class="getTitleStyle(scope.row.title)">{{scope.row.title}}</span>
                            <span class="message">{{scope.row.message}}</span>
                        </template>
                    </el-table-column>
                </el-table>
            </div>
        </el-dialog>
    </div>    
</template>

<script>
import { mapGetters } from 'vuex';

export default {
    name: 'index',
    computed: {
        ...mapGetters([
            'cache'
        ]),
        isAdmin: function(){
            let uInfo = this.cache.userinfo;
            if(uInfo)
                return (uInfo.role == 'admin' || uInfo.role == 'superman');
            else
                return false;        
        }
    },
    components:{
    },
    data () {
        return {
           showDlgModPwd: false,
           oldpwd:'',
           newpwd:'',
           confirmpwd:'',
           loading:false,
           notifies:[],
           lastNotify:null,
           showNotifies:false
        }
    },
    methods: {
        handleItemSel: function(index, idxPath, obj, e){
            
        },
        onLogout: function(e){
            this.$confirm('确定要注销登录吗？', '注销登录', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning'
            }).then(() => {
                this.$store.commit("logoutok");

                this.$router.push("/login");
            }).catch(() => {
      
            });
        },
        onModPwd: function(e){
            this.showDlgModPwd = true;
        },
        doModPwd: function(){
            let self = this;
            if(this.newpwd=='' || this.oldpwd=='' || this.confirmpwd==''){
                this.$alert("密码不能为空");
                return;
            }

            if(this.newpwd != this.confirmpwd){
                this.$alert("两次输入的新密码不一致");
                return;
            }

            this.loading = true;
            this.$api.modpwd(this.oldpwd, this.newpwd, (resObj)=>{
                if(resObj.result < 0){
                    self.$notify.error("密码修改失败：" + resObj.message, "修改密码");
                } else {
                    self.$notify.success("密码修改成功", "修改密码");
                    this.showDlgModPwd = false;
                }
                 setTimeout(()=>{
                    this.loading = false;
                },150);
            });
        },
        handleNotify:function(notify){
            this.notifies.push(notify);
            if(this.notifies.length > 100){
                this.notifies = this.notifies.slice(this.notifies.length - 100);
            }
            this.lastNotify = notify;
        },
        onClickScroller:function(e){
            this.showNotifies = !this.showNotifies;
        },
        getTitleStyle: function(title){
            if(title == '成交回报'){
                return 'title-success';
            } else {
                return 'title-warning';
            }
        },
        getIconStyle: function(title){
            if(title == '成交回报'){
                return 'el-icon-news';
            } else {
                return 'el-icon-warning-outline';
            }
        }
    },
    mounted(){
        if(!this.cache.isLogined){
            this.$router.push("/login");
        } 
    }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    #index{
        height: 100%;
        width: 100%;
        display: flex;
        flex-direction: column;
    }

    .statusbar{
        height:36px !important;
        display: inline-flex;
        flex-direction: row;
    }

    .row{
        display: inline-flex;
        flex-direction: row;
    }

    .el-menu{
        border-right: 0px solid transparent !important;
    }

    .user{
        font-size: 16px;
        display: block;
        margin: 3px 0;
    }

    .button{
        font-size: 18px;
        padding: 4px;
        font-weight: bold;
        color: #909399;
    }

    .button:hover{
        cursor:pointer;
    }

    .userhead{
        font-size:44px;
        color: #909399;
    }
    
    .userhead:hover{
        cursor:pointer;
        color: #F56C6C;
    }

    .group{
        background-color: #A3B8E3;
        padding:2px 4px;
        color: #2A3A57;
        border-radius: 2px;
    }

    .channel{
        background-color: #C2DBFF;
        padding:2px 4px;
        color: #2A3A57;
        border-radius: 2px;
    }

    .title-success{
        background-color: #9EE379;
        padding:2px 4px;
        color: #2A3A57;
        border-radius: 2px;
    }

    .title-warning{
        background-color: #FFD16E;
        padding:2px 4px;
        color: #2A3A57;
        border-radius: 2px;
    }

    .time{
        color: #5E93FC;
        padding:2px 4px;
    }

    .message{
        padding:2px 4px;
        color:#707070;
    }

    .scroller{
        padding-top:5px;
        padding-left:5px;
    }

    .scroller:hover{
        cursor:pointer;
        border: solid 1px #F56C6C;
        padding-top:4px;
        padding-left:4px;
    }
</style>
