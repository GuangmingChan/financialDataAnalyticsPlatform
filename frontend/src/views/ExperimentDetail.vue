<template>
  <div class="experiment-detail" v-loading="loading">
    <div v-if="experiment">
      <div class="header">
        <h1>{{ experiment.title }}</h1>
        <el-button type="primary" @click="startExperiment">开始实验</el-button>
      </div>
      
      <el-card class="info-card">
        <div class="info-grid">
          <div class="info-item">
            <span class="label">实验类别:</span>
            <el-tag :type="getTagType(experiment.category)">
              {{ getCategoryText(experiment.category) }}
            </el-tag>
          </div>
          <div class="info-item">
            <span class="label">难度级别:</span>
            <el-rate v-model="experiment.difficulty_level" disabled text-color="#ff9900"></el-rate>
          </div>
          <div class="info-item">
            <span class="label">预计时长:</span>
            <span>{{ experiment.estimated_duration }} 分钟</span>
          </div>
          <div class="info-item">
            <span class="label">数据来源:</span>
            <span>{{ experiment.data_source }}</span>
          </div>
        </div>
      </el-card>
      
      <el-card class="description-card">
        <div slot="header">
          <span>实验描述</span>
        </div>
        <p>{{ experiment.description }}</p>
      </el-card>
      
      <el-card class="prerequisites-card">
        <div slot="header">
          <span>预备知识</span>
        </div>
        <p>{{ experiment.prerequisites }}</p>
      </el-card>
      
      <el-card class="steps-card">
        <div slot="header">
          <span>实验步骤</span>
        </div>
        <el-steps direction="vertical" :active="activeStep">
          <el-step 
            v-for="step in experiment.steps" 
            :key="step.id" 
            :title="step.title" 
            :description="step.description">
          </el-step>
        </el-steps>
      </el-card>
    </div>
    
    <div v-else-if="!loading" class="not-found">
      <h2>未找到实验</h2>
      <el-button type="primary" @click="goBack">返回实验列表</el-button>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'ExperimentDetail',
  data() {
    return {
      loading: true,
      experiment: null,
      activeStep: 0
    };
  },
  methods: {
    async fetchExperiment() {
      this.loading = true;
      try {
        const id = this.$route.params.id;
        const response = await axios.get(`/api/v1/experiments/${id}`);
        this.experiment = response.data;
      } catch (error) {
        this.$message.error('获取实验详情失败: ' + error.message);
        this.experiment = null;
      } finally {
        this.loading = false;
      }
    },
    startExperiment() {
      const id = this.$route.params.id;
      this.$router.push(`/experiments/${id}/workspace`);
    },
    goBack() {
      this.$router.push('/experiments');
    },
    getCategoryText(category) {
      const categories = {
        'security': '证券分析',
        'bank': '银行分析',
        'insurance': '保险分析',
        'credit': '信贷分析',
        'investment': '投资分析',
        'risk': '风险管理'
      };
      return categories[category] || category;
    },
    getTagType(category) {
      const types = {
        'security': 'success',
        'bank': 'primary',
        'insurance': 'warning'
      };
      return types[category] || '';
    }
  },
  created() {
    this.fetchExperiment();
  }
};
</script>

<style scoped>
.experiment-detail {
  padding: 20px;
  max-width: 1000px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

h1 {
  font-size: 24px;
  margin: 0;
}

.info-card, .description-card, .prerequisites-card, .steps-card {
  margin-bottom: 20px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  grid-gap: 20px;
}

.info-item {
  display: flex;
  align-items: center;
}

.label {
  font-weight: bold;
  margin-right: 10px;
}

.not-found {
  text-align: center;
  padding: 40px;
}
</style> 