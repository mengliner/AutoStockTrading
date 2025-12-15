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