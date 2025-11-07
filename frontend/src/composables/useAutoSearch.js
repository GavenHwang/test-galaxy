/**
 * 自动搜索 Composable
 * 
 * 功能：
 * 1. 下拉框值变化后立即触发搜索
 * 2. 输入框值变化后，延迟指定时间（默认500ms）后触发搜索
 * 
 * 使用示例：
 * ```js
 * import { useAutoSearch } from '@/composables/useAutoSearch'
 * 
 * const searchForm = reactive({
 *   username: '',
 *   product: '',
 *   role: ''
 * })
 * 
 * const currentPage = ref(1)
 * 
 * // 配置自动搜索
 * useAutoSearch({
 *   searchForm,
 *   currentPage,
 *   onSearch: loadData,
 *   inputFields: ['username'],     // 输入框字段（防抖搜索）
 *   selectFields: ['product', 'role'], // 下拉框字段（立即搜索）
 *   debounceDelay: 500  // 可选，防抖延迟时间，默认500ms
 * })
 * ```
 */

import { watch } from 'vue'

/**
 * 配置自动搜索功能
 * @param {Object} options - 配置选项
 * @param {Object} options.searchForm - 搜索表单对象（reactive）
 * @param {Object} options.currentPage - 当前页码（ref）
 * @param {Function} options.onSearch - 搜索回调函数
 * @param {Array<string>} options.inputFields - 输入框字段名数组（防抖搜索）
 * @param {Array<string>} options.selectFields - 下拉框字段名数组（立即搜索）
 * @param {number} options.debounceDelay - 防抖延迟时间（毫秒），默认500
 */
export function useAutoSearch({
  searchForm,
  currentPage,
  onSearch,
  inputFields = [],
  selectFields = [],
  debounceDelay = 500
}) {
  // 防抖定时器
  let searchTimer = null

  // 监听下拉框变化，立即搜索
  if (selectFields.length > 0) {
    watch(
      () => selectFields.map(field => searchForm[field]),
      () => {
        if (currentPage) {
          currentPage.value = 1
        }
        onSearch()
      }
    )
  }

  // 监听输入框变化，防抖搜索
  if (inputFields.length > 0) {
    inputFields.forEach(field => {
      watch(
        () => searchForm[field],
        () => {
          // 清除之前的定时器
          if (searchTimer) {
            clearTimeout(searchTimer)
          }
          // 设置新的定时器
          searchTimer = setTimeout(() => {
            if (currentPage) {
              currentPage.value = 1
            }
            onSearch()
          }, debounceDelay)
        }
      )
    })
  }

  // 清理函数（组件卸载时调用）
  return () => {
    if (searchTimer) {
      clearTimeout(searchTimer)
    }
  }
}
