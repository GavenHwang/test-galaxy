<template>
  <div class="env-container">
    <!-- 头部：下拉框、按钮、搜索框 -->
    <div class="env-header" style="display: flex; justify-content: space-between; align-items: center; width: 100%; margin-bottom: 20px;">
      <!-- 左侧 -->
      <div style="display: flex; gap: 10px;">
        <el-dropdown split-button type="danger" @click="handleDropdownClick(selectedProject)">
          {{ selectedProject }}
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item
                v-for="item in projectName"
                :key="item"
                @click="handleDropdownClick(item)"
              >
                {{ item }}
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <el-button type="danger" @click="handleAddEnv" :disabled=true>新增环境</el-button>
      </div>

      <!-- 右侧 -->
      <div style="width: 200px;">
        <el-input
          placeholder="搜索环境..."
          v-model="searchQuery"
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><search /></el-icon>
          </template>
        </el-input>
      </div>
    </div>

    <!-- 表格 -->
    <el-table
        :data="tableData"
        border
        style="width: 100%; margin-bottom: 20px;"
        v-loading="loading"
    >
      <el-table-column prop="name" label="环境名称"  width="150"/>
      <el-table-column prop="domain" label="SCNET域名">
        <template #default="scope">
          <template v-if="scope.row.domain">
            <a 
              :href="scope.row.domain" 
              target="_blank" 
              class="domain-link"
            >
              {{ scope.row.domain }}
            </a>
          </template>
          <template v-else>
            <span class="empty-domain">暂无域名</span>
          </template>
        </template>
      </el-table-column>
            <el-table-column prop="ac_domain" label="AC域名">
        <template #default="scope">
          <template v-if="scope.row.ac_domain">
            <a 
              :href="scope.row.ac_domain" 
              target="_blank" 
              class="domain-link"
            >
              {{ scope.row.ac_domain }}
            </a>
          </template>
          <template v-else>
            <span class="empty-domain">暂无域名</span>
          </template>
        </template>
      </el-table-column>
      <el-table-column prop="updateTime" label="更新时间"  />
      <el-table-column prop="updater" label="更新人员"  />
      <el-table-column prop="needVersion" label="是否获取版本信息" width="200">
        <template #default="{ row }">
          <el-tag :type="row.needVersion ? 'success' : 'danger'">
            {{ row.needVersion ? '是' : '否' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column fixed="right" label="操作" width="300" align="center">
          <template #default="{ row }">
            <el-button type="danger" size="small" @click="handleDetail(row.id)">
              详细信息
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
    </el-table>

    <!-- 分页 -->
    <el-pagination
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :page-sizes="[5, 10, 20, 50]"
      :total="total"
      layout="total, sizes, prev, pager, next, jumper"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
      style="justify-content: flex-end;"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, getCurrentInstance } from 'vue';
import { Search } from '@element-plus/icons-vue';
import { useRouter } from 'vue-router'; // 用于跳转路由

const router = useRouter();

// 头部逻辑
const selectedProject = ref('');
const projectName = ref([]);
const searchQuery = ref('');

const handleDropdownClick = (item) => {
  selectedProject.value = item;
  fetchTableData(); // 切换项目时重新加载表格数据
};

const handleAddEnv = () => {
  console.log('新增环境');
};

const handleSearch = () => {
  console.log('搜索关键词:', searchQuery.value);
  currentPage.value = 1; // 搜索时重置到第一页
  fetchTableData();
};

// 表格逻辑
const tableData = ref([]);
const loading = ref(false);
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);
const {proxy} = getCurrentInstance()

// 获取所有的项目名称
const fetchProjectName = async () => {
  loading.value=true
  const projectData = await proxy.$api.getProjectName()
  for (let i = 0; i < projectData.length; i++) {
    projectName.value.push(projectData[i].name)
  }
  selectedProject.value = projectName.value[0]
  await fetchTableData()  
  loading.value = false
}

// 获取项目环境信息
const fetchTableData = async () => {
  tableData.value = [];
  const request_env_data = ref({
      project_name: selectedProject.value,
      page: currentPage.value,
      size: pageSize.value
    })
    const resData = await proxy.$api.getEnvData(request_env_data.value)
    const envData = resData.envs
    for (let i = 0; i < envData.length; i++) {
      tableData.value.push({
        "name": envData[i].name,
        "domain": envData[i].domain,
        "ac_domain": envData[i].ac_domain,
        "updateTime": envData[i].updated_at, 
        "updater": envData[i].user.username, 
        "needVersion": envData[i].need_version})
    }
    total.value = resData.total
  }

// 分页变化
const handleSizeChange = (val) => {
  pageSize.value = val;
  fetchTableData();
};

const handleCurrentChange = (val) => {
  currentPage.value = val;
  fetchTableData();
};

// 跳转到详情页
const handleDetail = (id) => {
  router.push(`/env/detail/${id}`);
};

// 初始化加载数据
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

.table-container {
  margin-top: @spacing-xl;
}

.domain-link {
  color: @primary-color;
  text-decoration: none;
  transition: @transition-base;
  border-bottom: 1px dashed @primary-color;
  
  &:hover {
    color: @primary-hover;
    border-bottom-color: @primary-hover;
  }
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
}

:deep(.el-pagination) {
  margin-top: @spacing-xl;
  padding: @spacing-lg 0;
}
</style>