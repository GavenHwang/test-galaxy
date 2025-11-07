<template>
  <div class="page-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div>
        <el-button type="primary" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          新建用例
        </el-button>
        <el-dropdown @command="handleBatchCommand" style="margin-left: 10px">
          <el-button>
            批量操作<el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="activate">批量激活</el-dropdown-item>
              <el-dropdown-item command="disable">批量禁用</el-dropdown-item>
              <el-dropdown-item command="delete">批量删除</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="用例名称">
          <el-input 
            v-model="searchForm.name" 
            placeholder="请输入用例名称" 
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="所属模块">
          <el-select 
            v-model="searchForm.module" 
            placeholder="请选择模块" 
            clearable
            filterable
          >
            <el-option 
              v-for="item in moduleOptions" 
              :key="item" 
              :label="item" 
              :value="item"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-select 
            v-model="searchForm.priority" 
            placeholder="请选择优先级" 
            clearable
          >
            <el-option label="高" value="高" />
            <el-option label="中" value="中" />
            <el-option label="低" value="低" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select 
            v-model="searchForm.status" 
            placeholder="请选择状态" 
            clearable
          >
            <el-option label="草稿" value="草稿" />
            <el-option label="激活" value="激活" />
            <el-option label="禁用" value="禁用" />
            <el-option label="归档" value="归档" />
          </el-select>
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
      @selection-change="handleSelectionChange"
      style="width: 100%"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column prop="name" label="用例名称" min-width="300" show-overflow-tooltip />
      <el-table-column prop="priority" label="优先级" width="100" align="center">
        <template #default="{ row }">
          <el-tag 
            :type="row.priority === '高' ? 'danger' : row.priority === '中' ? 'warning' : 'info'"
            size="small"
          >
            {{ row.priority }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag 
            :type="getStatusType(row.status)"
            size="small"
          >
            {{ row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="module" label="所属模块" width="150" />
      <el-table-column label="标签" width="250">
        <template #default="{ row }">
          <el-tag 
            v-for="tag in row.tags" 
            :key="tag" 
            size="small" 
            style="margin-right: 5px"
          >
            {{ tag }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="执行统计" width="150" align="center">
        <template #default="{ row }">
          <div>
            <div>共{{ row.execution_count }}次</div>
            <div v-if="row.last_execution_status" style="font-size: 12px; color: #909399">
              最近：<el-tag size="small" :type="row.last_execution_status === '通过' ? 'success' : 'danger'">
                {{ row.last_execution_status }}
              </el-tag>
            </div>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="created_by" label="创建人" width="120" />
      <el-table-column prop="created_time" label="创建时间" width="200" />
      <el-table-column label="操作" width="160" fixed="right" align="center">
        <template #default="{ row }">
          <div class="action-buttons">
            <el-tooltip content="查看" placement="top">
              <el-button 
                text 
                type="primary" 
                @click="handleView(row)"
                :icon="View"
              />
            </el-tooltip>
            <el-tooltip content="编辑" placement="top">
              <el-button 
                text 
                type="primary" 
                @click="handleEdit(row)"
                :icon="Edit"
              />
            </el-tooltip>
            <el-tooltip content="复制" placement="top">
              <el-button 
                text 
                type="primary" 
                @click="handleCopy(row)"
                :icon="CopyDocument"
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
import { Plus, ArrowDown, View, Edit, CopyDocument, Delete } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import {
  getTestCases,
  deleteTestCase,
  copyTestCase,
  batchUpdateCaseStatus,
  getModules
} from '@/api/uitest'
import { useAutoSearch } from '@/composables/useAutoSearch'

const router = useRouter()

// 表格数据
const tableData = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const loading = ref(false)
const selectedRows = ref([])

// 搜索表单
const searchForm = reactive({
  name: '',
  module: '',
  priority: '',
  status: ''
})

// 选项列表
const moduleOptions = ref([])

// 获取状态类型
const getStatusType = (status) => {
  const typeMap = {
    '草稿': 'info',
    '激活': 'success',
    '禁用': 'warning',
    '归档': 'danger'
  }
  return typeMap[status] || 'info'
}

// 加载表格数据
const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      ...searchForm
    }
    
    // 过滤空值
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null) {
        delete params[key]
      }
    })
    
    // 注意：响应拦截器在 code===200 时直接返回 data 字段
    const data = await getTestCases(params)
    tableData.value = data.items || []
    total.value = data.total || 0
  } catch (error) {
    console.error('加载数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 加载模块选项
const loadModules = async () => {
  try {
    const modules = await getModules()
    moduleOptions.value = modules || []
  } catch (error) {
    console.error('加载模块失败:', error)
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  loadData()
}

// 重置
const handleReset = () => {
  searchForm.name = ''
  searchForm.module = ''
  searchForm.priority = ''
  searchForm.status = ''
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

// 多选处理
const handleSelectionChange = (selection) => {
  selectedRows.value = selection
}

// 新建用例
const handleCreate = () => {
  router.push('/ui-test/test-cases/new')
}

// 查看用例
const handleView = (row) => {
  router.push(`/ui-test/test-cases/${row.id}`)
}

// 编辑用例
const handleEdit = (row) => {
  router.push(`/ui-test/test-cases/${row.id}/edit`)
}

// 复制用例
const handleCopy = (row) => {
  ElMessageBox.confirm(
    '是否复制该测试用例？',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    }
  ).then(async () => {
    try {
      await copyTestCase(row.id)
      ElMessage.success('复制成功')
      loadData()
    } catch (error) {
      console.error('复制失败:', error)
    }
  }).catch(() => {})
}

// 删除用例
const handleDelete = (row) => {
  ElMessageBox.confirm(
    '删除后不可恢复，是否确认删除？',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await deleteTestCase(row.id, false)
      ElMessage.success('删除成功')
      loadData()
    } catch (error) {
      console.error('删除失败:', error)
      // 如果错误消息包含"引用"，询问是否强制删除
      const errorMsg = error.message || error
      if (errorMsg.includes('引用')) {
        ElMessageBox.confirm(
          errorMsg + '，是否强制删除？',
          '警告',
          {
            confirmButtonText: '强制删除',
            cancelButtonText: '取消',
            type: 'warning'
          }
        ).then(async () => {
          try {
            await deleteTestCase(row.id, true)
            ElMessage.success('删除成功')
            loadData()
          } catch (err) {
            console.error('强制删除失败:', err)
          }
        }).catch(() => {})
      }
    }
  }).catch(() => {})
}

// 批量操作
const handleBatchCommand = (command) => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请先选择用例')
    return
  }
  
  const caseIds = selectedRows.value.map(row => row.id)
  
  if (command === 'activate') {
    batchUpdateStatus(caseIds, '激活')
  } else if (command === 'disable') {
    batchUpdateStatus(caseIds, '禁用')
  } else if (command === 'delete') {
    batchDelete(caseIds)
  }
}

