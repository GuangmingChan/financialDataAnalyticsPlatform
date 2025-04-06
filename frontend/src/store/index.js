import Vue from 'vue'
import Vuex from 'vuex'
import axios from 'axios'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    token: localStorage.getItem('token') || '',
    user: JSON.parse(localStorage.getItem('user') || '{}'),
    isAuthenticated: !!localStorage.getItem('token')
  },
  getters: {
    isAuthenticated: state => !!state.token,
    user: state => state.user,
    token: state => state.token,
    isAdmin: state => state.user && (state.user.is_superuser || state.user.role === 'admin')
  },
  mutations: {
    SET_TOKEN(state, token) {
      state.token = token
      state.isAuthenticated = !!token
      localStorage.setItem('token', token)
      // 设置axios默认的Authorization请求头
      if (token) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
      } else {
        delete axios.defaults.headers.common['Authorization']
      }
    },
    SET_USER(state, user) {
      state.user = user
      localStorage.setItem('user', JSON.stringify(user))
    },
    LOGOUT(state) {
      state.token = ''
      state.user = {}
      state.isAuthenticated = false
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      delete axios.defaults.headers.common['Authorization']
    }
  },
  actions: {
    setToken({ commit }, token) {
      commit('SET_TOKEN', token)
    },
    setUser({ commit }, user) {
      commit('SET_USER', user)
    },
    logout({ commit }) {
      commit('LOGOUT')
    }
  },
  modules: {
  }
})
