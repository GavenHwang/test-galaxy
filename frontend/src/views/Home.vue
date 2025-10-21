<script setup>
const getImageUrl = (user) => {
  return new URL(`../assets/images/${user}.jpg`, import.meta.url).href
}
</script>

<template>
  <div class="home">
    首页
  </div>
</template>

<style scoped lang="less">
.home {
  width: 100%;
  height: 100%;
  padding: 0px;
}

.user {
  width: 100%;
  height: 100%;
  padding: 0px;
}
</style>
