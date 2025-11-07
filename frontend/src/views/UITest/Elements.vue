<template>
  <div class="page-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div>
        <el-button type="primary" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          新建元素
        </el-button>
      </div>
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="元素名称">
          <el-input 
            v-model="searchForm.name" 
            placeholder="请输入元素名称" 
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="所属页面">
          <el-select 
            v-model="searchForm.page" 
            placeholder="请选择页面" 
            clearable
            filterable
          >
            <el-option 
              v-for="item in pageOptions" 
              :key="item" 
              :label="item" 
              :value="item"
            />
          </el-select>
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
        <el-form-item label="定位器类型">
          <el-select 
            v-model="searchForm.selector_type" 
            placeholder="请选择类型" 
            clearable
          >
            <el-option 
              v-for="item in selectorTypeOptions" 
              :key="item.value" 
              :label="item.label" 
              :value="item.value"
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
      <el-table-column prop="name" label="元素名称" width="180" />
      <el-table-column prop="selector_type" label="定位器类型" width="120">
        <template #default="{ row }">
          <el-tag size="small">{{ row.selector_type }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="selector_value" label="定位器值" min-width="200" show-overflow-tooltip />
      <el-table-column prop="page" label="所属页面" width="200" show-overflow-tooltip />
      <el-table-column prop="module" label="所属模块" width="120" />
      <el-table-column label="关联用例" width="100" align="center">
        <template #default="{ row }">
          <el-button 
            v-if="row.related_cases_count > 0"
            text 
            type="primary"
            @click="handleViewRelatedCases(row)"
          >
            {{ row.related_cases_count }}
          </el-button>
          <span v-else>0</span>
        </template>
      </el-table-column>
      <el-table-column prop="created_by" label="创建人" width="120" />
      <el-table-column prop="created_time" label="创建时间" width="180" />
      <el-table-column label="操作" width="180" fixed="right" align="center">
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
            <el-tooltip content="复制" placement="top">
              <el-button 
                text 
                type="primary" 
                @click="handleCopy(row)"
                :icon="CopyDocument"
              />
            </el-tooltip>
            <el-tooltip content="权限" placement="top">
              <el-button 
                text 
                type="primary" 
                @click="handleSetPermissions(row)"
                :icon="Lock"
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
        <el-form-item label="元素名称" prop="name">
          <el-input 
            v-model="formData.name" 
            placeholder="请输入元素名称"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="定位器类型" prop="selector_type">
          <el-select
            v-model="formData.selector_type"
            placeholder="请选择定位器类型"
            style="width: 100%"
          >
            <el-option
              v-for="item in selectorTypeOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="定位器值" prop="selector_value">
          <el-input
            v-model="formData.selector_value"
            type="textarea"
            :rows="2"
            placeholder="请输入定位器值"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="所属页面" prop="page">
          <el-select
            v-model="formData.page"
            placeholder="请选择或直接输入页面URL"
            filterable
            allow-create
            default-first-option
            style="width: 100%"
          >
            <el-option
              v-for="item in pageOptions"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
          <div class="form-tip">支持直接输入新的页面URL，或从列表中选择</div>
        </el-form-item>
        <el-form-item label="所属模块" prop="module">
          <el-select
            v-model="formData.module"
            placeholder="请选择或直接输入模块名称（可选）"
            filterable
            allow-create
            default-first-option
            clearable
            style="width: 100%"
          >
            <el-option
              v-for="item in moduleOptions"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
          <div class="form-tip">支持直接输入新的模块名称，或从列表中选择</div>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入描述"
            maxlength="1000"
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

    <!-- 权限设置抽屉 -->
    <el-drawer
      v-model="permissionDrawerVisible"
      title="设置元素权限"
      size="600px"
    >
      <div class="permission-content">
        <el-transfer
          v-model="selectedRoles"
          :data="allRoles"
          :titles="['可用角色', '已授权角色']"
          filterable
          :filter-placeholder="'搜索角色'"
        />
        <div class="drawer-footer">
          <el-button @click="permissionDrawerVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSavePermissions" :loading="permissionLoading">
            保存
          </el-button>
        </div>
      </div>
    </el-drawer>

    <!-- 关联用例抽屉 -->
    <el-drawer
      v-model="relatedCasesDrawerVisible"
      title="关联测试用例"
      size="700px"
    >
      <div class="related-cases-content">
        <el-empty v-if="relatedCases.length === 0" description="暂无关联用例" />
        <el-collapse v-else v-model="activeCaseIds">
          <el-collapse-item 
            v-for="caseItem in relatedCases" 
            :key="caseItem.case_id"
            :name="caseItem.case_id"
          >
            <template #title>
              <div class="case-title">
                <span>{{ caseItem.case_name }}</span>
                <el-tag size="small" type="info">{{ caseItem.step_count }} 个步骤</el-tag>
              </div>
            </template>
            <el-table :data="caseItem.steps" size="small" border>
              <el-table-column prop="step_number" label="步骤号" width="80" />
              <el-table-column prop="description" label="步骤描述" />
            </el-table>
          </el-collapse-item>
        </el-collapse>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Lock, CopyDocument } from '@element-plus/icons-vue'
