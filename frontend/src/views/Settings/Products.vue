<template>
  <div class="page-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div>
        <el-button type="primary" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          新建产品
        </el-button>
      </div>
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="产品名称">
          <el-input 
            v-model="searchForm.name" 
            placeholder="请输入产品名称" 
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
            <el-option label="全部" value="" />
            <el-option label="启用" value="启用" />
            <el-option label="禁用" value="禁用" />
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
      <el-table-column prop="sort_order" label="排序" width="80" align="center" />
      <el-table-column prop="name" label="产品名称" width="180" />
      <el-table-column prop="code" label="产品编码" width="150" />
      <el-table-column label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag v-if="row.status === '启用'" type="success">启用</el-tag>
          <el-tag v-else type="info">禁用</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="描述" show-overflow-tooltip />
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
            <el-tooltip :content="row.status === '启用' ? '禁用' : '启用'" placement="top">
              <el-button 
                text 
                type="primary" 
                @click="handleToggleStatus(row)"
                :icon="row.status === '启用' ? CircleClose : CircleCheck"
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
      width="500px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="产品名称" prop="name">
          <el-input 
            v-model="formData.name" 
            placeholder="请输入产品名称"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="产品编码" prop="code">
          <el-input 
            v-model="formData.code" 
            placeholder="请输入产品编码，如：PLATFORM"
            maxlength="50"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select
            v-model="formData.status"
            placeholder="请选择状态"
            style="width: 100%"
          >
            <el-option label="启用" value="启用" />
            <el-option label="禁用" value="禁用" />
          </el-select>
        </el-form-item>
        <el-form-item label="排序序号" prop="sort_order">
          <el-input-number
            v-model="formData.sort_order"
            :min="0"
            :max="9999"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入产品描述"
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, CircleCheck, CircleClose } from '@element-plus/icons-vue'
import {
  getProductList,
  createProduct,
  updateProduct,
  deleteProduct,
  updateProductStatus
} from '@/api/uitest'
import { useAutoSearch } from '@/composables/useAutoSearch'

// 表格数据
const tableData = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const loading = ref(false)

// 搜索表单
const searchForm = reactive({
  name: '',
  status: ''
})

// 对话框相关
const dialogVisible = ref(false)
const dialogTitle = ref('新建产品')
const formRef = ref(null)
const isEdit = ref(false)
const editId = ref(null)
const submitLoading = ref(false)

// 表单数据
const formData = reactive({
  name: '',
  code: '',
  status: '启用',
  sort_order: 0,
  description: ''
})

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入产品名称', trigger: 'blur' },
    { min: 1, max: 100, message: '长度在1-100个字符', trigger: 'blur' }
  ],
  code: [
    { pattern: /^[A-Za-z0-9_]*$/, message: '产品编码只能包含字母、数字和下划线', trigger: 'blur' },
    { max: 50, message: '最大长度50个字符', trigger: 'blur' }
  ],
  status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ],
  sort_order: [
    { type: 'number', min: 0, max: 9999, message: '排序序号范围0-9999', trigger: 'blur' }
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
    
    const data = await getProductList(params)
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
  searchForm.name = ''
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

// 新建产品
const handleCreate = async () => {
  isEdit.value = false
  dialogTitle.value = '新建产品'
  resetForm()
  
  // 设置默认排序序号为当前最大值+1
  if (tableData.value.length > 0) {
    const maxOrder = Math.max(...tableData.value.map(item => item.sort_order || 0))
    formData.sort_order = maxOrder + 1
  } else {
    formData.sort_order = 0
  }
  
  dialogVisible.value = true
}

// 编辑产品
const handleEdit = (row) => {
  isEdit.value = true
  editId.value = row.id
  dialogTitle.value = '编辑产品'
  
  Object.assign(formData, {
    name: row.name,
    code: row.code || '',
    status: row.status,
    sort_order: row.sort_order || 0,
    description: row.description || ''
  })
  
  dialogVisible.value = true
}

// 启用/禁用产品
const handleToggleStatus = (row) => {
  const newStatus = row.status === '启用' ? '禁用' : '启用'
  const message = newStatus === '启用' 
    ? '确定要启用该产品吗？启用后将在下拉选择器中显示' 
    : '确定要禁用该产品吗？禁用后将不在下拉选择器中显示'
  
  ElMessageBox.confirm(message, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await updateProductStatus(row.id, newStatus)
      ElMessage.success('状态更新成功')
      loadData()
    } catch (error) {
      console.error('状态更新失败:', error)
    }
  }).catch(() => {})
}

// 删除产品
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
      await deleteProduct(row.id)
      ElMessage.success('删除成功')
      loadData()
    } catch (error) {
      console.error('删除失败:', error)
    }
  }).catch(() => {})
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
        await updateProduct(editId.value, submitData)
      } else {
        await createProduct(submitData)
      }
      
      ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
      dialogVisible.value = false
      loadData()
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
  formData.code = ''
  formData.status = '启用'
  formData.sort_order = 0
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
})

// 配置自动搜索
useAutoSearch({
  searchForm,
  currentPage,
  onSearch: loadData,
  inputFields: ['name'],
  selectFields: ['status'],
  debounceDelay: 500
})
</script>

<style scoped lang="less">
@import '@/assets/less/variables.less';
</style>
