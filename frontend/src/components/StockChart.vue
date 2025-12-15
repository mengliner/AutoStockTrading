<template>
    <div ref="chartRef" class="chart-container" style="width: 100%; height: 500px;"></div>
  </template>
  
  <script setup>
  import { ref, onMounted, watch, defineProps } from 'vue'
  import * as echarts from 'echarts'
  import request from '@/api/request'
  
  const props = defineProps({ 
    tsCode: { type: String, required: true },
    startDate: { type: String, default: '20200101' },
    endDate: { type: String, default: '' }
  })
  
  const chartRef = ref(null)
  const chart = ref(null)
  
  const loadKlineData = async () => {
    try {
      const data = await request.get(`/api/stock/kline/${props.tsCode}`, {
        params: { start_date: props.startDate, end_date: props.endDate }
      })
      return data.map(item => [
        item.trade_date, 
        Number(item.open), 
        Number(item.close), 
        Number(item.low), 
        Number(item.high)
      ])
    } catch (e) {
      console.error('获取K线数据失败', e)
      return []
    }
  }
  
  const initChart = async () => {
    if (!chartRef.value) return
    chart.value = echarts.init(chartRef.value)
    const klineData = await loadKlineData()
    
    chart.value.setOption({
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'cross' }
      },
      xAxis: { type: 'category', data: klineData.map(item => item[0]) },
      yAxis: { type: 'value' },
      series: [{
        type: 'candlestick',
        data: klineData.map(item => item.slice(1))
      }]
    })
  }
  
  onMounted(initChart)
  watch([() => props.tsCode, () => props.startDate, () => props.endDate], initChart)
  </script>