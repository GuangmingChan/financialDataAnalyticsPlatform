<template>
  <div class="experiment-list">
    <h1>实验列表</h1>
    
    <el-row :gutter="20" class="filters">
      <el-col :span="8">
        <el-select v-model="categoryFilter" placeholder="按类别筛选" clearable>
          <el-option label="证券分析" value="security"></el-option>
          <el-option label="银行分析" value="bank"></el-option>
          <el-option label="保险分析" value="insurance"></el-option>
        </el-select>
      </el-col>
      <el-col :span="8">
        <el-select v-model="difficultyFilter" placeholder="按难度筛选" clearable>
          <el-option v-for="i in 5" :key="i" :label="`难度 ${i}`" :value="i"></el-option>
        </el-select>
      </el-col>
    </el-row>
    
    <el-table
      v-loading="loading"
      :data="filteredExperiments"
      style="width: 100%; margin-top: 20px;">
      <el-table-column prop="id" label="ID" width="80"></el-table-column>
      <el-table-column prop="title" label="实验名称"></el-table-column>
      <el-table-column prop="category" label="类别" width="120">
        <template slot-scope="scope">
          <el-tag 
            :type="getTagType(scope.row.category)">
            {{ getCategoryText(scope.row.category) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="难度" width="120">
        <template slot-scope="scope">
          <el-rate
            v-model="scope.row.difficulty_level"
            disabled
            text-color="#ff9900">
          </el-rate>
        </template>
      </el-table-column>
      <el-table-column prop="estimated_duration" label="预计时长" width="120">
        <template slot-scope="scope">
          {{ scope.row.estimated_duration }} 分钟
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150">
        <template slot-scope="scope">
          <el-button 
            size="small" 
            type="primary" 
            @click="viewExperiment(scope.row.id)">
            查看详情
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'ExperimentList',
  data() {
    return {
      loading: true,
      experiments: [],
      categoryFilter: '',
      difficultyFilter: ''
    };
  },
  computed: {
    filteredExperiments() {
      let filtered = this.experiments;
      
      if (this.categoryFilter) {
        filtered = filtered.filter(exp => exp.category === this.categoryFilter);
      }
      
      if (this.difficultyFilter) {
        filtered = filtered.filter(exp => exp.difficulty_level === this.difficultyFilter);
      }
      
      return filtered;
    }
  },
  methods: {
    async fetchExperiments() {
      this.loading = true;
      try {
        const response = await axios.get('/api/v1/experiments');
        this.experiments = response.data;
      } catch (error) {
        this.$message.error('获取实验列表失败: ' + error.message);
      } finally {
        this.loading = false;
      }
    },
    viewExperiment(id) {
      this.$router.push(`/experiments/${id}`);
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
    this.fetchExperiments();
  }
};
</script>

<style scoped>
.experiment-list {
  padding: 20px;
}

.filters {
  margin-top: 20px;
}

h1 {
  font-size: 24px;
  margin-bottom: 20px;
}
</style> 