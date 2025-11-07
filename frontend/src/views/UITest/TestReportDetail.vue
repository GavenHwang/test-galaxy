<template>
  <div class="test-report-detail-container">
    <div v-if="reportData" v-loading="loading">
      <!-- 报告概览 -->
      <el-card class="summary-card">
        <template #header>
          <div class="card-header">
            <span>报告详情</span>
            <el-button text @click="goBack">返回列表</el-button>
          </div>
        </template>
        
        <el-descriptions :column="3" border>
          <el-descriptions-item label="测试单名称">{{ reportData.test_task_name }}</el-descriptions-item>
          <el-descriptions-item label="测试单ID">
            <el-link type="primary" @click="goToTask(reportData.test_task_id)">
              {{ reportData.test_task_id }}
            </el-link>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ reportData.created_time }}</el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ reportData.start_time || '-' }}</el-descriptions-item>
          <el-descriptions-item label="结束时间">{{ reportData.end_time || '-' }}</el-descriptions-item>
          <el-descriptions-item label="执行时长">{{ formatDuration(reportData.execution_duration) }}</el-descriptions-item>
        </el-descriptions>
        
        <div class="statistics-area">
          <div class="stat-item">
            <div class="stat-value">{{ reportData.total_cases }}</div>
            <div class="stat-label">总用例数</div>
          </div>
          <div class="stat-item success">
            <div class="stat-value">{{ reportData.passed_cases }}</div>
            <div class="stat-label">通过</div>
          </div>
          <div class="stat-item danger">
            <div class="stat-value">{{ reportData.failed_cases }}</div>
            <div class="stat-label">失败</div>
          </div>
          <div class="stat-item info">
            <div class="stat-value">{{ reportData.skipped_cases }}</div>
            <div class="stat-label">跳过</div>
          </div>
          <div class="stat-item warning">
            <div class="stat-value">{{ Math.round(reportData.pass_rate) }}%</div>
            <div class="stat-label">通过率</div>
          </div>
        </div>
        
        <!-- 通过率图表 -->
        <div class="chart-container">
          <div ref="passRateChart" style="width: 100%; height: 350px"></div>
        </div>
      </el-card>

      <!-- 用例执行详情 -->
      <el-card class="detail-card">
        <template #header>
          <div class="card-header">
            <span>用例执行详情</span>
          </div>
        </template>
        
        <el-tabs v-model="activeTab">
          <el-tab-pane label="全部用例" name="all">
            <el-table :data="allCases" border stripe max-height="600">
              <el-table-column type="expand">
                <template #default="{ row }">
                  <div class="step-details">
                    <h4>执行步骤详情</h4>
                    <el-table :data="row.steps" border size="small">
                      <el-table-column prop="step_number" label="步骤序号" width="100" align="center" />
                      <el-table-column prop="action" label="操作类型" width="120" align="center" />
                      <el-table-column prop="description" label="操作描述" show-overflow-tooltip />
                      <el-table-column prop="input_data" label="输入数据" width="150" show-overflow-tooltip />
                      <el-table-column prop="status" label="状态" width="100" align="center">
                        <template #default="{ row: step }">
                          <el-tag :type="step.status === '通过' ? 'success' : 'danger'" size="small">
                            {{ step.status === '通过' ? '通过' : '失败' }}
                          </el-tag>
                        </template>
                      </el-table-column>
                      <el-table-column prop="duration" label="耗时" width="100" align="center">
                        <template #default="{ row: step }">
                          {{ formatDurationMs(step.duration) }}
                        </template>
                      </el-table-column>
                      <el-table-column prop="error_message" label="错误信息" show-overflow-tooltip />
                      <el-table-column label="截图" width="100" align="center">
                        <template #default="{ row: step }">
                          <el-button 
                            v-if="step.screenshot_path" 
                            text 
                            type="primary" 
                            size="small"
                            @click="viewScreenshot(step.screenshot_path)"
                          >
                            查看截图
                          </el-button>
                        </template>
                      </el-table-column>
                    </el-table>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="test_case_id" label="用例ID" width="100" />
              <el-table-column prop="status" label="状态" width="100" align="center">
                <template #default="{ row }">
                  <el-tag :type="row.status === '通过' ? 'success' : 'danger'" size="small">
                    {{ row.status === '通过' ? '通过' : '失败' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="duration" label="执行时长" width="120" align="center">
                <template #default="{ row }">
                  {{ formatDuration(row.duration) }}
                </template>
              </el-table-column>
              <el-table-column prop="start_time" label="开始时间" width="180" />
              <el-table-column prop="end_time" label="结束时间" width="180" />
              <el-table-column prop="error_message" label="错误信息" show-overflow-tooltip />
            </el-table>
          </el-tab-pane>
          
          <el-tab-pane label="失败用例" name="failed">
            <el-table :data="failedCases" border stripe max-height="600">
              <el-table-column type="expand">
                <template #default="{ row }">
                  <div class="step-details">
                    <h4>执行步骤详情</h4>
                    <el-table :data="row.steps" border size="small">
                      <el-table-column prop="step_number" label="步骤序号" width="100" align="center" />
                      <el-table-column prop="action" label="操作类型" width="120" align="center" />
                      <el-table-column prop="description" label="操作描述" show-overflow-tooltip />
                      <el-table-column prop="input_data" label="输入数据" width="150" show-overflow-tooltip />
                      <el-table-column prop="status" label="状态" width="100" align="center">
                        <template #default="{ row: step }">
                          <el-tag :type="step.status === '通过' ? 'success' : 'danger'" size="small">
                            {{ step.status === '通过' ? '通过' : '失败' }}
                          </el-tag>
                        </template>
                      </el-table-column>
                      <el-table-column prop="duration" label="耗时" width="100" align="center">
                        <template #default="{ row: step }">
                          {{ formatDurationMs(step.duration) }}
                        </template>
                      </el-table-column>
                      <el-table-column prop="error_message" label="错误信息" show-overflow-tooltip />
                      <el-table-column label="截图" width="100" align="center">
                        <template #default="{ row: step }">
                          <el-button 
                            v-if="step.screenshot_path" 
                            text 
                            type="primary" 
                            size="small"
                            @click="viewScreenshot(step.screenshot_path)"
                          >
                            查看截图
                          </el-button>
                        </template>
                      </el-table-column>
                    </el-table>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="test_case_id" label="用例ID" width="100" />
              <el-table-column prop="duration" label="执行时长" width="120" align="center">
                <template #default="{ row }">
                  {{ formatDuration(row.duration) }}
                </template>
              </el-table-column>
              <el-table-column prop="error_message" label="错误信息" show-overflow-tooltip />
              <el-table-column label="失败步骤" width="100" align="center">
                <template #default="{ row }">
                  {{ row.steps.filter(s => s.status === '失败').length }}
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </div>

    <!-- 截图查看对话框 -->
    <el-dialog v-model="screenshotVisible" title="执行截图" width="80%">
      <img :src="currentScreenshot" style="width: 100%" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getTestReportDetail } from '@/api/uitest'
import * as echarts from 'echarts'

const route = useRoute()
const router = useRouter()

// 数据
const reportData = ref(null)
const loading = ref(false)
const activeTab = ref('all')
const screenshotVisible = ref(false)
const currentScreenshot = ref('')
const passRateChart = ref(null)

// 计算属性
const allCases = computed(() => {
  return reportData.value?.cases || []
})

const failedCases = computed(() => {
  return allCases.value.filter(c => c.status === '失败')
})

// 格式化时长（秒）
const formatDuration = (seconds) => {
  if (!seconds) return '-'
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)
  
  if (hours > 0) {
    return `${hours}时${minutes}分${secs}秒`
  } else if (minutes > 0) {
    return `${minutes}分${secs}秒`
  } else {
    return `${secs}秒`
  }
}

