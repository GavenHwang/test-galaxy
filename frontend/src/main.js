import { createApp } from 'vue'
import App from './App.vue'
import '@/assets/less/index.less'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import { createPinia } from 'pinia'
// 引入mock,打开这行，数据按照mock进行展示
// import '@/api/mock.js'
import api from '@/api/api'
const pinia = createPinia()
const app = createApp(App)

// 注册函数请求的方法
app.config.globalProperties.$api = api
app.use(ElementPlus)
app.use(pinia)
app.use(router).mount('#app')
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}
