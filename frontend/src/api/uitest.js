/**
 * UI测试相关API接口
 */
import request from './request'

/**
 * 产品管理API
 */

// 创建产品
export const createProduct = (data) => {
  return request({
    url: '/api/products',
    method: 'post',
    data
  })
}

// 获取产品列表（分页）
export const getProductList = (params) => {
  return request({
    url: '/api/products',
    method: 'get',
    params
  })
}

// 获取所有启用的产品（不分页，供下拉选择器使用）
export const getAllProducts = () => {
  return request({
    url: '/api/products/all',
    method: 'get'
  })
}

// 获取单个产品详情
export const getProductDetail = (productId) => {
  return request({
    url: `/api/products/${productId}`,
    method: 'get'
  })
}

// 更新产品
export const updateProduct = (productId, data) => {
  return request({
    url: `/api/products/${productId}`,
    method: 'put',
    data
  })
}

// 删除产品
export const deleteProduct = (productId) => {
  return request({
    url: `/api/products/${productId}`,
    method: 'delete'
  })
}

// 更新产品状态
export const updateProductStatus = (productId, status) => {
  return request({
    url: `/api/products/${productId}/status`,
    method: 'patch',
    data: { status }
  })
}

/**
 * 测试用户管理API
 */

// 创建测试用户
export const createTestUser = (data) => {
  return request({
    url: '/api/ui-test/test-users',
    method: 'post',
    data
  })
}

// 获取测试用户列表
export const getTestUsers = (params) => {
  return request({
    url: '/api/ui-test/test-users',
    method: 'get',
    params
  })
}

// 获取单个测试用户详情
export const getTestUserDetail = (userId) => {
  return request({
    url: `/api/ui-test/test-users/${userId}`,
    method: 'get'
  })
}

// 更新测试用户
export const updateTestUser = (userId, data) => {
  return request({
    url: `/api/ui-test/test-users/${userId}`,
    method: 'put',
    data
  })
}

// 删除测试用户
export const deleteTestUser = (userId, force = false) => {
  return request({
    url: `/api/ui-test/test-users/${userId}`,
    method: 'delete',
    params: { force }
  })
}

// 获取产品列表
export const getProducts = () => {
  return request({
    url: '/api/ui-test/test-users/products/list',
    method: 'get'
  })
}

// 获取角色列表
export const getRoles = (product) => {
  return request({
    url: '/api/ui-test/test-users/roles/list',
    method: 'get',
    params: product ? { product } : {}
  })
}

/**
 * 页面元素管理API
 */

// 创建页面元素
export const createElement = (data) => {
  return request({
    url: '/api/ui-test/elements',
    method: 'post',
    data
  })
}

// 获取页面元素列表
export const getElements = (params) => {
  return request({
    url: '/api/ui-test/elements',
    method: 'get',
    params
  })
}

// 获取单个页面元素详情
export const getElementDetail = (elementId) => {
  return request({
    url: `/api/ui-test/elements/${elementId}`,
    method: 'get'
  })
}

// 更新页面元素
export const updateElement = (elementId, data) => {
  return request({
    url: `/api/ui-test/elements/${elementId}`,
    method: 'put',
    data
  })
}

// 删除页面元素
export const deleteElement = (elementId) => {
  return request({
    url: `/api/ui-test/elements/${elementId}`,
    method: 'delete'
  })
}

// 批量创建页面元素
export const batchCreateElements = (data) => {
  return request({
    url: '/api/ui-test/elements/batch',
    method: 'post',
    data
  })
}

// 获取元素关联的测试用例
export const getElementRelatedCases = (elementId) => {
  return request({
    url: `/api/ui-test/elements/${elementId}/related-cases`,
    method: 'get'
  })
}

// 获取元素权限
export const getElementPermissions = (elementId) => {
  return request({
    url: `/api/ui-test/elements/${elementId}/permissions`,
    method: 'get'
  })
}

// 设置元素权限
export const setElementPermissions = (elementId, data) => {
  return request({
    url: `/api/ui-test/elements/${elementId}/permissions`,
    method: 'post',
    data
  })
}

// 获取页面列表
export const getPages = () => {
  return request({
    url: '/api/ui-test/elements/pages/list',
    method: 'get'
  })
}

// 获取测试用例模块列表
export const getModules = () => {
  return request({
    url: '/api/ui-test/test-cases/modules/list',
    method: 'get'
  })
}

/**
 * 测试用例管理API
 */

// 创建测试用例
export const createTestCase = (data) => {
  return request({
    url: '/api/ui-test/test-cases',
    method: 'post',
    data
  })
}

// 获取测试用例列表
export const getTestCases = (params) => {
  return request({
    url: '/api/ui-test/test-cases',
    method: 'get',
    params
  })
}