// 格式化时长（毫秒）
const formatDurationMs = (milliseconds) => {
  if (!milliseconds) return '-'
  const seconds = milliseconds / 1000
  
  if (seconds < 1) {
    return `${milliseconds}毫秒`
  }
  
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = (seconds % 60).toFixed(2)
  
  if (hours > 0) {
    return `${hours}时${minutes}分${secs}秒`
  } else if (minutes > 0) {
    return `${minutes}分${secs}秒`
  } else {
    return `${secs}秒`
  }
}

// 查看截图
const viewScreenshot = (path) => {
  currentScreenshot.value = path
  screenshotVisible.value = true
}

// 返回列表
const goBack = () => {
  router.push('/ui-test/test-reports')
}

// 跳转到测试单详情
const goToTask = (taskId) => {
  router.push(`/ui-test/test-tasks/${taskId}`)
}

// 初始化图表
const initCharts = () => {
  if (!passRateChart.value || !reportData.value) return
  
  const chart = echarts.init(passRateChart.value)
  
  const option = {
    title: {
      text: '测试结果分布',
      left: 'center',
      top: 10  // 调高标题位置到距离顶部 10px
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      data: ['通过', '失败', '跳过']
    },
    series: [
      {
        name: '测试结果',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['50%', '55%'],  // 调整饼图垂直居中位置
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}: {c}'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 20,
            fontWeight: 'bold'
          }
        },
        data: [
          { 
            value: reportData.value.passed_cases, 
            name: '通过',
            itemStyle: { color: '#67C23A' }
          },
          { 
            value: reportData.value.failed_cases, 
            name: '失败',
            itemStyle: { color: '#F56C6C' }
          },
          { 
            value: reportData.value.skipped_cases, 
            name: '跳过',
            itemStyle: { color: '#909399' }
          }
        ]
      }
    ]
  }
  
  chart.setOption(option)
  
  // 响应式调整
  window.addEventListener('resize', () => {
    chart.resize()
  })
}

// 加载报告详情
const loadReportDetail = async () => {
  loading.value = true
  try {
    const reportId = route.params.id
    const report = await getTestReportDetail(reportId)
    reportData.value = report
    
    // 等待DOM更新后初始化图表
    await nextTick()
    initCharts()
  } catch (error) {
    console.error('加载报告详情失败:', error)
  } finally {
    loading.value = false
  }
}

// 页面加载
onMounted(() => {
  loadReportDetail()
})
</script>

<style scoped lang="less">
.test-report-detail-container {
  padding: 20px;
  
  .summary-card {
    margin-bottom: 20px;
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .statistics-area {
      display: flex;
      justify-content: space-around;
      padding: 30px 0;
      margin-top: 20px;
      
      .stat-item {
        text-align: center;
        
        .stat-value {
          font-size: 36px;
          font-weight: bold;
          color: #303133;
        }
        
        .stat-label {
          margin-top: 10px;
          font-size: 14px;
          color: #909399;
        }
        
        &.success .stat-value {
          color: #67C23A;
        }
        
        &.danger .stat-value {
          color: #F56C6C;
        }
        
        &.info .stat-value {
          color: #909399;
        }
        
        &.warning .stat-value {
          color: #E6A23C;
        }
      }
    }
    
    .chart-container {
      margin-top: 20px;
      padding: 20px;
      background: #f5f7fa;
      border-radius: 4px;
    }
  }
  
  .detail-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .step-details {
      padding: 20px;
      background: #f5f7fa;
      
      h4 {
        margin-bottom: 15px;
        color: #303133;
      }
    }
  }
}
</style>
