<template>
    <el-card>
      <div class="flex justify-between mb-4">
        <h2>定时任务管理</h2>
        <el-button type="primary" @click="showAddDialog = true">新增任务</el-button>
      </div>
  
      <el-table :data="tasks" border>
        <el-table-column prop="job_id" label="任务ID" />
        <el-table-column prop="job_name" label="任务名称" />
        <el-table-column prop="job_handler" label="处理函数" />
        <el-table-column prop="cron_expression" label="Cron表达式" />
        <el-table-column prop="is_enabled" label="状态">
          <template #default="scope">
            <el-switch 
              v-model="scope.row.is_enabled" 
              @change="handleStatusChange(scope.row)"
              :disabled="!scope.row.is_enabled"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作">
          <template #default="scope">
            <el-button size="small" @click="handleRun(scope.row)">执行</el-button>
            <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
            <el-button size="small" @click="showTaskLogs(scope.row.job_id)">日志</el-button>
          </template>
        </el-table-column>
      </el-table>
  
      <!-- 执行任务弹窗 -->
      <el-dialog title="执行任务" v-model="showRunDialog">
        <el-form :model="runParams">
          <el-form-item label="参数配置">
            <el-input
              type="textarea"
              v-model="runParams.json"
              placeholder='{"ts_codes": ["000001.SZ"], "start_date": "20230101"}'
              rows="5"
            ></el-input>
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="showRunDialog = false">取消</el-button>
          <el-button type="primary" @click="confirmRun">确认执行</el-button>
        </template>
      </el-dialog>
    </el-card>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import request from '@/api/request'
  
  const tasks = ref([])
  const showRunDialog = ref(false)
  const currentTask = ref(null)
  const runParams = ref({ json: '{}' })
  
  const loadTasks = async () => {
    const { data } = await request.get('/api/task/scheduler/jobs')
    tasks.value = data
  }
  
  const handleRun = (task) => {
    currentTask.value = task
    showRunDialog.value = true
  }
  
  const confirmRun = async () => {
    try {
      const params = JSON.parse(runParams.value.json)
      await request.post(`/api/task/run/${currentTask.value.job_handler.split('.').pop()}`, params)
      ElMessage.success('任务已触发')
      showRunDialog.value = false
    } catch (e) {
      ElMessage.error('执行失败')
    }
  }
  
  const handleStatusChange = async (task) => {
    await request.put(`/api/task/scheduler/jobs/${task.job_id}`, {
      is_enabled: task.is_enabled
    })
  }
  
  onMounted(loadTasks)
  </script>