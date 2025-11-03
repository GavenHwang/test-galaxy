<template>
    <el-aside :width="width">
        <el-menu
            background-color="#ffffff"
            text-color="#303133"
            active-text-color="#d9232c"
            :collapse="isCollapse"
            :collapse-transition="false"
            :default-active="activeMenu"
        >
            <h3 v-show="!isCollapse" class="sidebar-title">高性能计算</h3>
            <h3 v-show="isCollapse" class="sidebar-title-collapsed">计算</h3>
            <template v-for="item in list" :key="item.path">
                <!-- 没有子菜单的项 -->
                <el-menu-item 
                    v-if="!item.children || item.children.length === 0"
                    :index="item.path"
                    @click="handleMenu(item)"
                >
                    <component class="icons" :is="item.icon"></component>
                    <span>{{ item.label }}</span>
                </el-menu-item>
                
                <!-- 有子菜单的项 -->
                <el-sub-menu
                    v-else
                    :index="item.path"
                >
                    <template #title>
                        <component class="icons" :is="item.icon"></component>
                        <span>{{ item.label }}</span>
                    </template>
                    <el-menu-item-group>
                        <el-menu-item 
                            v-for="subItem in item.children"
                            :key="subItem.path"
                            :index="subItem.path"
                            @click="handleMenu(subItem)"
                        >
                            <component class="icons" :is="subItem.icon"></component>
                            <span>{{ subItem.label }}</span>
                        </el-menu-item>
                    </el-menu-item-group>
                </el-sub-menu>
            </template>
        </el-menu>
    </el-aside>
</template>

<script setup lang="ts">
import { computed, ref,getCurrentInstance,onMounted } from 'vue'
// 使用pinia
import {useAllDataStore} from '@/stores'
import { useRouter, useRoute } from 'vue-router'

// 数据
const list = ref([])

const {proxy} = getCurrentInstance()
const store = useAllDataStore()
// 定义是否折叠
const isCollapse = computed(()=>store.state.isCollapse)
// 定义折叠宽度
const width = computed(()=>store.state.isCollapse ? '64px' : "180px")
const router = useRouter()
const route = useRoute()
const activeMenu = computed(()=>route.path)
// 方法
const handleMenu = (item)=>{
    router.push(item.path)
    store.selectMenu(item)
}

const fetchMenuData = async () => {
    list.value =  await proxy.$api.getMenuData()
}
// 初始化加载数据
onMounted(() => {
  fetchMenuData();
});
</script>

<style lang="less" scoped>
@import '@/assets/less/variables.less';

.icons {
    width: 18px;
    height: 18px;
    margin-right: 5px;
}
.el-menu {
    border-right: none;
    
    .sidebar-title {
        line-height: 48px;
        color: @text-white;
        text-align: center;
        font-size: @font-size-md;
        font-weight: 600;
    }
    
    .sidebar-title-collapsed {
        line-height: 48px;
        color: @text-white;
        text-align: center;
        font-size: @font-size-base;
        font-weight: 600;
    }
}

:deep(.el-menu-item) {
    transition: @transition-base;
    border-left: 4px solid transparent;
    padding-left: @spacing-lg;
    height: 42px;
    line-height: 42px;
}

:deep(.el-menu-item:hover) {
    background-color: #f5f5f5 !important;
    color: @primary-color;
}

:deep(.el-menu-item.is-active) {
    background-color: @bg-white !important;
    border-left-color: @primary-color;
    color: @primary-color;
    font-weight: 500;
}

:deep(.el-sub-menu__title) {
    height: 42px;
    line-height: 42px;
    border-left: 4px solid transparent;
    padding-left: @spacing-lg !important;
}

:deep(.el-sub-menu__title:hover) {
    background-color: #f5f5f5 !important;
}

// 子菜单项样式
:deep(.el-menu-item-group__title) {
    padding: 0;
    height: 0;
    line-height: 0;
    overflow: hidden;
}

.el-aside {
    height: 100%;
    background-color: @bg-white;
    box-shadow: 2px 0 6px rgba(0, 21, 41, 0.08);
}
</style>
