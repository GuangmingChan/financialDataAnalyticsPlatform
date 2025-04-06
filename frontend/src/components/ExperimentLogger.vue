<template>
  <div class="experiment-logger">
    <el-card class="log-card">
      <div slot="header" class="log-header">
        <span>实验操作日志</span>
        <div class="header-actions">
          <el-switch
            v-model="autoScroll"
            active-text="自动滚动"
            inactive-text="">
          </el-switch>
          <el-button size="mini" type="primary" @click="generateReport">
            生成报告
          </el-button>
        </div>
      </div>
      
      <div class="log-content" ref="logContent">
        <div v-if="loading" class="loading-container">
          <el-skeleton :rows="5" animated />
        </div>
        
        <div v-else-if="logs.length === 0" class="empty-logs">
          <i class="el-icon-document"></i>
          <p>暂无操作日志</p>
        </div>
        
        <template v-else>
          <div 
            v-for="(log, index) in logs" 
            :key="index"
            class="log-item"
            :class="{'is-error': log.type === 'error', 'is-success': log.type === 'success'}">
            <div class="log-time">{{ formatTime(log.timestamp) }}</div>
            <div class="log-type" :class="'log-type-' + log.type">
              <i :class="logTypeIcon(log.type)"></i>
            </div>
            <div class="log-message">
              <div class="log-title">{{ log.message }}</div>
              <div v-if="log.details" class="log-details">
                <pre>{{ log.details }}</pre>
              </div>
              <div v-if="log.screenshot" class="log-screenshot">
                <img :src="log.screenshot" alt="操作截图" @click="previewImage(log.screenshot)" />
              </div>
            </div>
          </div>
        </template>
      </div>
      
      <div class="log-stats">
        <el-row :gutter="20">
          <el-col :span="8">
            <div class="stat-item">
              <div class="stat-value">{{ totalSteps }}</div>
              <div class="stat-label">总操作步骤</div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="stat-item">
              <div class="stat-value">{{ formatDuration(totalDuration) }}</div>
              <div class="stat-label">总耗时</div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="stat-item">
              <div class="stat-value">{{ successRate }}%</div>
              <div class="stat-label">成功率</div>
            </div>
          </el-col>
        </el-row>
      </div>
    </el-card>
    
    <!-- 图片预览 -->
    <el-dialog
      :visible.sync="previewVisible"
      width="70%"
      center>
      <img width="100%" :src="previewImage" alt="预览">
    </el-dialog>
    
    <!-- 报告生成对话框 -->
    <el-dialog
      title="实验报告"
      :visible.sync="reportDialogVisible"
      width="60%">
      <div class="report-content">
        <h2>《{{ experimentTitle }}》实验报告</h2>
        <p><strong>学生:</strong> {{ userName }}</p>
        <p><strong>实验日期:</strong> {{ formatDate(new Date()) }}</p>
        
        <div class="report-section">
          <h3>实验概述</h3>
          <p>{{ experimentDescription }}</p>
        </div>
        
        <div class="report-section">
          <h3>实验步骤</h3>
          <el-timeline>
            <el-timeline-item
              v-for="(step, index) in reportSteps"
              :key="index"
              :type="stepTypeClass(step.type)"
              :timestamp="formatTime(step.timestamp)">
              {{ step.message }}
              <div v-if="step.details" class="step-details">
                <pre>{{ step.details }}</pre>
              </div>
            </el-timeline-item>
          </el-timeline>
        </div>
        
        <div class="report-section">
          <h3>统计分析</h3>
          <el-row :gutter="20">
            <el-col :span="8">
              <el-card shadow="hover">
                <div slot="header">耗时分析</div>
                <div class="chart-container" ref="timeChart"></div>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card shadow="hover">
                <div slot="header">操作步骤分析</div>
                <div class="chart-container" ref="stepsChart"></div>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card shadow="hover">
                <div slot="header">操作结果分析</div>
                <div class="chart-container" ref="resultChart"></div>
              </el-card>
            </el-col>
          </el-row>
        </div>
        
        <div class="report-section">
          <h3>能力评估</h3>
          <el-table :data="skillsAssessment" border style="width: 100%">
            <el-table-column prop="skill" label="能力项"></el-table-column>
            <el-table-column prop="score" label="得分" width="100">
              <template slot-scope="scope">
                <el-rate
                  v-model="scope.row.score"
                  :colors="['#99A9BF', '#F7BA2A', '#FF9900']"
                  :max="5"
                  disabled>
                </el-rate>
              </template>
            </el-table-column>
            <el-table-column prop="comment" label="评语"></el-table-column>
          </el-table>
        </div>
        
        <div class="report-section">
          <h3>实验总结</h3>
          <el-input
            type="textarea"
            v-model="reportSummary"
            :rows="5"
            placeholder="请输入实验总结...">
          </el-input>
        </div>
      </div>
      
      <span slot="footer" class="dialog-footer">
        <el-button @click="reportDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="downloadReport">下载报告</el-button>
        <el-button type="success" @click="submitReport">提交报告</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import axios from 'axios';
