/*
 * @Author: mengliner 1219948661@qq.com
 * @Date: 2025-12-21 14:51:37
 * @LastEditors: mengliner 1219948661@qq.com
 * @LastEditTime: 2025-12-21 14:51:46
 * @FilePath: \AutoStockTrading\frontend\src\router\index.js
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 */
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const routes = [
  { path: '/login', component: () => import('@/views/auth/Login.vue') },
  { path: '/register', component: () => import('@/views/auth/Register.vue') },
  {
    path: '/',
    component: () => import('@/components/Layout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '/dashboard', component: () => import('@/views/dashboard/Index.vue') },
      { path: '/dashboard/stock-query', component: () => import('@/views/dashboard/StockQuery.vue') },
      { path: '/dashboard/favorites', component: () => import('@/views/dashboard/Favorites.vue') },
      { 
        path: '/system', 
        children: [
          { path: 'tasks', component: () => import('@/views/system/TaskManager.vue') },
          { path: 'users', component: () => import('@/views/system/UserManager.vue') },
          { path: 'roles', component: () => import('@/views/system/RoleManager.vue') },
          { path: 'monitor', component: () => import('@/views/system/SystemMonitor.vue') }
        ]
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})

export default router