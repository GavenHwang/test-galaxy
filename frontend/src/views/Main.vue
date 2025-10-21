<script setup>
import CommonAside from '@/components/CommonAside.vue';
import CommonHeader from '@/components/CommonHeader.vue';
import CommonTag from '@/components/CommonTag.vue';
</script>

<template>
  <div class="common-layout">
    <el-container class="lay-container">
      <!-- 自定义左侧组件 -->
      <common-aside/>
      <el-container>
        <!-- 右侧上方组件 -->
        <el-header class="el-header">
          <common-header/>
        </el-header>
        <common-tag/>
        <!-- 右侧下方组件 -->
        <el-main class="right-main">
          <router-view></router-view>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<style scoped lang="less">
.common-layout, .lay-container {
  height: 100%;
}

.el-header {
  background-color: #304156;
}


</style>
