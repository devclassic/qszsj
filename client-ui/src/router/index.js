import { createRouter, createWebHashHistory } from 'vue-router'
import asr from '../utils/asr'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', redirect: '/login' },
    { path: '/login', component: () => import('../views/login/Login.vue') },
    { path: '/home', component: () => import('../views/home/Home.vue') },
    { path: '/chat', component: () => import('../views/chat/Chat.vue') },
  ],
})

router.beforeEach(async (to, from, next) => {
  if (!asr.isConnected()) {
    asr.connect()
  }
  if (localStorage.getItem('wsurl') && to.path === '/login') {
    return next('/home')
  }
  return next()
})

export default router
