<template>
  <div class="test-case-detail-container">
    <!-- 主内容区 -->
    <el-card class="main-card">
      <template #header>
        <div class="card-header">
          <span>{{ pageTitle }}</span>
          <div class="header-actions">
            <el-button @click="handleCancel">取消</el-button>
            <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
          </div>
        </div>
      </template>

      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="120px">
        <!-- 基本信息 -->
        <el-divider content-position="left">基本信息</el-divider>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="用例名称" prop="name">
              <el-input v-model="formData.name" placeholder="请输入用例名称" :disabled="isView" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="所属模块" prop="module">
              <el-select 
                v-model="formData.module" 
                placeholder="请选择或输入模块" 
                filterable 
                allow-create
                :disabled="isView"
                style="width: 100%"
              >
                <el-option v-for="item in moduleOptions" :key="item" :label="item" :value="item" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="优先级" prop="priority">
              <el-select v-model="formData.priority" placeholder="请选择优先级" :disabled="isView" style="width: 100%">
                <el-option label="高" value="高" />
                <el-option label="中" value="中" />
                <el-option label="低" value="低" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-select v-model="formData.status" placeholder="请选择状态" :disabled="isView" style="width: 100%">
                <el-option label="草稿" value="草稿" />
                <el-option label="激活" value="激活" />
                <el-option label="禁用" value="禁用" />
                <el-option label="归档" value="归档" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="标签" prop="tags">
          <el-select
            v-model="formData.tags"
            multiple
            filterable
            allow-create
            placeholder="输入标签后按回车添加"
            :disabled="isView"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="用例描述" prop="description">
          <el-input 
            v-model="formData.description" 
            type="textarea" 
            :rows="3" 
            placeholder="请输入用例描述"
            :disabled="isView"
          />
        </el-form-item>

        <el-form-item label="前置条件" prop="precondition">
          <el-input 
            v-model="formData.precondition" 
            type="textarea" 
            :rows="2" 
            placeholder="请输入前置条件"
            :disabled="isView"
          />
        </el-form-item>

        <el-form-item label="预期结果" prop="expected_result">
          <el-input 
            v-model="formData.expected_result" 
            type="textarea" 
            :rows="2" 
            placeholder="请输入预期结果"
            :disabled="isView"
          />
        </el-form-item>

        <!-- 测试步骤 -->
        <el-divider content-position="left">
          <span>测试步骤</span>
          <el-button v-if="!isView" type="primary" size="small" @click="handleAddStep" style="margin-left: 10px">
            <el-icon><Plus /></el-icon>
            添加步骤
          </el-button>
        </el-divider>

        <div class="steps-container">
          <el-empty v-if="formData.steps.length === 0" description="暂无测试步骤" />
          
          <draggable 
            v-else
            v-model="formData.steps" 
            item-key="id"
            handle=".drag-handle"
            @end="handleStepDragEnd"
            :disabled="isView"
          >
            <template #item="{ element: step, index }">
              <el-card class="step-card" :class="{ 'is-view': isView }">
                <div class="step-header">
                  <div class="step-number">
                    <el-icon class="drag-handle" v-if="!isView"><Rank /></el-icon>
                    <span>步骤 {{ index + 1 }}</span>
                  </div>
                  <el-button v-if="!isView" text type="danger" @click="handleDeleteStep(index)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>

                <el-form-item label="操作类型" :prop="`steps.${index}.action`" :rules="stepRules.action">
                  <el-select 
                    v-model="step.action" 
                    placeholder="请选择操作类型" 
                    :disabled="isView"
                    style="width: 100%"
                  >
                    <el-option v-for="item in actionOptions" :key="item.value" :label="item.label" :value="item.value" />
                  </el-select>
                </el-form-item>

                <el-form-item 
                  v-if="needsElement(step.action)" 
                  label="页面元素" 
                  :prop="`steps.${index}.element_id`"
                  :rules="stepRules.element_id"
                >
                  <el-select 
                    v-model="step.element_id" 
                    placeholder="请选择页面元素" 
                    filterable
                    :disabled="isView"
                    style="width: 100%"
                  >
                    <el-option 
                      v-for="element in elementOptions" 
                      :key="element.id" 
                      :label="`${element.name} (${element.selector_type})`" 
                      :value="element.id"
                    />
                  </el-select>
                </el-form-item>

                <el-form-item 
                  v-if="needsInputData(step.action)" 
                  label="输入数据" 
                  :prop="`steps.${index}.input_data`"
                  :rules="stepRules.input_data"
                >
                  <el-input 
                    v-model="step.input_data" 
                    placeholder="请输入数据"
                    :disabled="isView"
                  />
                </el-form-item>

                <el-form-item label="等待时间(ms)" :prop="`steps.${index}.wait_time`">
                  <el-input-number 
                    v-model="step.wait_time" 
                    :min="0" 
                    :max="60000" 
                    :step="1000"
                    :disabled="isView"
                  />
                </el-form-item>

                <el-form-item label="步骤描述" :prop="`steps.${index}.description`" :rules="stepRules.description">
                  <el-input 
                    v-model="step.description" 
                    placeholder="请输入步骤描述"
                    :disabled="isView"
                  />
                </el-form-item>
              </el-card>
            </template>
          </draggable>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, Delete, Rank } from '@element-plus/icons-vue'
import draggable from 'vuedraggable'
import {
  getTestCaseDetail,
  createTestCase,
  updateTestCase,
  getModules,
  getElements
} from '@/api/uitest'

const route = useRoute()
const router = useRouter()

