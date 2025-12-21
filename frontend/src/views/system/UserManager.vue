<template>
    <el-card>
      <div class="flex justify-between mb-4">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索用户名"
          style="width: 300px"
          clearable
          @clear="loadUsers"
          @input="handleSearch"
        />
        <el-button type="primary" @click="showAddUser = true">新增用户</el-button>
      </div>
  
      <el-table :data="users" border>
        <el-table-column prop="id" label="用户ID" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="role" label="角色" />
        <el-table-column prop="created_at" label="创建时间" />
        <el-table-column label="操作">
          <template #default="scope">
            <el-button size="small" @click="handleAssignRole(scope.row)">分配角色</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
            <el-button size="small" @click="handleFreeze(scope.row)">
              {{ scope.row.status === 'active' ? '冻结' : '解冻' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import request from '@/api/request'
  
  const users = ref([])
  const searchKeyword = ref('')
  
  const loadUsers = async () => {
    const { data } = await request.get('/api/system/users')
    users.value = data
  }
  
  const handleSearch = (val) => {
    // 防抖处理
    clearTimeout(window.searchTimer)
    window.searchTimer = setTimeout(async () => {
      const { data } = await request.get('/api/system/users', {
        params: { keyword: val }
      })
      users.value = data
    }, 300)
  }
  
  onMounted(loadUsers)
  </script>