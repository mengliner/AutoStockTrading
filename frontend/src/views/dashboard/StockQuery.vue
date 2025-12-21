<template>
    <el-card>
      <el-form :inline="true" :model="queryForm" class="mb-4">
        <el-form-item label="股票代码">
          <el-input v-model="queryForm.tsCode" placeholder="例如：000001.SZ"></el-input>
        </el-form-item>
        <el-form-item label="开始日期">
          <el-date-picker
            v-model="queryForm.startDate"
            format="YYYYMMDD"
            value-format="YYYYMMDD"
            type="date"
            placeholder="选择开始日期"
          ></el-date-picker>
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker
            v-model="queryForm.endDate"
            format="YYYYMMDD"
            value-format="YYYYMMDD"
            type="date"
            placeholder="选择结束日期"
          ></el-date-picker>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleQuery">查询</el-button>
          <el-button @click="handleFavorite" v-if="queryForm.tsCode">
            <el-icon><star /></el-icon> 收藏
          </el-button>
        </el-form-item>
      </el-form>
      
      <StockChart 
        :ts-code="queryForm.tsCode"
        :start-date="queryForm.startDate"
        :end-date="queryForm.endDate"
      />
    </el-card>
  </template>
  
  <script setup>
  import { ref, reactive } from 'vue'
  import StockChart from '@/components/StockChart.vue'
  import { Star } from '@element-plus/icons-vue'
  import request from '@/api/request'
  
  const queryForm = reactive({
    tsCode: '',
    startDate: '',
    endDate: ''
  })
  
  const handleQuery = () => {
    // 触发图表重新加载
  }
  
  const handleFavorite = async () => {
    try {
      await request.post(`/api/stock/favorite/${queryForm.tsCode}`)
      ElMessage.success('收藏成功')
    } catch (e) {
      ElMessage.error(e.response?.data?.detail || '收藏失败')
    }
  }
  </script>