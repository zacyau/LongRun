import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/anchor'
    },
    {
      path: '/anchor',
      name: 'anchor',
      component: () => import('@/views/AnchorView.vue')
    },
    {
      path: '/hongli',
      name: 'hongli',
      component: () => import('@/views/HongliView.vue')
    },
    {
      path: '/growth-value',
      name: 'growthValue',
      component: () => import('@/views/GrowthValueView.vue')
    },
    {
      path: '/macdv',
      name: 'macdv',
      component: () => import('@/views/MacdvView.vue')
    }
  ]
})

export default router