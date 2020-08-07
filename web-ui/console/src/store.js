import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex);

const state = {
    //登陆相关信息
    cache: {
        userinfo: {
            loginid: "",
            name: "",
            loginip: "",
            logintime: ""
        },
        isLogined: false,
        loginid: ""
    },
    folders:[]
};

const getters = {
    cache: state => state.cache,
    folders: state => state.folders
};

const actions = {

};

const mutations = {
    loginok(state, ctx) {
        state.cache.userinfo = ctx.userinfo;
        state.cache.isLogined = true;
        state.cache.loginid = ctx.loginid;
    },
    logoutok(state) {
        state.cache.userinfo = {
            loginid: "",
            name: "",
            loginip: "",
            logintime: ""
        };
        state.cache.isLogined = false;
        state.cache.loginid = "";
    },
    setfolders(state, ctx){
        state.folders = ctx.folders;
    }
};

export default new Vuex.Store({
    state,
    getters,
    modules: {},
    actions,
    mutations
});