// 批量更新状态
const batchUpdateStatus = async (caseIds, status) => {
  try {
    await batchUpdateCaseStatus(caseIds, status)
    ElMessage.success('批量更新成功')
    loadData()
  } catch (error) {
    console.error('批量更新失败:', error)
  }
}

// 批量删除
const batchDelete = (caseIds) => {
  ElMessageBox.confirm(
    `确认删除选中的${caseIds.length}个用例吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    let successCount = 0
    for (const id of caseIds) {
      try {
        await deleteTestCase(id, true)
        successCount++
      } catch (error) {
        console.error('删除失败:', error)
      }
    }
    ElMessage.success(`成功删除${successCount}个用例`)
    loadData()
  }).catch(() => {})
}

// 页面加载
onMounted(() => {
  loadData()
  loadModules()
})

// 配置自动搜索
useAutoSearch({
  searchForm,
  currentPage,
  onSearch: loadData,
  inputFields: ['name'],                  // 输入框字段（防抖搜索）
  selectFields: ['module', 'priority', 'status'], // 下拉框字段（立即搜索）
  debounceDelay: 500                      // 防抖延迟 0.5秒
})
</script>

<style scoped lang="less">
@import '@/assets/less/variables.less';

.page-container {
  // 使用全局样式，无需重复定义
}
</style>
