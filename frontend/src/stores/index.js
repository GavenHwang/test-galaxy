// pinia的配置，组件之间的通信

import {defineStore} from 'pinia'
import {ref} from 'vue'

function initState() {
    return {
        isCollapse: false,
        tags: [
            {
                path: '/home',
                label: '首页',
                url: 'Home'
            }
        ],
        currentMenu: null
    }
}

export const useAllDataStore = defineStore('allData', () => {
    const state = ref(initState())

    // 添加tags
    function selectMenu(val) {
        if (val.path === '/home') {
            state.value.currentMenu = null
        } else {
            let index = state.value.tags.findIndex(item => item.path === val.path)
            index === -1 ? state.value.tags.push(val) : ''
        }
    }

    // 删除tags
    function updateMenu(val) {
        let index = state.value.tags.findIndex(item => item.path === val.path)
        state.value.tags.splice(index, 1)
    }
    // 初始化tags
    function initTags() {
        state.value.tags = [
            {
                path: '/home',
                label: '首页',
                url: 'Home'
            }
        ]
    }

    return {
        state,
        selectMenu,
        updateMenu,
        initTags
    }
})