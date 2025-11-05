<template>
    <div class="header">
        <div class="l-content">
            <el-button size="small" @click="handleCollapse">
                <el-icon class="icons">
                    <Fold v-if="!isCollapse" />
                    <Expand v-else />
                </el-icon>
            </el-button>
            <el-breadcrumb separator="/" class="bread">
                <el-breadcrumb-item 
                    v-for="(item, index) in breadcrumbList" 
                    :key="index"
                    :to="item.path ? { path: item.path } : undefined"
                >
                    {{ item.label }}
                </el-breadcrumb-item>
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
    import { ref, getCurrentInstance, computed } from 'vue'
    import { useRouter, useRoute } from 'vue-router'
    import { Fold, Expand } from '@element-plus/icons-vue'
    // 使用pinia
    import {useAllDataStore} from '@/stores'

    const {proxy} = getCurrentInstance()
    const router = useRouter()
    const route = useRoute()
    const store = useAllDataStore()
    
    // 路由元信息映射
    const routeMetaMap = {
        '/home': { label: '首页' },
        '/env/info': { label: '环境信息', parent: '环境' },
        '/env/version': { label: '组件版本', parent: '环境' },
        '/env/compare': { label: '版本比较', parent: '环境' },
        '/env/detail': { label: '环境详情', parent: '环境' },
        '/env/history': { label: '历史版本', parent: '环境' },
        '/user': { label: '用户管理' },
        '/ui-test/elements': { label: '页面元素', parent: 'UI测试' },
        '/ui-test/test-users': { label: '测试用户管理', parent: 'UI测试' },
        '/ui-test/test-cases': { label: '测试用例', parent: 'UI测试' },
        '/ui-test/test-suites': { label: '测试套件', parent: 'UI测试' },
        '/ui-test/test-tasks': { label: '测试单', parent: 'UI测试' },
        '/ui-test/test-reports': { label: '测试报告', parent: 'UI测试' },
    }
    
    // 动态生成面包屑
    const breadcrumbList = computed(() => {
        const path = route.path
        const breadcrumbs = [{ label: '首页', path: '/home' }]
        
        // 如果不是首页，添加当前页面的面包屑
        if (path !== '/home') {
            // 处理带参数的路由（如 /env/detail/123）
            let matchedPath = path
            Object.keys(routeMetaMap).forEach(key => {
                if (path.startsWith(key)) {
                    matchedPath = key
                }
            })
            
            const meta = routeMetaMap[matchedPath]
            if (meta) {
                // 如果有父级，先添加父级
                if (meta.parent) {
                    breadcrumbs.push({ label: meta.parent, path: undefined })
                }
                // 添加当前页
                breadcrumbs.push({ label: meta.label, path: undefined })
            }
        }
        
        return breadcrumbs
    })
    // 退出登录
    const handleExit = async ()=>{
        await proxy.$api.logout()
        localStorage.removeItem('token')
        
        // 清除tags只保留首页
        store.initTags()
        router.push('/login')
    }
    // 数据
    const getImageUrl = (user)=>{
        return new URL(`../assets/images/${user}.png`, import.meta.url).href
    }
    // 获取折叠状态
    const isCollapse = computed(() => store.state.isCollapse)
    // 方法
    function handleCollapse(){
        console.log(store)
        store.state.isCollapse = !store.state.isCollapse
    }
</script>

<style lang="less" scoped>
@import '@/assets/less/variables.less';

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    height: 100%;
    background: @bg-white;
    padding: 0 @spacing-xl;
    box-shadow: @box-shadow-base;
}
 
.icons {
    width: 20px;
    height: 20px;
    color: @text-primary;
}
 
.r-content {
    .user {
        width: 40px;
        height: 40px;
        border-radius: @border-radius-round;
        object-fit: cover;
        transition: @transition-base;
        cursor: pointer;
    }
}
 
.l-content {
    display: flex;
    align-items: center;
    .el-button {
        margin-right: @spacing-xl;
        background-color: @bg-white;
        border: 1px solid @border-base;
        color: @text-primary;
        transition: @transition-base;
        &:hover {
            background-color: @bg-hover;
            border-color: @primary-color;
            color: @primary-color;
        }
    }
}
 
// 面包屑文字颜色(使用 :deep 穿透 scoped)
:deep(.bread .el-breadcrumb__inner) {
    color: @text-primary !important;
    cursor: pointer !important;
    font-weight: 500;
}

:deep(.bread .el-breadcrumb__separator) {
    color: @text-placeholder !important;
}
</style>