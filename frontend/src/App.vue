<template>
  <el-container class="app-container">
    <el-header>
      <nav class="nav-header">
        <router-link to="/" class="logo">LearnOnline</router-link>
        <div class="nav-links">
          <!-- Guest links -->
          <router-link to="/login" v-if="!isLoggedIn">Login</router-link>
          <router-link to="/register" v-if="!isLoggedIn">Register</router-link>
          
          <!-- Logged in user links -->
          <template v-if="isLoggedIn">
            <router-link to="/quests">Quests</router-link>
            <router-link to="/admin" v-if="isAdmin">Admin</router-link>
            <span v-if="isAdmin" style="color: green; font-weight: bold; margin-left: 10px;">
              (Admin: {{ isAdmin ? 'Yes' : 'No' }})
            </span>
          </template>
          
          <!-- User dropdown -->
          <el-dropdown v-if="isLoggedIn">
            <span class="el-dropdown-link">
              {{ username }}<el-icon class="el-icon--right"><arrow-down /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>
                  <router-link to="/profile" class="dropdown-link">Profile</router-link>
                </el-dropdown-item>
                <el-dropdown-item>
                  <router-link to="/profile?tab=favorites" class="dropdown-link">My Favorites</router-link>
                </el-dropdown-item>
                <el-dropdown-item divided @click="logout">Logout</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </nav>
    </el-header>

    <el-main>
      <router-view></router-view>
    </el-main>

    <el-footer>
      <p>&copy; 2024 LearnOnline. All rights reserved.</p>
    </el-footer>
  </el-container>
</template>

<script>
import { computed } from 'vue'
import { useStore } from 'vuex'
import { ArrowDown } from '@element-plus/icons-vue'
import axios from 'axios'

export default {
  name: 'App',
  components: {
    ArrowDown
  },
  setup() {
    const store = useStore()
    const isLoggedIn = computed(() => store.state.auth.isLoggedIn)
    const username = computed(() => store.state.auth.user?.username || '')
    const isAdmin = computed(() => {
      // Debug info to help track admin status
      console.log('Computing isAdmin:', store.state.auth.user)
      return store.state.auth.user?.is_admin === true
    })
    
    // Try to fetch user data on app initialization if token exists
    if (localStorage.getItem('token')) {
      // Initialize axios headers
      const token = localStorage.getItem('token')
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
      
      // Fetch user data
      store.dispatch('auth/fetchUser').then(() => {
        console.log('User data fetched on app initialization')
        console.log('Admin status:', store.state.auth.user?.is_admin)
      })
    }

    const logout = () => {
      store.dispatch('auth/logout')
    }

    return {
      isLoggedIn,
      username,
      isAdmin,
      logout
    }
  }
}
</script>

<style>
.app-container {
  min-height: 100vh;
}

.nav-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 60px;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.logo {
  font-size: 1.5em;
  font-weight: bold;
  text-decoration: none;
  color: #409EFF;
}

.nav-links {
  display: flex;
  gap: 20px;
  align-items: center;
}

.nav-links a {
  text-decoration: none;
  color: #606266;
}

.nav-links a:hover {
  color: #409EFF;
}

.dropdown-link {
  text-decoration: none;
  color: inherit;
  display: block;
  width: 100%;
}

.el-footer {
  text-align: center;
  padding: 20px;
  background-color: #f5f7fa;
}
</style>