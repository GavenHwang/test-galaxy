<template>
  <div class="env-container">
    <!-- 头部布局 -->
    <div class="header">
      <!-- 左侧：级联选择器（带默认值） -->
      <div class="cascader-container">
        <el-cascader
          v-model="selectedEnv"
          :options="allEnvInfos"
          placeholder="请选择环境"
          clearable
          style="width: 240px"
           @change="handleEnvChange"
        />
      </div>

      <!-- 右侧：下拉选择器（刷新时间） + 刷新按钮 -->
    <div class="actions">
        <div style="width: 200px; margin-right: 10px">
            <el-input
            placeholder="搜索组件..."
            v-model="searchQuery"
            clearable
            @input="handleSearch"
            >
            <template #prefix>
                <el-icon><search /></el-icon>
            </template>
            </el-input>
        </div>
        <el-button
          type="danger"
          :icon="Refresh"
          @click="fetchEnvVersion"
          style="margin-right: 10px"
        >
          刷新
        </el-button>
 
        <el-button
          type="danger"
          :icon="RefreshRight"
          @click="handleForceRefresh"
        >
          强制刷新
        </el-button>
      </div>
    </div>

    <!-- 表格（带分页） -->
    <div class="table-container">
      <el-table
        :data="tableData"
        border
        style="width: 100%"
        v-loading="loading"
        header-align="center"         
      >
        <el-table-column prop="component" label="组件名称" width="200" />
        <el-table-column prop="version" label="版本信息" />
        <el-table-column prop="ctime" label="开始时间" />
        <el-table-column prop="time" label="更新时间"  />
        <el-table-column prop="compare" label="master差异" width="150"/>
        <el-table-column label="历史版本" width="200" align="center" >
          <template #default="{ row }">
            <el-button
              type="text"
              @click="handleViewHistory(row.component)"
            >
              查看历史
            </el-button>
          </template>
        </el-table-column>
      </el-table>

        <!-- 分页 -->
        <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[5, 10, 20, 50]"
        :pager-count="5"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        style="justify-content: flex-end;"
        />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, getCurrentInstance } from 'vue';
import { Refresh, RefreshRight } from '@element-plus/icons-vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const {proxy} = getCurrentInstance()

// 级联选择器数据（带默认值）
const selectedEnv = ref([]);
const allEnvInfos = ref([]);

// 表格数据
const tableData = ref([]);

const searchQuery = ref('');

// 分页
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);
const loading = ref(false);

// 获取所有的项目名称和环境
const fetchProjectName = async () => {
  const projectData = await proxy.$api.getProjectEnv()
  for (let i = 0; i < projectData.length; i++) {
    if (i === 0 ){ 
      selectedEnv.value.push(projectData[i].name)
    }
    const envs = ref([])
    if (projectData[i].envs.length === 0) {
      continue
    }
    for (let j = 0; j < projectData[i].envs.length; j++) {
      if (j === 0 ){ 
        selectedEnv.value.push(projectData[i].envs[j].name)
      }
      envs.value.push({id: projectData[i].envs[j].id, value: projectData[i].envs[j].name, label: projectData[i].envs[j].name})
    }
    allEnvInfos.value.push({
                    value: projectData[i].name,
                    label: projectData[i].name,
                    children: envs.value,
                  })
  }
  fetchEnvVersion();
};

const handleEnvChange = (value) => {
  currentPage.value = 1;
  selectedEnv.value = value;
  fetchEnvVersion();
};
// 获取环境版本信息
const fetchEnvVersion = async () => {
  tableData.value = [];
  const requestData = ref({project_name: selectedEnv.value[0], env_name: selectedEnv.value[1],page: currentPage.value, size: pageSize.value})
  const versionData = await proxy.$api.getVersionData(requestData.value)
  for (let i = 0; i < versionData.versions.length; i++) {
    tableData.value.push({
      component: versionData.versions[i].component.name,
      version: versionData.versions[i].version,
      time: versionData.versions[i].updated_at,
      compare: versionData.versions[i].compare,
      ctime: versionData.versions[i].created_at,
      id: versionData.versions[i].id
    });
  };
  total.value = versionData.total
};

// 强制刷新
const handleForceRefresh = () => {
  loading.value = true;
  const requestData = ref({project_name: selectedEnv.value[0], env_name: selectedEnv.value[1]})
  proxy.$api.refreshVersion(requestData.value).then(() => {
    loading.value = false;
    fetchEnvVersion();
  });
};

// 查看历史版本（跳转到新页面）
const handleViewHistory = (componentName) => {
  router.push(
    `/env/history/${selectedEnv.value[0].toLocaleLowerCase()}-${selectedEnv.value[1].toLocaleLowerCase()}-${componentName}`,
  );
};

// 分页变化
const handleSizeChange = (val) => {
  pageSize.value = val;
  fetchEnvVersion();
};

const handleCurrentChange = (val) => {
  currentPage.value = val;
  fetchEnvVersion();
};

const handleSearch = () => {
  console.log('搜索组件:', searchQuery.value);
  currentPage.value = 1; // 搜索时重置到第一页
  fetchTableData();
};

// 模拟初始化加载数据
onMounted(() => {
  fetchProjectName();
});
</script>

<style scoped lang="less">
@import '@/assets/less/variables.less';

.env-container {
  padding: @spacing-xxl;
  background-color: @bg-white;
  border-radius: @border-radius-large;
  box-shadow: @box-shadow-base;
  min-height: calc(100vh - 180px);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: @spacing-xl;
  padding-bottom: @spacing-lg;
  border-bottom: 1px solid #f0f0f0;
}

.cascader-container {
  flex: 1;
}

.actions {
  display: flex;
  align-items: center;
  gap: @spacing-md;
  
  .el-button {
    border-radius: @border-radius-medium;
    height: 36px;
    font-weight: 500;
  }
}

.table-container {
  margin-top: @spacing-xl;
}

:deep(.el-table) {
  border-radius: @border-radius-large;
  overflow: hidden;
  
  .el-table__header th {
    background-color: @bg-light;
    font-weight: 600;
    color: @text-primary;
  }
  
  .el-table__row {
    transition: @transition-base;
    
    &:hover {
      background-color: @bg-hover;
    }
  }
  
  .el-button--text {
    color: @primary-color;
    transition: @transition-base;
    
    &:hover {
      color: @primary-hover;
      background-color: @primary-shadow;
    }
  }
}

:deep(.el-pagination) {
  margin-top: @spacing-xl;
  padding: @spacing-lg 0;
}

:deep(.el-cascader) {
  .el-input__wrapper {
    border-radius: @border-radius-medium;
  }
}

:deep(.el-input) {
  .el-input__wrapper {
    border-radius: @border-radius-medium;
  }
}
</style>