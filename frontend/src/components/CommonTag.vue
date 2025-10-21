<template>
    <div class="tags">
        <el-tag
            v-for="(tag, index) in tags"
            :key="tag.path"
            :closable="tag.path != '/home'"
            :effect="route.path === tag.path ? 'dark' : 'plain'"
            @click="handleMenu(tag)"
            @close="handleClose(tag, index)"
        >
        {{tag.label}}
        </el-tag>
    </div>
</template>
<script setup>
    import {computed} from 'vue'
    import { useRoute,useRouter } from 'vue-router';
    import {useAllDataStore} from '@/stores'

    const route = useRoute()
    const router = useRouter()
    const store = useAllDataStore()
    const tags = computed(()=>store.state.tags)
    const handleMenu = (tag)=>{
        router.push(tag.path)
        store.selectMenu(tag)
    }
    const handleClose = (tag, index)=>{
        store.updateMenu(tag)
        // 如果点击关闭的tab不是当前页面，直接关闭
        if(tag.path !== route.path){
            return
        }else{
            store.selectMenu(tags.value[index -1])
            router.push(tags.value[index -1].path)
        }
    }
</script>
<style scoped lang="less">
.tags{
    margin: 20px 0 0 20px;
}
.el-tag{
    margin-right: 10px;
}
</style>