// 获取单个测试用例详情
export const getTestCaseDetail = (caseId) => {
  return request({
    url: `/api/ui-test/test-cases/${caseId}`,
    method: 'get'
  })
}

// 更新测试用例
export const updateTestCase = (caseId, data) => {
  return request({
    url: `/api/ui-test/test-cases/${caseId}`,
    method: 'put',
    data
  })
}

// 删除测试用例
export const deleteTestCase = (caseId, force = false) => {
  return request({
    url: `/api/ui-test/test-cases/${caseId}`,
    method: 'delete',
    params: { force }
  })
}

// 复制测试用例
export const copyTestCase = (caseId) => {
  return request({
    url: `/api/ui-test/test-cases/${caseId}/copy`,
    method: 'post'
  })
}

// 更新用例状态
export const updateCaseStatus = (caseId, status) => {
  return request({
    url: `/api/ui-test/test-cases/${caseId}/status`,
    method: 'patch',
    params: { status }
  })
}

// 获取测试步骤列表
export const getTestSteps = (caseId) => {
  return request({
    url: `/api/ui-test/test-cases/${caseId}/steps`,
    method: 'get'
  })
}

// 创建测试步骤
export const createTestStep = (caseId, data) => {
  return request({
    url: `/api/ui-test/test-cases/${caseId}/steps`,
    method: 'post',
    data
  })
}

// 更新测试步骤
export const updateTestStep = (stepId, data) => {
  return request({
    url: `/api/ui-test/test-cases/steps/${stepId}`,
    method: 'put',
    data
  })
}

// 删除测试步骤
export const deleteTestStep = (stepId) => {
  return request({
    url: `/api/ui-test/test-cases/steps/${stepId}`,
    method: 'delete'
  })
}

// 调整步骤顺序
export const reorderSteps = (caseId, stepIds) => {
  return request({
    url: `/api/ui-test/test-cases/${caseId}/steps/reorder`,
    method: 'post',
    data: stepIds
  })
}

// 获取用例权限
export const getCasePermissions = (caseId) => {
  return request({
    url: `/api/ui-test/test-cases/${caseId}/permissions`,
    method: 'get'
  })
}

// 设置用例权限
export const setCasePermissions = (caseId, roles) => {
  return request({
    url: `/api/ui-test/test-cases/${caseId}/permissions`,
    method: 'post',
    data: roles
  })
}

// 获取执行历史
export const getCaseExecutions = (caseId, params) => {
  return request({
    url: `/api/ui-test/test-cases/${caseId}/executions`,
    method: 'get',
    params
  })
}

// 获取执行趋势
export const getExecutionTrend = (caseId, days = 30) => {
  return request({
    url: `/api/ui-test/test-cases/${caseId}/execution-trend`,
    method: 'get',
    params: { days }
  })
}

// 批量更新状态
export const batchUpdateCaseStatus = (caseIds, status) => {
  return request({
    url: '/api/ui-test/test-cases/batch-update-status',
    method: 'post',
    data: { case_ids: caseIds, status }
  })
}

/**
 * 测试套件管理API
 */

// 创建测试套件
export const createTestSuite = (data) => {
  return request({
    url: '/api/ui-test/test-suites',
    method: 'post',
    data
  })
}

// 获取测试套件列表
export const getTestSuites = (params) => {
  return request({
    url: '/api/ui-test/test-suites',
    method: 'get',
    params
  })
}

// 获取单个测试套件详情
export const getTestSuiteDetail = (suiteId) => {
  return request({
    url: `/api/ui-test/test-suites/${suiteId}`,
    method: 'get'
  })
}

// 更新测试套件
export const updateTestSuite = (suiteId, data) => {
  return request({
    url: `/api/ui-test/test-suites/${suiteId}`,
    method: 'put',
    data
  })
}

// 删除测试套件
export const deleteTestSuite = (suiteId, force = false) => {
  return request({
    url: `/api/ui-test/test-suites/${suiteId}`,
    method: 'delete',
    params: { force }
  })
}

// 预览匹配用例
export const previewMatchedCases = (suiteId, filterConditions) => {
  return request({
    url: `/api/ui-test/test-suites/${suiteId}/preview`,
    method: 'post',
    data: filterConditions
  })
}

// 获取套件用例
export const getSuiteCases = (suiteId) => {
  return request({
    url: `/api/ui-test/test-suites/${suiteId}/cases`,
    method: 'get'
  })
}

// 添加用例到套件
export const addCasesToSuite = (suiteId, caseIds) => {
  return request({
    url: `/api/ui-test/test-suites/${suiteId}/cases`,
    method: 'post',
    data: caseIds
  })
}

// 从套件移除用例
export const removeCaseFromSuite = (suiteId, caseId) => {
  return request({
    url: `/api/ui-test/test-suites/${suiteId}/cases/${caseId}`,
    method: 'delete'
  })
}

