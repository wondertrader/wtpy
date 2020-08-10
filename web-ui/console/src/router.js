import Vue from 'vue'
import Router from 'vue-router'

Vue.use(Router);

import Login from '@/components/login'

import Index from '@/components/Index'
import Monitor from '@/components/monitor/main'
import Deploy from '@/components/deploy/main'
import Backtest from '@/components/backtest/main'
import Schedule from '@/components/schedule/main'
import Admins from '@/components/admins/main'


export default new Router({
    routes: [
        { 
            path: '/',
            redirect: '/login', 
        },
        {
            path: '/login',
            name: 'Login',
            component: Login,
        },
        {
            path: '/index',
            name: 'Index',
            component: Index,
            redirect: '/monitor', 
            children: [
                {path: '/monitor', name:"monitor", component: Monitor},
                {path: '/deploy', name:"deploy", component: Deploy},
                {path: '/backtest', name:"backtest", component: Backtest},
                {path: '/schedule', name:"schedule", component: Schedule},
                {path: '/admins', name:"admins", component: Admins}
            ]
        }
    ]
})
