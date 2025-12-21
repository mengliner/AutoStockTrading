// frontend/src/main.js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'  // 若使用路由
import { createPinia } from 'pinia'

const app = createApp(App)
app.use(createPinia())
app.use(router)  // 若使用路由
app.mount('#app')