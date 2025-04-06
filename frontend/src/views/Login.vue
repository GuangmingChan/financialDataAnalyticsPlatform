<template>
  <div class="login-container">
    <div class="login-box">
      <h2>金融大数据虚拟仿真实验平台</h2>
      
      <el-form :model="loginForm" status-icon :rules="rules" ref="loginForm" class="login-form">
        <el-form-item prop="username">
          <el-input 
            v-model="loginForm.username" 
            prefix-icon="el-icon-user" 
            placeholder="用户名/邮箱">
          </el-input>
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input 
            v-model="loginForm.password" 
            prefix-icon="el-icon-lock" 
            placeholder="密码" 
            type="password"
            @keyup.enter.native="submitForm('loginForm')">
          </el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            :loading="loading" 
            @click="submitForm('loginForm')" 
            class="login-button">
            登录
          </el-button>
        </el-form-item>
        
        <div class="form-footer">
          <span>还没有账号？</span>
          <router-link to="/register" class="register-link">立即注册</router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex'
import axios from 'axios'

export default {
  name: 'LoginForm',
  data() {
    return {
      loginForm: {
        username: '',
        password: ''
      },
      loading: false,
      rules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, message: '密码长度至少为6个字符', trigger: 'blur' }
        ]
      }
    }
  },
  methods: {
    ...mapActions(['setUser', 'setToken']),
    submitForm(formName) {
      this.$refs[formName].validate(async (valid) => {
        if (valid) {
          this.loading = true
          try {
            // 将用户名当作登录凭证（可以是邮箱或用户名）
            const formData = new URLSearchParams();
            formData.append('username', this.loginForm.username);
            formData.append('password', this.loginForm.password);
            
            const response = await axios.post('/api/v1/users/login', formData, {
              headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
              }
            })
            
            // 保存token和用户信息
            const token = response.data.access_token
            this.setToken(token)
            
            // 获取用户信息
            const userResponse = await axios.get('/api/v1/users/me', {
              headers: {
                'Authorization': `Bearer ${token}`
              }
            })
            
            this.setUser(userResponse.data)
            
            // 登录成功后重定向到首页
            this.$message.success('登录成功')
            this.$router.push('/')
          } catch (error) {
            let errorMsg = '登录失败'
            if (error.response) {
              errorMsg = error.response.data.detail || errorMsg
            }
            this.$message.error(errorMsg)
          } finally {
            this.loading = false
          }
        }
      })
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f7fa;
}

.login-box {
  width: 400px;
  padding: 30px;
  border-radius: 5px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  background-color: white;
}

h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #409EFF;
}

.login-form {
  margin-top: 30px;
}

.login-button {
  width: 100%;
}

.form-footer {
  margin-top: 20px;
  text-align: center;
  font-size: 14px;
  color: #606266;
}

.register-link {
  color: #409EFF;
  text-decoration: none;
  margin-left: 5px;
}
</style> 