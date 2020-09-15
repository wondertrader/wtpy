<template>
    <div id="app">
        <router-view/>
    </div>
</template>

<script>
export default {
    name: 'App'
}
</script>

<style>
#app {
    font-family: 'Avenir', Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    /*text-align: center;*/
    /* color: #2c3e50; */
    height: 100vh;
    width: 100%;
}

body{
    margin: 0px;
}

.el-main{
    padding: 4px !important;
}

.box{
    border:1px solid #E4E7ED;
    margin:4px;
    border-radius:4px;
}

/* 滚动条 */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track-piece {
    background-color: #f1f1f1;
    border-radius: 2px;
}
::-webkit-scrollbar-thumb:vertical {
    height: 6px;
    background-color: #cccccc;
    border-radius: 2px;
}
::-webkit-scrollbar-thumb:horizontal {
    width: 6px;
    background-color: #cccccc;
    border-radius: 2px;
}

.el-table td, .el-table th {
    padding: 4px 0;
}

.text-danger{
    color:#F56C6C;
    font-weight: bold;
}

.text-warning{
    color:#E6A23C;
    font-weight: bold;
}

.text-success{
    color:#67C23A;
    font-weight: bold;
}

.text-info{
    color:#909399;
    font-weight: bold;
}
</style>
