<template>
  <div class="user-center">
    <el-card class="user-info-card">
      <div class="user-header">
        <el-avatar :size="80" icon="el-icon-user-solid"></el-avatar>
        <div class="user-details">
          <h2>{{ user.username }}</h2>
          <p>邮箱: {{ user.email }}</p>
          <p>注册时间: {{ formatDate(user.created_at) }}</p>
        </div>
      </div>
    </el-card>

    <el-tabs v-model="activeTab" class="tabs-container">
      <el-tab-pane label="实验提交记录" name="submissions">
        <el-card>
          <div class="submissions-header">
            <h3>我的实验提交</h3>
            <el-input
              placeholder="搜索实验名称"
              v-model="searchQuery"
              class="search-input"
              prefix-icon="el-icon-search">
            </el-input>
          </div>
          
          <el-table
            v-loading="loading"
            :data="filteredSubmissions"
            stripe
            style="width: 100%">
            <el-table-column
              prop="id"
              label="ID"
              width="70">
            </el-table-column>
            <el-table-column
              prop="experiment_title"
              label="实验名称"
              min-width="200">
              <template slot-scope="scope">
                <router-link :to="`/experiments/${scope.row.experiment_id}`">
                  {{ scope.row.experiment_title || `实验 #${scope.row.experiment_id}` }}
                </router-link>
              </template>
            </el-table-column>
            <el-table-column
              prop="submitted_at"
              label="提交时间"
              width="180">
              <template slot-scope="scope">
                {{ formatDate(scope.row.submitted_at) }}
              </template>
            </el-table-column>
            <el-table-column
              prop="status"
              label="状态"
              width="120">
              <template slot-scope="scope">
                <el-tag :type="getStatusType(scope.row.status)">
                  {{ getStatusText(scope.row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column
              prop="score"
              label="分数"
              width="100">
              <template slot-scope="scope">
                <span v-if="scope.row.score">{{ scope.row.score }}</span>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column
              label="操作"
              width="150">
              <template slot-scope="scope">
                <el-button 
                  size="mini" 
                  type="primary" 
                  @click="viewSubmission(scope.row)">
                  查看
                </el-button>
                <el-button 
                  size="mini" 
                  type="danger" 
                  @click="deleteSubmission(scope.row)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
      
      <el-tab-pane label="学习进度" name="progress">
        <el-card>
          <h3>学习进度统计</h3>
          <div class="progress-cards">
            <el-card class="progress-card">
              <div class="progress-icon"><i class="el-icon-s-data"></i></div>
              <div class="progress-value">{{ completedExperiments }}</div>
              <div class="progress-label">已完成实验</div>
            </el-card>
            
            <el-card class="progress-card">
              <div class="progress-icon"><i class="el-icon-trophy"></i></div>
              <div class="progress-value">{{ avgScore.toFixed(1) }}</div>
              <div class="progress-label">平均分数</div>
            </el-card>
            
            <el-card class="progress-card">
              <div class="progress-icon"><i class="el-icon-time"></i></div>
              <div class="progress-value">{{ totalHours }}</div>
              <div class="progress-label">学习小时数</div>
            </el-card>
          </div>
          
          <div class="category-progress">
            <h4>按类别统计</h4>
            <div v-for="(item, index) in categoryStats" :key="index" class="category-item">
              <div class="category-name">{{ getCategoryName(item.category) }}</div>
              <el-progress 
                :percentage="item.percentage" 
                :color="getCategoryColor(item.category)">
              </el-progress>
            </div>
          </div>
        </el-card>
      </el-tab-pane>
      
      <el-tab-pane label="收藏实验" name="favorites">
        <el-card v-if="favorites.length > 0">
          <div class="experiment-grid">
            <div v-for="experiment in favorites" :key="experiment.id" class="experiment-card">
              <el-card>
                <div class="experiment-title">{{ experiment.title }}</div>
                <div class="experiment-description">{{ experiment.description }}</div>
                <div class="experiment-footer">
                  <el-tag size="small">{{ getCategoryName(experiment.category) }}</el-tag>
                  <el-button 
                    type="primary" 
                    size="small" 
                    @click="goToExperiment(experiment.id)">
                    查看详情
                  </el-button>
                </div>
              </el-card>
            </div>
          </div>
        </el-card>
        <el-empty v-else description="暂无收藏实验"></el-empty>
      </el-tab-pane>
      
      <el-tab-pane label="个人设置" name="settings">
        <el-card>
          <el-form 
            :model="userForm" 
            status-icon 
            :rules="rules"
            ref="userForm" 
            label-width="100px">
            <el-form-item label="用户名" prop="username">
              <el-input v-model="userForm.username"></el-input>
            </el-form-item>
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="userForm.email" type="email"></el-input>
            </el-form-item>
            <el-form-item label="新密码" prop="password">
              <el-input v-model="userForm.password" type="password"></el-input>
            </el-form-item>
            <el-form-item label="确认密码" prop="confirmPassword">
              <el-input v-model="userForm.confirmPassword" type="password"></el-input>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="updateUserInfo">保存更改</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>
      
      <!-- 系统管理员菜单 -->
      <el-tab-pane v-if="isAdmin" label="系统管理" name="admin">
        <el-card>
          <el-menu class="admin-menu" mode="vertical">
            <el-menu-item index="1" @click="goToUserCenter">
              <i class="el-icon-user"></i>
              <span>个人中心</span>
            </el-menu-item>
            <el-menu-item index="2" @click="goToUserManagement">
              <i class="el-icon-s-custom"></i>
              <span>用户管理</span>
            </el-menu-item>
            <el-menu-item index="3" @click="goToSubmissions">
              <i class="el-icon-document"></i>
              <span>提交记录</span>
            </el-menu-item>
            <el-menu-item index="4" @click="goToExperiments">
              <i class="el-icon-s-data"></i>
              <span>实验管理</span>
            </el-menu-item>
          </el-menu>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- 提交详情对话框 -->
    <el-dialog title="提交详情" :visible.sync="dialogVisible" width="60%">
      <div v-if="currentSubmission">
        <h4>实验: {{ currentSubmission.experiment_title || `实验 #${currentSubmission.experiment_id}` }}</h4>
        <p><strong>提交时间:</strong> {{ formatDate(currentSubmission.submitted_at) }}</p>
        <p><strong>状态:</strong> {{ getStatusText(currentSubmission.status) }}</p>
        <p v-if="currentSubmission.score"><strong>分数:</strong> {{ currentSubmission.score }}</p>
        
        <el-divider></el-divider>
        
        <h4>报告内容:</h4>
        <div class="report-content">
          {{ currentSubmission.data?.report_content || "无报告内容" }}
        </div>
        
        <h4>代码提交:</h4>
        <div v-if="currentSubmission.data?.code_submissions">
          <div v-for="(code, stepId) in currentSubmission.data.code_submissions" :key="stepId">
            <h5>步骤 {{ stepId }}:</h5>
            <pre class="code-block">{{ code }}</pre>
          </div>
        </div>
        <div v-else>无代码提交</div>
        
        <div v-if="currentSubmission.feedback" class="feedback-section">
          <h4>评分反馈:</h4>
          <el-alert type="success" :closable="false">
            {{ currentSubmission.feedback }}
          </el-alert>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import axios from 'axios'
import { mapGetters } from 'vuex'

export default {
  name: 'UserCenter',
  data() {
    const validatePass2 = (rule, value, callback) => {
      if (value !== this.userForm.password) {
        callback(new Error('两次输入密码不一致!'))
      } else {
        callback()
      }
    }
    
    return {
      activeTab: 'submissions',
      loading: false,
      submissions: [],
      favorites: [],
      experiments: [],
      searchQuery: '',
      dialogVisible: false,
      currentSubmission: null,
      userForm: {
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
      },
      rules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
        ],
        email: [
          { required: true, message: '请输入邮箱地址', trigger: 'blur' },
          { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
        ],
        confirmPassword: [
          { validator: validatePass2, trigger: 'blur' }
        ]
      },
      totalHours: 20, // 模拟数据
      categoryStats: [
        { category: 'bank', percentage: 60 },
        { category: 'security', percentage: 75 },
        { category: 'insurance', percentage: 40 }
      ]
    }
  },
  computed: {
    ...mapGetters(['user', 'isAuthenticated']),
    
    isAdmin() {
      return this.user && (this.user.is_superuser || this.user.role === 'admin');
    },
    
    filteredSubmissions() {
      if (!this.searchQuery) {
        return this.submissions
      }
      
      const query = this.searchQuery.toLowerCase()
      return this.submissions.filter(sub => {
        return (sub.experiment_title || '').toLowerCase().includes(query)
      })
    },
    
    completedExperiments() {
      return this.submissions.filter(sub => sub.status === 'graded').length
    },
    
    avgScore() {
      const scoredSubmissions = this.submissions.filter(sub => sub.score)
      if (scoredSubmissions.length === 0) return 0
      
      const sum = scoredSubmissions.reduce((acc, sub) => acc + sub.score, 0)
      return sum / scoredSubmissions.length
    }
  },
  created() {
    // 确保从localStorage加载用户信息以防止刷新问题
    const localStorageUser = JSON.parse(localStorage.getItem('user') || '{}');
    
    // 如果store中没有用户信息但localStorage有，同步到store
    if (!this.user || !this.user.id) {
      if (localStorageUser && localStorageUser.id) {
        this.$store.dispatch('setUser', localStorageUser);
        console.log('从localStorage恢复用户信息到store:', localStorageUser);
      }
    }
    
    this.fetchUserData();
    this.userForm.username = this.user.username || localStorageUser.username;
    this.userForm.email = this.user.email || localStorageUser.email;
  },
  methods: {
    async fetchUserData() {
      this.loading = true
      try {
        // 获取正确的用户信息
        const storeUser = this.$store.getters.user || {};
        const localStorageUser = JSON.parse(localStorage.getItem('user') || '{}');
        
        // 在不同位置查找用户ID
        const userId = storeUser.id || localStorageUser.id || 1;
        console.log("当前用户ID (Store):", storeUser.id);
        console.log("当前用户ID (localStorage):", localStorageUser.id);
        console.log("实际使用的用户ID:", userId);
        
        // 确保store中有正确的用户信息
        if (localStorageUser.id && (!storeUser.id || storeUser.id !== localStorageUser.id)) {
          console.log("更新store中的用户信息");
          this.$store.dispatch('setUser', localStorageUser);
        }
        
        // 获取提交记录
        const submissionsResponse = await axios.get(`/api/v1/experiments/users/${userId}/submissions`)
        console.log("获取到的提交记录:", submissionsResponse.data);
        this.submissions = submissionsResponse.data || [];
        
        // 获取所有实验
        const experimentsResponse = await axios.get('/api/v1/experiments')
        this.experiments = experimentsResponse.data || [];
        
        // 为提交添加实验标题
        this.submissions.forEach(sub => {
          const experiment = this.experiments.find(exp => exp.id === sub.experiment_id)
          if (experiment) {
            sub.experiment_title = experiment.title
          } else {
            console.log(`未找到实验ID: ${sub.experiment_id}的实验信息`);
            sub.experiment_title = `实验 #${sub.experiment_id}`
          }
        })
        
        console.log("处理后的提交记录:", this.submissions);
        
        // 模拟收藏数据（实际项目中应从API获取）
        this.favorites = this.experiments.slice(0, 3)
      } catch (error) {
        console.error('获取用户数据失败', error)
        this.$message.error('获取用户数据失败: ' + (error.response?.data?.detail || error.message))
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
    
    getStatusType(status) {
      const types = {
        'submitted': 'info',
        'grading': 'warning',
        'graded': 'success',
        'failed': 'danger'
      }
      return types[status] || 'info'
    },
    
    getStatusText(status) {
      const texts = {
        'submitted': '已提交',
        'grading': '评分中',
        'graded': '已评分',
        'failed': '失败'
      }
      return texts[status] || status
    },
    
    getCategoryName(category) {
      const names = {
        'bank': '银行金融',
        'security': '证券投资',
        'insurance': '保险'
      }
      return names[category] || category
    },
    
    getCategoryColor(category) {
      const colors = {
        'bank': '#409EFF',
        'security': '#67C23A',
        'insurance': '#E6A23C'
      }
      return colors[category] || '#909399'
    },
    
    viewSubmission(submission) {
      this.currentSubmission = submission
      this.dialogVisible = true
    },
    
    goToExperiment(id) {
      this.$router.push(`/experiments/${id}`)
    },
    
    goToUserManagement() {
      this.$router.push('/admin/users')
    },
    
    goToSubmissions() {
      this.$router.push('/admin/submissions')
    },
    
    goToExperiments() {
      this.$router.push('/admin/experiments')
    },
    
    goToUserCenter() {
      this.activeTab = 'submissions'
    },
    
    updateUserInfo() {
      this.$refs.userForm.validate(async (valid) => {
        if (valid) {
          try {
            // 在实际项目中应调用API更新用户信息
            this.$message.success('个人信息更新成功')
          } catch (error) {
            console.error('更新个人信息失败', error)
            this.$message.error('更新个人信息失败')
          }
        }
      })
    },
    
    async deleteSubmission(submission) {
      try {
        // 显示确认对话框
        await this.$confirm('确认删除这条提交记录吗？此操作不可恢复', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        });
        
        // 获取用户ID和认证令牌
        const userId = this.user.id || 1;
        const token = this.$store.getters.token;
        const isAdmin = this.isAdmin; // 使用计算属性检查是否为管理员
        
        // 添加消息提示
        this.$message.info('正在删除...');
        
        // 调用API删除提交，添加认证头和明确的管理员标志
        const response = await axios.delete(
          `/api/v1/experiments/submissions/${submission.id}?user_id=${userId}&is_admin=${isAdmin}`,
          {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          }
        );
        
        console.log('删除成功:', response.data);
        
        // 提示用户
        this.$message.success('提交记录已成功删除');
        
        // 重新获取提交记录
        await this.fetchUserData();
      } catch (error) {
        if (error === 'cancel') {
          return; // 用户取消删除
        }
        
        console.error('删除提交记录失败', error);
        
        // 提供更详细的错误信息
        let errorMessage = '删除提交记录失败';
        if (error.response) {
          if (error.response.data && error.response.data.detail) {
            errorMessage += `: ${error.response.data.detail}`;
          } else {
            errorMessage += `: 服务器返回错误 (${error.response.status})`;
          }
        } else if (error.message) {
          errorMessage += `: ${error.message}`;
        }
        
        this.$message.error(errorMessage);
      }
    }
  }
}
</script>

<style scoped>
.user-center {
  padding: 20px;
}

.user-info-card {
  margin-bottom: 20px;
}

.user-header {
  display: flex;
  align-items: center;
}

.user-details {
  margin-left: 20px;
}

.user-details h2 {
  margin-top: 0;
  margin-bottom: 10px;
}

.user-details p {
  margin: 5px 0;
  color: #606266;
}

.tabs-container {
  margin-top: 20px;
}

.submissions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.submissions-header h3 {
  margin: 0;
}

.search-input {
  width: 250px;
}

.progress-cards {
  display: flex;
  justify-content: space-between;
  margin-bottom: 30px;
}

.progress-card {
  width: 30%;
  text-align: center;
  padding: 15px;
}

.progress-icon {
  font-size: 36px;
  color: #409EFF;
  margin-bottom: 10px;
}

.progress-value {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 5px;
}

.progress-label {
  color: #606266;
}

.category-progress {
  margin-top: 20px;
}

.category-item {
  margin-bottom: 15px;
}

.category-name {
  margin-bottom: 5px;
}

.experiment-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.experiment-card {
  height: 100%;
}

.experiment-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 10px;
}

.experiment-description {
  color: #606266;
  margin-bottom: 15px;
  height: 60px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

.experiment-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.report-content {
  background-color: #f8f8f8;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 20px;
  white-space: pre-wrap;
}

.code-block {
  background-color: #f8f8f8;
  padding: 15px;
  border-radius: 4px;
  overflow-x: auto;
  margin-bottom: 15px;
}

.feedback-section {
  margin-top: 20px;
}

.admin-menu {
  border-right: none;
}

.admin-menu .el-menu-item {
  height: 50px;
  line-height: 50px;
  font-size: 14px;
  margin: 5px 0;
}

.admin-menu .el-menu-item:hover {
  background-color: #f5f7fa;
}

.admin-menu .el-menu-item i {
  margin-right: 5px;
  font-size: 18px;
}
</style> 