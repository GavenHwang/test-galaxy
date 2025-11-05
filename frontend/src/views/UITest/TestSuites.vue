<template>
  <div class="test-suites-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item>UI测试</el-breadcrumb-item>
        <el-breadcrumb-item>测试套件管理</el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <!-- 操作工具栏 -->
    <div class="toolbar">
      <el-button type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon>
        新建套件
      </el-button>
    </div>

    <!-- 搜索筛选区 -->
    <div class="search-area">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="套件名称">
          <el-input 
            v-model="searchForm.name" 
            placeholder="请输入套件名称" 
            clearable
            @keyup.enter="handleSearch"
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
      <el-table-column prop="name" label="套件名称" width="250" show-overflow-tooltip />
      <el-table-column prop="description" label="描述" show-overflow-tooltip />
      <el-table-column prop="case_count" label="用例数量" width="100" align="center" />
      <el-table-column label="筛选条件" width="250">
        <template #default="{ row }">
          <div v-if="row.filter_conditions && Object.keys(row.filter_conditions).length > 0">
            <el-tag 
              v-for="(value, key) in getFilterDisplay(row.filter_conditions)" 
              :key="key" 
              size="small" 
              style="margin-right: 5px; margin-bottom: 5px"
            >
              {{ key }}: {{ value }}
            </el-tag>
          </div>
          <span v-else style="color: #909399">无</span>
        </template>
      </el-table-column>
      <el-table-column prop="created_by" label="创建人" width="100" />
      <el-table-column prop="created_time" label="创建时间" width="180" />
      <el-table-column label="操作" width="280" fixed="right">
        <template #default="{ row }">
          <el-button text type="primary" @click="handleView(row)">查看</el-button>
          <el-button text type="primary" @click="handleEdit(row)">编辑</el-button>
          <el-button text type="primary" @click="handleSync(row)">同步</el-button>
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

    <!-- 创建/编辑套件对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="800px"
      @close="handleDialogClose"
    >
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="100px">
        <el-form-item label="套件名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入套件名称" />
        </el-form-item>
        <el-form-item label="套件描述" prop="description">
          <el-input 
            v-model="formData.description" 
            type="textarea" 
            :rows="3"
            placeholder="请输入套件描述" 
          />
        </el-form-item>
        
        <el-divider content-position="left">筛选条件配置</el-divider>
        
        <el-form-item label="所属模块">
          <el-select 
            v-model="formData.filter_conditions.module" 
            multiple
            placeholder="请选择模块" 
            clearable
            filterable
            style="width: 100%"
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
            v-model="formData.filter_conditions.priority" 
            multiple
            placeholder="请选择优先级" 
            clearable
            style="width: 100%"
          >
            <el-option label="高" value="高" />
            <el-option label="中" value="中" />
            <el-option label="低" value="低" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="用例状态">
          <el-select 
            v-model="formData.filter_conditions.status" 
            multiple
            placeholder="请选择状态" 
            clearable
            style="width: 100%"
          >
            <el-option label="草稿" value="草稿" />
            <el-option label="激活" value="激活" />
            <el-option label="禁用" value="禁用" />
            <el-option label="归档" value="归档" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="创建人">
          <el-input v-model="formData.filter_conditions.created_by" placeholder="多个创建人用逗号分隔" />
        </el-form-item>
        
        <el-form-item label="标签">
          <el-input v-model="formData.filter_conditions.tags" placeholder="多个标签用逗号分隔" />
        </el-form-item>
        
        <el-form-item>
          <el-button @click="handlePreview">预览匹配用例</el-button>
          <span v-if="previewCount !== null" style="margin-left: 10px; color: #409EFF">
            预计匹配 {{ previewCount }} 个用例
          </span>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 查看套件详情对话框 -->
    <el-dialog
      v-model="viewDialogVisible"
      title="套件详情"
      width="1000px"
    >
      <div v-if="currentSuite">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="套件名称">{{ currentSuite.name }}</el-descriptions-item>
          <el-descriptions-item label="用例数量">{{ currentSuite.case_count }}</el-descriptions-item>
          <el-descriptions-item label="创建人">{{ currentSuite.created_by }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ currentSuite.created_time }}</el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">{{ currentSuite.description || '无' }}</el-descriptions-item>
        </el-descriptions>
        
        <el-divider content-position="left">关联用例列表</el-divider>
        
        <el-table :data="currentSuite.cases" border stripe max-height="400">
          <el-table-column prop="name" label="用例名称" show-overflow-tooltip />
          <el-table-column prop="priority" label="优先级" width="80" align="center">
            <template #default="{ row }">
              <el-tag 
                :type="row.priority === '高' ? 'danger' : row.priority === '中' ? 'warning' : 'info'"
                size="small"
              >
                {{ row.priority }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="80" align="center">
            <template #default="{ row }">
              <el-tag size="small">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="sort_order" label="执行顺序" width="100" align="center" />
        </el-table>
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
  getTestSuites,
  createTestSuite,
  updateTestSuite,
  deleteTestSuite,
  getTestSuiteDetail,
  previewMatchedCases,
  syncSuiteCases,
  getModules
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
  created_by: ''
})

