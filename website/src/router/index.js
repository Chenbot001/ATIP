import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import RankingView from '../views/RankingView.vue'
import AuthorProfileView from '../views/AuthorProfileView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/ranking/:metric',
    name: 'ranking',
    component: RankingView,
    props: true
  },
  {
    path: '/author/:id',
    name: 'author',
    component: AuthorProfileView,
    props: true
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 