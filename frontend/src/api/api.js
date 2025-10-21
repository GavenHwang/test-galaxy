import request from "./request";
import qs from 'qs';

export default {
    // 环境信息页面的请求接口
    getMenuData() {
        return request({
            url: "api/user/get_menu",
            method: "get"
        })
    },
    // 环境信息页面的请求接口
    getEnvData(data) {
        return request({
            url: "api/env/envs",
            method: "get",
            data: data
        })
    },
    // 环境信息页面的请求接口
    getUserData(data) {
        return request({
            url: "api/user/info",
            method: "get",
            data: data
        })
    },
    // 添加用户
    addUser(data) {
        return request({
            url: "api/user/add_user",
            method: "post",
            data: data
        })
    },
    // 删除用户
    deleteUser(data) {
        return request({
            url: "api/user/delete_user",
            method: "delete",
            data: data
        })
    },
    // 重置密码
    resetPassword(data) {
        return request({
            url: "api/user/reset_password",
            method: "post",
            data: data
        })
    },
    // 登录接口
    login(data) {
        return request({
            url: "api/login",
            method: "post",
            data: qs.stringify(data), // 转为 key=value&key2=value2 格式
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        })
    },
    // 登出接口
    logout() {
        return request({
            url: "api/logout",
            method: "post"
        })
    },
    // 获取所有项目名称
    getProjectName() {
        return request({
            url: "api/env/projects",
            method: "get"
        })
    },
    // 获取所有项目和项目的环境信息
    getProjectEnv() {
        return request({
            url: "api/env/project_envs",
            method: "get"
        })
    },
    // 获取环境的当前版本信息
    getVersionData(data){
        return request({
            url: "api/env/env_versions",
            method: "get",
            data: data
        })
    },
    //强制刷新环境版本信息
    refreshVersion(data){
        return request({
            url: "api/env/refresh_env_versions",
            method: "post",
            data: data
        })
    },
}