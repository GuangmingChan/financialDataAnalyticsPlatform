<template>
  <div class="user-list">
    <el-card>
      <div slot="header" class="header">
        <span>用户管理</span>
        <el-input
          placeholder="搜索用户名或邮箱"
          v-model="searchQuery"
          class="search-input"
          prefix-icon="el-icon-search">
        </el-input>
      </div>
      
      <el-table
        v-loading="loading"
        :data="filteredUsers"
        stripe
        style="width: 100%">
        <el-table-column
          prop="id"
          label="ID"
          width="70">
        </el-table-column>
        <el-table-column
          prop="username"
          label="用户名"
          width="150">
        </el-table-column>
        <el-table-column
          prop="email"
          label="邮箱"
          width="220">
        </el-table-column>
        <el-table-column
          prop="created_at"
          label="注册时间"
          width="180">
          <template slot-scope="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column
          prop="role"
          label="角色"
          width="120">
          <template slot-scope="scope">
            <el-tag :type="getRoleType(scope.row)">
              {{ getRoleName(scope.row) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          prop="is_active"
          label="状态"
          width="100">
          <template slot-scope="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
              {{ scope.row.is_active ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          label="操作"
          width="200">
          <template slot-scope="scope">
            <el-button 
              size="mini" 
              type="primary" 
              @click="viewUser(scope.row)">
              查看
            </el-button>
            <el-button 
              size="mini" 
              type="success" 
              @click="editUser(scope.row)">
              编辑
            </el-button>
            <el-button 
              size="mini" 
              :type="scope.row.is_active ? 'danger' : 'warning'"
              @click="toggleUserStatus(scope.row)">
              {{ scope.row.is_active ? '禁用' : '启用' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 用户详情对话框 -->
    <el-dialog title="用户详情" :visible.sync="dialogVisible" width="50%">
      <div v-if="currentUser" class="user-detail">
        <div class="user-info">
          <h3>{{ currentUser.username }}</h3>
          <p><strong>邮箱:</strong> {{ currentUser.email }}</p>
          <p><strong>注册时间:</strong> {{ formatDate(currentUser.created_at) }}</p>
          <p><strong>角色:</strong> {{ getRoleName(currentUser) }}</p>
          <p><strong>状态:</strong> {{ currentUser.is_active ? '正常' : '禁用' }}</p>
          <p v-if="currentUser.full_name"><strong>姓名:</strong> {{ currentUser.full_name }}</p>
        </div>
      </div>
    </el-dialog>

    <!-- 编辑用户对话框 -->
    <el-dialog title="编辑用户" :visible.sync="editDialogVisible" width="50%">
      <el-form v-if="editForm" :model="editForm" :rules="rules" ref="editForm" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="editForm.username"></el-input>
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="editForm.email"></el-input>
        </el-form-item>
        <el-form-item label="姓名" prop="full_name">
          <el-input v-model="editForm.full_name"></el-input>
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="editForm.role" placeholder="请选择角色">
            <el-option label="普通用户" value="user"></el-option>
            <el-option label="管理员" value="admin"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="editForm.is_active"></el-switch>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="editForm.password" type="password" placeholder="不修改则留空"></el-input>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveUser">保存</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'UserList',
  data() {
    return {
      loading: false,
      users: [],
      searchQuery: '',
      dialogVisible: false,
      editDialogVisible: false,
      currentUser: null,
      editForm: null,
      rules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
        ],
        email: [
          { required: true, message: '请输入邮箱地址', trigger: 'blur' },
          { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
        ],
        role: [
          { required: true, message: '请选择角色', trigger: 'change' }
        ]
      }
    }
  },
  computed: {
    filteredUsers() {
      if (!this.searchQuery) {
        return this.users
      }
      
      const query = this.searchQuery.toLowerCase()
      return this.users.filter(user => {
        return user.username.toLowerCase().includes(query) || 
               user.email.toLowerCase().includes(query)
      })
    }
  },
  created() {
    this.fetchUsers()
  },
  methods: {
    async fetchUsers() {
      this.loading = true
      try {
        // 获取认证Token
        const token = this.$store.getters.token;
        
        // 设置请求头，包含认证信息
        const response = await axios.get('/api/v1/users/all', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        this.users = response.data
      } catch (error) {
        console.error('获取用户列表失败', error)
        this.$message.error('获取用户列表失败: ' + (error.response?.data?.detail || error.message))
      } finally {
        this.loading = false
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return '-'
      
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN', { 
        year: 'numeric', 
        month: '2-digit', 
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    
    getRoleType(user) {
      if (user.is_superuser) return 'danger'
      if (user.role === 'admin') return 'warning'
      return 'info'
    },
    
    getRoleName(user) {
      if (user.is_superuser) return '超级管理员'
      if (user.role === 'admin') return '管理员'
      return '普通用户'
    },
    
    viewUser(user) {
      this.currentUser = user
      this.dialogVisible = true
    },
    
    editUser(user) {
      this.currentUser = user
      this.editForm = {
        id: user.id,
        username: user.username,
        email: user.email,
        full_name: user.full_name || '',
        role: user.is_superuser ? 'admin' : (user.role || 'user'),
        is_active: user.is_active,
        password: ''
      }
      this.editDialogVisible = true
    },
    
    async toggleUserStatus(user) {
      try {
        await this.$confirm(
          `确定要${user.is_active ? '禁用' : '启用'}用户 "${user.username}" 吗？`, 
          '提示', 
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        // 在真实项目中应调用API更新用户状态
        // await axios.put(`/api/v1/users/${user.id}`, { is_active: !user.is_active })
        
        // 模拟API调用
        user.is_active = !user.is_active
        
        this.$message.success(`已${user.is_active ? '启用' : '禁用'}用户 "${user.username}"`)
      } catch (error) {
        if (error === 'cancel') return
        
        console.error('更新用户状态失败', error)
        this.$message.error('更新用户状态失败: ' + (error.response?.data?.detail || error.message))
      }
    },
    
    async saveUser() {
      this.$refs.editForm.validate(async (valid) => {
        if (valid) {
          try {
            // 在真实项目中应调用API更新用户信息
            // await axios.put(`/api/v1/users/${this.editForm.id}`, this.editForm)
            
            // 模拟API调用
            const userIndex = this.users.findIndex(u => u.id === this.currentUser.id)
            if (userIndex !== -1) {
              const updatedUser = {
                ...this.users[userIndex],
                username: this.editForm.username,
                email: this.editForm.email,
                full_name: this.editForm.full_name,
                role: this.editForm.role,
                is_superuser: this.editForm.role === 'admin',
                is_active: this.editForm.is_active
              }
              this.users.splice(userIndex, 1, updatedUser)
            }
            
            this.$message.success('用户信息已更新')
            this.editDialogVisible = false
          } catch (error) {
            console.error('更新用户信息失败', error)
            this.$message.error('更新用户信息失败: ' + (error.response?.data?.detail || error.message))
          }
        }
      })
    }
  }
}
</script>

<style scoped>
.user-list {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-input {
  width: 250px;
}

.user-detail {
  padding: 0 20px;
}

.user-info h3 {
  margin-top: 0;
}

.user-info p {
  margin: 10px 0;
}
</style> 