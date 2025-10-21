import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  // resolve添加别名
  resolve:{
    alias:[
      {
        find: '@',
        replacement: '/src'
      }
    ]
  }
})