import {
  getElements,
  createElement,
  updateElement,
  deleteElement,
  getPages,
  getModules,
  getElementPermissions,
  setElementPermissions,
  getElementRelatedCases,
  getRoles
} from '@/api/uitest'
import { useAutoSearch } from '@/composables/useAutoSearch'

// 定位器类型选项
const selectorTypeOptions = [
  { label: 'ID', value: 'ID' },
  { label: 'NAME', value: 'NAME' },
  { label: 'CSS', value: 'CSS' },
  { label: 'XPATH', value: 'XPATH' },
  { label: 'CLASS_NAME', value: 'CLASS_NAME' },
  { label: 'TAG_NAME', value: 'TAG_NAME' },
  { label: 'LINK_TEXT', value: 'LINK_TEXT' },
  { label: 'PARTIAL_LINK_TEXT', value: 'PARTIAL_LINK_TEXT' },
  { label: 'TEST_ID', value: 'TEST_ID' }
]

// 表格数据
const tableData = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const loading = ref(false)

// 搜索表单
const searchForm = reactive({
  name: '',
  page: '',
  module: '',
  selector_type: ''
})

// 选项列表
const pageOptions = ref([])
const moduleOptions = ref([])

// 对话框相关
const dialogVisible = ref(false)
const dialogTitle = ref('新建页面元素')
const formRef = ref(null)
const isEdit = ref(false)
const editId = ref(null)
const submitLoading = ref(false)

// 表单数据
const formData = reactive({
  name: '',
  selector_type: '',
  selector_value: '',
  page: '',
  module: '',
  description: ''
})

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入元素名称', trigger: 'blur' },
    { min: 1, max: 100, message: '长度在1-100个字符', trigger: 'blur' }
  ],
  selector_type: [
    { required: true, message: '请选择定位器类型', trigger: 'change' }
  ],
  selector_value: [
    { required: true, message: '请输入定位器值', trigger: 'blur' },
    { min: 1, max: 500, message: '长度在1-500个字符', trigger: 'blur' }
  ],
  page: [
    { required: true, message: '请选择或输入页面URL', trigger: 'blur' },
    { min: 1, max: 500, message: '长度在1-500个字符', trigger: 'blur' }
  ],
  module: [
    { max: 100, message: '最多100个字符', trigger: 'blur' }
  ],
  description: [
    { max: 1000, message: '描述最多1000个字符', trigger: 'blur' }
  ]
}

// 权限设置相关
const permissionDrawerVisible = ref(false)
const permissionLoading = ref(false)
const currentElementId = ref(null)
const allRoles = ref([])
const selectedRoles = ref([])

