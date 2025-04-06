<template>
  <div class="submission-list">
    <el-card>
      <div slot="header" class="header">
        <span>实验提交记录管理</span>
        <div class="filter-box">
          <el-input
            placeholder="搜索实验名称或用户"
            v-model="searchQuery"
            class="search-input"
            prefix-icon="el-icon-search">
          </el-input>
          <el-select v-model="statusFilter" placeholder="状态筛选" clearable>
            <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value">
            </el-option>
          </el-select>
        </div>
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
          label="用户"
          width="120">
          <template slot-scope="scope">
            {{ getUserName(scope.row) }}
          </template>
        </el-table-column>
        <el-table-column
          prop="experiment_title"
          label="实验名称"
          min-width="180">
          <template slot-scope="scope">
            <router-link :to="`/experiments/${scope.row.experiment_id}`">
              {{ scope.row.experiment_title || `实验 #${scope.row.experiment_id}` }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column
          prop="submitted_at"
          label="提交时间"
          width="160">
          <template slot-scope="scope">
            {{ formatDate(scope.row.submitted_at) }}
          </template>
        </el-table-column>
        <el-table-column
          prop="status"
          label="状态"
          width="100">
          <template slot-scope="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          prop="score"
          label="分数"
          width="80">
          <template slot-scope="scope">
            <span v-if="scope.row.score">{{ scope.row.score }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column
          label="操作"
          width="200">
          <template slot-scope="scope">
            <el-button 
              size="mini" 
              type="primary" 
              @click="viewSubmission(scope.row)">
              查看
            </el-button>
            <el-button 
              size="mini" 
              type="success" 
              @click="gradeSubmission(scope.row)"
              v-if="scope.row.status === 'submitted'">
              评分
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

    <!-- 提交详情对话框 -->
    <el-dialog title="提交详情" :visible.sync="dialogVisible" width="60%">
      <div v-if="currentSubmission">
        <div class="submission-header">
          <h4>实验: {{ currentSubmission.experiment_title || `实验 #${currentSubmission.experiment_id}` }}</h4>
          <p><strong>用户:</strong> {{ getUserName(currentSubmission) }}</p>
          <p><strong>提交时间:</strong> {{ formatDate(currentSubmission.submitted_at) }}</p>
          <p><strong>状态:</strong> {{ getStatusText(currentSubmission.status) }}</p>
          <p v-if="currentSubmission.score"><strong>分数:</strong> {{ currentSubmission.score }}</p>
        </div>
        
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

    <!-- 评分对话框 -->
    <el-dialog title="提交评分" :visible.sync="gradeDialogVisible" width="50%">
      <el-form :model="gradeForm" label-width="80px">
        <el-form-item label="分数">
          <el-input-number v-model="gradeForm.score" :min="0" :max="100"></el-input-number>
        </el-form-item>
        <el-form-item label="反馈">
          <el-input
            type="textarea"
            :rows="4"
            placeholder="请输入评分反馈..."
            v-model="gradeForm.feedback">
          </el-input>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="gradeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitGrade">确认</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'SubmissionList',
  data() {
    return {
      loading: false,
      submissions: [],
      experiments: [],
      searchQuery: '',
      statusFilter: '',
      dialogVisible: false,
      gradeDialogVisible: false,
      currentSubmission: null,
      gradeForm: {
        score: 80,
        feedback: ''
      },
      statusOptions: [
        { value: 'submitted', label: '已提交' },
        { value: 'grading', label: '评分中' },
        { value: 'graded', label: '已评分' },
        { value: 'failed', label: '失败' }
      ]
    }
  },
  computed: {
    filteredSubmissions() {
      if (!this.searchQuery && !this.statusFilter) {
        return this.submissions
      }
      
      return this.submissions.filter(sub => {
        let matchesSearch = true
        let matchesStatus = true
        
        if (this.searchQuery) {
          const query = this.searchQuery.toLowerCase()
          const title = (sub.experiment_title || '').toLowerCase()
          const userName = this.getUserName(sub).toLowerCase()
          matchesSearch = title.includes(query) || userName.includes(query)
        }
        
        if (this.statusFilter) {
          matchesStatus = sub.status === this.statusFilter
        }
        
        return matchesSearch && matchesStatus
      })
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    async fetchData() {
      this.loading = true;
      try {
        // 获取token
        const token = this.$store.getters.token;
        
        // 创建基本配置
        const config = {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        };
        
        // 获取所有提交记录 - 使用更简单的方式并添加错误处理
        try {
          console.log("正在获取实验提交记录...");
          
          // 添加超时设置和重试，提高可靠性
          const response = await axios.get('/api/v1/experiments/submissions', {
            ...config,
            timeout: 15000, // 15秒超时
            withCredentials: true // 确保包含凭证
          });
          
          console.log("成功获取实验提交记录 - 响应状态:", response.status);
          console.log("响应数据类型:", typeof response.data, Array.isArray(response.data));
          console.log("响应数据长度:", Array.isArray(response.data) ? response.data.length : "不是数组");
          
          if (Array.isArray(response.data)) {
            this.submissions = response.data;
            
            // 如果返回的数据为空，显示提示信息但不报错
            if (this.submissions.length === 0) {
              this.$message.info('暂无实验提交记录');
            }
          } else {
            console.warn("响应数据不是数组格式:", response.data);
            this.submissions = [];
            this.$message.warning('获取的数据格式不符合预期，已重置为空');
          }
        } catch (err) {
          console.error("获取实验提交记录失败:", err);
          if (err.response) {
            console.error("- 状态码:", err.response.status);
            console.error("- 响应头:", err.response.headers);
            console.error("- 错误详情:", err.response.data);
          } else if (err.request) {
            console.error("- 请求已发送但未收到响应:", err.request);
          } else {
            console.error("- 请求配置错误:", err.message);
          }
          
          this.submissions = [];
          let errorMsg = '无法获取实验提交记录';
          
          if (err.response) {
            if (err.response.status === 403) {
              errorMsg += '（没有足够权限）';
            } else if (err.response.status === 401) {
              errorMsg += '（未登录或会话已过期）';
              // 可能需要重定向到登录页面
              this.$message.error(errorMsg);
              setTimeout(() => {
                this.$router.push('/login');
              }, 2000);
              return;
            } else if (err.response.data && err.response.data.detail) {
              errorMsg += `（${err.response.data.detail}）`;
            } else {
              errorMsg += `（错误码: ${err.response.status}）`;
            }
          } else if (err.code === 'ECONNABORTED') {
            errorMsg += '（请求超时）';
          } else {
            errorMsg += '，请稍后再试';
          }
          
          this.$message.error(errorMsg);
        }
        
        // 获取所有实验数据 - 使用更简单的方式并添加错误处理
        try {
          console.log("正在获取实验数据...");
          const expsResponse = await axios.get('/api/v1/experiments', config);
          console.log("成功获取实验数据:", expsResponse.data);
          this.experiments = Array.isArray(expsResponse.data) ? expsResponse.data : [];
        } catch (err) {
          console.error("获取实验数据失败:", err);
          this.experiments = [];
        }
        
        // 尝试为提交添加实验标题
        if (this.submissions.length > 0 && this.experiments.length > 0) {
          this.submissions.forEach(sub => {
            const experiment = this.experiments.find(exp => exp.id === sub.experiment_id);
            if (experiment) {
              sub.experiment_title = experiment.title;
            } else {
              sub.experiment_title = `实验 #${sub.experiment_id}`;
            }
          });
        }
      } catch (error) {
        console.error('获取数据过程中发生错误:', error);
        
        // 提供更具体的错误信息
        let errorMessage = '获取数据失败';
        if (error.response) {
          if (error.response.status === 401) {
            errorMessage += ': 未授权访问，请重新登录';
          } else if (error.response.status === 403) {
            errorMessage += ': 没有访问权限';
          } else if (error.response.data && error.response.data.detail) {
            errorMessage += `: ${error.response.data.detail}`;
          }
        } else if (error.message) {
          errorMessage += `: ${error.message}`;
        }
        
        this.$message.error(errorMessage);
      } finally {
        this.loading = false;
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
    
    getUserName(submission) {
      if (submission.user_info && submission.user_info.username) {
        return submission.user_info.username
      } else {
        return `用户 ${submission.user_id}`
      }
    },
    
    viewSubmission(submission) {
      this.currentSubmission = submission
      this.dialogVisible = true
    },
    
    gradeSubmission(submission) {
      this.currentSubmission = submission
      this.gradeForm = {
        score: 80,
        feedback: ''
      }
      this.gradeDialogVisible = true
    },
    
    async submitGrade() {
      if (!this.currentSubmission) return;
      
      this.$message.info('正在提交评分...');
      
      try {
        const token = this.$store.getters.token;
        
        const response = await axios.put(
          `/api/v1/experiments/submissions/${this.currentSubmission.id}/grade`, 
          {
            score: this.gradeForm.score,
            feedback: this.gradeForm.feedback
          },
          {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          }
        );
        
        console.log('评分成功:', response.data);
        this.$message.success('评分成功');
        this.gradeDialogVisible = false;
        
        // 重新获取数据
        await this.fetchData();
      } catch (error) {
        console.error('评分失败:', error);
        
        let errorMessage = '评分失败';
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
    },
    
    async deleteSubmission(submission) {
      try {
        await this.$confirm('确认删除这条提交记录吗？此操作不可恢复', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        });
        
        this.$message.info('正在删除...');
        
        const token = this.$store.getters.token;
        
        const response = await axios.delete(
          `/api/v1/experiments/submissions/${submission.id}?user_id=1&is_admin=true`,
          {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          }
        );
        
        console.log('删除成功:', response.data);
        this.$message.success('提交记录已成功删除');
        
        // 重新获取数据
        await this.fetchData();
      } catch (error) {
        if (error === 'cancel') return;
        
        console.error('删除提交记录失败:', error);
        
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
.submission-list {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-box {
  display: flex;
  gap: 10px;
}

.search-input {
  width: 220px;
}

.submission-header {
  margin-bottom: 20px;
}

.submission-header h4 {
  margin-top: 0;
  margin-bottom: 10px;
}

.submission-header p {
  margin: 5px 0;
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
</style> 