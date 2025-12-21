/*
 * @Author: mengliner 1219948661@qq.com
 * @Date: 2025-12-15 16:47:49
 * @LastEditors: mengliner 1219948661@qq.com
 * @LastEditTime: 2025-12-21 15:10:50
 * @FilePath: \AutoStockTrading\frontend\src\api\request.js
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 */
import axios from 'axios'
import { useAuthStore } from '@/store/auth'

const request = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 5000
})

// 请求拦截器：添加Token
request.interceptors.request.use(config => {
  const authStore = useAuthStore()
  if (authStore.token) {
    config.headers.Authorization = `Bearer ${authStore.token}`
  }
  return config
})

// 响应拦截器：处理错误
request.interceptors.response.use(
  response => response.data,
  error => {
    if (error.response?.status === 401) {
      const authStore = useAuthStore()
      authStore.logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default request