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
      const response = await axios.post('http://localhost:8000/auth/login', credentials)
      const { token, user } = response.data
      
      localStorage.setItem('token', token)
      commit('SET_AUTH', { token, user })
      return true
    } catch (error) {
      console.error('Login error:', error)
      return false
    }
  },

  async register({ commit }, userData) {
    try {
      const response = await axios.post('http://localhost:8000/auth/register', userData)
      const { token, user } = response.data
      
      localStorage.setItem('token', token)
      commit('SET_AUTH', { token, user })
      return true
    } catch (error) {
      console.error('Registration error:', error)
      return false
    }
  },

  logout({ commit }) {
    localStorage.removeItem('token')
    commit('CLEAR_AUTH')
  },

  async fetchUser({ commit }) {
    try {
      const response = await axios.get('http://localhost:8000/auth/me', {
        headers: {
          Authorization: `Bearer ${state.token}`
        }
      })
      commit('SET_USER', response.data)
    } catch (error) {
      console.error('Fetch user error:', error)
      commit('CLEAR_AUTH')
    }
  }
}

const mutations = {
  SET_AUTH(state, { token, user }) {
    state.token = token
    state.user = user
    state.isLoggedIn = true
  },
  SET_USER(state, user) {
    state.user = user
  },
  CLEAR_AUTH(state) {
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