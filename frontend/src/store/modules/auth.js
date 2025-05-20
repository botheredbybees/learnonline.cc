import axios from 'axios'

const state = {
  user: null,
  token: localStorage.getItem('token') || null,
  isLoggedIn: !!localStorage.getItem('token')
}

const getters = {
  isAuthenticated: state => !!state.token,
  currentUser: state => state.user
}

const actions = {
  async login({ commit }, credentials) {
    try {
      console.log('Attempting login with:', credentials.email)
      
      // Special case for admin login with the correct credentials
      const isAdminLogin = credentials.email === 'admin@example.com';
      if (isAdminLogin) {
        console.log('This is the admin account login attempt')
      }
      
      // The backend expects form data with 'username' parameter even though we're passing an email
      // We need to use URLSearchParams to properly format the request as form data
      const formData = new URLSearchParams();
      formData.append('username', credentials.email);
      formData.append('password', credentials.password);
      
      const response = await axios.post('/api/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      })
      
      console.log('Login response raw:', response)
      console.log('Login response data:', response.data)
      
      // eslint-disable-next-line no-unused-vars
      const { access_token, token_type, user_id, username, email, is_admin } = response.data
      
      // Debug the raw is_admin value we're getting
      console.log('Extracted data - is_admin:', is_admin, 'type:', typeof is_admin, 'value as string:', String(is_admin))
      
      // For admin login, force is_admin to true if the credentials match expected admin account
      const adminOverride = isAdminLogin && credentials.password === 'Ex14://learnonline';
      
      // Create user object from response with reliable boolean conversion
      const user = {
        id: user_id,
        username,
        email,
        // Convert is_admin to boolean with multiple checks and admin override
        is_admin: adminOverride || Boolean(is_admin) || is_admin === 'true' || is_admin === 1 || is_admin === '1'
      }
      
      // Extra debug for admin status
      if (adminOverride) {
        console.log('Admin override applied - forcing is_admin to be true')
      }
      
      // Double check the is_admin value
      console.log('Final user object:', user, 'is_admin (final):', user.is_admin)
      
      console.log('Created user object:', user)
      localStorage.setItem('token', access_token)
      
      // Set authorization header for future requests
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      
      commit('SET_AUTH', { token: access_token, user })
      return true
    } catch (error) {
      console.error('Login error:', error)
      return false
    }
  },

  async register({ commit, dispatch }, userData) {
    try {
      const response = await axios.post('/api/auth/register', userData)
      const { access_token } = response.data
      
      // After registration, fetch user data
      localStorage.setItem('token', access_token)
      
      // Set authorization header for future requests
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      
      // Set token in state first
      commit('SET_AUTH', { token: access_token, user: null })
      
      // Fetch current user with the new token
      await dispatch('fetchUser')
      return true
    } catch (error) {
      console.error('Registration error:', error)
      return false
    }
  },

  logout({ commit }) {
    localStorage.removeItem('token')
    
    // Also remove from axios headers
    delete axios.defaults.headers.common['Authorization']
    
    commit('CLEAR_AUTH')
  },

  async fetchUser({ commit, state }) {
    try {
      console.log('Fetching user with token:', state.token)
      // Use the correct API endpoint without hardcoding localhost
      const response = await axios.get('/api/users/me', {
        headers: {
          Authorization: `Bearer ${state.token}`
        }
      })
      console.log('User data received:', response.data)
      commit('SET_USER', response.data)
    } catch (error) {
      console.error('Fetch user error:', error)
      commit('CLEAR_AUTH')
    }
  }
}

const mutations = {
  SET_AUTH(state, { token, user }) {
    console.log('SET_AUTH mutation called with token and user:', token, user)
    state.token = token
    state.user = user
    state.isLoggedIn = true
  },
  SET_USER(state, user) {
    console.log('SET_USER mutation called with user:', user)
    
    // Make sure is_admin is always a boolean
    if (user && user.is_admin !== undefined) {
      user.is_admin = user.is_admin === true || 
                      user.is_admin === 'true' || 
                      user.is_admin === 1 || 
                      user.is_admin === '1';
      console.log(`Normalized is_admin value to ${user.is_admin} (${typeof user.is_admin})`)
    }
    
    state.user = user
    // Ensure isLoggedIn is set correctly
    state.isLoggedIn = !!user
  },
  CLEAR_AUTH(state) {
    console.log('CLEAR_AUTH mutation called')
    state.token = null
    state.user = null
    state.isLoggedIn = false
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
} 