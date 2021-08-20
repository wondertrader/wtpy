/*
 * @Descripttion: Automatically generated file comment
 * @version: 
 * @Author: Wesley
 * @Date: 2021-08-05 18:49:24
 * @LastEditors: Wesley
 * @LastEditTime: 2021-08-20 14:28:08
 */
// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'
import store from './store';

import VueSocketIO from 'vue-socket.io'

import ElementUI from 'element-ui';
import './themes/theme-black/index.css';

import echarts from 'echarts' 
Vue.prototype.$echarts = echarts;

Vue.config.productionTip = false;

Vue.use(ElementUI);

Vue.use(new VueSocketIO({
    debug: false,
    // 服务器端地址
    connection: 'http://' + document.domain + ':' + location.port,
    vuex: {}
}));

import Api from './js/api.js'
Vue.prototype.$api = new Api();

/* eslint-disable no-new */
new Vue({
  store: store,
  el: '#app',
  router,
  components: { App },
  template: '<App/>'
})
