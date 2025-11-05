<template>
  <div class="test-users-container">
    <!-- 操作工具栏 -->
    <div class="toolbar">
      <el-button type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon>
        新建用户
      </el-button>
    </div>

    <!-- 搜索筛选区 -->
    <div class="search-area">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="用户名">
          <el-input 
            v-model="searchForm.username" 
            placeholder="请输入用户名" 
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="产品">
          <el-select 
            v-model="searchForm.product" 
            placeholder="请选择产品" 
            clearable
            filterable
          >
            <el-option 
              v-for="item in productOptions" 
              :key="item" 
              :label="item" 
              :value="item"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="角色">
          <el-select 
            v-model="searchForm.role_name" 
            placeholder="请选择角色" 
            clearable
            filterable
          >
            <el-option 
              v-for="item in roleOptions" 
              :key="item" 
              :label="item" 
              :value="item"
            />
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
      style="width: 100%"
    >
      <el-table-column prop="username" label="用户名" width="150" />
      <el-table-column label="密码" width="180">
        <template #default="{ row }">
          <div class="password-cell">
            <span>{{ passwordVisible[row.id] ? row.actualPassword : '******' }}</span>
            <el-button 
              text 
              @click="togglePassword(row)"
              :icon="passwordVisible[row.id] ? View : Hide"
            />
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="product" label="产品" width="150" />
      <el-table-column prop="role_name" label="角色" width="150" />
      <el-table-column prop="description" label="描述" show-overflow-tooltip />
      <el-table-column prop="created_by" label="创建人" width="120" />
      <el-table-column prop="created_time" label="创建时间" width="180" />
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
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

    <!-- 新建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input 
            v-model="formData.username" 
            placeholder="请输入用户名"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="formData.password"
            :type="formPasswordVisible ? 'text' : 'password'"
            placeholder="请输入密码"
            maxlength="255"
            show-word-limit
          >
            <template #suffix>
              <el-icon 
                @click="formPasswordVisible = !formPasswordVisible"
                style="cursor: pointer"
              >
                <component :is="formPasswordVisible ? View : Hide" />
              </el-icon>
            </template>
          </el-input>
          <div v-if="isEdit" class="form-tip">不修改密码请留空</div>
        </el-form-item>
        <el-form-item label="产品" prop="product">
          <el-select
            v-model="formData.product"
            placeholder="请选择或输入产品"
            filterable
            allow-create
            style="width: 100%"
          >
            <el-option
              v-for="item in productOptions"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="角色" prop="role_name">
          <el-select
            v-model="formData.role_name"
            placeholder="请选择或输入角色"
            filterable
            allow-create
            style="width: 100%"
          >
            <el-option
              v-for="item in roleOptions"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入描述"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, View, Hide } from '@element-plus/icons-vue'
import {
  getTestUsers,
  createTestUser,
  updateTestUser,
  deleteTestUser,
  getProducts,
  getRoles,
  getTestUserDetail
} from '@/api/uitest'

// 表格数据
const tableData = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const loading = ref(false)

// 搜索表单
const searchForm = reactive({
  username: '',
  product: '',
  role_name: ''
})

// 产品和角色选项
const productOptions = ref([])
const roleOptions = ref([])

// 密码显示状态
const passwordVisible = ref({})

// 对话框相关
const dialogVisible = ref(false)
const dialogTitle = ref('新建测试用户')
const formRef = ref(null)
const isEdit = ref(false)
const editId = ref(null)
const submitLoading = ref(false)
const formPasswordVisible = ref(false)

// 表单数据
const formData = reactive({
  username: '',
  password: '',
  product: '',
  role_name: '',
  description: ''
})

