<template>
    <div class="header">
        <div class="l-content">
            <el-button size="small" @click="handleCollapse">
                <component class="icons" is="menu"></component>
            </el-button>
            <el-breadcrumb separator="/" class="bread">
                <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            </el-breadcrumb>
        </div>
        <div class="r-content">
            <el-dropdown>
                <span class="el-dropdown-link">
                    <img :src="getImageUrl('user')" class="user"/>
                </span>
                <template #dropdown>
                    <el-dropdown-menu>
                        <el-dropdown-item>个人中心</el-dropdown-item>
                        <el-dropdown-item @click="handleExit">退出</el-dropdown-item>
                    </el-dropdown-menu>
                </template>
            </el-dropdown>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { ref,getCurrentInstance} from 'vue'
    import { useRouter, useRoute } from 'vue-router'
    // 使用pinia
    import {useAllDataStore} from '@/stores'

    const {proxy} = getCurrentInstance()
    const router = useRouter()
    // 退出登录
    const handleExit = async ()=>{
        await proxy.$api.logout()
        localStorage.removeItem('token')
        
        // 清除tags只保留首页
        const store = useAllDataStore()
        store.initTags()
        router.push('/login')
    }
    // 数据
    const getImageUrl = (user)=>{
        return new URL(`../assets/images/${user}.png`, import.meta.url).href
    }
    const store = useAllDataStore()
    // 方法
    function handleCollapse(){
        console.log(store)
        store.state.isCollapse = !store.state.isCollapse
    }
</script>

<style lang="less" scoped>
.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    height: 100%;
    background-color: #304156; // 添加背景色以匹配侧边栏
}
 
.icons {
    width: 20px;
    height: 20px;
    color: #fff; // 确保图标颜色与背景对比明显
}
 
.r-content {
    .user {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        object-fit: cover; // 防止图片变形
    }
}
 
.l-content {
    display: flex;
    align-items: center;
    .el-button {
        margin-right: 20px;
        background-color: transparent; // 按钮透明化，融合背景
        border: none;
        &:hover {
            background-color: rgba(255, 255, 255, 0.1); // 悬停效果
        }
    }
}
 
// 面包屑文字颜色（使用 :deep 穿透 scoped）
:deep(.bread .el-breadcrumb__inner) {
    color: #fff !important;
    cursor: pointer !important;
}
</style>