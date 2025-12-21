/*
 * @Author: mengliner 1219948661@qq.com
 * @Date: 2025-12-21 15:13:24
 * @LastEditors: mengliner 1219948661@qq.com
 * @LastEditTime: 2025-12-21 15:13:41
 * @FilePath: \AutoStockTrading\frontend\src\directives\permission.js
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 */
import { useUserStore } from '@/store/user'

export const permissionDirective = {
  mounted(el, binding) {
    const { value } = binding
    const userStore = useUserStore()
    const permissions = userStore.permissions

    if (value && !permissions.includes(value)) {
      el.style.display = 'none'
    }
  }
}