import axios from 'axios'

const state = {
  token: localStorage.getItem('token') || '',
  user: JSON.parse(localStorage.getItem('user')) || null,
  loading: false,
  error: null
}

const getters = {
  isAuthenticated: state => !!state.token,
  currentUser: state => state.user,
  userRole: state => state.user ? state.user.role : null,
  authError: state => state.error,
  isAuthLoading: state => state.loading
}

const actions = {
  async login({ commit }, credentials) {
    commit('setLoading', true)
    commit('setError', null)
    
    try {
      // Replace with your actual API endpoint
      const response = await axios.post('/api/auth/login', credentials)
      
      if (response.data && response.data.token) {
        const token = response.data.token
        const user = response.data.user
        
        // Store auth data
        localStorage.setItem('token', token)
        localStorage.setItem('user', JSON.stringify(user))
        
        // Update state
        commit('setToken', token)
        commit('setUser', user)
        
        // Set authorization header for future requests
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
        
        return response.data
      }
    } catch (error) {
      commit('setError', error.response?.data?.message || 'Login failed')
      throw error
    } finally {
      commit('setLoading', false)
    }
  },
  
  logout({ commit }) {
    // Clear authentication data
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    delete axios.defaults.headers.common['Authorization']
    
    // Reset state
    commit('setToken', '')
    commit('setUser', null)
  }
}

const mutations = {
  setToken(state, token) {
    state.token = token
  },
  setUser(state, user) {
    state.user = user
  },
  setLoading(state, loading) {
    state.loading = loading
  },
  setError(state, error) {
    state.error = error
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