import * as echarts from 'echarts';

export default {
  name: 'ExperimentLogger',
  props: {
    experimentId: {
      type: [String, Number],
      required: true
    },
    experimentTitle: {
      type: String,
      default: '未命名实验'
    },
    experimentDescription: {
      type: String,
      default: ''
    },
    userId: {
      type: [String, Number],
      required: true
    },
    userName: {
      type: String,
      default: '匿名用户'
    }
  },
  data() {
    return {
      logs: [],
      loading: false,
      autoScroll: true,
      previewVisible: false,
      previewImage: '',
      reportDialogVisible: false,
      reportSummary: '',
      startTime: Date.now(),
      timeChartInstance: null,
      stepsChartInstance: null,
      resultChartInstance: null,
      skillsAssessment: [
        { skill: '数据分析能力', score: 0, comment: '' },
        { skill: '问题解决能力', score: 0, comment: '' },
        { skill: '工具使用能力', score: 0, comment: '' },
        { skill: '代码编写能力', score: 0, comment: '' },
        { skill: '创新思维能力', score: 0, comment: '' }
      ],
    };
  },
  computed: {
    totalSteps() {
      return this.logs.length;
    },
    totalDuration() {
      if (this.logs.length === 0) return 0;
      const lastLog = this.logs[this.logs.length - 1];
      return lastLog.timestamp - this.startTime;
    },
    successRate() {
      if (this.logs.length === 0) return 0;
      const successLogs = this.logs.filter(log => log.type === 'success');
      return Math.round((successLogs.length / this.logs.length) * 100);
    },
    reportSteps() {
      // 获取重要的步骤用于报告
      return this.logs.filter(log => 
        log.type === 'info' || 
        log.type === 'success' || 
        log.type === 'error'
      );
    }
  },
  mounted() {
    this.fetchLogs();
    
    // 监听实验操作事件
    this.$root.$on('experiment-action', this.logAction);
    
    // 每30秒自动保存日志
    this.autoSaveInterval = setInterval(() => {
      this.saveLogs();
    }, 30000);
  },
  beforeDestroy() {
    this.$root.$off('experiment-action', this.logAction);
    clearInterval(this.autoSaveInterval);
    
    // 销毁图表实例
    [this.timeChartInstance, this.stepsChartInstance, this.resultChartInstance].forEach(chart => {
      if (chart) {
        chart.dispose();
      }
    });
  },
  methods: {
    async fetchLogs() {
      this.loading = true;
      try {
        // 实际项目中调用后端API
        // const response = await axios.get(`/api/v1/experiments/${this.experimentId}/logs?user_id=${this.userId}`);
        // this.logs = response.data;
        
        // 模拟数据
        await this.simulateFetchLogs();
        
        if (this.logs.length > 0) {
          this.startTime = this.logs[0].timestamp;
        }
        
        this.scrollToBottom();
      } catch (error) {
        console.error('获取实验日志失败', error);
      } finally {
        this.loading = false;
      }
    },
    
    simulateFetchLogs() {
      return new Promise(resolve => {
        setTimeout(() => {
          const now = Date.now();
          this.logs = [
            {
              type: 'info',
              message: '开始实验',
              details: `实验: ${this.experimentTitle}`,
              timestamp: now - 3600000, // 1小时前
            },
            {
              type: 'info',
              message: '加载数据',
              details: '数据加载成功，共500条记录',
              timestamp: now - 3540000, // 59分钟前
            },
            {
              type: 'success',
              message: '数据预处理完成',
              details: '处理缺失值: 25条\n标准化数值特征: 5列',
              timestamp: now - 3480000, // 58分钟前
            },
            {
              type: 'error',
              message: '模型训练失败',
              details: 'ValueError: Features dimensions mismatch',
              timestamp: now - 3300000, // 55分钟前
            },
            {
              type: 'info',
              message: '修改特征工程代码',
              timestamp: now - 3180000, // 53分钟前
            },
            {
              type: 'success',
              message: '模型训练成功',
              details: '训练准确率: 0.87\n验证准确率: 0.83',
              timestamp: now - 3000000, // 50分钟前
            }
          ];
          resolve();
        }, 500);
      });
    },
    
    logAction(action) {
      const log = {
        type: action.type || 'info',
        message: action.message,
        details: action.details,
        screenshot: action.screenshot,
        timestamp: Date.now()
      };
      
      this.logs.push(log);
      
      if (this.autoScroll) {
        this.$nextTick(() => {
          this.scrollToBottom();
        });
      }
      
      // 实际应用中可以发送到后端
      // axios.post(`/api/v1/experiments/${this.experimentId}/logs`, {
      //   user_id: this.userId,
      //   log: log
      // });
    },
    
    saveLogs() {
      console.log('保存日志...', this.logs.length);
      // 实际项目中调用后端API
      // axios.post(`/api/v1/experiments/${this.experimentId}/logs/batch`, {
      //   user_id: this.userId,
      //   logs: this.logs
      // });
    },
    
    scrollToBottom() {
      const container = this.$refs.logContent;
      if (container) {
        container.scrollTop = container.scrollHeight;
      }
    },
    
    formatTime(timestamp) {
      const date = new Date(timestamp);
      return date.toLocaleTimeString();
    },
    
    formatDate(date) {
      return date.toLocaleDateString();
    },
    
    formatDuration(ms) {
      const seconds = Math.floor(ms / 1000);
      const minutes = Math.floor(seconds / 60);
      const hours = Math.floor(minutes / 60);
      
      return `${hours}时${minutes % 60}分${seconds % 60}秒`;
    },
    
    logTypeIcon(type) {
      const icons = {
        'info': 'el-icon-info',
        'success': 'el-icon-success',
        'warning': 'el-icon-warning',
        'error': 'el-icon-error'
      };
      
      return icons[type] || 'el-icon-info';
    },
    
    stepTypeClass(type) {
      const classes = {
        'info': 'primary',
        'success': 'success',
        'warning': 'warning',
        'error': 'danger'
      };
      
      return classes[type] || 'primary';
    },
    
    previewImage(src) {
      this.previewImage = src;
      this.previewVisible = true;
    },
    
    generateReport() {
      this.reportDialogVisible = true;
      this.analyzeSkills();
      
      this.$nextTick(() => {
        this.renderReportCharts();
      });
    },
    
    analyzeSkills() {
      // 根据实验日志分析学生能力
      // 实际项目中应该调用后端API进行更复杂的分析
      
      // 模拟分析结果
      this.skillsAssessment = [
        { skill: '数据分析能力', score: 4, comment: '数据分析较为全面，能够从多个维度解读数据。' },
        { skill: '问题解决能力', score: 3.5, comment: '能够解决基本问题，但复杂问题处理能力有待提高。' },
        { skill: '工具使用能力', score: 4.5, comment: '对分析工具的使用非常熟练，能够充分利用工具特性。' },
        { skill: '代码编写能力', score: 3, comment: '代码基本正确，但可读性和效率有待提高。' },
        { skill: '创新思维能力', score: 2.5, comment: '解决方案较为常规，创新性不足。' }
      ];
    },
    
    renderReportCharts() {
      // 渲染时间耗时图表
      this.renderTimeChart();
      
      // 渲染步骤分析图表
      this.renderStepsChart();
      
      // 渲染结果分析图表
      this.renderResultChart();
    },
    
    renderTimeChart() {
      if (this.timeChartInstance) {
        this.timeChartInstance.dispose();
      }
      
      const chartDom = this.$refs.timeChart;
      this.timeChartInstance = echarts.init(chartDom);
      
      // 计算每个步骤的耗时
      const stepDurations = [];
      for (let i = 0; i < this.logs.length - 1; i++) {
        const duration = (this.logs[i + 1].timestamp - this.logs[i].timestamp) / 60000; // 分钟
        stepDurations.push({
          name: `步骤${i + 1}`,
          duration: Math.round(duration * 10) / 10
        });
      }
      
      const option = {
        tooltip: {
          trigger: 'axis',
          formatter: '{b}: {c} 分钟'
        },
        xAxis: {
          type: 'category',
          data: stepDurations.map(step => step.name)
        },
        yAxis: {
          type: 'value',
          name: '耗时(分钟)'
        },
        series: [{
          data: stepDurations.map(step => step.duration),
          type: 'bar'
        }]
      };
      
      this.timeChartInstance.setOption(option);
    },
    
    renderStepsChart() {
      if (this.stepsChartInstance) {
        this.stepsChartInstance.dispose();
      }
      
      const chartDom = this.$refs.stepsChart;
      this.stepsChartInstance = echarts.init(chartDom);
      
      // 统计不同类型的步骤数量
      const typeCounts = {
        'info': 0,
        'success': 0,
        'warning': 0,
        'error': 0
      };
      
      this.logs.forEach(log => {
        if (typeCounts[log.type] !== undefined) {
          typeCounts[log.type]++;
        }
      });
      
      const option = {
        tooltip: {
          trigger: 'item',
          formatter: '{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          left: 'left',
          data: ['信息', '成功', '警告', '错误']
        },
        series: [
          {
            type: 'pie',
            radius: '50%',
            data: [
              { value: typeCounts.info, name: '信息', itemStyle: { color: '#409EFF' } },
              { value: typeCounts.success, name: '成功', itemStyle: { color: '#67C23A' } },
              { value: typeCounts.warning, name: '警告', itemStyle: { color: '#E6A23C' } },
              { value: typeCounts.error, name: '错误', itemStyle: { color: '#F56C6C' } }
            ],
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            }
          }
        ]
      };
      
      this.stepsChartInstance.setOption(option);
    },
    
    renderResultChart() {
      if (this.resultChartInstance) {
        this.resultChartInstance.dispose();
      }
      
      const chartDom = this.$refs.resultChart;
      this.resultChartInstance = echarts.init(chartDom);
      
      // 能力雷达图
      const option = {
        tooltip: {},
        radar: {
          indicator: this.skillsAssessment.map(item => ({
            name: item.skill,
            max: 5
          }))
        },
        series: [{
          type: 'radar',
          data: [
            {
              value: this.skillsAssessment.map(item => item.score),
              name: '能力评估',
              areaStyle: {
                color: 'rgba(64, 158, 255, 0.2)'
              },
              lineStyle: {
                color: '#409EFF'
              }
            }
          ]
        }]
      };
      
      this.resultChartInstance.setOption(option);
    },
    
    downloadReport() {
      // 实际项目中应该调用后端API生成PDF报告
      this.$message.success('报告下载中...');
      
      // 模拟下载
      setTimeout(() => {
        this.$message.info('实际项目中应该调用后端API生成PDF报告');
      }, 1000);
    },
    
    async submitReport() {
      try {
        // 实际项目中应该调用后端API提交报告
        // await axios.post(`/api/v1/experiments/${this.experimentId}/reports`, {
        //   user_id: this.userId,
        //   summary: this.reportSummary,
        //   skills_assessment: this.skillsAssessment,
        //   logs: this.logs
        // });
        
        // 模拟提交
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        this.$message.success('报告已成功提交');
        this.reportDialogVisible = false;
        
        // 通知父组件
        this.$emit('report-submitted');
      } catch (error) {
        this.$message.error('提交报告失败: ' + error.message);
      }
    }
  }
};
</script>

