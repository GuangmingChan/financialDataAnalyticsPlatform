<template>
  <div class="experiment-workspace" v-loading="loading">
    <el-container>
      <!-- 左侧步骤导航 -->
      <el-aside width="280px" class="steps-sidebar">
        <div class="experiment-info">
          <h3>{{ experiment ? experiment.title : '加载中...' }}</h3>
        </div>
        
        <el-menu 
          :default-active="currentStepId.toString()" 
          class="steps-menu"
          @select="selectStep">
          <el-menu-item 
            v-for="step in steps" 
            :key="step.id" 
            :index="step.id.toString()">
            <i class="el-icon-document"></i>
            <span>{{ step.title }}</span>
          </el-menu-item>
        </el-menu>
        
        <div class="action-buttons">
          <el-button type="success" size="medium" @click="submitExperiment">提交实验</el-button>
          <el-button size="medium" @click="exitExperiment">退出实验</el-button>
        </div>
      </el-aside>
      
      <!-- 主要内容区域 -->
      <el-container>
        <!-- 步骤内容 -->
        <el-main class="experiment-content">
          <div v-if="currentStep" class="step-content">
            <h2>{{ currentStep.title }}</h2>
            <p class="step-description">{{ currentStep.description }}</p>
            
            <!-- 代码编辑器 -->
            <el-card class="code-editor-card">
              <div slot="header">
                <span>代码编辑区</span>
                <el-button 
                  style="float: right; padding: 3px 0" 
                  type="text"
                  @click="runCode">
                  运行代码
                </el-button>
              </div>
              <div class="code-editor">
                <textarea ref="codeEditor" v-model="codeContent"></textarea>
              </div>
            </el-card>
            
            <!-- 结果显示区 -->
            <el-card class="result-card" v-if="hasResult">
              <div slot="header">
                <span>运行结果</span>
                <el-button 
                  style="float: right; padding: 3px 0" 
                  type="text"
                  @click="clearResult">
                  清除结果
                </el-button>
              </div>
              <div class="result-content">
                <pre>{{ executionResult }}</pre>
                <div v-if="resultCharts.length > 0" class="result-charts">
                  <div 
                    v-for="(chart, index) in resultCharts" 
                    :key="index"
                    class="chart-container">
                    <img :src="'data:image/png;base64,' + chart" />
                  </div>
                </div>
              </div>
            </el-card>
          </div>
          
          <div v-else class="no-step-selected">
            <h3>请从左侧选择一个实验步骤</h3>
          </div>
        </el-main>
      </el-container>
    </el-container>
    
    <!-- 提交实验对话框 -->
    <el-dialog
      title="提交实验报告"
      :visible.sync="submitDialogVisible"
      width="50%">
      <el-form :model="submissionForm" label-width="120px">
        <el-form-item label="实验报告内容">
          <el-input
            type="textarea"
            :rows="8"
            placeholder="请输入您的实验报告内容..."
            v-model="submissionForm.reportContent">
          </el-input>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="submitDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmSubmission">确认提交</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import axios from 'axios';
import CodeMirror from 'codemirror';
import 'codemirror/lib/codemirror.css';
import 'codemirror/theme/material.css';
import 'codemirror/mode/python/python';

