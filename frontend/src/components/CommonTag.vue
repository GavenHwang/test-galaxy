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
@import '@/assets/less/variables.less';

.tags {
  margin: 0;
  padding: @spacing-md @spacing-xl;
  background-color: @bg-white;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  align-items: center;
  overflow-x: auto;
  overflow-y: hidden;
  white-space: nowrap;
  
  &::-webkit-scrollbar {
    height: 4px;
  }
  
  &::-webkit-scrollbar-track {
    background: transparent;
  }
  
  &::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 2px;
    
    &:hover {
      background: #a8a8a8;
    }
  }
}

.el-tag {
  margin-right: @spacing-sm;
  cursor: pointer;
  border-radius: @border-radius-base;
  transition: @transition-base;
  font-size: @font-size-sm;
  padding: 0 @spacing-md;
  height: 28px;
  line-height: 28px;
  background-color: @bg-white;
  color: @primary-color;
  border-color: @primary-color;
  
  &:hover {
    transform: translateY(-1px);
  }
  
  &.is-dark {
    background-color: @primary-color;
    border-color: @primary-color;
    color: @text-white;
    box-shadow: 0 2px 4px @primary-shadow;
  }
}
</style>