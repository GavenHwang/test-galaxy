<template>
  <div class="page-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <!-- 第一列：左侧操作按钮 -->
      <div>
        <el-button type="primary" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          新建用户
        </el-button>
      </div>
      
      <!-- 第二列：搜索表单 -->
      <el-form :inline="true" :model="searchForm">
        <div class="search-fields-wrapper expanded">
          <el-form-item label="用户名">
            <el-input 
              v-model="searchForm.username" 
              placeholder="请输入用户名" 
              clearable
              @keyup.enter="handleSearch"
            />
          </el-form-item>
          <el-form-item label="角色">
            <el-select 
              v-model="searchForm.role_name" 
              placeholder="请选择角色" 
              clearable
              filterable
            >
              <el-option 
                v-for="item in searchRoleOptions" 
                :key="item" 
                :label="item" 
                :value="item"
              />
            </el-select>
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
                :key="item.name" 
                :label="item.name" 
                :value="item.name"
              />
            </el-select>
          </el-form-item>
        </div>
      </el-form>
      
      <!-- 第三列：搜索按钮 -->
      <div class="search-buttons">
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
      <el-table-column prop="product" label="产品" width="150" />
      <el-table-column prop="role_name" label="角色" width="150" />
      <el-table-column prop="role_code" label="角色Code" width="150" />
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
      <el-table-column prop="description" label="描述" show-overflow-tooltip />
      <el-table-column prop="created_by" label="创建人" width="120" />
      <el-table-column prop="created_time" label="创建时间" width="180" />
      <el-table-column label="操作" width="100" fixed="right" align="center">
        <template #default="{ row }">
          <div class="action-buttons">
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
        :current-page="currentPage"
        :page-size="pageSize"
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
        <el-form-item label="产品" prop="product">
          <el-select
            v-model="formData.product"
            placeholder="请选择产品"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="item in productOptions"
              :key="item.name"
              :label="item.name"
              :value="item.name"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="角色" prop="role_name">
          <el-select
            v-model="formData.role_name"
            placeholder="请选择已有角色或直接输入新角色名称"
            filterable
            allow-create
            default-first-option
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
        <el-form-item label="角色Code" prop="role_code">
          <el-input 
            v-model="formData.role_code" 
            placeholder="请输入角色编码，如：ADMIN"
            maxlength="50"
            show-word-limit
          />
        </el-form-item>
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
import { ref, reactive, onMounted, getCurrentInstance, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, View, Hide, Edit, Delete } from '@element-plus/icons-vue'
import {
  getTestUsers,
  createTestUser,
  updateTestUser,
  deleteTestUser,
  getRoles,
  getTestUserDetail
} from '@/api/uitest'
import { getAllProducts } from '@/api/uitest'
import { useAutoSearch } from '@/composables/useAutoSearch'

const { proxy } = getCurrentInstance()

// 表格数据
const tableData = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const loading = ref(false)

// 搜索表单
const searchForm = reactive({
  username: '',
  product: '',
  role_name: ''
})

// 产品和角色选项
const productOptions = ref([])
const roleOptions = ref([]) // 当前显示的角色选项（根据产品过滤后的，用于表单）
const allRoleOptions = ref([]) // 所有角色选项（不过滤产品）
const searchRoleOptions = ref([]) // 搜索框的角色选项（根据搜索框产品过滤）

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
  role_code: '',
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
  role_code: [
    { required: true, message: '请输入角色编码', trigger: 'blur' },
    { min: 1, max: 50, message: '长度在1-50个字符', trigger: 'blur' },
    { pattern: /^[A-Za-z0-9]+$/, message: '角色编码只能包含大小写英文字符和数字', trigger: 'blur' }
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
    const products = await getAllProducts()  // 从 test_products 表获取
    
    console.log('产品列表:', products)
    
    // 直接使用返回的数组数据
    productOptions.value = products || []
    
    console.log('产品选项已设置:', productOptions.value)
  } catch (error) {
    console.error('加载选项失败:', error)
    ElMessage.error('加载选项失败: ' + (error.message || error))
  }
}

// 根据产品加载角色列表
const loadRolesByProduct = async (product) => {
  try {
    const roles = await getRoles(product)  // 传入product参数进行过滤
    console.log('角色列表:', roles)
    roleOptions.value = roles || []
    console.log('角色选项已设置:', roleOptions.value)
    return roles
  } catch (error) {
    console.error('加载角色失败:', error)
    ElMessage.error('加载角色失败: ' + (error.message || error))
    return []
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
  // 清空角色选项，等待选择产品后再加载
  roleOptions.value = []
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
    role_code: row.role_code || '',
    description: row.description || ''
  })
  
  dialogVisible.value = true
  loadOptions()
  // 根据产品加载对应的角色列表
  if (row.product) {
    loadRolesByProduct(row.product)
  }
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
  formData.role_code = ''
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
  // 初始加载所有角色用于搜索框
  loadRolesByProduct().then(roles => {
    searchRoleOptions.value = roles || []
  })
})

// 监听产品选择变化，联动更新角色列表（表单）
watch(() => formData.product, (newProduct) => {
  if (newProduct) {
    // 清空当前选择的角色
    formData.role_name = ''
    // 根据新选择的产品加载角色列表
    loadRolesByProduct(newProduct)
  } else {
    // 产品为空时，清空角色列表
    roleOptions.value = []
    formData.role_name = ''
  }
})

// 监听搜索框产品变化，联动更新角色列表（搜索框）
watch(() => searchForm.product, async (newProduct) => {
  if (newProduct) {
    // 清空当前选择的角色
    searchForm.role_name = ''
    // 根据新选择的产品加载角色列表
    const roles = await loadRolesByProduct(newProduct)
    searchRoleOptions.value = roles || []
  } else {
    // 产品为空时，加载所有角色
    const roles = await loadRolesByProduct()
    searchRoleOptions.value = roles || []
    searchForm.role_name = ''
  }
})

// 配置自动搜索
useAutoSearch({
  searchForm,
  currentPage,
  onSearch: loadData,
  inputFields: ['username'],           // 输入框字段（防抖搜索）
  selectFields: ['product', 'role_name'], // 下拉框字段（立即搜索）
  debounceDelay: 500                   // 防抖延迟 0.5秒
})
</script>

<style scoped lang="less">
@import '@/assets/less/variables.less';

.page-container {
  // 使用全局样式，无需重复定义
  
  .password-cell {
    display: flex;
    align-items: center;
    gap: @spacing-sm;
    
    span {
      flex: 1;
    }
  }
  
  .form-tip {
    font-size: @font-size-xs;
    color: @text-placeholder;
    margin-top: @spacing-xs;
  }
}
</style>
