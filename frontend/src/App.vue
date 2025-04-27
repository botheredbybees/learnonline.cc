<template>
  <el-container class="app-container">
    <el-header>
      <nav class="nav-header">
        <router-link to="/" class="logo">LearnOnline</router-link>
        <div class="nav-links">
          <router-link to="/courses">Courses</router-link>
          <router-link to="/about">About</router-link>
          <router-link to="/login" v-if="!isLoggedIn">Login</router-link>
          <router-link to="/register" v-if="!isLoggedIn">Register</router-link>
          <el-dropdown v-if="isLoggedIn">
            <span class="el-dropdown-link">
              {{ username }}<el-icon class="el-icon--right"><arrow-down /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>Profile</el-dropdown-item>
                <el-dropdown-item>Settings</el-dropdown-item>
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

export default {
  name: 'App',
  components: {
    ArrowDown
  },
  setup() {
    const store = useStore()
    const isLoggedIn = computed(() => store.state.auth.isLoggedIn)
    const username = computed(() => store.state.auth.user?.username || '')

    const logout = () => {
      store.dispatch('auth/logout')
    }

    return {
      isLoggedIn,
      username,
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

.el-footer {
  text-align: center;
  padding: 20px;
  background-color: #f5f7fa;
}
</style> 