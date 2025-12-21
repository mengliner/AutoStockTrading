<!--
 * @Author: mengliner 1219948661@qq.com
 * @Date: 2025-12-21 14:52:03
 * @LastEditors: mengliner 1219948661@qq.com
 * @LastEditTime: 2025-12-21 14:52:36
 * @FilePath: \AutoStockTrading\frontend\src\components\Layout.vue
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
-->
<template>
    <el-container style="height: 100vh">
      <el-aside width="200px" class="aside">
        <el-menu
          default-active="1"
          class="el-menu-vertical-demo"
          @select="handleMenuSelect"
        >
          <el-sub-menu index="dashboard">
            <template #title>
              <el-icon><dashboard /></el-icon>
              <span>工作台</span>
            </template>
            <el-menu-item index="/dashboard/stock-query">个股查询</el-menu-item>
            <el-menu-item index="/dashboard/favorites">收藏列表</el-menu-item>
          </el-sub-menu>
          
          <el-sub-menu index="system">
            <template #title>
              <el-icon><setting /></el-icon>
              <span>系统管理</span>
            </template>
            <el-menu-item index="/system/tasks">定时任务管理</el-menu-item>
            <el-menu-item index="/system/users">用户管理</el-menu-item>
            <el-menu-item index="/system/roles">角色管理</el-menu-item>
            <el-menu-item index="/system/monitor">系统监控</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-aside>
      
      <el-container>
        <el-header class="header">
          <div class="flex justify-end items-center">
            <el-dropdown>
              <span class="user-info">{{ userInfo.username }}</span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>
        
        <el-main class="main">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import { useRouter } from 'vue-router'
  import { Dashboard, Setting } from '@element-plus/icons-vue'
  import { useAuthStore } from '@/store/auth'
  import request from '@/api/request'
  
  const router = useRouter()
  const authStore = useAuthStore()
  const userInfo = ref({})
  
  const handleMenuSelect = (index) => {
    router.push(index)
  }
  
  const handleLogout = () => {
    authStore.logout()
    router.push('/login')
  }
  
  const loadUserInfo = async () => {
    const data = await request.get('/api/user/me')
    userInfo.value = data
  }
  
  onMounted(loadUserInfo)
  </script>