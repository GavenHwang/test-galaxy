<template>
  <div class="test-task-form-container">
    <el-card class="main-card">
      <template #header>
        <div class="card-header">
          <span>{{ pageTitle }}</span>
          <div class="header-actions">
            <el-button @click="handleCancel">取消</el-button>
            <el-button type="primary" @click="handleSubmit" :loading="submitting">提交</el-button>
          </div>
        </div>
      </template>

      <el-steps :active="currentStep" finish-status="success" align-center style="margin-bottom: 30px">
        <el-step title="基本信息" />
        <el-step title="执行配置" />
        <el-step title="选择测试内容" />
        <el-step title="确认提交" />
      </el-steps>

      <!-- 步骤1: 基本信息 -->
      <div v-show="currentStep === 0">
        <el-form :model="formData" :rules="formRules" ref="formRef" label-width="100px">
          <el-form-item label="所属产品" prop="product">
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
          <el-descriptions-item label="所属产品">{{ formData.product }}</el-descriptions-item>
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

      <!-- 步骤按钮 -->
      <div class="step-buttons">
        <el-button @click="handlePrevStep" v-if="currentStep > 0">上一步</el-button>
        <el-button type="primary" @click="handleNextStep" v-if="currentStep < 3">下一步</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  createTestTask,
  updateTestTask,
  getTestTaskDetail,
  getTestSuites,
  getTestCases,
  getAllProducts
} from '@/api/uitest'

const route = useRoute()
const router = useRouter()

// 页面模式
const taskId = computed(() => route.params.id)
const isNew = computed(() => route.path.endsWith('/new'))
const isEdit = computed(() => route.path.includes('/edit'))
const pageTitle = computed(() => {
  if (isNew.value) return '新建测试单'
  if (isEdit.value) return '编辑测试单'
  return '查看测试单'
})

// 表单相关
const formRef = ref(null)
const submitting = ref(false)
const currentStep = ref(0)
const contentTab = ref('suite')

// 表单数据
const formData = reactive({
  product: '',
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

// 选项数据
const productOptions = ref([])
const selectedSuites = ref([])
const selectedCases = ref([])
const availableSuites = ref([])
const availableCases = ref([])

// 表单验证规则
const formRules = {
  product: [
    { required: true, message: '请选择产品', trigger: 'change' }
  ],
  name: [
    { required: true, message: '请输入测试单名称', trigger: 'blur' }
  ],
  environment: [
    { required: true, message: '请输入测试环境', trigger: 'blur' }
  ]
}

// 加载产品列表
const loadProducts = async () => {
  try {
    const products = await getAllProducts()
    productOptions.value = products || []
  } catch (error) {
    console.error('加载产品失败:', error)
  }
}

// 加载可用套件和用例
const loadAvailableContent = async () => {
  try {
    // 加载套件
    const suiteData = await getTestSuites({ page: 1, page_size: 1000 })
    availableSuites.value = suiteData.items.map(item => ({
      id: item.id,
      name: item.name
    }))
    
    // 加载用例
    const caseData = await getTestCases({ page: 1, page_size: 1000, status: '激活' })
    availableCases.value = caseData.items.map(item => ({
      id: item.id,
      name: item.name
    }))
  } catch (error) {
    console.error('加载可用内容失败:', error)
  }
}

// 加载测试单详情
const loadTaskDetail = async () => {
  if (isNew.value) return
  
  try {
    const data = await getTestTaskDetail(taskId.value)
    Object.assign(formData, {
      product: data.product || '',
      name: data.name,
      description: data.description || '',
      environment: data.environment,
      execute_config: data.execute_config || formData.execute_config
    })
    
    // 加载已选的套件和用例
    if (data.suite_ids) {
      selectedSuites.value = data.suite_ids
    }
    if (data.case_ids) {
      selectedCases.value = data.case_ids
    }
  } catch (error) {
    console.error('加载测试单失败:', error)
  }
}

// 上一步
const handlePrevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

// 下一步
const handleNextStep = async () => {
  // 第一步需要验证表单
  if (currentStep.value === 0) {
    try {
      await formRef.value.validate()
    } catch (error) {
      return
    }
  }
  
  // 第三步需要验证是否选择了测试内容
  if (currentStep.value === 2) {
    if (selectedSuites.value.length === 0 && selectedCases.value.length === 0) {
      ElMessage.warning('请至少选择一个测试套件或测试用例')
      return
    }
  }
  
  if (currentStep.value < 3) {
    currentStep.value++
  }
}

// 提交
const handleSubmit = async () => {
  if (submitting.value) return
  
  submitting.value = true
  try {
    const submitData = {
      product: formData.product,
      name: formData.name,
      description: formData.description,
      environment: formData.environment,
      execute_config: formData.execute_config,
      suite_ids: selectedSuites.value,
      case_ids: selectedCases.value
    }
    
    if (isEdit.value) {
      await updateTestTask(taskId.value, submitData)
      ElMessage.success('更新成功')
    } else {
      await createTestTask(submitData)
      ElMessage.success('创建成功')
    }
    
    router.push('/ui-test/test-tasks')
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error(error.message || '提交失败')
  } finally {
    submitting.value = false
  }
}

// 取消
const handleCancel = () => {
  router.back()
}

// 页面初始化
onMounted(() => {
  loadProducts()
  loadAvailableContent()
  loadTaskDetail()
})
</script>

<style scoped>
.test-task-form-container {
  padding: 20px;
}

.main-card {
  min-height: calc(100vh - 120px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.step-buttons {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}
</style>
