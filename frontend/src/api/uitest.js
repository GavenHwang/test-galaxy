/**
 * UI测试相关API接口
 */
import request from './request'

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
export const getRoles = () => {
  return request({
    url: '/api/ui-test/test-users/roles/list',
    method: 'get'
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

// 获取模块列表
export const getModules = () => {
  return request({
    url: '/api/ui-test/elements/modules/list',
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
