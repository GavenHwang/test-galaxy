import axios from "axios";
import {ElMessage} from "element-plus";
import router from '@/router'; // 导入路由实例

const service = axios.create(
    {
        baseURL: config.baseUrl
    }
);
import config from "../config";

// 添加请求拦截器
service.interceptors.request.use(function (config) {
    // 添加认证token
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
}, function (error) {
    // 对请求错误做些什么
    return Promise.reject(error);
});

// 添加响应拦截器
service.interceptors.response.use(
    (res) => {
        const {code, data, msg} = res.data
        if (code === 200) {
            return data
        } else {
            const NETWORK_ERROR = "网络错误......"
            ElMessage.error(msg || NETWORK_ERROR)
            return Promise.reject(msg || NETWORK_ERROR)
        }
    },
    (error) => {
        if (error.response) {
            // 服务器返回了响应，但状态码是错误范围
            const {status, data} = error.response;

            if (status === 401) {
                // 处理未授权
                localStorage.removeItem("token");
                localStorage.removeItem("userInfo");
                router.push("/login");
                return Promise.reject("未授权");
            }

            // 其他错误状态码
            ElMessage.error(data.msg || `请求失败，状态码：${status}`);
        } else {
            // 网络错误或请求未完成
            ElMessage.error("网络连接失败");
        }
        return Promise.reject(error);
    }
);

function request(options) {
    options.method = options.method || "get"
    // 关于get请求参数的调整
    if (options.method.toLowerCase() === 'get') {
        options.params = options.data
    }
    return service(options)
}

export default request