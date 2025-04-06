import Vue from 'vue'
import VueRouter from 'vue-router'
import HomePage from '../views/Home.vue'  // 更新引用名
import ExperimentList from '../views/ExperimentList.vue'
import ExperimentDetail from '../views/ExperimentDetail.vue'
import ExperimentWorkspace from '../views/ExperimentWorkspace.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import CustomCode from '../views/CustomCode.vue'
import UserCenter from '../views/UserCenter.vue'  // 导入新的用户中心组件
import store from '../store'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'HomePage',  // 更新路由名
    component: HomePage,
    meta: { requiresAuth: true }
  },
  {
    path: '/experiments',
    name: 'ExperimentList',
    component: ExperimentList,
    meta: { requiresAuth: true }
  },
  {
    path: '/experiments/:id',
    name: 'ExperimentDetail',
    component: ExperimentDetail,
    meta: { requiresAuth: true }
  },
  {
    path: '/experiments/:id/workspace',
    name: 'ExperimentWorkspace',
    component: ExperimentWorkspace,
    meta: { requiresAuth: true }
  },
  {
    path: '/custom-code',
    name: 'CustomCode',
    component: CustomCode,
    meta: { requiresAuth: true }
  },
  {
    path: '/user-center',
    name: 'UserCenter',
    component: UserCenter,
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { guest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { guest: true }
  },
  // 管理员路由
  {
    path: '/admin',
    component: () => import('../views/admin/AdminDashboard.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      {
        path: '',
        redirect: 'dashboard'
      },
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: {
          render: h => h('div', [
            h('h3', '管理员控制面板'),
            h('p', '欢迎使用金融大数据虚拟仿真平台管理系统')
          ])
        }
      },
      {
        path: 'submissions',
        name: 'AdminSubmissions',
        component: () => import('../views/admin/SubmissionList.vue')
      },
      {
        path: 'users',
        name: 'AdminUsers',
        component: () => import('../views/admin/UserList.vue')
      },
      // 其他管理员子路由
    ]
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

// 导航守卫
router.beforeEach((to, from, next) => {
  const isAuthenticated = store.getters.isAuthenticated
  
  // 需要登录的页面
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!isAuthenticated) {
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
    } else {
      next()
    }
  } 
  // 只允许未登录用户访问的页面（如登录、注册页）
  else if (to.matched.some(record => record.meta.guest)) {
    if (isAuthenticated) {
      next({ path: '/' })
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