<style scoped>
.experiment-logger {
  height: 100%;
}

.log-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 15px;
  align-items: center;
}

.log-content {
  flex: 1;
  overflow-y: auto;
  padding: 10px 0;
  min-height: 200px;
  max-height: 400px;
}

.empty-logs {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #909399;
}

.empty-logs i {
  font-size: 40px;
  margin-bottom: 10px;
}

.log-item {
  display: flex;
  margin-bottom: 10px;
  padding: 10px;
  border-radius: 4px;
  background-color: #f7f7f7;
}

.log-item.is-error {
  background-color: #fef0f0;
}

.log-item.is-success {
  background-color: #f0f9eb;
}

.log-time {
  min-width: 80px;
  color: #909399;
  font-size: 12px;
}

.log-type {
  margin-right: 10px;
  font-size: 16px;
}

.log-type-info {
  color: #409EFF;
}

.log-type-success {
  color: #67C23A;
}

.log-type-warning {
  color: #E6A23C;
}

.log-type-error {
  color: #F56C6C;
}

.log-message {
  flex: 1;
}

.log-title {
  font-weight: bold;
  margin-bottom: 5px;
}

.log-details {
  background-color: rgba(0, 0, 0, 0.03);
  padding: 8px;
  border-radius: 4px;
  margin-top: 5px;
  font-family: monospace;
  font-size: 12px;
  white-space: pre-wrap;
}

.log-screenshot {
  margin-top: 10px;
}

.log-screenshot img {
  max-width: 200px;
  max-height: 100px;
  border-radius: 4px;
  cursor: pointer;
  border: 1px solid #ddd;
}

.log-stats {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #ebeef5;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 20px;
  font-weight: bold;
  color: #409EFF;
}

.stat-label {
  font-size: 12px;
  color: #606266;
}

/* 报告相关样式 */
.report-content {
  margin-bottom: 20px;
}

.report-section {
  margin-bottom: 30px;
}

.chart-container {
  height: 200px;
}

.step-details {
  background-color: #f5f7fa;
  padding: 8px;
  border-radius: 4px;
  margin-top: 5px;
  font-family: monospace;
  font-size: 12px;
}
</style> 