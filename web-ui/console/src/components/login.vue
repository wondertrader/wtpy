<template>
    <div class="loginBox"  v-loading="loading">
        <div class="login">
            <div class="loginForm">
                 <el-row>
                    <h2>交易控制中心</h2>
                </el-row>
                <el-row>
                    <el-input v-model="loginid" placeholder="用户名"></el-input>
                </el-row>
                <el-row>
                    <el-input v-model="passwd" placeholder="密码" type="password"></el-input>
                </el-row>
                <el-row>
                    <el-checkbox v-model="saveuser" style="float:right;">保存用户名</el-checkbox>
                </el-row>
                <el-row style="margin-top:30px;">
                    <el-button type="primary" @click="doLogin()" plain>登 录</el-button>
                </el-row>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: "Login",
    data() {
        return {
            loginid: "",
            passwd: "",
            saveuser:true,
            loading: false
        };
    },
    methods: {
        doLogin: function () {
            let self = this;
            let loginid = self.loginid;
            let passwd = self.passwd;
            self.loading = true;
            this.$api.login(loginid, passwd, (resObj) => {
                if (resObj.result < 0) {
                    self.$alert("用户登录出错：" + resObj.message, "登录失败");
                } else {
                    let userinfo = resObj.userinfo;
                    localStorage.setItem("last_user", loginid);
                    localStorage.setItem("save_user", self.saveuser?"true":"false");

                    this.$store.commit("loginok", {
                        isLogined: true,
                        loginid: loginid,
                        userinfo:userinfo
                    });

                    this.$socket.emit("connect", 1)

                    self.$router.push("/index");
                }
                self.loading = false;
            });
        },
    },
    mounted() {
        this.saveuser = localStorage.getItem("save_user") == 'true';
        if(this.saveuser)
            this.loginid = localStorage.getItem("last_user");
    },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
* {
    margin: 0;
}

.el-input__inner {
    border-radius: 10px !important;
    height: 35px !important;
    line-height: 35px !important;
    font-size: 12px;
}

.el-button {
    width: 100%;
    border-radius: 10px;
    height: 35px !important;
    line-height: 35px !important;
    padding: 0;
}

.el-checkbox__label {
    font-size: 12px;
    color: #a7aab2;
    padding-left: 5px;
}

.loginBox {
    flex: 1;
    display: flex;
    justify-content: center;
    align-items: center;
    height:100vh;
    width:100%;
}

.login {
    width: 240px;
    height: 400px;
    text-align: center;
}

.logo {
    width: 100px;
    margin: 0 auto;
}

.log img {
    width: 100%;
}

.loginForm {
    margin-top: 30px;
}

.loginForm div {
    width: 100%;
    margin: 5px auto;
}
</style>