// 表单验证规则
const formRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 100, message: '长度在2-100个字符', trigger: 'blur' }
  ],
  password: [
    { 
      validator: (rule, value, callback) => {
        if (isEdit.value && !value) {
          // 编辑时密码可以为空
          callback()
        } else if (!value) {
          callback(new Error('请输入密码'))
        } else if (value.length < 6 || value.length > 255) {
          callback(new Error('密码长度在6-255个字符'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  product: [
    { required: true, message: '请选择或输入产品', trigger: 'blur' },
    { min: 1, max: 100, message: '长度在1-100个字符', trigger: 'blur' }
  ],
  role_name: [
    { required: true, message: '请选择或输入角色', trigger: 'blur' },
    { min: 1, max: 100, message: '长度在1-100个字符', trigger: 'blur' }
  ],
  description: [
    { max: 500, message: '描述最多500个字符', trigger: 'blur' }
  ]
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
    
    // 注意：响应拦截器在 code===200 时直接返回 data
    const data = await getTestUsers(params)
    tableData.value = data.items || []
    total.value = data.total || 0
  } catch (error) {
    console.error('加载数据失败:', error)
    // 响应拦截器已经显示了错误消息
  } finally {
    loading.value = false
  }
}

// 加载产品和角色选项
const loadOptions = async () => {
  try {
    // 注意：响应拦截器在 code===200 时直接返回 data，所以这里收到的就是数组
    const [products, roles] = await Promise.all([
      getProducts(),
      getRoles()
    ])
    
    console.log('产品列表:', products)
    console.log('角色列表:', roles)
    
    // 直接使用返回的数组数据
    productOptions.value = products || []
    roleOptions.value = roles || []
    
    console.log('产品选项已设置:', productOptions.value)
    console.log('角色选项已设置:', roleOptions.value)
  } catch (error) {
    console.error('加载选项失败:', error)
    ElMessage.error('加载选项失败: ' + (error.message || error))
  }
}

// 切换密码显示
const togglePassword = async (row) => {
  const id = row.id
  
  if (!passwordVisible.value[id]) {
    // 如果要显示密码，先获取明文密码
    try {
      // 注意：响应拦截器在 code===200 时直接返回 data
      const userData = await getTestUserDetail(id)
      row.actualPassword = userData.password
      passwordVisible.value[id] = true
    } catch (error) {
      console.error('获取密码失败:', error)
    }
  } else {
    // 隐藏密码
    passwordVisible.value[id] = false
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  loadData()
}

// 重置
const handleReset = () => {
  searchForm.username = ''
  searchForm.product = ''
  searchForm.role_name = ''
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

// 新建用户
const handleCreate = () => {
  isEdit.value = false
  dialogTitle.value = '新建测试用户'
  resetForm()
  dialogVisible.value = true
  loadOptions()
}

// 编辑用户
const handleEdit = (row) => {
  isEdit.value = true
  editId.value = row.id
  dialogTitle.value = '编辑测试用户'
  
  // 深拷贝数据
  Object.assign(formData, {
    username: row.username,
    password: '', // 编辑时密码留空
    product: row.product,
    role_name: row.role_name,
    description: row.description || ''
  })
  
  dialogVisible.value = true
  loadOptions()
}

// 删除用户
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
      // 注意：响应拦截器在 code!==200 时会reject，所以需要 try-catch
      await deleteTestUser(row.id, false)
      ElMessage.success('删除成功')
      loadData()
    } catch (error) {
      // 检查是否是关联错误（需要根据实际错误信息判断）
      const errorMsg = error?.message || error || ''
      if (errorMsg.includes('关联')) {
        // 存在关联，询问是否强制删除
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
            await deleteTestUser(row.id, true)
            ElMessage.success('删除成功')
            loadData()
          } catch (forceError) {
            console.error('强制删除失败:', forceError)
          }
        }).catch(() => {})
      } else {
        console.error('删除失败:', error)
      }
    }
  }).catch(() => {
    // 取消删除
  })
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitLoading.value = true
    try {
      const submitData = { ...formData }
      
      // 如果是编辑且密码为空，删除password字段
      if (isEdit.value && !submitData.password) {
        delete submitData.password
      }
      
      // 注意：响应拦截器在 code===200 时直接返回 data 字段
      // 所以这里收到的是用户数据对象，而不是完整响应对象
      if (isEdit.value) {
        await updateTestUser(editId.value, submitData)
      } else {
        await createTestUser(submitData)
      }
      
      // 成功执行到这里说明没有抛出异常（响应拦截器会在失败时reject）
      ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
      dialogVisible.value = false
      loadData()
      loadOptions() // 刷新选项列表
    } catch (error) {
      console.error('提交失败:', error)
      // 响应拦截器已经显示了错误消息，这里不需要重复显示
      // ElMessage.error('操作失败')
    } finally {
      submitLoading.value = false
    }
  })
}

// 重置表单
const resetForm = () => {
  formData.username = ''
  formData.password = ''
  formData.product = ''
  formData.role_name = ''
  formData.description = ''
  formPasswordVisible.value = false
  
  if (formRef.value) {
    formRef.value.clearValidate()
  }
}

// 对话框关闭
const handleDialogClose = () => {
  resetForm()
}

// 页面加载
onMounted(() => {
  loadData()
  loadOptions()
})
</script>

<style scoped lang="less">
.test-users-container {
  padding: 20px;
  
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
  
  .password-cell {
    display: flex;
    align-items: center;
    gap: 8px;
    
    span {
      flex: 1;
    }
  }
  
  .pagination {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
  
  .form-tip {
    font-size: 12px;
    color: #909399;
    margin-top: 4px;
  }
}
</style>
