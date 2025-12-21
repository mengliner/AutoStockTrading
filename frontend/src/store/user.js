/*
 * @Author: mengliner 1219948661@qq.com
 * @Date: 2025-12-21 15:10:07
 * @LastEditors: mengliner 1219948661@qq.com
 * @LastEditTime: 2025-12-21 15:10:12
 * @FilePath: \AutoStockTrading\frontend\src\store\user.js
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 */
import { defineStore } from 'pinia'
import request from '@/api/request'

export const useUserStore = defineStore('user', {
  state: () => ({
    info: null,
    roles: [],
    permissions: []
  }),
  getters: {
    isAdmin: (state) => state.roles.includes('admin')
  },
  actions: {
    async fetchUserInfo() {
      try {
        const data = await request.get('/api/user/me')
        this.info = data
        this.roles = data.roles || []
        this.permissions = data.permissions || []
        return data
      } catch (error) {
        console.error('获取用户信息失败', error)
        throw error
      }
    },
    clearUserInfo() {
      this.info = null
      this.roles = []
      this.permissions = []
    }
  }
})