<template>
  <div class="peer-review">
    <el-card class="review-card">
      <div slot="header" class="review-header">
        <span>实验互评</span>
        <el-button
          size="mini"
          type="primary"
          @click="submitAllReviews"
          :disabled="!canSubmit">
          提交所有评价
        </el-button>
      </div>
      
      <el-tabs v-model="activeTab">
        <el-tab-pane label="待评价实验" name="pending">
          <div v-if="loading" class="loading-container">
            <el-skeleton :rows="5" animated />
          </div>
          
          <div v-else-if="pendingReviews.length === 0" class="empty-container">
            <el-empty description="暂无待评价实验"></el-empty>
          </div>
          
          <div v-else>
            <el-card v-for="(item, index) in pendingReviews" 
                     :key="item.id" 
                     class="submission-card"
                     :class="{ 'active-card': activeSubmission && activeSubmission.id === item.id }">
              <div class="submission-header" @click="selectSubmission(item)">
                <div class="submission-info">
                  <h4>{{ item.experiment.title }}</h4>
                  <div class="meta">
                    <span><i class="el-icon-user"></i> {{ item.anonymous ? '匿名用户' : item.user.name }}</span>
                    <span><i class="el-icon-time"></i> {{ formatDate(item.submitTime) }}</span>
                  </div>
                </div>
                <el-tag v-if="item.reviewed" type="success">已评</el-tag>
                <el-tag v-else type="warning">待评</el-tag>
              </div>
            </el-card>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="我收到的评价" name="received">
          <div v-if="loading" class="loading-container">
            <el-skeleton :rows="5" animated />
          </div>
          
          <div v-else-if="receivedReviews.length === 0" class="empty-container">
            <el-empty description="暂无收到的评价"></el-empty>
          </div>
          
          <div v-else>
            <el-collapse accordion>
              <el-collapse-item v-for="review in receivedReviews" :key="review.id" 
                                :title="review.experiment.title + ' - ' + formatDate(review.reviewTime)">
                <div class="review-content">
                  <div class="review-ratings">
                    <el-row :gutter="20">
                      <el-col :span="8">
                        <h4>创新性评分</h4>
                        <el-rate
                          v-model="review.innovationScore"
                          disabled
                          show-score>
                        </el-rate>
                      </el-col>
                      <el-col :span="8">
                        <h4>完整性评分</h4>
                        <el-rate
                          v-model="review.completenessScore"
                          disabled
                          show-score>
                        </el-rate>
                      </el-col>
                      <el-col :span="8">
                        <h4>实用性评分</h4>
                        <el-rate
                          v-model="review.practicalityScore"
                          disabled
                          show-score>
                        </el-rate>
                      </el-col>
                    </el-row>
                  </div>
                  
                  <div class="review-comment">
                    <h4>评价意见</h4>
                    <p>{{ review.comment }}</p>
                  </div>
                  
                  <div class="overall-score">
                    <h4>总分: {{ calculateOverallScore(review) }}</h4>
                  </div>
                </div>
              </el-collapse-item>
            </el-collapse>
          </div>
        </el-tab-pane>
      </el-tabs>
      
      <!-- 右侧评价面板 -->
      <div class="review-panel" v-if="activeSubmission">
        <div class="panel-header">
          <h3>{{ activeSubmission.experiment.title }}</h3>
          <el-button size="mini" type="text" @click="closePanel">
            <i class="el-icon-close"></i>
          </el-button>
        </div>
        
        <el-scrollbar class="panel-content">
          <el-tabs>
            <el-tab-pane label="提交内容">
              <div class="submission-content">
                <h4>实验步骤执行情况</h4>
                <el-steps direction="vertical" :active="activeSubmission.completedSteps.length">
                  <el-step 
                    v-for="(step, index) in activeSubmission.experiment.steps" 
                    :key="index" 
                    :title="step.title"
                    :description="step.description">
                  </el-step>
                </el-steps>
                
                <div class="result-section">
                  <h4>实验结果</h4>
                  <div class="result-preview">
                    <el-image 
                      v-if="activeSubmission.resultImage"
                      :src="activeSubmission.resultImage" 
                      fit="contain" 
                      :preview-src-list="[activeSubmission.resultImage]">
                    </el-image>
                    <pre v-else-if="activeSubmission.resultText">{{ activeSubmission.resultText }}</pre>
                    <el-empty v-else description="无结果数据"></el-empty>
                  </div>
                </div>
                
                <div class="code-section">
                  <h4>实验代码</h4>
                  <pre class="code-preview">{{ activeSubmission.code }}</pre>
                </div>
              </div>
            </el-tab-pane>
            
            <el-tab-pane label="评价打分">
              <div class="review-form">
                <el-form :model="reviewForm" label-position="top">
                  <el-form-item label="创新性 - 实验方法或结果是否具有创新点">
                    <el-rate
                      v-model="reviewForm.innovationScore"
                      :colors="['#99A9BF', '#F7BA2A', '#FF9900']"
                      show-text
                      :texts="ratingTexts">
                    </el-rate>
                  </el-form-item>
                  
                  <el-form-item label="完整性 - 实验步骤是否完整，结果是否完备">
                    <el-rate
                      v-model="reviewForm.completenessScore"
                      :colors="['#99A9BF', '#F7BA2A', '#FF9900']"
                      show-text
                      :texts="ratingTexts">
                    </el-rate>
                  </el-form-item>
                  
                  <el-form-item label="实用性 - 实验成果是否具有实际应用价值">
                    <el-rate
                      v-model="reviewForm.practicalityScore"
                      :colors="['#99A9BF', '#F7BA2A', '#FF9900']"
                      show-text
                      :texts="ratingTexts">
                    </el-rate>
                  </el-form-item>
                  
                  <el-form-item label="评价意见">
                    <el-input
                      type="textarea"
                      v-model="reviewForm.comment"
                      :rows="4"
                      placeholder="请详细描述您对该实验的评价，包括优点、不足和改进建议">
                    </el-input>
                  </el-form-item>
                  
                  <el-form-item>
                    <el-button type="primary" @click="submitReview" :loading="submitting">提交评价</el-button>
                    <el-button @click="resetReviewForm">重置</el-button>
                  </el-form-item>
                </el-form>
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-scrollbar>
      </div>
      
      <!-- 评价指导对话框 -->
      <el-dialog
        title="评价指导"
        :visible.sync="guideDialogVisible"
        width="50%">
        <el-collapse accordion>
          <el-collapse-item title="如何进行公正的同行评议？" name="1">
            <p>同行评议是科学研究中重要的质量控制机制。评价他人的实验时，请遵循以下原则：</p>
            <ol>
              <li><strong>客观公正</strong>：基于实验内容进行评价，避免个人偏见</li>
              <li><strong>具体详实</strong>：提供具体的评价意见，而非简单的"好"或"不好"</li>
              <li><strong>建设性</strong>：指出不足的同时，提供改进建议</li>
              <li><strong>尊重原创</strong>：欣赏和肯定创新点，即使与主流方法不同</li>
            </ol>
          </el-collapse-item>
          
          <el-collapse-item title="评分标准解释" name="2">
            <h4>创新性 (5分)</h4>
            <ul>
              <li>5分：方法具有显著创新，提出了新颖的解决方案</li>
              <li>4分：在已有方法基础上有明显改进或创新点</li>
              <li>3分：使用合适的方法，有一定的个性化调整</li>
              <li>2分：直接使用常规方法，缺乏个人创新</li>
              <li>1分：方法选择不当或存在明显错误</li>
            </ul>
            
            <h4>完整性 (5分)</h4>
            <ul>
              <li>5分：实验步骤完整，结果全面，分析透彻</li>
              <li>4分：实验基本完整，结果较为全面</li>
              <li>3分：实验完成了主要步骤，结果基本可用</li>
              <li>2分：实验步骤有所缺失，结果不完整</li>
              <li>1分：实验严重不完整，结果缺失或无法使用</li>
            </ul>
            
            <h4>实用性 (5分)</h4>
            <ul>
              <li>5分：成果可直接应用，具有显著实用价值</li>
              <li>4分：成果实用性强，经过少量调整可应用</li>
              <li>3分：成果具有一定实用价值</li>
              <li>2分：成果实用性有限</li>
              <li>1分：成果难以应用于实际场景</li>
            </ul>
          </el-collapse-item>
          
          <el-collapse-item title="如何撰写有效的评价意见" name="3">
            <p>高质量的评价意见应该包含以下要素：</p>
            <ol>
              <li><strong>总体评价</strong>：对实验整体的简要评价</li>
              <li><strong>优点</strong>：列举实验中的亮点和值得肯定的方面</li>
              <li><strong>不足</strong>：指出实验中存在的问题或可改进之处</li>
              <li><strong>改进建议</strong>：提供具体、可操作的改进建议</li>
              <li><strong>其他评论</strong>：其他想要分享的观点或建议</li>
            </ol>
            <p>例如：</p>
            <pre>该实验整体设计合理，分析过程清晰。
