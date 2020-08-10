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

import JsonViewer from 'vue-json-viewer'
Vue.use(JsonViewer)

Vue.use(new VueSocketIO({
    debug: false,
    // 服务器端地址
    connection: 'http://' + document.domain + ':' + location.port,
    vuex: {
    }
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
