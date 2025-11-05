<template>
  <div class="test-tasks-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item>UI测试</el-breadcrumb-item>
        <el-breadcrumb-item>测试单管理</el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <!-- 操作工具栏 -->
    <div class="toolbar">
      <el-button type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon>
        新建测试单
      </el-button>
    </div>

    <!-- 搜索筛选区 -->
    <div class="search-area">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="测试单名称">
          <el-input 
            v-model="searchForm.name" 
            placeholder="请输入测试单名称" 
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select 
            v-model="searchForm.status" 
            placeholder="请选择状态" 
            clearable
          >
            <el-option label="待执行" value="PENDING" />
            <el-option label="执行中" value="RUNNING" />
            <el-option label="已完成" value="COMPLETED" />
            <el-option label="已失败" value="FAILED" />
            <el-option label="已取消" value="CANCELLED" />
          </el-select>
        </el-form-item>
        <el-form-item label="环境">
          <el-input 
            v-model="searchForm.environment" 
            placeholder="请输入环境" 
            clearable
          />
        </el-form-item>
        <el-form-item label="创建人">
          <el-input 
            v-model="searchForm.created_by" 
            placeholder="请输入创建人" 
            clearable
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
      <el-table-column prop="name" label="测试单名称" width="250" show-overflow-tooltip />
      <el-table-column prop="environment" label="测试环境" width="120" />
      <el-table-column prop="status" label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)" size="small">
            {{ getStatusText(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="执行进度" width="200" align="center">
        <template #default="{ row }">
          <div v-if="row.total_cases > 0">
            <el-progress 
              :percentage="Math.round(row.progress * 100)" 
              :status="getProgressStatus(row.status)"
            />
            <div style="font-size: 12px; color: #909399; margin-top: 5px">
              {{ row.executed_cases }}/{{ row.total_cases }}
            </div>
          </div>
          <span v-else style="color: #909399">-</span>
        </template>
      </el-table-column>
      <el-table-column label="通过率" width="100" align="center">
        <template #default="{ row }">
          <span v-if="row.executed_cases > 0">
            {{ Math.round((row.passed_cases / row.executed_cases) * 100) }}%
          </span>
          <span v-else style="color: #909399">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="created_by" label="创建人" width="100" />
      <el-table-column prop="created_time" label="创建时间" width="180" />
      <el-table-column label="操作" width="300" fixed="right">
        <template #default="{ row }">
          <el-button 
            text 
            type="primary" 
            @click="handleView(row)"
          >
            查看
          </el-button>
          <el-button 
            text 
            type="success" 
            @click="handleExecute(row)"
            :disabled="row.status === 'RUNNING'"
          >
            执行
          </el-button>
          <el-button 
            text 
            type="warning" 
            @click="handleCancel(row)"
            :disabled="row.status !== 'RUNNING'"
          >
            取消
          </el-button>
          <el-button text type="primary" @click="handleEdit(row)">编辑</el-button>
          <el-button text type="danger" @click="handleDelete(row)">删除</el-button>
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

    <!-- 创建/编辑测试单对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="900px"
      @close="handleDialogClose"
    >
      <el-steps :active="currentStep" finish-status="success" align-center style="margin-bottom: 30px">
        <el-step title="基本信息" />
        <el-step title="执行配置" />
        <el-step title="选择测试内容" />
        <el-step title="确认提交" />
      </el-steps>

      <!-- 步骤1: 基本信息 -->
      <div v-show="currentStep === 0">
        <el-form :model="formData" :rules="formRules" ref="formRef" label-width="100px">
          <el-form-item label="测试单名称" prop="name">
            <el-input v-model="formData.name" placeholder="请输入测试单名称" />
          </el-form-item>
          <el-form-item label="测试单描述" prop="description">
            <el-input 
              v-model="formData.description" 
              type="textarea" 
              :rows="3"
              placeholder="请输入测试单描述" 
            />
          </el-form-item>
          <el-form-item label="测试环境" prop="environment">
            <el-input v-model="formData.environment" placeholder="请输入测试环境，如：测试环境、预生产环境" />
          </el-form-item>
        </el-form>
      </div>

      <!-- 步骤2: 执行配置 -->
      <div v-show="currentStep === 1">
        <el-form :model="formData.execute_config" label-width="120px">
          <el-form-item label="失败停止">
            <el-switch v-model="formData.execute_config.stop_on_failure" />
            <span style="margin-left: 10px; color: #909399; font-size: 12px">
              开启后，遇到用例失败将停止执行
            </span>
          </el-form-item>
          <el-form-item label="失败重试">
            <el-switch v-model="formData.execute_config.retry_on_failure" />
            <span style="margin-left: 10px; color: #909399; font-size: 12px">
              开启后，失败的用例将自动重试
            </span>
          </el-form-item>
          <el-form-item label="重试次数" v-if="formData.execute_config.retry_on_failure">
            <el-input-number 
              v-model="formData.execute_config.max_retry_times" 
              :min="1" 
              :max="5"
            />
          </el-form-item>
          <el-form-item label="执行超时">
            <el-input-number 
              v-model="formData.execute_config.timeout" 
              :min="60" 
              :max="3600"
            />
            <span style="margin-left: 10px; color: #909399; font-size: 12px">
              秒
            </span>
          </el-form-item>
          <el-form-item label="并发执行">
            <el-switch v-model="formData.execute_config.parallel" />
            <span style="margin-left: 10px; color: #909399; font-size: 12px">
              开启后，用例将并发执行
            </span>
          </el-form-item>
          <el-form-item label="并发数" v-if="formData.execute_config.parallel">
            <el-input-number 
              v-model="formData.execute_config.parallel_count" 
              :min="1" 
              :max="10"
            />
          </el-form-item>
        </el-form>
      </div>

      <!-- 步骤3: 选择测试内容 -->
      <div v-show="currentStep === 2">
        <el-tabs v-model="contentTab">
          <el-tab-pane label="按套件选择" name="suite">
            <el-transfer
              v-model="selectedSuites"
              :data="availableSuites"
              :titles="['可用套件', '已选套件']"
              :props="{ key: 'id', label: 'name' }"
              filterable
              filter-placeholder="请输入套件名称"
            />
          </el-tab-pane>
          <el-tab-pane label="按用例选择" name="case">
            <el-transfer
              v-model="selectedCases"
              :data="availableCases"
              :titles="['可用用例', '已选用例']"
              :props="{ key: 'id', label: 'name' }"
              filterable
              filter-placeholder="请输入用例名称"
            />
          </el-tab-pane>
        </el-tabs>
      </div>

      <!-- 步骤4: 确认提交 -->
      <div v-show="currentStep === 3">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="测试单名称">{{ formData.name }}</el-descriptions-item>
          <el-descriptions-item label="测试环境">{{ formData.environment }}</el-descriptions-item>
          <el-descriptions-item label="失败停止">{{ formData.execute_config.stop_on_failure ? '是' : '否' }}</el-descriptions-item>
          <el-descriptions-item label="失败重试">{{ formData.execute_config.retry_on_failure ? '是' : '否' }}</el-descriptions-item>
          <el-descriptions-item label="并发执行">{{ formData.execute_config.parallel ? '是' : '否' }}</el-descriptions-item>
          <el-descriptions-item label="执行超时">{{ formData.execute_config.timeout }}秒</el-descriptions-item>
          <el-descriptions-item label="选择套件数">{{ selectedSuites.length }}个</el-descriptions-item>
          <el-descriptions-item label="选择用例数">{{ selectedCases.length }}个</el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">{{ formData.description || '无' }}</el-descriptions-item>
        </el-descriptions>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button @click="handlePrevStep" v-if="currentStep > 0">上一步</el-button>
          <el-button type="primary" @click="handleNextStep" v-if="currentStep < 3">下一步</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitting" v-if="currentStep === 3">
            提交
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 查看测试单详情对话框 -->
    <el-dialog
      v-model="viewDialogVisible"
      title="测试单详情"
      width="1000px"
    >
      <div v-if="currentTask">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="测试单名称">{{ currentTask.name }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(currentTask.status)">
              {{ getStatusText(currentTask.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="测试环境">{{ currentTask.environment }}</el-descriptions-item>
          <el-descriptions-item label="创建人">{{ currentTask.created_by }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ currentTask.created_time }}</el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ currentTask.start_time || '-' }}</el-descriptions-item>
          <el-descriptions-item label="结束时间">{{ currentTask.end_time || '-' }}</el-descriptions-item>
          <el-descriptions-item label="执行进度">
            {{ currentTask.executed_cases }}/{{ currentTask.total_cases }}
          </el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">{{ currentTask.description || '无' }}</el-descriptions-item>
        </el-descriptions>
        
        <el-divider content-position="left">执行结果</el-divider>
        
        <div style="display: flex; justify-content: space-around; padding: 20px 0">
          <el-statistic title="总用例数" :value="currentTask.total_cases" />
          <el-statistic title="已执行" :value="currentTask.executed_cases" />
          <el-statistic title="通过" :value="currentTask.passed_cases" value-style="color: #67C23A" />
          <el-statistic title="失败" :value="currentTask.failed_cases" value-style="color: #F56C6C" />
        </div>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="viewDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { 
  getTestTasks,
  createTestTask,
  updateTestTask,
  deleteTestTask,
  getTestTaskDetail,
  executeTestTask,
  cancelTestTask,
  getTestSuites,
  getTestCases
} from '@/api/uitest'

// 表格数据
const tableData = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const loading = ref(false)

// 搜索表单
const searchForm = reactive({
  name: '',
  status: '',
  environment: '',
  created_by: ''
})

// 对话框
const dialogVisible = ref(false)
const dialogTitle = ref('新建测试单')
const formRef = ref(null)
const submitting = ref(false)
const editingId = ref(null)
const currentStep = ref(0)
const contentTab = ref('suite')

// 查看详情对话框
const viewDialogVisible = ref(false)
const currentTask = ref(null)

// 表单数据
const formData = reactive({
  name: '',
  description: '',
  environment: '',
  execute_config: {
    stop_on_failure: false,
    retry_on_failure: false,
    max_retry_times: 3,
    timeout: 300,
    parallel: false,
    parallel_count: 3
  }
})

// 测试内容选择
const selectedSuites = ref([])
const selectedCases = ref([])
const availableSuites = ref([])
const availableCases = ref([])

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入测试单名称', trigger: 'blur' }
  ],
  environment: [
    { required: true, message: '请输入测试环境', trigger: 'blur' }
  ]
}

// 获取状态类型
const getStatusType = (status) => {
  const typeMap = {
    'PENDING': 'info',
    'RUNNING': 'warning',
    'COMPLETED': 'success',
    'FAILED': 'danger',
    'CANCELLED': 'info'
  }
  return typeMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const textMap = {
    'PENDING': '待执行',
    'RUNNING': '执行中',
    'COMPLETED': '已完成',
    'FAILED': '已失败',
    'CANCELLED': '已取消'
  }
  return textMap[status] || status
}

// 获取进度状态
const getProgressStatus = (status) => {
  if (status === 'COMPLETED') return 'success'
  if (status === 'FAILED') return 'exception'
  return undefined
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
    
    const res = await getTestTasks(params)
    if (res.code === 200) {
      tableData.value = res.data.items || []
      total.value = res.data.total || 0
    } else {
      ElMessage.error(res.msg || '获取数据失败')
    }
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 加载可用套件和用例
const loadAvailableContent = async () => {
  try {
    // 加载套件
    const suiteRes = await getTestSuites({ page: 1, page_size: 1000 })
    if (suiteRes.code === 200) {
      availableSuites.value = suiteRes.data.items.map(item => ({
        id: item.id,
        name: item.name
      }))
    }
    
    // 加载用例
    const caseRes = await getTestCases({ page: 1, page_size: 1000, status: '激活' })
    if (caseRes.code === 200) {
      availableCases.value = caseRes.data.items.map(item => ({
        id: item.id,
        name: item.name
      }))
    }
  } catch (error) {
    console.error('加载可用内容失败:', error)
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
  searchForm.status = ''
  searchForm.environment = ''
  searchForm.created_by = ''
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

// 新建测试单
const handleCreate = () => {
  editingId.value = null
  dialogTitle.value = '新建测试单'
  currentStep.value = 0
  resetForm()
  loadAvailableContent()
  dialogVisible.value = true
}

// 查看测试单
const handleView = async (row) => {
  try {
    const res = await getTestTaskDetail(row.id)
    if (res.code === 200) {
      currentTask.value = res.data
      viewDialogVisible.value = true
    } else {
      ElMessage.error(res.msg || '获取详情失败')
    }
  } catch (error) {
    console.error('获取详情失败:', error)
    ElMessage.error('获取详情失败')
  }
}

// 编辑测试单
const handleEdit = async (row) => {
  editingId.value = row.id
  dialogTitle.value = '编辑测试单'
  currentStep.value = 0
  
  try {
    const res = await getTestTaskDetail(row.id)
    if (res.code === 200) {
      const task = res.data
      formData.name = task.name
      formData.description = task.description
      formData.environment = task.environment
      formData.execute_config = task.execute_config || {
        stop_on_failure: false,
        retry_on_failure: false,
        max_retry_times: 3,
        timeout: 300,
        parallel: false,
        parallel_count: 3
      }
      
      await loadAvailableContent()
      dialogVisible.value = true
    } else {
      ElMessage.error(res.msg || '获取测试单信息失败')
    }
  } catch (error) {
    console.error('获取测试单信息失败:', error)
    ElMessage.error('获取测试单信息失败')
  }
}

// 执行测试单
const handleExecute = (row) => {
  ElMessageBox.confirm(
    '是否立即执行该测试单？',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    }
  ).then(async () => {
    try {
      const res = await executeTestTask(row.id)
      if (res.code === 200) {
        ElMessage.success('测试单已开始执行')
        loadData()
      } else {
        ElMessage.error(res.msg || '执行失败')
      }
    } catch (error) {
      console.error('执行失败:', error)
      ElMessage.error('执行失败')
    }
  }).catch(() => {})
}

// 取消执行
const handleCancel = (row) => {
  ElMessageBox.confirm(
    '是否取消执行该测试单？',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const res = await cancelTestTask(row.id)
      if (res.code === 200) {
        ElMessage.success('已取消执行')
        loadData()
      } else {
        ElMessage.error(res.msg || '取消失败')
      }
    } catch (error) {
      console.error('取消失败:', error)
      ElMessage.error('取消失败')
    }
  }).catch(() => {})
}

// 删除测试单
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
      const res = await deleteTestTask(row.id)
      if (res.code === 200) {
        ElMessage.success('删除成功')
        loadData()
      } else {
        ElMessage.error(res.msg || '删除失败')
      }
    } catch (error) {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

// 步骤导航
const handleNextStep = async () => {
  if (currentStep.value === 0) {
    // 验证基本信息
    if (!formRef.value) return
    await formRef.value.validate((valid) => {
      if (valid) {
        currentStep.value++
      }
    })
  } else {
    currentStep.value++
  }
}

const handlePrevStep = () => {
  currentStep.value--
}

// 提交表单
const handleSubmit = async () => {
  submitting.value = true
  try {
    const data = {
      name: formData.name,
      description: formData.description,
      environment: formData.environment,
      execute_config: formData.execute_config,
      suites: selectedSuites.value,
      cases: selectedCases.value
    }
    
    const res = editingId.value 
      ? await updateTestTask(editingId.value, data)
      : await createTestTask(data)
      
    if (res.code === 200) {
      ElMessage.success(res.msg || (editingId.value ? '更新成功' : '创建成功'))
      dialogVisible.value = false
      loadData()
    } else {
      ElMessage.error(res.msg || '操作失败')
    }
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('提交失败')
  } finally {
    submitting.value = false
  }
}

// 重置表单
const resetForm = () => {
  formData.name = ''
  formData.description = ''
  formData.environment = ''
  formData.execute_config = {
    stop_on_failure: false,
    retry_on_failure: false,
    max_retry_times: 3,
    timeout: 300,
    parallel: false,
    parallel_count: 3
  }
  selectedSuites.value = []
  selectedCases.value = []
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

// 对话框关闭
const handleDialogClose = () => {
  currentStep.value = 0
  resetForm()
}

// 页面加载
onMounted(() => {
  loadData()
})
</script>

<style scoped lang="less">
.test-tasks-container {
  padding: 20px;
  
  .page-header {
    margin-bottom: 20px;
  }
  
  .toolbar {
    margin-bottom: 20px;
  }
  
  .search-area {
    margin-bottom: 20px;
    padding: 20px;
    background: #fff;
    border-radius: 4px;
    
    .search-form {
      .el-form-item {
        margin-bottom: 0;
      }
    }
  }
  
  .pagination {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
