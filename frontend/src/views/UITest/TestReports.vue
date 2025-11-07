<template>
  <div class="page-container">
    <!-- 搜索筛选区 -->
    <div class="page-header">
      <div></div>
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="测试单ID">
          <el-input 
            v-model="searchForm.test_task_id" 
            placeholder="请输入测试单ID" 
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 数据表格 -->
    <el-table
      :data="tableData"
      stripe
      border
      v-loading="loading"
      style="width: 100%"
    >
      <el-table-column prop="id" label="报告ID" width="100" />
      <el-table-column prop="test_task_id" label="测试单ID" width="120" />
      <el-table-column label="执行结果" min-width="350">
        <template #default="{ row }">
          <div style="display: flex; align-items: center; gap: 10px">
            <el-tag type="success" size="small">通过 {{ row.passed_cases }}</el-tag>
            <el-tag type="danger" size="small">失败 {{ row.failed_cases }}</el-tag>
            <el-tag type="info" size="small">跳过 {{ row.skipped_cases }}</el-tag>
            <el-tag type="warning" size="small">总计 {{ row.total_cases }}</el-tag>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="通过率" width="200" align="center">
        <template #default="{ row }">
          <el-progress 
            :percentage="Math.round(row.pass_rate)" 
            :status="row.pass_rate >= 90 ? 'success' : (row.pass_rate >= 70 ? 'warning' : 'exception')"
          />
        </template>
      </el-table-column>
      <el-table-column prop="duration" label="执行时长" width="150" align="center">
        <template #default="{ row }">
          {{ formatDuration(row.duration) }}
        </template>
      </el-table-column>
      <el-table-column prop="start_time" label="开始时间" width="200" />
      <el-table-column prop="end_time" label="结束时间" width="200" />
      <el-table-column prop="created_time" label="创建时间" width="200" />
      <el-table-column label="操作" width="100" fixed="right" align="center">
        <template #default="{ row }">
          <div class="action-buttons">
            <el-tooltip content="查看详情" placement="top">
              <el-button 
                text 
                type="primary" 
                @click="handleView(row)"
                :icon="View"
              />
            </el-tooltip>
            <el-tooltip content="删除" placement="top">
              <el-button 
                text 
                type="danger" 
                @click="handleDelete(row)"
                :icon="Delete"
              />
            </el-tooltip>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页组件 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import { View, Delete } from '@element-plus/icons-vue'
import { getTestReports, deleteTestReport } from '@/api/uitest'

const router = useRouter()

// 表格数据
const tableData = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const loading = ref(false)

// 搜索表单
const searchForm = reactive({
  test_task_id: ''
})

// 格式化时长
const formatDuration = (seconds) => {
  if (!seconds) return '-'
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)
  
  if (hours > 0) {
    return `${hours}时${minutes}分${secs}秒`
  } else if (minutes > 0) {
    return `${minutes}分${secs}秒`
  } else {
    return `${secs}秒`
  }
}

// 加载表格数据
const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    if (searchForm.test_task_id) {
      params.test_task_id = parseInt(searchForm.test_task_id)
    }
    
    const data = await getTestReports(params)
    tableData.value = data.items || []
    total.value = data.total || 0
  } catch (error) {
    console.error('加载数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  loadData()
}

// 重置
const handleReset = () => {
  searchForm.test_task_id = ''
  currentPage.value = 1
  loadData()
}

// 分页相关
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  loadData()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  loadData()
}

// 查看报告
const handleView = (row) => {
  router.push(`/ui-test/test-reports/${row.id}`)
}

// 删除报告
const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确认删除测试报告 (ID: ${row.id}) 吗？删除后将无法恢复。`,
    '警告',
    {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await deleteTestReport(row.id)
      ElMessage.success('删除成功')
      loadData()
    } catch (error) {
      console.error('删除失败:', error)
    }
  }).catch(() => {
    // 用户取消删除
  })
}

// 页面加载
onMounted(() => {
  loadData()
})
</script>

<style scoped lang="less">
@import '@/assets/less/variables.less';

.page-container {
  // 使用全局样式，无需重复定义
}
</style>