优点：数据预处理方法选择恰当，可视化图表直观易懂，结论有理有据。
不足：模型选择时缺乏对比分析，部分参数选择缺乏解释。
建议：可以尝试对比3-4种不同模型的性能，增加对超参数选择的解释，并考虑增加模型验证的内容。
总的来说，这是一个完成度较高的实验，通过上述改进可以进一步提升质量。</pre>
          </el-collapse-item>
        </el-collapse>
      </el-dialog>
    </el-card>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'PeerReview',
  props: {
    userId: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      activeTab: 'pending',
      loading: true,
      submitting: false,
      pendingReviews: [],
      receivedReviews: [],
      activeSubmission: null,
      reviewForm: {
        innovationScore: 0,
        completenessScore: 0,
        practicalityScore: 0,
        comment: ''
      },
      ratingTexts: ['较差', '一般', '满意', '良好', '优秀'],
      guideDialogVisible: false
    };
  },
  computed: {
    canSubmit() {
      return this.pendingReviews.some(review => review.reviewed && !review.submitted);
    }
  },
  created() {
    this.fetchPendingReviews();
    this.fetchReceivedReviews();
    
    // 首次使用显示评价指导
    const hasSeenGuide = localStorage.getItem('hasSeenPeerReviewGuide');
    if (!hasSeenGuide) {
      this.guideDialogVisible = true;
      localStorage.setItem('hasSeenPeerReviewGuide', 'true');
    }
  },
  methods: {
    fetchPendingReviews() {
      this.loading = true;
      
      // 模拟API调用
      setTimeout(() => {
        this.pendingReviews = [
          {
            id: '1',
            experiment: {
              id: '101',
              title: '银行客户信用风险预测模型',
              steps: [
                { title: '数据加载与理解', description: '加载数据并分析基本结构' },
                { title: '数据预处理', description: '处理缺失值和异常值' },
                { title: '特征工程', description: '创建相关特征并进行归一化' },
                { title: '模型训练', description: '选择合适的模型并训练' },
                { title: '模型评估', description: '使用适当的指标评估模型性能' }
              ]
            },
            user: { id: '201', name: '张三' },
            submitTime: new Date(2023, 5, 15, 14, 30),
            anonymous: false,
            completedSteps: [0, 1, 2, 3, 4],
            resultText: 'Model Accuracy: 0.87\nPrecision: 0.84\nRecall: 0.79\nF1-Score: 0.81',
            code: 'import pandas as pd\nimport numpy as np\nfrom sklearn.model_selection import train_test_split\nfrom sklearn.ensemble import RandomForestClassifier\nfrom sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score\n\n# 加载数据\ndf = pd.read_csv("credit_data.csv")\n\n# 数据预处理\ndf = df.dropna()\nX = df.drop("default", axis=1)\ny = df["default"]\n\n# 划分训练测试集\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)\n\n# 模型训练\nmodel = RandomForestClassifier(n_estimators=100, random_state=42)\nmodel.fit(X_train, y_train)\n\n# 模型评估\ny_pred = model.predict(X_test)\naccuracy = accuracy_score(y_test, y_pred)\nprecision = precision_score(y_test, y_pred)\nrecall = recall_score(y_test, y_pred)\nf1 = f1_score(y_test, y_pred)\n\nprint(f"Model Accuracy: {accuracy:.2f}")\nprint(f"Precision: {precision:.2f}")\nprint(f"Recall: {recall:.2f}")\nprint(f"F1-Score: {f1:.2f}")',
            reviewed: false,
            submitted: false
          },
          {
            id: '2',
            experiment: {
              id: '102',
              title: '股票市场技术指标分析',
              steps: [
                { title: '数据获取', description: '从API获取股票历史数据' },
                { title: '计算技术指标', description: '计算常用技术指标如RSI、MACD等' },
                { title: '指标可视化', description: '绘制技术指标图表' },
                { title: '交易信号分析', description: '分析买入卖出信号' },
                { title: '回测策略', description: '回测基于技术指标的交易策略' }
              ]
            },
            user: { id: '202', name: '李四' },
            submitTime: new Date(2023, 5, 16, 10, 15),
            anonymous: false,
            completedSteps: [0, 1, 2, 3],
            resultImage: 'https://example.com/images/stock_analysis.png', // 实际项目中应该是真实链接
            code: '# 股票技术分析代码...',
            reviewed: false,
            submitted: false
          }
        ];
        
        this.loading = false;
      }, 1000);
    },
    
    fetchReceivedReviews() {
      // 模拟API调用
      setTimeout(() => {
        this.receivedReviews = [
          {
            id: '301',
            experiment: {
              id: '103',
              title: '保险客户流失预测模型'
            },
            reviewer: { id: '202', name: '李四' },
            reviewTime: new Date(2023, 5, 10, 9, 20),
            innovationScore: 4,
            completenessScore: 5,
            practicalityScore: 3,
            comment: '模型选择恰当，数据预处理做得很细致。特别赞赏对特征重要性的分析，帮助理解了影响客户流失的关键因素。建议可以尝试更多的模型比较，并探索一些更高级的特征工程方法来进一步提升模型性能。整体而言是一个高质量的实验。'
          },
          {
            id: '302',
            experiment: {
              id: '104',
              title: '个人消费贷款风险控制'
            },
            reviewer: { id: '203', name: '王五' },
            reviewTime: new Date(2023, 5, 12, 16, 45),
            innovationScore: 3,
            completenessScore: 4,
            practicalityScore: 5,
            comment: '实验整体完成度高，尤其是风险评分卡的设计很有实用价值。代码结构清晰，易于理解。不足之处在于缺乏对模型稳定性的测试，建议增加不同时间窗口的交叉验证，以验证模型在不同经济环境下的表现。'
          }
        ];
      }, 1200);
    },
    
    selectSubmission(submission) {
      this.activeSubmission = submission;
      
      // 如果已经评价过，回填表单
      if (submission.reviewed) {
        this.reviewForm = {
          innovationScore: submission.reviewData.innovationScore,
          completenessScore: submission.reviewData.completenessScore,
          practicalityScore: submission.reviewData.practicalityScore,
          comment: submission.reviewData.comment
        };
      } else {
        // 重置表单
        this.resetReviewForm();
      }
    },
    
    closePanel() {
      this.activeSubmission = null;
    },
    
    resetReviewForm() {
      this.reviewForm = {
        innovationScore: 0,
        completenessScore: 0,
        practicalityScore: 0,
        comment: ''
      };
    },
    
    submitReview() {
      if (!this.reviewForm.innovationScore || 
          !this.reviewForm.completenessScore || 
          !this.reviewForm.practicalityScore) {
        this.$message.warning('请完成所有评分项');
        return;
      }
      
      if (!this.reviewForm.comment.trim()) {
        this.$message.warning('请填写评价意见');
        return;
      }
      
      this.submitting = true;
      
      // 模拟API提交
      setTimeout(() => {
        // 更新本地数据状态
        const index = this.pendingReviews.findIndex(item => item.id === this.activeSubmission.id);
        if (index !== -1) {
          this.pendingReviews[index].reviewed = true;
          this.pendingReviews[index].reviewData = { ...this.reviewForm };
          
          this.$message.success('评价已保存');
        }
        
        this.submitting = false;
      }, 800);
    },
    
    submitAllReviews() {
      const reviewedCount = this.pendingReviews.filter(r => r.reviewed && !r.submitted).length;
      
      this.$confirm(`确定要提交${reviewedCount}条评价吗？提交后将无法修改。`, '提交确认', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        // 模拟API提交
        setTimeout(() => {
          this.pendingReviews.forEach(review => {
            if (review.reviewed) {
              review.submitted = true;
            }
          });
          
          this.$message.success('所有评价已成功提交');
        }, 1000);
      }).catch(() => {});
    },
    
    formatDate(date) {
      if (!date) return '';
      return new Date(date).toLocaleString();
    },
    
    calculateOverallScore(review) {
      const total = (review.innovationScore + review.completenessScore + review.practicalityScore) / 3;
      return total.toFixed(1);
    }
  }
};
</script>

