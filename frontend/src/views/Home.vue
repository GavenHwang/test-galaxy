<script setup>
import { ref, onMounted } from 'vue'

const getImageUrl = (user) => {
  return new URL(`../assets/images/${user}.jpg`, import.meta.url).href
}

// 添加一些统计数据示例
const statsData = ref([
  { title: '系统用户', value: '1', icon: 'User', color: '#c8232c' },
  { title: '项目数量', value: '3', icon: 'Grid', color: '#67c23a' },
  { title: '环境配置', value: '3', icon: 'Setting', color: '#e6a23c' },
  { title: '组件版本', value: '46', icon: 'Box', color: '#f56c6c' },
])
</script>

<template>
  <div class="home">
    <div class="welcome-section">
      <h1 class="welcome-title">欢迎使用 Galaxy 平台</h1>
      <p class="welcome-subtitle">高性能计算环境管理系统</p>
    </div>

    <div class="stats-grid">
      <div 
        v-for="(stat, index) in statsData" 
        :key="index" 
        class="stat-card"
        :style="{ borderLeftColor: stat.color }"
      >
        <div class="stat-content">
          <div class="stat-info">
            <h3 class="stat-title">{{ stat.title }}</h3>
            <p class="stat-value" :style="{ color: stat.color }">{{ stat.value }}</p>
          </div>
          <div class="stat-icon" :style="{ backgroundColor: stat.color + '20' }">
            <el-icon :size="32" :color="stat.color">
              <component :is="stat.icon" />
            </el-icon>
          </div>
        </div>
      </div>
    </div>

    <div class="quick-actions">
      <h2 class="section-title">快捷操作</h2>
      <div class="action-grid">
        <el-button type="primary" plain size="large" @click="$router.push('/env/info')">
          <el-icon><View /></el-icon>
          查看环境
        </el-button>
        <el-button type="success" plain size="large" @click="$router.push('/env/version')">
          <el-icon><Document /></el-icon>
          组件版本
        </el-button>
        <el-button type="warning" plain size="large" @click="$router.push('/env/compare')">
          <el-icon><Connection /></el-icon>
          版本对比
        </el-button>
        <el-button type="info" plain size="large" @click="$router.push('/user')">
          <el-icon><User /></el-icon>
          用户管理
        </el-button>
      </div>
    </div>
  </div>
</template>

<style scoped lang="less">
.home {
  width: 100%;
  height: 100%;
  padding: 24px;
  background-color: #f0f2f5;
  min-height: calc(100vh - 180px);
}

.welcome-section {
  background: #ffffff;
  padding: 40px;
  border-radius: 12px;
  margin-bottom: 32px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);

  .welcome-title {
    font-size: 36px;
    font-weight: 700;
    color: #d9232c;
    margin: 0 0 12px 0;
  }

  .welcome-subtitle {
    font-size: 18px;
    color: #666;
    margin: 0;
  }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.stat-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 24px;
  border-left: 4px solid;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  }

  .stat-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .stat-info {
    flex: 1;
  }

  .stat-title {
    font-size: 14px;
    color: #7f8c8d;
    margin: 0 0 8px 0;
    font-weight: 500;
  }

  .stat-value {
    font-size: 32px;
    font-weight: 700;
    margin: 0;
  }

  .stat-icon {
    width: 64px;
    height: 64px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.quick-actions {
  background: #ffffff;
  padding: 32px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);

  .section-title {
    font-size: 20px;
    font-weight: 600;
    color: #333;
    margin: 0 0 24px 0;
  }

  .action-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;

    .el-button {
      height: 56px;
      font-size: 16px;
      border-radius: 12px;
      font-weight: 500;
      transition: all 0.3s ease;

      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      }

      .el-icon {
        margin-right: 8px;
      }
    }
  }
}

.user {
  width: 100%;
  height: 100%;
  padding: 0px;
}
</style>
