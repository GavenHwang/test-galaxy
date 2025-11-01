<template>
  <div class="env-container">
    <div class="user-header">
      <el-button type="primary" plain @click="dialogFormVisible = true">新增</el-button>
      <el-form :inline="true">
        <el-form-item>
          <el-input placeholder="请输入用户名" v-model="username"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
        </el-form-item>
      </el-form>
    </div>
    <div class="table">
      <el-table :data="tableData" style="width: 100%; margin-bottom: 20px;" border class="centered-table">
        <el-table-column fixed prop="name" label="用户名" align="center"/>
        <el-table-column
            prop="role"
            label="角色"
            :formatter="(row, column, cellValue) => {
                    if (cellValue === 'superuser') return '管理员';
                    if (cellValue === 'common') return '普通用户';
                    return '其他';
                }"
            align="center"
        />
        <!-- <el-table-column prop="state" label="是否活跃" /> -->
        <el-table-column prop="create_time" label="创建时间" align="center"/>
        <el-table-column prop="last_time" label="最后登录时间" align="center"/>
        <el-table-column fixed="right" label="操作" width="200" align="center">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleRestPwd(row.id)">
              重置密码
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <!-- 分页 -->
      <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          style="justify-content: flex-end;"
      />
    </div>
    <el-dialog
        v-model="dialogFormVisible"
        title="添加用户"
        width="500"
        @close="handleDialogClose"
    >
      <!-- 添加 ref 和 rules -->
      <el-form :model="form" :rules="rules" ref="userFormRef">
        <el-form-item label="用户名" :label-width="formLabelWidth" prop="name">
          <el-input v-model="form.name" placeholder="请输入用户名"/>
        </el-form-item>

        <el-form-item label="用户类型" :label-width="formLabelWidth" prop="role">
          <el-select v-model="form.role" placeholder="请选择用户角色" style="width: 100%">
            <el-option
                v-for="item in roleOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
            />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="handleCancel">取消</el-button>
          <el-button type="primary" @click="handleSubmit">提交</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import {ref, onMounted, getCurrentInstance, reactive} from 'vue';

// 表格数据
const tableData = ref([])
// 请求代理
const {proxy} = getCurrentInstance()

// 分页数据
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 弹窗控制
const dialogFormVisible = ref(false)
const formLabelWidth = '140px'

// 搜索框的值
const username = ref(''); // 响应式数据

// 添加用户表单数据
const form = reactive({
  name: '',
  role: ''
})

// 表单验证规则
const validateUsername = (rule, value, callback) => {
  const commonUsernameRegex = /^[A-Za-z][A-Za-z0-9_]{1,19}$/
  if (!value) {
    return callback(new Error('请输入用户名'))
  }
  if (!commonUsernameRegex.test(value)) {
    return callback(new Error('用户名由2-20位字母、数字、下划线组成，且必须以字母开头'))
  }
  callback()
}
// 表单验证规则
const rules = {
  name: [
    {validator: validateUsername, trigger: 'blur'}
  ],
  role: [
    {required: true, message: '请选择用户角色', trigger: 'change'} // select 推荐用 change
  ]
}
// 用户表单
const userFormRef = ref(null)

// 角色选项
const roleOptions = ref([
  {label: '管理员', value: 'superuser'},
  {label: '普通成员', value: 'common'}
])

// 请求参数 & 获取数据
const fetchTableData = async () => {
  const request_user_data = ref({page: currentPage.value, size: pageSize.value, username: username.value})
  try {
    const userData = await proxy.$api.getUserData(request_user_data.value)
    tableData.value = userData.data
    total.value = userData.total
  } catch (err) {

  }
}

// 添加用户提交表单（带验证）
const handleSubmit = async () => {
  if (!userFormRef.value) return

  try {
    // 先校验
    await userFormRef.value.validate()

    // 校验通过，提交数据
    await proxy.$api.addUser({
      name: form.name.trim(),
      role: form.role
    })

    proxy.$message.success('用户添加成功')
    dialogFormVisible.value = false // 关闭弹窗 → 自动清空（通过 @close）
    fetchTableData() // 刷新列表
  } catch (error) {
    // 如果是校验失败，validate() 会自动提示，无需额外处理
    if (error !== 'error') {
      proxy.$message.error('添加用户失败，请稍后重试')
    }
  }
}

