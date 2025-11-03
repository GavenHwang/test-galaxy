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
}

// 选中状态的标签（dark 效果）
:deep(.el-tag.el-tag--dark) {
  background-color: @primary-color !important;
  border-color: @primary-color !important;
  color: @text-white !important;
  box-shadow: 0 2px 4px @primary-shadow;
}

// 确保关闭按钮样式生效
:deep(.el-tag__close) {
  color: @tag-close-color;
  transition: @transition-fast;
  
  &:hover {
    color: @text-white;
    background-color: @tag-close-hover;
  }
}

:deep(.el-tag--dark .el-tag__close) {
  color: rgba(255, 255, 255, 0.8);
  
  &:hover {
    color: @text-white;
    background-color: rgba(255, 255, 255, 0.2);
  }
}
</style>