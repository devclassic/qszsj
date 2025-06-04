import { createRouter, createWebHashHistory } from 'vue-router'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', redirect: '/login' },
    { path: '/login', component: () => import('../views/login/Login.vue') },
    { path: '/home', component: () => import('../views/home/Home.vue') },
    { path: '/chat', component: () => import('../views/chat/Chat.vue') },
  ],
})

export default router
