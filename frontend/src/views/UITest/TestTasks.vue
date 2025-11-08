<template>
  <div class="page-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <!-- 第一列：左侧操作按钮 -->
      <div>
        <el-button type="primary" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          新建测试单
        </el-button>
      </div>
      
      <!-- 第二列：搜索表单 -->
      <el-form :inline="true" :model="searchForm">
        <div ref="searchFieldsWrapper" :class="['search-fields-wrapper', searchExpanded ? 'expanded' : 'collapsed']" >
          <el-form-item label="测试单名称">
            <el-input 
              v-model="searchForm.name" 
              placeholder="请输入测试单名称" 
              clearable
              @keyup.enter="handleSearch"
            />
          </el-form-item>
          <el-form-item label="所属产品">
            <el-select 
              v-model="searchForm.product" 
              placeholder="请选择产品" 
              clearable
              filterable
            >
              <el-option 
                v-for="item in productOptions" 
                :key="item.name" 
                :label="item.name" 
                :value="item.name"
              />
            </el-select>
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
        </div>
      </el-form>
      
      <!-- 第三列：搜索按钮 -->
      <div class="search-buttons">
        <!-- 展开/收起按钮 -->
        <el-button 
          v-if="showToggleButton" 
          @click="searchExpanded = !searchExpanded"
          text
          :title="searchExpanded ? '收起' : '展开'"
        >
          <el-icon :class="{ 'rotated': searchExpanded }"><ArrowDown /></el-icon>
        </el-button>
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button @click="handleReset">重置</el-button>
      </div>
    </div>

    <!-- 数据表格 -->
    <el-table
      :data="tableData"
      stripe
      border
      v-loading="loading"
      style="width: 100%"
    >
      <el-table-column prop="name" label="测试单名称" width="500" show-overflow-tooltip />
      <el-table-column prop="product" label="所属产品" width="120" />
      <el-table-column prop="environment" label="测试环境" width="100" />
      <el-table-column prop="status" label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag 
            :type="getStatusType(row.status)" 
            :class="getStatusClass(row.status)"
            size="small"
          >
            {{ getStatusText(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="执行进度" width="200" align="center">
        <template #default="{ row }">
          <!-- 待执行状态不显示进度 -->
          <span v-if="row.status === '待执行'" style="color: #909399">-</span>
          <!-- 其他状态显示进度 -->
          <div v-else-if="row.total_cases > 0">
            <!-- 进度条单独一行 -->
            <el-progress 
              :percentage="Math.round(row.progress)" 
              :status="getProgressStatus(row.status)"
              :show-text="false"
            />
            <!-- 百分比和执行条数在第二行 -->
            <div style="font-size: 12px; color: #606266; margin-top: 8px; font-weight: 500">
              {{ Math.round(row.progress) }}% ({{ row.executed_cases }}/{{ row.total_cases }})
            </div>
          </div>
          <span v-else style="color: #909399">-</span>
        </template>
      </el-table-column>
      <el-table-column label="通过率" width="120" align="center">
        <template #default="{ row }">
          <span v-if="row.executed_cases > 0">
            {{ Math.round((row.passed_cases / row.executed_cases) * 100) }}%
          </span>
          <span v-else style="color: #909399">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="created_by" label="创建人" width="120" />
      <el-table-column prop="created_time" label="创建时间" width="200" />
      <el-table-column label="操作" width="320" fixed="right" align="center" >
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
            <!-- 执行中：显示暂停按钮 -->
            <el-tooltip content="暂停" placement="top" v-if="row.status === '执行中'">
              <el-button 
                text 
                type="warning" 
                @click="handlePause(row)"
                :icon="VideoPause"
              />
            </el-tooltip>
            <!-- 已暂停：显示继续按钮 -->
            <el-tooltip content="继续" placement="top" v-else-if="row.status === '已暂停'">
              <el-button 
                text 
                type="success" 
                @click="handleResume(row)"
                :icon="VideoPlay"
              />
            </el-tooltip>
            <!-- 其他状态：显示执行按钮 -->
            <el-tooltip content="执行" placement="top" v-else>
              <el-button 
                text 
                type="success" 
                @click="handleExecute(row)"
                :disabled="row.status === '执行中'"
                :icon="VideoPlay"
              />
            </el-tooltip>
            <!-- 重新执行按钮 -->
            <el-tooltip content="重新执行" placement="top">
              <el-button 
                text 
                type="warning" 
                @click="handleRestart(row)"
                :disabled="row.status === '执行中'"
                :icon="RefreshRight"
              />
            </el-tooltip>
            <!-- 取消执行按钮 -->
            <el-tooltip content="取消" placement="top">
              <el-button 
                text 
                type="danger" 
                @click="handleCancel(row)"
                :disabled="row.status !== '执行中' && row.status !== '已暂停'"
                :icon="CircleClose"
              />
            </el-tooltip>
            <!-- 查看日志按钮 -->
            <el-tooltip content="查看日志" placement="top">
              <el-button 
                text 
                type="info" 
                @click="handleViewLog(row)"
                :disabled="row.status === '待执行'"
                :icon="Document"
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

    <!-- 查看执行日志对话框 -->
    <el-dialog
      v-model="logDialogVisible"
      title="执行日志"
      width="1000px"
      @close="stopLogPolling"
    >
      <div 
        ref="logContainer"
        class="log-container"
      >
        <pre v-if="executionLog" class="log-content">{{ executionLog }}</pre>
        <div v-else class="log-empty">
          <el-empty description="暂无日志" />
        </div>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="logDialogVisible = false">关闭</el-button>
          <el-button type="primary" @click="loadLog" :disabled="isLogComplete">
            刷新
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, nextTick, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, View, Edit, Delete, VideoPlay, VideoPause, RefreshRight, CircleClose, Document, Loading, CircleCheck, ArrowDown } from '@element-plus/icons-vue'
import { 
  getTestTasks,
  deleteTestTask,
  getTestTaskDetail,
  executeTestTask,
  cancelTestTask,
  pauseTestTask,
  resumeTestTask,
  restartTestTask,
  getTestTaskLog,
  getAllProducts
} from '@/api/uitest'
import { useAutoSearch } from '@/composables/useAutoSearch'

const router = useRouter()

// 搜索表单展开/收起状态
const searchExpanded = ref(false)  // 默认折叠，只显示一行
const searchFieldsWrapper = ref(null)

// 根据搜索框数量判断是否显示展开按钮（超过4个就显示）
const showToggleButton = computed(() => {
  // 测试单有5个搜索条件，超过4个，显示展开按钮
  return 5 > 4
})

// 表格数据
const tableData = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)  // 默认每页显示10条
const loading = ref(false)

// 搜索表单
const searchForm = reactive({
  name: '',
  product: '',
  status: '',
  environment: '',
  created_by: ''
})

// 选项数据
const productOptions = ref([])

// 查看详情对话框
const viewDialogVisible = ref(false)
const currentTask = ref(null)

// 查看日志对话框
const logDialogVisible = ref(false)
const executionLog = ref('')
const logOffset = ref(0)
const logTimer = ref(null)
const currentLogTaskId = ref(null)
const isLogComplete = ref(false)
const logContainer = ref(null)

// 获取状态类型
const getStatusType = (status) => {
  const typeMap = {
    'PENDING': '',        // 待执行 - 灰色
    'RUNNING': '',        // 执行中 - 蓝色
    'PAUSED': 'warning',  // 已暂停 - 橙色
    'COMPLETED': 'success', // 已完成 - 绿色
    'FAILED': 'danger',   // 已失败 - 红色
    'CANCELLED': 'info'   // 已取消 - 灰蓝色
  }
  return typeMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const textMap = {
    'PENDING': '待执行',
    'RUNNING': '执行中',
    'PAUSED': '已暂停',
    'COMPLETED': '已完成',
    'FAILED': '已失败',
    'CANCELLED': '已取消'
  }
  return textMap[status] || status
}

// 获取状态样式类
const getStatusClass = (status) => {
  const classMap = {
    'PENDING': 'status-pending',
    'RUNNING': 'status-running',
    'PAUSED': 'status-paused',
    'COMPLETED': 'status-completed',
    'FAILED': 'status-failed',
    'CANCELLED': 'status-cancelled'
  }
  return classMap[status] || ''
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
    
    const data = await getTestTasks(params)
    tableData.value = data.items || []
    total.value = data.total || 0
  } catch (error) {
    console.error('加载数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 加载产品选项
const loadProducts = async () => {
  try {
    const products = await getAllProducts()
    productOptions.value = products || []
  } catch (error) {
    console.error('加载产品失败:', error)
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
  searchForm.product = ''
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
  router.push('/ui-test/test-tasks/new')
}

// 查看测试单
const handleView = async (row) => {
  try {
    const task = await getTestTaskDetail(row.id)
    currentTask.value = task
    viewDialogVisible.value = true
  } catch (error) {
    console.error('获取详情失败:', error)
  }
}

// 编辑测试单
const handleEdit = (row) => {
  router.push(`/ui-test/test-tasks/${row.id}/edit`)
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
      await executeTestTask(row.id)
      ElMessage.success('测试单已开始执行')
      loadData()
    } catch (error) {
      console.error('执行失败:', error)
    }
  }).catch(() => {})
}

// 暂停执行
const handlePause = async (row) => {
  try {
    await pauseTestTask(row.id)
    ElMessage.success('已暂停执行')
    loadData()
  } catch (error) {
    console.error('暂停失败:', error)
    ElMessage.error(error.response?.data?.msg || '暂停失败')
  }
}

// 继续执行
const handleResume = async (row) => {
  try {
    await resumeTestTask(row.id)
    ElMessage.success('已继续执行')
    loadData()
  } catch (error) {
    console.error('继续失败:', error)
    ElMessage.error(error.response?.data?.msg || '继续失败')
  }
}

// 重新执行
const handleRestart = (row) => {
  ElMessageBox.confirm(
    '重新执行将清理已有执行结果，从头开始执行。是否继续？',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await restartTestTask(row.id)
      ElMessage.success('测试单已开始重新执行')
      loadData()
    } catch (error) {
      console.error('重新执行失败:', error)
      ElMessage.error(error.response?.data?.msg || '重新执行失败')
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
      await cancelTestTask(row.id)
      ElMessage.success('已取消执行')
      loadData()
    } catch (error) {
      console.error('取消失败:', error)
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
      await deleteTestTask(row.id)
      ElMessage.success('删除成功')
      loadData()
    } catch (error) {
      console.error('删除失败:', error)
    }
  }).catch(() => {})
}