export default {
  name: 'ExperimentWorkspace',
  data() {
    return {
      loading: true,
      experiment: null,
      steps: [],
      currentStepId: 1,
      currentStep: null,
      codeContent: '# 在这里编写您的代码\nimport pandas as pd\nimport numpy as np\nimport matplotlib.pyplot as plt\n\n# 您的代码开始\n',
      executionResult: '',
      resultCharts: [],
      hasResult: false,
      codeMirror: null,
      submitDialogVisible: false,
      submissionForm: {
        reportContent: ''
      },
      submitLoading: false,
      experimentId: null,
      userId: null
    };
  },
  methods: {
    async fetchExperiment() {
      try {
        const id = this.$route.params.id;
        const response = await axios.get(`/api/v1/experiments/${id}`);
        this.experiment = response.data;
        
        // 如果服务器从experiments_data.json返回的实验数据中包含步骤，直接使用
        if (this.experiment && this.experiment.steps && Array.isArray(this.experiment.steps)) {
          this.steps = this.experiment.steps;
          console.log("使用实验中包含的步骤数据");
        } else {
          // 否则单独获取步骤
          await this.fetchExperimentSteps();
        }
        
        this.experimentId = id;
        
        // 从store获取用户ID
        this.userId = this.$store.getters.user.id || 1;
        console.log("提交实验的用户ID:", this.userId);
        
        // 如果有步骤数据，选择第一个步骤
        if (this.steps.length > 0) {
          this.selectStep(this.steps[0].id.toString());
        }
      } catch (error) {
        this.$message.error('获取实验详情失败: ' + error.message);
      } finally {
        this.loading = false;
      }
    },
    async fetchExperimentSteps() {
      try {
        const id = this.$route.params.id;
        // 使用新的API端点获取带有示例代码的步骤
        const response = await axios.get(`/api/v1/experiments/${id}/steps_with_code`);
        console.log('获取到带有示例代码的步骤:', response.data);
        this.steps = response.data;
        if (this.steps.length > 0) {
          this.selectStep(this.steps[0].id.toString());
        }
      } catch (error) {
        console.error('获取实验步骤失败:', error);
        this.$message.error('获取实验步骤失败: ' + error.message);
        
        // 如果新API失败，回退到旧API
        try {
          const id = this.$route.params.id;
          const response = await axios.get(`/api/v1/experiments/${id}/steps`);
          this.steps = response.data;
          if (this.steps.length > 0) {
            this.selectStep(this.steps[0].id.toString());
          }
        } catch (fallbackError) {
          this.$message.error('获取实验步骤失败: ' + fallbackError.message);
        }
      }
    },
    selectStep(stepId) {
      this.currentStepId = parseInt(stepId);
      this.currentStep = this.steps.find(step => step.id === this.currentStepId);
      
      // 设置默认代码显示
      this.setDefaultCode();
      
      // 尝试加载实验数据
      this.loadStepData();
    },
    async loadStepData() {
      if (!this.currentStep) return;
      
      try {
        // 首先检查当前步骤是否包含示例代码
        if (this.currentStep.example_code) {
          console.log('使用步骤中自带的示例代码');
          this.codeContent = this.currentStep.example_code;
          
          // 如果编辑器已初始化，更新内容
          if (this.codeMirror) {
            this.codeMirror.setValue(this.currentStep.example_code);
          }
          return;
        }
        
        const experimentId = this.$route.params.id;
        
        // 如果没有自定义示例代码，继续使用默认生成代码的逻辑
        const response = await axios.get(`/api/v1/experiments/${experimentId}/data`);
        
        // 防御性检查API返回的数据格式
        if (!response || !response.data) {
          console.warn('API未返回预期数据');
          return;
        }
        
        // 保护性地处理数据
        let sampleData = [];
        
        try {
          // 不尝试使用slice，而是手动构建数组
          const responseData = response.data;
          
          // 如果是数组，取前5个元素
          if (Array.isArray(responseData)) {
            sampleData = responseData.slice(0, 5);
          } 
          // 如果有data字段且是数组
          else if (responseData.data && Array.isArray(responseData.data)) {
            sampleData = responseData.data.slice(0, 5);
          }
          // 如果是对象
          else if (typeof responseData === 'object') {
            // 把对象转换为示例数据
            sampleData = [responseData];
          }
          // 其他情况
          else {
            // 创建一个默认数据结构
            sampleData = [{ '示例数据': '请添加您的代码逻辑' }];
          }
        } catch (error) {
          console.error('处理数据样本时出错:', error);
          sampleData = [{ '示例数据': '请添加您的代码逻辑' }];
        }
        
        const exampleCode = `# 步骤：${this.currentStep.title}\n` +
                          `# ${this.currentStep.description}\n\n` +
                          `import pandas as pd\nimport numpy as np\nimport matplotlib.pyplot as plt\n\n` +
                          `# 加载实验数据\n` +
                          `data = pd.DataFrame(${JSON.stringify(sampleData)})\n\n` +
                          `# 数据预览\n` +
                          `print(data.head())\n\n` +
                          `# 在这里添加您的分析代码\n`;
        
        this.codeContent = exampleCode;
        
        // 如果编辑器已初始化，更新内容
        if (this.codeMirror) {
          this.codeMirror.setValue(exampleCode);
        }
      } catch (error) {
        console.error('加载步骤数据失败:', error);
      }
    },
    setDefaultCode() {
      const stepName = this.currentStep ? this.currentStep.title : '实验步骤';
      const stepDesc = this.currentStep ? this.currentStep.description : '';
      
      const defaultCode = `# 步骤：${stepName}\n` +
                        `# ${stepDesc}\n\n` +
                        `import pandas as pd\nimport numpy as np\nimport matplotlib.pyplot as plt\n\n` +
                        `# 示例数据\n` +
                        `data = pd.DataFrame({\n` +
                        `    '列1': [1, 2, 3, 4, 5],\n` +
                        `    '列2': [10, 20, 30, 40, 50]\n` +
                        `})\n\n` +
                        `# 数据预览\n` +
                        `print(data.head())\n\n` +
                        `# 在这里添加您的分析代码\n`;
      
      this.codeContent = defaultCode;
      
      // 如果编辑器已初始化，更新内容
      if (this.codeMirror) {
        this.codeMirror.setValue(defaultCode);
      }
    },
    initCodeEditor() {
      // 手动创建textarea元素
      if (!this.$refs.codeEditor) {
        console.error('代码编辑器容器不存在');
        return;
      }
      
      const container = this.$refs.codeEditor;
      
      try {
        // 如果编辑器已存在，先销毁
        if (this.codeMirror) {
          this.codeMirror.toTextArea();
          this.codeMirror = null;
        }
        
        // 初始化编辑器
        this.codeMirror = CodeMirror.fromTextArea(container, {
          lineNumbers: true,
          mode: 'python',
          theme: 'material',
          indentUnit: 4,
          smartIndent: true,
          lineWrapping: true,
          foldGutter: true,
          gutters: ["CodeMirror-linenumbers", "CodeMirror-foldgutter"],
          extraKeys: {"Ctrl-Space": "autocomplete"}
        });
        
        // 设置代码并监听变化
        this.codeMirror.setValue(this.codeContent);
        this.codeMirror.on('change', (cm) => {
          this.codeContent = cm.getValue();
        });
        
        console.log('代码编辑器初始化成功');
      } catch (error) {
        console.error('初始化代码编辑器失败:', error);
      }
    },
    async runCode() {
      this.hasResult = true;
      this.executionResult = '执行中...\n';
      this.resultCharts = [];
      
      try {
        const response = await axios.post('/api/v1/execute-code/execute-code', {
          code: this.codeContent,
          experiment_id: this.$route.params.id,
          step_id: this.currentStepId
        });
        
        this.executionResult = response.data.output || 'No output';
        
        if (response.data.charts && response.data.charts.length > 0) {
          this.resultCharts = response.data.charts;
        }
      } catch (error) {
        this.executionResult = '执行错误: ' + (error.response?.data?.detail || error.message);
      }
    },
    clearResult() {
      this.hasResult = false;
      this.executionResult = '';
      this.resultCharts = [];
    },
    async submitExperiment() {
      this.submitLoading = true;
      
      try {
        // 获取用户ID - 使用与用户中心相同的逻辑
        const storeUser = this.$store.getters.user || {};
        const localStorageUser = JSON.parse(localStorage.getItem('user') || '{}');
        const userId = storeUser.id || localStorageUser.id || 1;
        
        console.log("提交时使用的用户ID (Store):", storeUser.id);
        console.log("提交时使用的用户ID (localStorage):", localStorageUser.id);
        console.log("实际提交使用的用户ID:", userId);
        
        // 确保store中有正确的用户信息
        if (localStorageUser.id && (!storeUser.id || storeUser.id !== localStorageUser.id)) {
          console.log("提交前更新store中的用户信息");
          this.$store.dispatch('setUser', localStorageUser);
        }
        
        // Simple data for submission
        const submissionData = {
          report_content: "简单报告内容",
          code_submissions: { "1": "#简单的代码示例" }
        };

        console.log("提交的数据:", submissionData);
        
        // 使用原生 XMLHttpRequest
        const response = await new Promise((resolve, reject) => {
          const xhr = new XMLHttpRequest();
          xhr.open('POST', `/api/v1/experiments/${this.experimentId}/submit?user_id=${userId}`);
          xhr.setRequestHeader('Content-Type', 'application/json');
          
          xhr.onload = function() {
            if (this.status >= 200 && this.status < 300) {
              resolve(JSON.parse(xhr.response));
            } else {
              reject({
                status: this.status,
                statusText: xhr.statusText,
                response: xhr.response
              });
            }
          };
          
          xhr.onerror = function() {
            reject({
              status: this.status,
              statusText: xhr.statusText,
              response: xhr.response
            });
          };
          
          xhr.send(JSON.stringify(submissionData));
        });
        
        console.log("提交成功:", response);
        this.$message.success("实验报告提交成功");
        
        // 延迟后跳转到个人中心页面
        setTimeout(() => {
          this.$router.push('/user-center');
        }, 1500);
        
      } catch (error) {
        console.error("提交失败:", error);
        this.$message.error(`提交失败: ${error.response || error.statusText || '未知错误'}`);
      } finally {
        this.submitLoading = false;
      }
    },
    exitExperiment() {
      this.$confirm('确定要退出实验吗？未保存的代码将会丢失。', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.$router.push('/experiments');
      }).catch(() => {});
    }
  },
  mounted() {
    this.fetchExperiment();
    
    // 等待DOM渲染完成后初始化编辑器
    this.$nextTick(() => {
      // 延迟初始化避免DOM不存在的问题
      setTimeout(() => {
        this.initCodeEditor();
      }, 500);
    });
  },
  beforeDestroy() {
    if (this.codeMirror) {
      this.codeMirror.toTextArea();
    }
  }
};
</script>

<style scoped>
.experiment-workspace {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.steps-sidebar {
  background-color: #f5f7fa;
  border-right: 1px solid #e6e6e6;
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.experiment-info {
  padding: 20px;
  border-bottom: 1px solid #e6e6e6;
}

.steps-menu {
  flex: 1;
  border-right: none;
}

.action-buttons {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.experiment-content {
  padding: 20px;
  overflow-y: auto;
}

.step-description {
  margin-bottom: 20px;
  color: #606266;
}

.code-editor-card, .result-card {
  margin-bottom: 20px;
}

.code-editor {
  height: 500px;
}

.result-content {
  min-height: 100px;
  max-height: 600px;
  overflow-y: auto;
}

.result-content pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.result-charts {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-top: 20px;
}

.chart-container {
  max-width: 100%;
  overflow: auto;
}

.chart-container img {
  max-width: 100%;
}

.no-step-selected {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
  color: #909399;
}
</style> 