// 关联用例相关
const relatedCasesDrawerVisible = ref(false)
const relatedCases = ref([])
const activeCaseIds = ref([])

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
    
    const data = await getElements(params)
    tableData.value = data.items || []
    total.value = data.total || 0
  } catch (error) {
    console.error('加载数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 加载选项
const loadOptions = async () => {
  try {
    const [pages, modules] = await Promise.all([
      getPages(),
      getModules()
    ])
    
    pageOptions.value = pages || []
    moduleOptions.value = modules || []
  } catch (error) {
    console.error('加载选项失败:', error)
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
  searchForm.page = ''
  searchForm.module = ''
  searchForm.selector_type = ''
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

// 新建元素
const handleCreate = () => {
  isEdit.value = false
  dialogTitle.value = '新建页面元素'
  resetForm()
  dialogVisible.value = true
  loadOptions()
}

// 编辑元素
const handleEdit = (row) => {
  isEdit.value = true
  editId.value = row.id
  dialogTitle.value = '编辑页面元素'
  
  // 深拷贝数据
  Object.assign(formData, {
    name: row.name,
    selector_type: row.selector_type,
    selector_value: row.selector_value,
    page: row.page,
    module: row.module || '',
    description: row.description || ''
  })
  
  dialogVisible.value = true
  loadOptions()
}

// 复制元素
const handleCopy = (row) => {
  isEdit.value = false
  editId.value = null
  dialogTitle.value = '复制页面元素'
  
  // 复制数据，名称加上 "_副本" 后缀
  Object.assign(formData, {
    name: row.name + '_副本',
    selector_type: row.selector_type,
    selector_value: row.selector_value,
    page: row.page,
    module: row.module || '',
    description: row.description || ''
  })
  
  dialogVisible.value = true
  loadOptions()
}

// 删除元素
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
      await deleteElement(row.id)
      ElMessage.success('删除成功')
      loadData()
    } catch (error) {
      console.error('删除失败:', error)
    }
  }).catch(() => {})
}

// 设置权限
const handleSetPermissions = async (row) => {
  currentElementId.value = row.id
  
  try {
    const [roles, perms] = await Promise.all([
      getRoles(),
      getElementPermissions(row.id)
    ])
    
    allRoles.value = (roles || []).map(role => ({
      key: role,
      label: role
    }))
    selectedRoles.value = perms || []
    
    permissionDrawerVisible.value = true
  } catch (error) {
    console.error('加载权限失败:', error)
  }
}

// 保存权限
const handleSavePermissions = async () => {
  permissionLoading.value = true
  try {
    await setElementPermissions(currentElementId.value, {
      roles: selectedRoles.value
    })
    
    ElMessage.success('权限设置成功')
    permissionDrawerVisible.value = false
    loadData()
  } catch (error) {
    console.error('设置权限失败:', error)
  } finally {
    permissionLoading.value = false
  }
}

// 查看关联用例
const handleViewRelatedCases = async (row) => {
  try {
    const cases = await getElementRelatedCases(row.id)
    relatedCases.value = cases || []
    activeCaseIds.value = relatedCases.value.length > 0 ? [relatedCases.value[0].case_id] : []
    relatedCasesDrawerVisible.value = true
  } catch (error) {
    console.error('加载关联用例失败:', error)
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitLoading.value = true
    try {
      const submitData = { ...formData }
      
      if (isEdit.value) {
        await updateElement(editId.value, submitData)
      } else {
        await createElement(submitData)
      }
      
      ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
      dialogVisible.value = false
      loadData()
      loadOptions()
    } catch (error) {
      console.error('提交失败:', error)
    } finally {
      submitLoading.value = false
    }
  })
}

// 重置表单
const resetForm = () => {
  formData.name = ''
  formData.selector_type = ''
  formData.selector_value = ''
  formData.page = ''
  formData.module = ''
  formData.description = ''
  
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

// 配置自动搜索
useAutoSearch({
  searchForm,
  currentPage,
  onSearch: loadData,
  inputFields: ['name'],                           // 输入框字段（防抖搜索）
  selectFields: ['page', 'module', 'selector_type'], // 下拉框字段（立即搜索）
  debounceDelay: 500                               // 防抖延迟 0.5秒
})
</script>

<style scoped lang="less">
@import '@/assets/less/variables.less';

.page-container {
  // 使用全局样式，无需重复定义
  
  .form-tip {
    font-size: @font-size-xs;
    color: @text-placeholder;
    margin-top: @spacing-xs;
  }
  
  .permission-content {
    padding: @spacing-xl;
    
    .drawer-footer {
      margin-top: @spacing-xl;
      text-align: right;
    }
  }
  
  .related-cases-content {
    padding: @spacing-xl;
    
    .case-title {
      display: flex;
      align-items: center;
      justify-content: space-between;
      width: 100%;
      padding-right: @spacing-xl;
    }
  }
}
</style>
