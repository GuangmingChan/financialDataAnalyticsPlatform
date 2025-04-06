<template>
  <div class="home">
    <div class="welcome-message" v-if="user.full_name">
      <h2>欢迎回来，{{ user.full_name }}！</h2>
    </div>
    <h1>金融大数据虚拟仿真实验平台</h1>
    <p class="description">本平台提供证券、银行和保险领域的数据分析实验，帮助您提升金融大数据处理能力。</p>
    
    <div class="action-buttons">
      <el-button type="primary" @click="startExperiment">开始实验</el-button>
      <el-button type="success" @click="goToCustomCode">自定义代码实验室</el-button>
    </div>
    
    <div class="feature-cards">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="8">
          <el-card class="feature-card">
            <div slot="header">
              <i class="el-icon-s-cooperation"></i>
              <span>虚拟仿真实验</span>
            </div>
            <div class="card-content">
              通过真实场景模拟，深入了解金融业务流程与数据分析方法
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="12" :md="8">
          <el-card class="feature-card">
            <div slot="header">
              <i class="el-icon-s-data"></i>
              <span>大数据分析</span>
            </div>
            <div class="card-content">
              使用专业工具和方法，挖掘金融数据价值，提升分析能力
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="12" :md="8">
          <el-card class="feature-card">
            <div slot="header">
              <i class="el-icon-s-platform"></i>
              <span>自定义探索</span>
            </div>
            <div class="card-content">
              在自定义代码实验室中自由编写Python代码，进行个性化探索
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  name: 'HomePage',
  computed: {
    ...mapGetters(['user'])
  },
  methods: {
    startExperiment() {
      this.$router.push('/experiments');
    },
    goToCustomCode() {
      this.$router.push('/custom-code');
    }
  }
}
</script>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 40px 20px;
}

.welcome-message {
  margin-bottom: 20px;
  color: #409EFF;
}

h1 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  color: #303133;
}

.description {
  max-width: 600px;
  margin-bottom: 2rem;
  color: #606266;
  line-height: 1.6;
}

.action-buttons {
  display: flex;
  gap: 15px;
  margin-bottom: 40px;
}

.el-button {
  padding: 12px 30px;
  font-size: 16px;
}

.feature-cards {
  width: 100%;
  max-width: 1200px;
  margin-top: 20px;
}

.feature-card {
  height: 100%;
  transition: all 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.el-card__header {
  display: flex;
  align-items: center;
}

.el-card__header i {
  font-size: 20px;
  margin-right: 8px;
  color: #409EFF;
}

.card-content {
  padding: 15px 0;
  color: #606266;
  line-height: 1.6;
}
</style>
