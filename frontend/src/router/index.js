import { createRouter, createWebHistory } from 'vue-router';
import store from '../store'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue')
  },
  {
    path: '/test-admin',
    name: 'TestAdminLogin',
    component: () => import('../views/TestAdminLogin.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { guest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
    meta: { guest: true }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('../views/Admin.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/units/:id',
    name: 'Unit',
    component: () => import('../views/Unit.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/quests',
    name: 'Quests',
    component: () => import('../views/Quests.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/quests/:id',
    name: 'QuestDetail',
    component: () => import('../views/Quests.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/intro-quest/:id',
    name: 'IntroductoryQuest',
    component: () => import('../views/IntroductoryQuest.vue'),
    // No auth required for introductory quests
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/Profile.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/admin-test',
    name: 'AdminTest',
    component: () => import('../views/AdminTest.vue'),
    // No auth required for this test route
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// Navigation guards
router.beforeEach((to, from, next) => {
  const isLoggedIn = store.state.auth.isLoggedIn
  const currentUser = store.state.auth.user
  const isAdmin = Boolean(currentUser?.is_admin)
  
  console.log(`Route navigation: ${from.path} → ${to.path}`)
  console.log(`Auth state: isLoggedIn=${isLoggedIn}, isAdmin=${isAdmin}`)
  console.log('Current user:', currentUser)

  // For admin route, do extra checks
  if (to.path === '/admin') {
    console.log('Admin route requested, checking permissions carefully')
    console.log('User is_admin flag:', currentUser?.is_admin, 'type:', typeof currentUser?.is_admin)
    
    // Force admin if using the admin credentials
    if (currentUser?.email === 'admin@example.com' && currentUser?.id) {
      console.log('Email is "admin@example.com", treating as admin regardless of flag')
      // We'll continue below with the normal requiresAdmin check
    }
  }

  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!isLoggedIn) {
      console.log('Not logged in, redirecting to Login')
      next({ name: 'Login' })
    } else if (to.matched.some(record => record.meta.requiresAdmin)) {
      // Check for admin permissions
      const isAdminByFlag = Boolean(currentUser?.is_admin);
      const isAdminByEmail = currentUser?.email === 'admin@example.com';
      
      if (!isAdminByFlag && !isAdminByEmail) {
        // If route requires admin but user is not an admin
        console.log('Route requires admin but user is not admin, redirecting to Home')
        console.log('User:', currentUser)
        console.log('Is admin by flag:', isAdminByFlag)
        console.log('Is admin by email:', isAdminByEmail)
        next({ name: 'Home' })
      } else {
        console.log('Admin access granted to', to.path)
        next()
      }
    } else {
      console.log('Auth check passed, proceeding to route')
      next()
    }
  } else if (to.matched.some(record => record.meta.guest)) {
    if (isLoggedIn) {
      console.log('Already logged in, redirecting to Home')
      next({ name: 'Home' })
    } else {
      console.log('Guest route, proceeding')
      next()
    }
  } else {
    console.log('Public route, proceeding')
    next()
  }
})

export default router