// 查看执行日志
const handleViewLog = async (row) => {
  currentLogTaskId.value = row.id
  logDialogVisible.value = true
  executionLog.value = ''
  logOffset.value = 0
  isLogComplete.value = false
  
  // 立即加载一次日志
  await loadLog()
  
  // 如果任务正在执行中，启动自动刷新
  if (row.status === 'RUNNING') {
    startLogPolling()
  }
}

// 加载日志内容
const loadLog = async () => {
  if (!currentLogTaskId.value || isLogComplete.value) return
  
  try {
    const data = await getTestTaskLog(currentLogTaskId.value, logOffset.value)
    
    // 追加新日志
    if (data.log_content) {
      executionLog.value += data.log_content
      logOffset.value = data.next_offset
      
      // 自动滚动到底部
      await nextTick()
      if (logContainer.value) {
        logContainer.value.scrollTop = logContainer.value.scrollHeight
      }
    }
    
    // 检查是否完成
    if (data.is_complete) {
      isLogComplete.value = true
      stopLogPolling()
    }
  } catch (error) {
    // request.js 拦截器已经弹出了错误提示
    // 这里只需要停止轮询，并在404时关闭对话框
    stopLogPolling()
    
    // 如果是日志文件不存在的错误，延迟关闭对话框
    if (error && (error.includes('日志文件不存在') || error.includes('暂无执行日志'))) {
      setTimeout(() => {
        logDialogVisible.value = false
      }, 2000)
    }
  }
}

