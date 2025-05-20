<template>
  <div class="test-admin-login">
    <h1>Testing Admin Login</h1>
    <div class="status">
      <h2>Login Status</h2>
      <p v-if="loading">Logging in...</p>
      <div v-else-if="error">
        <p style="color: red">Error: {{ error }}</p>
      </div>
      <div v-else-if="success">
        <p style="color: green">Login successful!</p>
        <p>User: {{ JSON.stringify(user) }}</p>
        <p>Is Admin: {{ isAdmin ? 'Yes' : 'No' }}</p>
      </div>
      <button @click="testLogin" :disabled="loading">Test Admin Login</button>
      <button @click="logAuthState">Log Auth State</button>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import axios from 'axios';

export default {
  name: 'TestAdminLogin',
  setup() {
    const store = useStore();
    const router = useRouter();
    const loading = ref(false);
    const success = ref(false);
    const error = ref('');
    const user = computed(() => store.state.auth.user);
    const isAdmin = computed(() => store.state.auth.user?.is_admin);
    
    const testLogin = async () => {
      loading.value = true;
      error.value = '';
      success.value = false;
      
      try {
        // Use the provided admin credentials
        const loginResult = await store.dispatch('auth/login', {
          email: 'admin@example.com',
          password: 'Ex14://learnonline' 
        });
        
        if (loginResult) {
          success.value = true;
          console.log('Login successful');
          console.log('User:', store.state.auth.user);
          console.log('Is Admin:', store.state.auth.user?.is_admin);
          
          // Check if user is admin
          if (store.state.auth.user?.is_admin) {
            console.log('Admin detected, should navigate to admin page');
            setTimeout(() => router.push('/admin'), 1000);
          } else {
            console.log('User is not admin');
          }
        } else {
          error.value = 'Login returned false';
        }
      } catch (e) {
        error.value = e.message || 'Unknown error';
        console.error('Login error:', e);
      } finally {
        loading.value = false;
      }
    };
    
    const logAuthState = () => {
      console.log('Current auth state:', {
        user: store.state.auth.user,
        isLoggedIn: store.state.auth.isLoggedIn,
        token: store.state.auth.token?.substring(0, 10) + '...',
        isAdmin: store.state.auth.user?.is_admin
      });
      
      // Check axios headers
      console.log('Axios auth header:', axios.defaults.headers.common['Authorization'] ? 
        'Set (starts with ' + axios.defaults.headers.common['Authorization'].substring(0, 15) + '...)' : 
        'Not set');
    };
    
    return {
      loading,
      success,
      error,
      user,
      isAdmin,
      testLogin,
      logAuthState
    };
  }
};
</script>

<style scoped>
.test-admin-login {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}
.status {
  border: 1px solid #ccc;
  padding: 20px;
  margin-top: 20px;
}
button {
  padding: 10px 15px;
  margin-right: 10px;
  margin-top: 20px;
  cursor: pointer;
}
</style>