// 对话框
const dialogVisible = ref(false)
const dialogTitle = ref('新建套件')
const formRef = ref(null)
const submitting = ref(false)
const editingId = ref(null)
const previewCount = ref(null)

// 查看详情对话框
const viewDialogVisible = ref(false)
const currentSuite = ref(null)

// 表单数据
const formData = reactive({
  name: '',
  description: '',
  filter_conditions: {
    module: [],
    priority: [],
    status: [],
    created_by: '',
    tags: ''
  }
})

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入套件名称', trigger: 'blur' }
  ]
}

// 选项列表
const moduleOptions = ref([])

// 筛选条件显示
const getFilterDisplay = (conditions) => {
  const display = {}
  if (conditions.module && conditions.module.length > 0) {
    display['模块'] = conditions.module.join(', ')
  }
  if (conditions.priority && conditions.priority.length > 0) {
    display['优先级'] = conditions.priority.join(', ')
  }
  if (conditions.status && conditions.status.length > 0) {
    display['状态'] = conditions.status.join(', ')
  }
  if (conditions.created_by) {
    display['创建人'] = conditions.created_by
  }
  if (conditions.tags) {
    display['标签'] = conditions.tags
  }
  return display
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
    
    const res = await getTestSuites(params)
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

// 加载模块选项
const loadModules = async () => {
  try {
    const res = await getModules()
    if (res.code === 200) {
      moduleOptions.value = res.data || []
    }
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

// 新建套件
const handleCreate = () => {
  editingId.value = null
  dialogTitle.value = '新建套件'
  resetForm()
  dialogVisible.value = true
}

// 查看套件
const handleView = async (row) => {
  try {
    const res = await getTestSuiteDetail(row.id)
    if (res.code === 200) {
      currentSuite.value = res.data
      viewDialogVisible.value = true
    } else {
      ElMessage.error(res.msg || '获取详情失败')
    }
  } catch (error) {
    console.error('获取详情失败:', error)
    ElMessage.error('获取详情失败')
  }
}

// 编辑套件
const handleEdit = async (row) => {
  editingId.value = row.id
  dialogTitle.value = '编辑套件'
  
  try {
    const res = await getTestSuiteDetail(row.id)
    if (res.code === 200) {
      const suite = res.data
      formData.name = suite.name
      formData.description = suite.description
      
      // 处理筛选条件
      const conditions = suite.filter_conditions || {}
      formData.filter_conditions.module = conditions.module || []
      formData.filter_conditions.priority = conditions.priority || []
      formData.filter_conditions.status = conditions.status || []
      formData.filter_conditions.created_by = Array.isArray(conditions.created_by) 
        ? conditions.created_by.join(', ') 
        : (conditions.created_by || '')
      formData.filter_conditions.tags = Array.isArray(conditions.tags) 
        ? conditions.tags.join(', ') 
        : (conditions.tags || '')
      
      dialogVisible.value = true
    } else {
      ElMessage.error(res.msg || '获取套件信息失败')
    }
  } catch (error) {
    console.error('获取套件信息失败:', error)
    ElMessage.error('获取套件信息失败')
  }
}

// 同步套件
const handleSync = (row) => {
  ElMessageBox.confirm(
    '同步操作将根据筛选条件重新匹配用例，是否继续？',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const res = await syncSuiteCases(row.id)
      if (res.code === 200) {
        ElMessage.success(res.msg || '同步成功')
        loadData()
      } else {
        ElMessage.error(res.msg || '同步失败')
      }
    } catch (error) {
      console.error('同步失败:', error)
      ElMessage.error('同步失败')
    }
  }).catch(() => {})
}

// 删除套件
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
      const res = await deleteTestSuite(row.id, false)
      if (res.code === 200) {
        ElMessage.success('删除成功')
        loadData()
      } else if (res.code === 400 && res.msg.includes('测试单')) {
        // 存在引用，询问是否强制删除
        ElMessageBox.confirm(
          res.msg + '，是否强制删除？',
          '警告',
          {
            confirmButtonText: '强制删除',
            cancelButtonText: '取消',
            type: 'warning'
          }
        ).then(async () => {
          const forceRes = await deleteTestSuite(row.id, true)
          if (forceRes.code === 200) {
            ElMessage.success('删除成功')
            loadData()
          } else {
            ElMessage.error(forceRes.msg || '删除失败')
          }
        })
      } else {
        ElMessage.error(res.msg || '删除失败')
      }
    } catch (error) {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

// 预览匹配用例
const handlePreview = async () => {
  const conditions = buildFilterConditions()
  
  try {
    const res = await previewMatchedCases(0, conditions)
    if (res.code === 200) {
      previewCount.value = res.data.matched_count
      ElMessage.success(`预计匹配 ${res.data.matched_count} 个用例`)
    } else {
      ElMessage.error(res.msg || '预览失败')
    }
  } catch (error) {
    console.error('预览失败:', error)
    ElMessage.error('预览失败')
  }
}

// 构建筛选条件
const buildFilterConditions = () => {
  const conditions = {}
  
  if (formData.filter_conditions.module.length > 0) {
    conditions.module = formData.filter_conditions.module
  }
  if (formData.filter_conditions.priority.length > 0) {
    conditions.priority = formData.filter_conditions.priority
  }
  if (formData.filter_conditions.status.length > 0) {
    conditions.status = formData.filter_conditions.status
  }
  if (formData.filter_conditions.created_by) {
    conditions.created_by = formData.filter_conditions.created_by.split(',').map(s => s.trim()).filter(s => s)
  }
  if (formData.filter_conditions.tags) {
    conditions.tags = formData.filter_conditions.tags.split(',').map(s => s.trim()).filter(s => s)
  }
  
  return conditions
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const data = {
          name: formData.name,
          description: formData.description,
          filter_conditions: buildFilterConditions()
        }
        
        const res = editingId.value 
          ? await updateTestSuite(editingId.value, data)
          : await createTestSuite(data)
          
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
  })
}

// 重置表单
const resetForm = () => {
  formData.name = ''
  formData.description = ''
  formData.filter_conditions = {
    module: [],
    priority: [],
    status: [],
    created_by: '',
    tags: ''
  }
  previewCount.value = null
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

// 对话框关闭
const handleDialogClose = () => {
  resetForm()
}

// 页面加载
onMounted(() => {
  loadData()
  loadModules()
})
</script>

<style scoped lang="less">
.test-suites-container {
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
