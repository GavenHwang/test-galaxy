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