// 取消并清空
const handleCancel = () => {
  dialogFormVisible.value = false
  if (userFormRef.value) {
    userFormRef.value.resetFields() // 清空字段 + 清除校验提示
  }
}

// 关闭弹窗时清空表单
const handleDialogClose = () => {
  if (userFormRef.value) {
    userFormRef.value.resetFields() // 清空字段 + 清除校验提示
  }
}

// 点击搜索
const handleSearch = () => {
  currentPage.value = 1

  fetchTableData()
}
// 分页事件
const handleSizeChange = (val) => {
  pageSize.value = val
  fetchTableData()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchTableData()
}

// 操作按钮（示例）
const handleRestPwd = async (id) => {
  try {
    // 校验通过，提交数据
    await proxy.$api.resetPassword({
      user_id: id,
    })

    proxy.$message.success('重置密码成功')
  } catch (error) {
    // 如果是删除失败，validate() 会自动提示，无需额外处理
    if (error !== 'error') {
      proxy.$message.error('重置密码失败，请稍后重试')
    }
  }
}
const handleDelete = async (id) => {
  try {
    // 校验通过，提交数据
    await proxy.$api.deleteUser({
      user_id: id,
    })

    proxy.$message.success('删除用户成功')
    fetchTableData() // 刷新列表
  } catch (error) {
    // 如果是删除失败，validate() 会自动提示，无需额外处理
    if (error !== 'error') {
      proxy.$message.error('删除用户失败，请稍后重试')
    }
  }
}

// 初始化
onMounted(() => {
  fetchTableData()
})
</script>

<style scoped lang="less">
.env-container {
  padding: 24px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  min-height: calc(100vh - 180px);
}

.user-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;

  .el-button {
    height: 36px;
    border-radius: 6px;
    font-weight: 500;
  }

  .el-form {
    margin-bottom: 0;
  }

  .el-input {
    width: 240px;
    
    :deep(.el-input__wrapper) {
      border-radius: 6px;
    }
  }
}

.table {
  .el-table {
    border-radius: 8px;
    overflow: hidden;
    
    :deep(.el-table__header) {
      th {
        background-color: #fafafa;
        font-weight: 600;
        color: #333;
        font-size: 14px;
      }
    }

    :deep(.el-table__row) {
      transition: all 0.3s;
      
      &:hover {
        background-color: #f5f7fa;
      }
    }

    :deep(.el-table__cell) {
      padding: 14px 0;
    }

    :deep(.el-button) {
      border-radius: 4px;
      font-size: 13px;
      padding: 6px 12px;
      transition: all 0.3s;
      
      &:hover {
        transform: translateY(-1px);
      }
    }
  }

  .el-pagination {
    margin-top: 20px;
    padding: 16px 0;
  }
}

.centered-table {
  :deep(.el-table__cell) {
    text-align: center !important;
  }
  
  :deep(.el-table__header th) {
    text-align: center !important;
  }
}

// 对话框样式优化
:deep(.el-dialog) {
  border-radius: 12px;
  
  .el-dialog__header {
    padding: 20px 24px;
    border-bottom: 1px solid #f0f0f0;
    
    .el-dialog__title {
      font-size: 18px;
      font-weight: 600;
      color: #333;
    }
  }

  .el-dialog__body {
    padding: 24px;
  }

  .el-dialog__footer {
    padding: 16px 24px;
    border-top: 1px solid #f0f0f0;
    
    .dialog-footer {
      .el-button {
        border-radius: 6px;
        padding: 10px 24px;
        font-weight: 500;
      }
    }
  }

  .el-form-item {
    margin-bottom: 20px;
    
    .el-input {
      :deep(.el-input__wrapper) {
        border-radius: 6px;
      }
    }

    .el-select {
      :deep(.el-input__wrapper) {
        border-radius: 6px;
      }
    }
  }
}
</style>
