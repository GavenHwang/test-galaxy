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