// 调整用例顺序
export const reorderSuiteCases = (suiteId, caseIds) => {
  return request({
    url: `/api/ui-test/test-suites/${suiteId}/cases/reorder`,
    method: 'post',
    data: caseIds
  })
}

// 同步筛选条件
export const syncSuiteCases = (suiteId) => {
  return request({
    url: `/api/ui-test/test-suites/${suiteId}/sync`,
    method: 'post'
  })
}

/**
 * 测试单管理API
 */

// 创建测试单
export const createTestTask = (data) => {
  return request({
    url: '/api/ui-test/test-tasks',
    method: 'post',
    data
  })
}

// 获取测试单列表
export const getTestTasks = (params) => {
  return request({
    url: '/api/ui-test/test-tasks',
    method: 'get',
    params
  })
}

// 获取单个测试单详情
export const getTestTaskDetail = (taskId) => {
  return request({
    url: `/api/ui-test/test-tasks/${taskId}`,
    method: 'get'
  })
}

// 更新测试单
export const updateTestTask = (taskId, data) => {
  return request({
    url: `/api/ui-test/test-tasks/${taskId}`,
    method: 'put',
    data
  })
}

// 删除测试单
export const deleteTestTask = (taskId) => {
  return request({
    url: `/api/ui-test/test-tasks/${taskId}`,
    method: 'delete'
  })
}

// 执行测试单
export const executeTestTask = (taskId) => {
  return request({
    url: `/api/ui-test/test-tasks/${taskId}/execute`,
    method: 'post'
  })
}

// 取消执行
export const cancelTestTask = (taskId) => {
  return request({
    url: `/api/ui-test/test-tasks/${taskId}/cancel`,
    method: 'post'
  })
}

// 暂停执行
export const pauseTestTask = (taskId) => {
  return request({
    url: `/api/ui-test/test-tasks/${taskId}/pause`,
    method: 'post'
  })
}

// 继续执行
export const resumeTestTask = (taskId) => {
  return request({
    url: `/api/ui-test/test-tasks/${taskId}/resume`,
    method: 'post'
  })
}

// 重新执行
export const restartTestTask = (taskId) => {
  return request({
    url: `/api/ui-test/test-tasks/${taskId}/restart`,
    method: 'post'
  })
}

// 获取执行进度
export const getTaskProgress = (taskId) => {
  return request({
    url: `/api/ui-test/test-tasks/${taskId}/progress`,
    method: 'get'
  })
}

// 获取执行日志（支持增量读取）
export const getTestTaskLog = (taskId, offset = 0) => {
  return request({
    url: `/api/ui-test/test-tasks/${taskId}/log`,
    method: 'get',
    params: { offset }
  })
}

// 获取测试内容
export const getTaskContents = (taskId) => {
  return request({
    url: `/api/ui-test/test-tasks/${taskId}/contents`,
    method: 'get'
  })
}

// 添加测试内容
export const addTaskContent = (taskId, itemType, itemId) => {
  return request({
    url: `/api/ui-test/test-tasks/${taskId}/contents`,
    method: 'post',
    params: { item_type: itemType, item_id: itemId }
  })
}

// 移除测试内容
export const removeTaskContent = (taskId, contentId) => {
  return request({
    url: `/api/ui-test/test-tasks/${taskId}/contents/${contentId}`,
    method: 'delete'
  })
}

// 调整执行顺序
export const reorderTaskContents = (taskId, contentIds) => {
  return request({
    url: `/api/ui-test/test-tasks/${taskId}/contents/reorder`,
    method: 'post',
    data: contentIds
  })
}

// 获取执行报告列表
export const getTaskReports = (taskId) => {
  return request({
    url: `/api/ui-test/test-tasks/${taskId}/reports`,
    method: 'get'
  })
}

/**
 * 测试报告管理API
 */

// 获取测试报告列表
export const getTestReports = (params) => {
  return request({
    url: '/api/ui-test/test-reports',
    method: 'get',
    params
  })
}

// 获取测试报告详情
export const getTestReportDetail = (reportId) => {
  return request({
    url: `/api/ui-test/test-reports/${reportId}`,
    method: 'get'
  })
}

// 获取报告摘要
export const getReportSummary = (reportId) => {
  return request({
    url: `/api/ui-test/test-reports/${reportId}/summary`,
    method: 'get'
  })
}

// 对比多个报告
export const compareReports = (reportIds) => {
  return request({
    url: '/api/ui-test/test-reports/compare',
    method: 'get',
    params: { report_ids: reportIds.join(',') }
  })
}

// 删除测试报告
export const deleteTestReport = (reportId) => {
  return request({
    url: `/api/ui-test/test-reports/${reportId}`,
    method: 'delete'
  })
}
