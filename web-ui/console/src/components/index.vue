<template>
    <div id="index" style="height:100%;">
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
                        <div style="flex:0;margin:8px;font-size:14px;">
                            <el-row>
                                <el-col :span="10">
                                    <a>登录用户：</a>
                                </el-col>
                                <el-col :span="14">
                                    <a>{{cache.userinfo.name}}({{cache.loginid}})</a>
                                </el-col>
                            </el-row>
                            <el-row>
                                <el-col :span="10">
                                    <a>登录IP：</a>
                                </el-col>
                                <el-col :span="14">
                                    <a>{{cache.userinfo.loginip}}</a>
                                </el-col>
                            </el-row>
                            <el-row>
                                <a>登录时间：</a>
                            </el-row>
                            <el-row>
                                <a>{{cache.userinfo.logintime}}</a>
                            </el-row>
                        </div>
                        </div>
                    </div>
                </div>
            </el-aside>
            <el-container>
                <el-main style="border-bottom: 2px solid #E4E7ED;">
                    <keep-alive>
                        <router-view ref="main"></router-view>
                    </keep-alive>
                </el-main>
                <el-footer class="statusbar">
                    <div style="flex:1;">
                    </div>
                    <div style="flex:0;margin-top:4px; min-width:150px;">
                        <i class="el-icon-connection" style="color:dark-green;padding-right:8px;"></i><a>推送通道已连接</a>
                    </div>  
                </el-footer>
            </el-container>
        </el-container>
        <el-dialog
            title="用户管理"
            :visible.sync="showadmins"
            width="25%">
            <Admins/>
        </el-dialog>
    </div>    
</template>

<script>
import { mapGetters } from 'vuex';

import Admins from './admins/main'

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
        Admins
    },
    data () {
        return {
            showadmins: false,
        }
    },
    methods: {
        handleItemSel: function(index, idxPath, obj, e){
            // console.log(index, idxPath, obj, e);
            if(index == "admins"){
                this.showadmins = true;
            }
        }
    },
    mounted(){
        // console.log("mounted");
        if(!this.cache.isLogined){
            this.$router.push("/login");
        } else {
           
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
</style>