<style scoped>
.peer-review {
  height: 100%;
}

.review-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  position: relative;
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.submission-card {
  margin-bottom: 15px;
  cursor: pointer;
  transition: box-shadow 0.3s;
}

.submission-card:hover {
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
}

.active-card {
  border-color: #409EFF;
  box-shadow: 0 2px 12px 0 rgba(64, 158, 255, 0.2);
}

.submission-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.submission-info h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
}

.meta {
  font-size: 13px;
  color: #909399;
}

.meta span {
  margin-right: 15px;
}

.meta i {
  margin-right: 4px;
}

.loading-container, .empty-container {
  padding: 20px 0;
}

.review-panel {
  position: absolute;
  right: 0;
  top: 0;
  width: 60%;
  height: 100%;
  background: #fff;
  box-shadow: -2px 0 10px rgba(0, 0, 0, 0.1);
  z-index: 100;
  display: flex;
  flex-direction: column;
  transition: transform 0.3s;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #EBEEF5;
}

.panel-header h3 {
  margin: 0;
  font-size: 18px;
}

.panel-content {
  flex: 1;
  padding: 20px;
  overflow: auto;
}

.submission-content h4, 
.review-form h4 {
  margin-top: 20px;
  margin-bottom: 15px;
  font-size: 16px;
  color: #303133;
}

.result-preview {
  background: #f5f7fa;
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 20px;
}

.code-preview {
  background: #f5f7fa;
  border-radius: 4px;
  padding: 15px;
  margin: 0;
  overflow: auto;
  font-family: monospace;
  white-space: pre-wrap;
}

.review-content {
  padding: 10px 0;
}

.review-ratings {
  margin-bottom: 20px;
}

.review-comment h4 {
  margin: 15px 0 10px;
}

.review-comment p {
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
  margin: 0;
}

.overall-score {
  text-align: right;
  margin-top: 15px;
}

.overall-score h4 {
  font-size: 16px;
  color: #67C23A;
}
</style> 