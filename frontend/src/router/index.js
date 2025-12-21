import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth'

// 路由懒加载
const Login = () => import('@/views/Login.vue')
const Register = () => import('@/views/Register.vue')
const Workbench = () => import('@/views/Workbench.vue')
const Favorites = () => import('@/views/Favorites.vue')
const StockDetail = () => import('@/views/StockDetail.vue')
const SystemManagement = () => import('@/views/SystemManagement.vue')
const UserManagement = () => import('@/views/system/UserManagement.vue')
const RoleManagement = () => import('@/views/system/RoleManagement.vue')
const TaskManagement = () => import('@/views/system/TaskManagement.vue')
const SystemMonitor = () => import('@/views/system/SystemMonitor.vue')

const routes = [
  { path: '/login', name: 'Login', component: Login, meta: { guest: true } },
  { path: '/register', name: 'Register', component: Register, meta: { guest: true } },
  {
    path: '/',
    name: 'Workbench',
    component: Workbench,
    meta: { requiresAuth: true }
  },
  {
    path: '/favorites',
    name: 'Favorites',
    component: Favorites,
    meta: { requiresAuth: true }
  },
  {
    path: '/stock/:tsCode',
    name: 'StockDetail',
    component: StockDetail,
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/system',
    name: 'SystemManagement',
    component: SystemManagement,
    meta: { requiresAuth: true, role: 'admin' },
    children: [
      { path: 'users', name: 'UserManagement', component: UserManagement },
      { path: 'roles', name: 'RoleManagement', component: RoleManagement },
      { path: 'tasks', name: 'TaskManagement', component: TaskManagement },
      { path: 'monitor', name: 'SystemMonitor', component: SystemMonitor }
    ]
  },
  { path: '/:pathMatch(.*)*', redirect: '/' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const isAuthenticated = authStore.isAuthenticated

  // 未登录用户只能访问登录和注册页
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
    return
  }

  // 已登录用户不能访问登录和注册页
  if (to.meta.guest && isAuthenticated) {
    next('/')
    return
  }

  // 管理员权限控制
  if (to.meta.role && authStore.user?.role !== to.meta.role) {
    next('/')
    return
  }

  next()
})

export default router