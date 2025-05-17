<template>
  <div class="register-container">
    <el-card class="register-card">
      <template #header>
        <div class="card-header">
          <h2>Create an Account</h2>
        </div>
      </template>
      
      <el-form 
        ref="registerForm" 
        :model="formData" 
        :rules="rules" 
        label-position="top"
        @submit.prevent="handleRegister"
      >
        <el-form-item label="Full Name" prop="name">
          <el-input 
            v-model="formData.name" 
            placeholder="Enter your full name"
            prefix-icon="el-icon-user"
          />
        </el-form-item>
        
        <el-form-item label="Email" prop="email">
          <el-input 
            v-model="formData.email" 
            type="email" 
            placeholder="Enter your email"
            prefix-icon="el-icon-message"
          />
        </el-form-item>
        
        <el-form-item label="Password" prop="password">
          <el-input 
            v-model="formData.password" 
            type="password" 
            placeholder="Create a password"
            prefix-icon="el-icon-lock"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="Confirm Password" prop="confirmPassword">
          <el-input 
            v-model="formData.confirmPassword" 
            type="password" 
            placeholder="Confirm your password"
            prefix-icon="el-icon-lock"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="User Type" prop="userType">
          <el-select 
            v-model="formData.userType" 
            placeholder="Select your user type"
            class="user-type-select"
          >
            <el-option label="Student" value="student" />
            <el-option label="Mentor" value="mentor" />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-checkbox v-model="formData.agreeToTerms" prop="agreeToTerms">
            I agree to the <el-link type="primary" @click="showTerms">Terms and Conditions</el-link>
          </el-checkbox>
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            native-type="submit" 
            :loading="loading" 
            class="register-button"
          >
            Register
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="login-link">
        <p>Already have an account? <el-link type="primary" @click="$router.push('/login')">Login</el-link></p>
      </div>
    </el-card>
    
    <!-- Terms and Conditions Dialog -->
    <el-dialog
      v-model="termsDialogVisible"
      title="Terms and Conditions"
      width="50%"
    >
      <div class="terms-content">
        <h3>LearnOnline Terms and Conditions</h3>
        <p>By using LearnOnline, you agree to the following terms and conditions:</p>
        <ol>
          <li>You will provide accurate and complete information during registration.</li>
          <li>You are responsible for maintaining the confidentiality of your account.</li>
          <li>You will not share your account credentials with others.</li>
          <li>You will use the platform for educational purposes only.</li>
          <li>You will respect the intellectual property rights of others.</li>
          <li>You will not engage in any activity that disrupts the platform.</li>
        </ol>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="termsDialogVisible = false">Close</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { defineComponent, ref, reactive, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { transferGuestProgress, getCookie } from '@/utils/guestUtils'

export default defineComponent({
  name: 'RegisterView',
  setup() {
    const store = useStore()
    const router = useRouter()
    const route = useRoute()
    const registerForm = ref(null)
    const loading = ref(false)
    const termsDialogVisible = ref(false)
    const fromQuest = ref(false)
    const hasGuestProgress = ref(false)
    
    const formData = reactive({
      name: '',
      email: '',
      password: '',
      confirmPassword: '',
      userType: '',
      agreeToTerms: false
    })
    
    const validatePass = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('Please enter your password'))
      } else {
        if (formData.confirmPassword !== '') {
          registerForm.value.validateField('confirmPassword')
        }
        callback()
      }
    }
    
    const validatePass2 = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('Please enter your password again'))
      } else if (value !== formData.password) {
        callback(new Error('Two passwords do not match'))
      } else {
        callback()
      }
    }
    
    const rules = {
      name: [
        { required: true, message: 'Please enter your name', trigger: 'blur' },
        { min: 2, message: 'Name must be at least 2 characters', trigger: 'blur' }
      ],
      email: [
        { required: true, message: 'Please enter your email', trigger: 'blur' },
        { type: 'email', message: 'Please enter a valid email', trigger: 'blur' }
      ],
      password: [
        { required: true, validator: validatePass, trigger: 'blur' },
        { min: 6, message: 'Password must be at least 6 characters', trigger: 'blur' }
      ],
      confirmPassword: [
        { required: true, validator: validatePass2, trigger: 'blur' }
      ],
      userType: [
        { required: true, message: 'Please select your user type', trigger: 'change' }
      ],
      agreeToTerms: [
        { 
          validator: (rule, value, callback) => {
            if (!value) {
              callback(new Error('You must agree to the terms and conditions'))
            } else {
              callback()
            }
          }, 
          trigger: 'change' 
        }
      ]
    }
    
    const handleRegister = async () => {
      if (!registerForm.value) return
      
      try {
        await registerForm.value.validate()
        loading.value = true
        
        const success = await store.dispatch('auth/register', {
          name: formData.name,
          email: formData.email,
          password: formData.password,
          userType: formData.userType
        })
        
        if (success) {
          ElMessage.success('Registration successful')
          
          // If there's guest progress, transfer it to the new account
          if (hasGuestProgress.value) {
            try {
              await transferGuestProgress()
              ElMessage.success('Your progress has been saved to your new account!')
            } catch (err) {
              console.error('Error transferring progress:', err)
              // Don't show error to user, just log it - the main registration was successful
            }
          }
          
          // Redirect based on registration source
          if (fromQuest.value) {
            // If from quest completion, redirect to quests page
            router.push('/quests')
          } else {
            // Otherwise redirect to home
            router.push('/')
          }
        } else {
          ElMessage.error('Registration failed')
        }
      } catch (error) {
        console.error('Registration error:', error)
        ElMessage.error('An error occurred during registration')
      } finally {
        loading.value = false
      }
    }
    
    const showTerms = () => {
      termsDialogVisible.value = true
    }
    
    // Check if user has guest progress or came from an introductory quest
    onMounted(() => {
      // Check for quest param in URL
      if (route.query.from === 'quest') {
        fromQuest.value = true;
      }
      
      // Check for guest progress cookie
      if (getCookie('guest_id')) {
        hasGuestProgress.value = true;
      }
    });
    
    return {
      registerForm,
      formData,
      rules,
      loading,
      termsDialogVisible,
      fromQuest,
      hasGuestProgress,
      handleRegister,
      showTerms
    }
  }
})
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 120px);
  padding: 20px;
}

.register-card {
  width: 100%;
  max-width: 500px;
}

.card-header {
  text-align: center;
}

.card-header h2 {
  margin: 0;
  color: #409EFF;
}

.user-type-select {
  width: 100%;
}

.register-button {
  width: 100%;
}

.login-link {
  text-align: center;
  margin-top: 20px;
}

.terms-content {
  max-height: 400px;
  overflow-y: auto;
  padding: 0 20px;
}

@media (max-width: 768px) {
  .register-container {
    padding: 10px;
  }
}
</style> 