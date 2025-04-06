<template>
  <div class="teacher-evaluation">
    <el-card class="eval-card">
      <div slot="header" class="eval-header">
        <span>实验评估</span>
        <div class="header-actions">
          <el-select v-model="currentClass" placeholder="选择班级" size="small" @change="fetchSubmissions">
            <el-option
              v-for="item in classes"
              :key="item.id"
              :label="item.name"
              :value="item.id">
            </el-option>
          </el-select>
          <el-button type="primary" size="small" @click="exportGrades">导出成绩</el-button>
        </div>
      </div>
      
      <div class="evaluation-container" v-loading="loading">
        <!-- 左侧提交列表 -->
        <div class="submissions-list">
          <el-input
            placeholder="搜索学生或实验"
            prefix-icon="el-icon-search"
            v-model="searchQuery"
            clearable>
          </el-input>
          
          <div class="filter-options">
            <el-radio-group v-model="statusFilter" size="small">
              <el-radio-button label="all">全部</el-radio-button>
              <el-radio-button label="pending">待评</el-radio-button>
              <el-radio-button label="evaluated">已评</el-radio-button>
            </el-radio-group>
          </div>
          
          <el-scrollbar class="submissions-scrollbar">
            <div 
              v-for="submission in filteredSubmissions" 
              :key="submission.id"
              class="submission-item"
              :class="{ 'active': currentSubmission && currentSubmission.id === submission.id }"
              @click="selectSubmission(submission)">
              <div class="submission-meta">
                <div class="student-info">
                  <span class="student-name">{{ submission.student.name }}</span>
                  <span class="student-id">{{ submission.student.id }}</span>
                </div>
                <div class="experiment-title">{{ submission.experiment.title }}</div>
                <div class="submission-time">提交时间: {{ formatDate(submission.submitTime) }}</div>
              </div>
              
              <div class="submission-status">
                <el-tag v-if="submission.evaluated" type="success" size="small">已评</el-tag>
                <el-tag v-else type="info" size="small">待评</el-tag>
              </div>
            </div>
            
            <div v-if="filteredSubmissions.length === 0" class="empty-list">
              <el-empty description="暂无符合条件的提交"></el-empty>
            </div>
          </el-scrollbar>
        </div>
        
        <!-- 右侧评估区域 -->
        <div class="evaluation-area" v-if="currentSubmission">
          <el-tabs v-model="activeTab">
            <!-- 实验内容 -->
            <el-tab-pane label="实验内容" name="content">
              <div class="content-section">
                <h3>{{ currentSubmission.experiment.title }}</h3>
                <div class="student-info-header">
                  <span>学生: {{ currentSubmission.student.name }}</span>
                  <span>学号: {{ currentSubmission.student.id }}</span>
                  <span>提交时间: {{ formatDate(currentSubmission.submitTime) }}</span>
                </div>
                
                <el-divider content-position="left">实验过程</el-divider>
                <div class="process-timeline">
                  <el-timeline>
                    <el-timeline-item
                      v-for="(log, index) in currentSubmission.logs"
                      :key="index"
                      :timestamp="formatTime(log.timestamp)"
                      :type="getTimelineItemType(log.type)">
                      <h4>{{ log.title }}</h4>
                      <p>{{ log.description }}</p>
                      <div v-if="log.screenshot" class="log-screenshot">
                        <el-image
                          :src="log.screenshot"
                          :preview-src-list="[log.screenshot]"
                          fit="contain"
                          style="max-height: 150px;">
                        </el-image>
                      </div>
                    </el-timeline-item>
                  </el-timeline>
                </div>
                
                <el-divider content-position="left">实验代码</el-divider>
                <div class="code-section">
                  <pre class="code-display">{{ currentSubmission.code }}</pre>
                </div>
                
                <el-divider content-position="left">实验结果</el-divider>
                <div class="result-section">
                  <div v-if="currentSubmission.resultType === 'image'" class="result-image">
                    <el-image
                      :src="currentSubmission.resultUrl"
                      :preview-src-list="[currentSubmission.resultUrl]"
                      fit="contain">
                    </el-image>
                  </div>
                  <pre v-else-if="currentSubmission.resultType === 'text'" class="result-text">{{ currentSubmission.resultContent }}</pre>
                  <el-empty v-else description="无结果数据"></el-empty>
                </div>
                
                <el-divider content-position="left">同行评议</el-divider>
                <div class="peer-reviews">
                  <el-collapse v-if="currentSubmission.peerReviews && currentSubmission.peerReviews.length > 0">
                    <el-collapse-item 
                      v-for="(review, index) in currentSubmission.peerReviews" 
                      :key="index"
                      :title="`同行评议 #${index + 1} - 总分: ${calculateReviewScore(review)}`">
                      <div class="review-details">
                        <div class="review-scores">
                          <div class="score-item">
                            <span class="score-label">创新性:</span>
                            <el-rate v-model="review.innovationScore" disabled></el-rate>
                          </div>
                          <div class="score-item">
                            <span class="score-label">完整性:</span>
                            <el-rate v-model="review.completenessScore" disabled></el-rate>
                          </div>
                          <div class="score-item">
                            <span class="score-label">实用性:</span>
                            <el-rate v-model="review.practicalityScore" disabled></el-rate>
                          </div>
                        </div>
                        <div class="review-comment">
                          <div class="comment-label">评价意见:</div>
                          <div class="comment-content">{{ review.comment }}</div>
                        </div>
                      </div>
                    </el-collapse-item>
                  </el-collapse>
                  <el-empty v-else description="暂无同行评议"></el-empty>
                </div>
              </div>
            </el-tab-pane>
            
            <!-- 评分评价 -->
            <el-tab-pane label="评分评价" name="evaluation">
              <div class="evaluation-form">
                <el-form :model="evaluationForm" ref="evaluationForm" label-width="120px">
                  <el-divider content-position="left">自动评分</el-divider>
                  
                  <el-form-item label="算法正确性">
                    <div class="auto-grade">
                      <span class="grade-value">{{ evaluationForm.algorithmAccuracy }}分</span>
                      <span class="grade-max">/ 20分</span>
                      <el-tooltip content="基于算法实现的正确性和执行结果自动计算" placement="top">
                        <i class="el-icon-info"></i>
                      </el-tooltip>
                    </div>
                  </el-form-item>
                  
                  <el-form-item label="实验完整性">
                    <div class="auto-grade">
                      <span class="grade-value">{{ evaluationForm.completeness }}分</span>
                      <span class="grade-max">/ 15分</span>
                      <el-tooltip content="基于提交的实验步骤完成情况自动计算" placement="top">
                        <i class="el-icon-info"></i>
                      </el-tooltip>
                    </div>
                  </el-form-item>
                  
                  <el-form-item label="同行评议平均分">
                    <div class="auto-grade">
                      <span class="grade-value">{{ evaluationForm.peerReviewScore }}分</span>
                      <span class="grade-max">/ 15分</span>
                      <el-tooltip content="基于同行评议的平均得分折算" placement="top">
                        <i class="el-icon-info"></i>
                      </el-tooltip>
                    </div>
                  </el-form-item>
                  
                  <el-divider content-position="left">教师评分</el-divider>
                  
                  <el-form-item label="代码质量" prop="codeQuality">
                    <el-slider
                      v-model="evaluationForm.codeQuality"
                      :step="1"
                      :max="20"
                      show-stops
                      show-input>
                    </el-slider>
                    <div class="score-hint">
                      <span>代码风格、可读性、注释、错误处理等</span>
                    </div>
                  </el-form-item>
                  
                  <el-form-item label="实验报告质量" prop="reportQuality">
                    <el-slider
                      v-model="evaluationForm.reportQuality"
                      :step="1"
                      :max="20"
                      show-stops
                      show-input>
                    </el-slider>
                    <div class="score-hint">
                      <span>分析深度、逻辑严密性、结论合理性等</span>
                    </div>
                  </el-form-item>
                  
                  <el-form-item label="创新加分" prop="innovationBonus">
                    <el-slider
                      v-model="evaluationForm.innovationBonus"
                      :step="1"
                      :max="10"
                      show-stops
                      show-input>
                    </el-slider>
                    <div class="score-hint">
                      <span>实验方法创新、拓展性思考、额外功能实现等</span>
                    </div>
                  </el-form-item>
                  
                  <el-form-item label="教师评语" prop="comment">
                    <el-input
                      type="textarea"
                      :rows="4"
                      placeholder="请输入评语，包括优点、存在的问题以及改进建议"
                      v-model="evaluationForm.comment">
                    </el-input>
                  </el-form-item>
                  
                  <el-divider content-position="left">最终成绩</el-divider>
                  
                  <div class="final-score">
                    <div class="score-breakdown">
                      <el-tooltip content="算法正确性 + 实验完整性 + 同行评议分 + 代码质量 + 实验报告质量 + 创新加分" placement="top">
                        <div class="total-formula">
                          {{ evaluationForm.algorithmAccuracy }} + {{ evaluationForm.completeness }} + {{ evaluationForm.peerReviewScore }} + {{ evaluationForm.codeQuality }} + {{ evaluationForm.reportQuality }} + {{ evaluationForm.innovationBonus }} = {{ calculateTotalScore() }}
                        </div>
                      </el-tooltip>
                    </div>
                    
                    <div class="final-grade">
                      <span class="final-label">最终成绩:</span>
                      <span class="final-value">{{ calculateTotalScore() }}</span>
                      <span class="final-max">/ 100</span>
                    </div>
                  </div>
                  
                  <div class="form-actions">
                    <el-button type="primary" @click="submitEvaluation" :loading="submitting">提交评估</el-button>
                    <el-button @click="resetEvaluation">重置</el-button>
                  </div>
                </el-form>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
        
        <div class="no-selection" v-else>
          <el-empty description="请选择一个实验提交进行评估"></el-empty>
        </div>
      </div>
    </el-card>
    
    <!-- 导出成绩对话框 -->
    <el-dialog
      title="导出成绩"
      :visible.sync="exportDialogVisible"
      width="450px">
      <div class="export-options">
        <el-form label-width="100px">
          <el-form-item label="班级">
            <el-select v-model="exportClass" placeholder="选择班级">
              <el-option
                v-for="item in classes"
                :key="item.id"
                :label="item.name"
                :value="item.id">
              </el-option>
            </el-select>
          </el-form-item>
          
          <el-form-item label="实验">
            <el-select v-model="exportExperiment" placeholder="选择实验">
              <el-option
                v-for="item in experiments"
                :key="item.id"
                :label="item.title"
                :value="item.id">
              </el-option>
            </el-select>
          </el-form-item>
          
          <el-form-item label="格式">
            <el-radio-group v-model="exportFormat">
              <el-radio label="excel">Excel</el-radio>
              <el-radio label="csv">CSV</el-radio>
            </el-radio-group>
          </el-form-item>
          
          <el-form-item label="内容">
            <el-checkbox-group v-model="exportContent">
              <el-checkbox label="基本信息">基本信息</el-checkbox>
              <el-checkbox label="详细得分">详细得分</el-checkbox>
              <el-checkbox label="评语">评语</el-checkbox>
            </el-checkbox-group>
          </el-form-item>
        </el-form>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="exportDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="doExportGrades">确定导出</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'TeacherEvaluation',
  data() {
    return {
      loading: true,
      submitting: false,
      searchQuery: '',
      statusFilter: 'all',
      currentClass: '',
      currentSubmission: null,
      activeTab: 'content',
      submissions: [],
      classes: [
        { id: 'cs2021', name: '计算机科学2021级' },
        { id: 'fin2021', name: '金融工程2021级' },
        { id: 'ds2022', name: '数据科学2022级' }
      ],
      experiments: [
        { id: 'exp1', title: '银行客户信用风险预测模型' },
        { id: 'exp2', title: '股票市场技术指标分析' },
        { id: 'exp3', title: '保险产品推荐系统' }
      ],
      evaluationForm: {
        algorithmAccuracy: 0,
        completeness: 0,
        peerReviewScore: 0,
        codeQuality: 0,
        reportQuality: 0,
        innovationBonus: 0,
        comment: ''
      },
      exportDialogVisible: false,
      exportClass: '',
      exportExperiment: '',
      exportFormat: 'excel',
      exportContent: ['基本信息', '详细得分']
    };
  },
  computed: {
    filteredSubmissions() {
      let result = [...this.submissions];
      
      // 搜索过滤
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        result = result.filter(submission => 
          submission.student.name.toLowerCase().includes(query) || 
          submission.student.id.toLowerCase().includes(query) ||
          submission.experiment.title.toLowerCase().includes(query)
        );
      }
      
      // 状态过滤
      if (this.statusFilter !== 'all') {
        if (this.statusFilter === 'pending') {
          result = result.filter(submission => !submission.evaluated);
        } else if (this.statusFilter === 'evaluated') {
          result = result.filter(submission => submission.evaluated);
        }
      }
      
      return result;
    }
  },
  mounted() {
    this.fetchSubmissions();
  },
  methods: {
    fetchSubmissions() {
      this.loading = true;
      
      // 模拟API调用
      setTimeout(() => {
        // 生成模拟数据
        this.submissions = [
          {
            id: 'sub1',
            student: { id: '20210101', name: '张三' },
            experiment: { id: 'exp1', title: '银行客户信用风险预测模型' },
            submitTime: new Date(2023, 4, 15, 14, 30),
            evaluated: true,
            evaluationData: {
              algorithmAccuracy: 18,
              completeness: 12,
              peerReviewScore: 12,
              codeQuality: 15,
              reportQuality: 16,
              innovationBonus: 6,
              comment: '整体表现优秀，代码规范，实验过程完整。创新性地使用了集成学习方法提升了模型性能。建议进一步探索特征工程对模型的影响。'
            },
            logs: [
              { timestamp: new Date(2023, 4, 15, 10, 5), type: 'info', title: '开始实验', description: '创建实验项目' },
              { timestamp: new Date(2023, 4, 15, 10, 20), type: 'info', title: '数据加载', description: '成功加载银行客户数据' },
              { timestamp: new Date(2023, 4, 15, 11, 15), type: 'warning', title: '数据异常', description: '发现数据存在缺失值，进行处理' },
              { timestamp: new Date(2023, 4, 15, 12, 0), type: 'info', title: '特征工程', description: '完成特征选择和工程化' },
              { timestamp: new Date(2023, 4, 15, 13, 30), type: 'success', title: '模型训练', description: '完成模型训练与评估' },
              { timestamp: new Date(2023, 4, 15, 14, 20), type: 'success', title: '提交实验', description: '完成实验并提交结果' }
            ],
            code: `import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# 加载数据
df = pd.read_csv("credit_data.csv")

# 数据预处理
df = df.dropna()
X = df.drop("default", axis=1)
y = df["default"]

# 划分训练测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 模型训练
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 模型评估
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print(f"Model Accuracy: {accuracy:.2f}")
print(f"Precision: {precision:.2f}")
print(f"Recall: {recall:.2f}")
print(f"F1-Score: {f1:.2f}")`,
            resultType: 'text',
            resultContent: 'Model Accuracy: 0.87\nPrecision: 0.84\nRecall: 0.79\nF1-Score: 0.81',
            peerReviews: [
              {
                reviewerId: '20210102',
                innovationScore: 4,
                completenessScore: 5,
                practicalityScore: 4,
                comment: '代码结构清晰，模型选择恰当。特别赞赏使用了多种评估指标而不仅仅是准确率。建议可以尝试不同的特征选择方法和降维技术，以进一步提高模型性能。'
              },
              {
                reviewerId: '20210103',
                innovationScore: 3,
                completenessScore: 5,
                practicalityScore: 5,
                comment: '实验过程完整，数据处理合理。模型选择的随机森林适合此类问题。缺乏一些创新性的尝试，比如可以探索其他模型或特征工程方法。报告详尽，结论有理有据。'
              }
            ]
          },
          {
            id: 'sub2',
            student: { id: '20210102', name: '李四' },
            experiment: { id: 'exp2', title: '股票市场技术指标分析' },
            submitTime: new Date(2023, 4, 16, 10, 15),
            evaluated: false,
            logs: [
              { timestamp: new Date(2023, 4, 16, 8, 10), type: 'info', title: '开始实验', description: '创建股票分析项目' },
              { timestamp: new Date(2023, 4, 16, 8, 30), type: 'info', title: '数据获取', description: '从API获取股票历史数据' },
              { timestamp: new Date(2023, 4, 16, 9, 15), type: 'info', title: '技术指标计算', description: '计算MA, MACD, RSI等技术指标' },
              { timestamp: new Date(2023, 4, 16, 9, 45), type: 'success', title: '创建可视化', description: '绘制技术指标走势图' },
              { timestamp: new Date(2023, 4, 16, 10, 10), type: 'success', title: '提交实验', description: '完成实验并提交结果' }
            ],
            code: '# 股票技术分析代码...',
            resultType: 'image',
            resultUrl: 'https://example.com/images/stock_analysis.png',
            peerReviews: [
              {
                reviewerId: '20210101',
                innovationScore: 4,
                completenessScore: 4,
                practicalityScore: 5,
                comment: '技术指标选择全面，可视化效果好。分析过程逻辑清晰，实用性很强。建议可以加入更多的回测数据来验证策略的有效性。'
              }
            ]
          },
          {
            id: 'sub3',
            student: { id: '20210103', name: '王五' },
            experiment: { id: 'exp3', title: '保险产品推荐系统' },
            submitTime: new Date(2023, 4, 17, 16, 45),
            evaluated: false,
            logs: [
              { timestamp: new Date(2023, 4, 17, 13, 20), type: 'info', title: '开始实验', description: '创建推荐系统项目' },
              { timestamp: new Date(2023, 4, 17, 14, 30), type: 'warning', title: '数据问题', description: '客户数据存在不一致性，进行清洗' },
              { timestamp: new Date(2023, 4, 17, 15, 45), type: 'info', title: '模型构建', description: '实现协同过滤算法' },
              { timestamp: new Date(2023, 4, 17, 16, 30), type: 'success', title: '系统测试', description: '测试推荐系统性能' },
              { timestamp: new Date(2023, 4, 17, 16, 40), type: 'success', title: '提交实验', description: '完成实验并提交结果' }
            ],
            code: '# 保险产品推荐系统代码...',
            resultType: 'text',
            resultContent: 'Recommendation System Evaluation:\nPrecision@5: 0.82\nRecall@5: 0.68\nF1@5: 0.74\nMAP: 0.79\nCoverage: 0.83',
            peerReviews: []
          }
        ];
        
        this.loading = false;
      }, 1000);
    },
    
    selectSubmission(submission) {
      this.currentSubmission = submission;
      
      // 如果已评估，填充表单
      if (submission.evaluated && submission.evaluationData) {
        this.evaluationForm = { ...submission.evaluationData };
      } else {
        // 自动计算部分分数
        this.evaluationForm = {
          algorithmAccuracy: this.calculateAlgorithmScore(submission),
          completeness: this.calculateCompletenessScore(submission),
          peerReviewScore: this.calculatePeerReviewAverage(submission),
          codeQuality: 0,
          reportQuality: 0,
          innovationBonus: 0,
          comment: ''
        };
      }
    },
    
    calculateAlgorithmScore(submission) {
      // 模拟算法分数计算逻辑
      // 实际应用中可能基于测试用例和结果准确性来打分
      return Math.floor(Math.random() * 5) + 15; // 15-20分之间
    },
    
    calculateCompletenessScore(submission) {
      // 基于实验步骤完成情况
      if (!submission.logs) return 0;
      
      const completedSteps = submission.logs.filter(log => 
        log.type === 'success' || log.type === 'info'
      ).length;
      
      // 根据完成步骤比例计算分数
      const totalPossibleSteps = 5; // 假设每个实验有5个标准步骤
      return Math.round((completedSteps / totalPossibleSteps) * 15);
    },
    
    calculatePeerReviewAverage(submission) {
      if (!submission.peerReviews || submission.peerReviews.length === 0) {
        return 0;
      }
      
      // 计算同行评议平均分
      const totalScores = submission.peerReviews.map(review => 
        this.calculateReviewScore(review)
      );
      
      const average = totalScores.reduce((sum, score) => sum + score, 0) / totalScores.length;
      
      // 将5分制转换为15分制
      return Math.round(average * 3);
    },
    
    calculateReviewScore(review) {
      // 计算单个评议的平均分
      return ((review.innovationScore + review.completenessScore + review.practicalityScore) / 3).toFixed(1);
    },
    
    calculateTotalScore() {
      const { 
        algorithmAccuracy, 
        completeness, 
        peerReviewScore, 
        codeQuality, 
        reportQuality, 
        innovationBonus 
      } = this.evaluationForm;
      
      const total = algorithmAccuracy + completeness + peerReviewScore + 
                    codeQuality + reportQuality + innovationBonus;
                    
      return total;
    },
    
    resetEvaluation() {
      if (this.currentSubmission) {
        this.evaluationForm = {
          algorithmAccuracy: this.calculateAlgorithmScore(this.currentSubmission),
          completeness: this.calculateCompletenessScore(this.currentSubmission),
          peerReviewScore: this.calculatePeerReviewAverage(this.currentSubmission),
          codeQuality: 0,
          reportQuality: 0,
          innovationBonus: 0,
          comment: ''
        };
      }
    },
    
    submitEvaluation() {
      if (!this.currentSubmission) return;
      
      this.submitting = true;
      
      // 模拟API调用
      setTimeout(() => {
        // 更新本地数据
        const index = this.submissions.findIndex(sub => sub.id === this.currentSubmission.id);
        if (index !== -1) {
          this.submissions[index].evaluated = true;
          this.submissions[index].evaluationData = { ...this.evaluationForm };
          this.currentSubmission.evaluated = true;
          this.currentSubmission.evaluationData = { ...this.evaluationForm };
        }
        
        this.$message.success('评估已保存成功');
        this.submitting = false;
      }, 800);
    },
    
    exportGrades() {
      this.exportClass = this.currentClass;
      this.exportDialogVisible = true;
    },
    
    doExportGrades() {
      this.$message.success('成绩已导出');
      this.exportDialogVisible = false;
    },
    
    formatDate(date) {
      if (!date) return '';
      return new Date(date).toLocaleString();
    },
    
    formatTime(date) {
      if (!date) return '';
      const d = new Date(date);
      return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`;
    },
    
    getTimelineItemType(type) {
      switch(type) {
        case 'success': return 'success';
        case 'warning': return 'warning';
        case 'error': return 'danger';
        default: return 'primary';
      }
    }
  }
};
</script>

<style scoped>
.teacher-evaluation {
  height: 100%;
}

.eval-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.eval-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.evaluation-container {
  display: flex;
  height: calc(100% - 60px);
  overflow: hidden;
}

.submissions-list {
  width: 300px;
  border-right: 1px solid #EBEEF5;
  padding-right: 15px;
  display: flex;
  flex-direction: column;
}

.filter-options {
  margin: 10px 0;
}

.submissions-scrollbar {
  flex: 1;
  overflow: auto;
}

.submission-item {
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 10px;
  border: 1px solid #EBEEF5;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.submission-item:hover {
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
}

.submission-item.active {
  border-color: #409EFF;
  background-color: rgba(64, 158, 255, 0.1);
}

.student-info {
  display: flex;
  align-items: center;
  margin-bottom: 5px;
}

.student-name {
  font-weight: bold;
  margin-right: 8px;
}

.student-id {
  color: #909399;
  font-size: 12px;
}

.experiment-title {
  margin-bottom: 5px;
  font-size: 14px;
}

.submission-time {
  font-size: 12px;
  color: #909399;
}

.evaluation-area {
  flex: 1;
  padding: 0 15px;
  overflow: auto;
}

.no-selection {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}

.student-info-header {
  display: flex;
  gap: 15px;
  color: #606266;
  margin-bottom: 20px;
}

.process-timeline {
  margin: 20px 0;
}

.code-section, .result-section {
  margin: 20px 0;
}

.code-display {
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  font-family: monospace;
  overflow: auto;
  white-space: pre-wrap;
}

.result-text {
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  font-family: monospace;
  white-space: pre-wrap;
}

.log-screenshot {
  margin-top: 10px;
}

.peer-reviews {
  margin: 20px 0;
}

.review-details {
  padding: 10px;
}

.review-scores {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 15px;
}

.score-item {
  display: flex;
  align-items: center;
}

.score-label {
  width: 60px;
  margin-right: 5px;
}

.review-comment {
  margin-top: 10px;
}

.comment-label {
  font-weight: bold;
  margin-bottom: 5px;
}

.comment-content {
  background-color: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
}

.evaluation-form {
  padding: 10px;
}

.auto-grade {
  display: flex;
  align-items: center;
}

.grade-value {
  font-weight: bold;
  font-size: 16px;
  color: #409EFF;
}

.grade-max {
  margin-left: 5px;
  color: #909399;
}

.el-icon-info {
  margin-left: 10px;
  color: #909399;
  cursor: help;
}

.score-hint {
  margin-top: 5px;
  color: #909399;
  font-size: 12px;
}

.final-score {
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  margin: 20px 0;
}

.score-breakdown {
  margin-bottom: 15px;
}

.total-formula {
  font-family: monospace;
}

.final-grade {
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.final-label {
  margin-right: 10px;
}

.final-value {
  font-size: 24px;
  font-weight: bold;
  color: #67C23A;
}

.final-max {
  margin-left: 5px;
  color: #909399;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.empty-list {
  padding: 20px 0;
}

.export-options {
  padding: 10px;
}
</style> 