// 启动日志轮询
const startLogPolling = () => {
  stopLogPolling()
  logTimer.value = setInterval(() => {
    loadLog()
  }, 2000) // 每2秒刷新一次
}

// 停止日志轮询
const stopLogPolling = () => {
  if (logTimer.value) {
    clearInterval(logTimer.value)
    logTimer.value = null
  }
}

// 关闭日志对话框时停止轮询
watch(logDialogVisible, (newVal) => {
  if (!newVal) {
    stopLogPolling()
  }
})

// 组件卸载时停止轮询
onUnmounted(() => {
  stopLogPolling()
})

// 配置自动搜索
useAutoSearch({
  searchForm,
  currentPage,
  onSearch: loadData,
  inputFields: ['name', 'environment', 'created_by'], // 输入框字段（防抖搜索）
  selectFields: ['product', 'status'],                 // 下拉框字段（立即搜索）
  debounceDelay: 500                                  // 防抖延迟 0.5秒
})
</script>

<style scoped lang="less">
@import '@/assets/less/variables.less';

.page-container {
  // 使用全局样式，无需重复定义
  
  // 状态标签自定义颜色
  :deep(.el-tag) {
    &.status-pending {
      background-color: @bg-light;
      color: @text-placeholder;
      border-color: @border-lighter;
    }
    
    &.status-running {
      background-color: #e1f3fa;
      color: #409eff;
      border-color: #b3d8ff;
    }
    
    &.status-paused {
      background-color: @warning-light;
      color: @warning-color;
      border-color: @warning-border;
    }
    
    &.status-completed {
      background-color: #f0f9ff;
      color: @success-color;
      border-color: @success-border;
    }
    
    &.status-failed {
      background-color: #fef0f0;
      color: #f56c6c;
      border-color: #fbc4c4;
    }
    
    &.status-cancelled {
      background-color: @bg-light;
      color: @text-placeholder;
      border-color: @border-dark;
    }
  }
  
  // 日志容器样式
  .log-container {
    height: 500px;
    overflow-y: auto;
    background-color: #1e1e1e;
    border-radius: @border-radius-base;
    padding: @spacing-lg;
    
    .log-content {
      margin: 0;
      color: #d4d4d4;
      font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
      font-size: @font-size-sm;
      line-height: 1.6;
      white-space: pre-wrap;
      word-wrap: break-word;
    }
    
    .log-empty {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100%;
    }
  }
}
</style>
