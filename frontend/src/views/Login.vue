<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <h2>Login to LearnOnline</h2>
        </div>
      </template>
      
      <el-form 
        ref="loginForm" 
        :model="loginForm" 
        :rules="rules" 
        label-position="top"
        @submit.prevent="handleLogin"
      >
        <el-form-item label="Email" prop="email">
          <el-input 
            v-model="loginForm.email" 
            type="email" 
            placeholder="Enter your email"
            prefix-icon="el-icon-message"
          />
        </el-form-item>
        
        <el-form-item label="Password" prop="password">
          <el-input 
            v-model="loginForm.password" 
            type="password" 
            placeholder="Enter your password"
            prefix-icon="el-icon-lock"
            show-password
          />
        </el-form-item>
        
        <el-form-item>
          <el-checkbox v-model="loginForm.remember">Remember me</el-checkbox>
          <el-link type="primary" class="forgot-password" @click="$router.push('/forgot-password')">
            Forgot password?
          </el-link>
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            native-type="submit" 
            :loading="loading" 
            class="login-button"
          >
            Login
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="register-link">
        <p>Don't have an account? <el-link type="primary" @click="$router.push('/register')">Register</el-link></p>
      </div>
    </el-card>
  </div>
</template>

<script>
import { defineComponent, ref, reactive } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

export default defineComponent({
  name: 'LoginView',
  setup() {
    const store = useStore()
    const router = useRouter()
    const loginForm = ref(null)
    const loading = ref(false)
    
    const formData = reactive({
      email: '',
      password: '',
      remember: false
    })
    
    const rules = {
      email: [
        { required: true, message: 'Please enter your email', trigger: 'blur' },
        { type: 'email', message: 'Please enter a valid email', trigger: 'blur' }
      ],
      password: [
        { required: true, message: 'Please enter your password', trigger: 'blur' },
        { min: 6, message: 'Password must be at least 6 characters', trigger: 'blur' }
      ]
    }
    
    const handleLogin = async () => {
      if (!loginForm.value) return
      
      try {
        await loginForm.value.validate()
        loading.value = true
        
        const success = await store.dispatch('auth/login', {
          email: formData.email,
          password: formData.password
        })
        
        if (success) {
          ElMessage.success('Login successful')
          router.push('/')
        } else {
          ElMessage.error('Invalid email or password')
        }
      } catch (error) {
        console.error('Login error:', error)
        ElMessage.error('An error occurred during login')
      } finally {
        loading.value = false
      }
    }
    
    return {
      loginForm,
      formData,
      rules,
      loading,
      handleLogin
    }
  }
})
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 120px);
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 400px;
}

.card-header {
  text-align: center;
}

.card-header h2 {
  margin: 0;
  color: #409EFF;
}

.login-button {
  width: 100%;
}

.forgot-password {
  float: right;
}

.register-link {
  text-align: center;
  margin-top: 20px;
}

@media (max-width: 768px) {
  .login-container {
    padding: 10px;
  }
}
</style> 