<!--
 * @Author: mengliner 1219948661@qq.com
 * @Date: 2025-12-21 14:49:06
 * @LastEditors: mengliner 1219948661@qq.com
 * @LastEditTime: 2025-12-21 14:51:27
 * @FilePath: \AutoStockTrading\frontend\src\views\auth\Login.vue
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
-->
<template>
    <div class="login-container">
      <el-card class="login-card">
        <h2 class="title">股票数据管理系统</h2>
        <el-form ref="form" :model="form" :rules="rules" label-width="80px">
          <el-form-item label="用户名" prop="username">
            <el-input v-model="form.username" placeholder="请输入用户名"></el-input>
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input v-model="form.password" type="password" placeholder="请输入密码"></el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleLogin" class="w-full">登录</el-button>
          </el-form-item>
          <el-link type="info" @click="$router.push('/register')" class="register-link">
            还没有账号？立即注册
          </el-link>
        </el-form>
      </el-card>
    </div>
  </template>
  <script setup>
  import { ref, reactive } from 'vue'
  import { useRouter } from 'vue-router'
  import { useAuthStore } from '@/store/auth'
  import request from '@/api/request'
  
  const router = useRouter()
  const authStore = useAuthStore()
  const form = reactive({
    username: '',
    password: ''
  })
  
  const rules = {
    username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
    password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
  }
  
  const formRef = ref(null)
  
  const handleLogin = async () => {
    try {
      const { access_token } = await request.post('/api/user/login', form)
      authStore.setToken(access_token)
      router.push('/dashboard')
    } catch (e) {
      console.error('登录失败', e)
    }
  }
  </script>
  
  <style scoped>
  .login-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    background-color: #f5f7fa;
  }
  
  .login-card {
    width: 400px;
    padding: 20px;
  }
  
  .title {
    text-align: center;
    margin-bottom: 20px;
  }
  
  .w-full {
    width: 100%;
  }
  
  .register-link {
    display: block;
    text-align: center;
    margin-top: 10px;
  }
  </style>