<template>
  <div class="register-container">
    <div class="register-box">
      <h2>用户注册</h2>
      
      <el-form :model="registerForm" status-icon :rules="rules" ref="registerForm" class="register-form">
        <el-form-item prop="username">
          <el-input 
            v-model="registerForm.username" 
            prefix-icon="el-icon-user" 
            placeholder="用户名">
          </el-input>
        </el-form-item>
        
        <el-form-item prop="email">
          <el-input 
            v-model="registerForm.email" 
            prefix-icon="el-icon-message" 
            placeholder="邮箱">
          </el-input>
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input 
            v-model="registerForm.password" 
            prefix-icon="el-icon-lock" 
            type="password" 
            placeholder="密码">
          </el-input>
        </el-form-item>
        
        <el-form-item prop="confirmPassword">
          <el-input 
            v-model="registerForm.confirmPassword" 
            prefix-icon="el-icon-lock" 
            type="password" 
            placeholder="确认密码">
          </el-input>
        </el-form-item>
        
        <el-form-item prop="fullName">
          <el-input 
            v-model="registerForm.fullName" 
            prefix-icon="el-icon-user" 
            placeholder="姓名">
          </el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            :loading="loading" 
            @click="submitForm('registerForm')" 
            class="register-button">
            注册
          </el-button>
        </el-form-item>
        
        <div class="form-footer">
          <span>已有账号？</span>
          <router-link to="/login" class="login-link">返回登录</router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'RegisterForm',
  data() {
    // 密码一致性校验
    const validatePass = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请再次输入密码'))
      } else if (value !== this.registerForm.password) {
        callback(new Error('两次输入密码不一致!'))
      } else {
        callback()
      }
    }
    
    return {
      registerForm: {
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
        fullName: ''
      },
      loading: false,
      rules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 3, message: '用户名长度至少为3个字符', trigger: 'blur' }
        ],
        email: [
          { required: true, message: '请输入邮箱地址', trigger: 'blur' },
          { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, message: '密码长度至少为6个字符', trigger: 'blur' }
        ],
        confirmPassword: [
          { required: true, message: '请再次输入密码', trigger: 'blur' },
          { validator: validatePass, trigger: 'blur' }
        ],
        fullName: [
          { required: true, message: '请输入姓名', trigger: 'blur' }
        ]
      }
    }
  },
  methods: {
    submitForm(formName) {
      this.$refs[formName].validate(async (valid) => {
        if (valid) {
          this.loading = true
          try {
            await axios.post('/api/v1/users/register', {
              username: this.registerForm.username,
              email: this.registerForm.email,
              password: this.registerForm.password,
              full_name: this.registerForm.fullName,
              is_active: true,
              is_superuser: false,
              role: 'student'
            })
            
            this.$message.success('注册成功，请登录')
            this.$router.push('/login')
          } catch (error) {
            let errorMsg = '注册失败'
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
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f7fa;
}

.register-box {
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

.register-form {
  margin-top: 20px;
}

.register-button {
  width: 100%;
}

.form-footer {
  margin-top: 20px;
  text-align: center;
  font-size: 14px;
  color: #606266;
}

.login-link {
  color: #409EFF;
  text-decoration: none;
  margin-left: 5px;
}
</style> 