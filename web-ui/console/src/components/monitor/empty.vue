<template>
    <div class="empty-box">
        <div class="content">
            <h2>尚未添加组合</h2>
        </div>
    </div>    
</template>

<script>
export default {
    name: 'empty',
    components: {
    },
    data () {
        return {
            
        }
    },
    methods: {
    }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.empty-box {
    display: flex;
    justify-content: center;
    align-items: center;
    height:100vh;
    width:100%;
}

.content{
    width: 240px;
    height: 400px;
    text-align: center;
}
</style>