// 页面模式
const caseId = computed(() => route.params.id)
const isNew = computed(() => route.path.endsWith('/new'))
const isEdit = computed(() => route.path.includes('/edit'))
const isView = computed(() => !isNew.value && !isEdit.value)
const pageTitle = computed(() => {
  if (isNew.value) return '新建测试用例'
  if (isEdit.value) return '编辑测试用例'
  return '查看测试用例'
})

// 表单数据
const formRef = ref(null)
const saving = ref(false)
const formData = reactive({
  name: '',
  description: '',
  priority: '中',
  module: '',
  tags: [],
  status: '草稿',
  precondition: '',
  expected_result: '',
  steps: []
})

// 选项数据
const moduleOptions = ref([])
const elementOptions = ref([])

// 操作类型选项
const actionOptions = [
  { label: '页面导航', value: 'navigate' },
  { label: '点击', value: 'click' },
  { label: '输入文本', value: 'type' },
  { label: '选择下拉', value: 'select' },
  { label: '等待', value: 'wait' },
  { label: '等待元素', value: 'wait_for_element' },
  { label: '断言文本', value: 'assert_text' },
  { label: '断言存在', value: 'assert_exists' },
  { label: '截图', value: 'screenshot' },
  { label: '悬停', value: 'hover' },
  { label: '清空输入', value: 'clear' },
  { label: '执行脚本', value: 'execute_script' }
]

// 判断是否需要元素
const needsElement = (action) => {
  return ['click', 'type', 'select', 'wait_for_element', 'assert_text', 'assert_exists', 'hover', 'clear'].includes(action)
}

// 判断是否需要输入数据
const needsInputData = (action) => {
  return ['navigate', 'type', 'select', 'assert_text', 'execute_script'].includes(action)
}

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入用例名称', trigger: 'blur' },
    { min: 1, max: 200, message: '长度在1-200个字符', trigger: 'blur' }
  ],
  priority: [
    { required: true, message: '请选择优先级', trigger: 'change' }
  ],
  status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ]
}

// 步骤验证规则
const stepRules = {
  action: [
    { required: true, message: '请选择操作类型', trigger: 'change' }
  ],
  element_id: [
    { required: true, message: '请选择页面元素', trigger: 'change' }
  ],
  input_data: [
    { required: true, message: '请输入数据', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入步骤描述', trigger: 'blur' }
  ]
}

// 加载用例详情
const loadCaseDetail = async () => {
  if (isNew.value) return
  
  try {
    const data = await getTestCaseDetail(caseId.value)
    Object.assign(formData, {
      name: data.name,
      description: data.description || '',
      priority: data.priority,
      module: data.module || '',
      tags: data.tags || [],
      status: data.status,
      precondition: data.precondition || '',
      expected_result: data.expected_result || '',
      steps: data.steps || []
    })
  } catch (error) {
    console.error('加载用例失败:', error)
  }
}

// 加载选项
const loadOptions = async () => {
  try {
    const [modules, elementsData] = await Promise.all([
      getModules(),
      getElements({ page: 1, page_size: 1000 })
    ])
    
    moduleOptions.value = modules || []
    elementOptions.value = elementsData.items || []
  } catch (error) {
    console.error('加载选项失败:', error)
  }
}

// 添加步骤
const handleAddStep = () => {
  formData.steps.push({
    id: Date.now(), // 临时ID
    action: '',
    element_id: null,
    input_data: '',
    wait_time: 0,
    description: '',
    sort_order: formData.steps.length + 1
  })
}

// 删除步骤
const handleDeleteStep = (index) => {
  formData.steps.splice(index, 1)
}

// 步骤拖拽结束
const handleStepDragEnd = () => {
  // 更新步骤顺序
  formData.steps.forEach((step, index) => {
    step.sort_order = index + 1
    step.step_number = index + 1
  })
}

// 保存
const handleSave = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    // 验证步骤
    if (formData.steps.length === 0) {
      ElMessage.warning('请至少添加一个测试步骤')
      return
    }
    
    saving.value = true
    try {
      const submitData = {
        name: formData.name,
        description: formData.description,
        priority: formData.priority,
        module: formData.module,
        tags: formData.tags,
        status: formData.status,
        precondition: formData.precondition,
        expected_result: formData.expected_result
      }
      
      let res
      if (isNew.value) {
        res = await createTestCase(submitData)
      } else {
        res = await updateTestCase(caseId.value, submitData)
      }
      
      ElMessage.success(isNew.value ? '创建成功' : '更新成功')
      
      // 保存步骤（这里简化处理，实际应该调用步骤API）
      // TODO: 调用步骤创建/更新API
      
      router.push('/ui-test/test-cases')
    } catch (error) {
      console.error('保存失败:', error)
    } finally {
      saving.value = false
    }
  })
}

// 取消
const handleCancel = () => {
  router.back()
}

// 页面加载
onMounted(() => {
  loadOptions()
  loadCaseDetail()
})
</script>

<style scoped lang="less">
.test-case-detail-container {
  padding: 20px;
  
  .main-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
  }
  
  .steps-container {
    margin-top: 20px;
    
    .step-card {
      margin-bottom: 15px;
      cursor: move;
      
      &.is-view {
        cursor: default;
      }
      
      .step-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
        
        .step-number {
          display: flex;
          align-items: center;
          gap: 10px;
          font-weight: bold;
          
          .drag-handle {
            cursor: move;
            font-size: 18px;
            color: #909399;
          }
        }
      }
    }
  }
}
</style>
