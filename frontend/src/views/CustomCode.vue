<template>
  <div class="custom-code-view">
    <el-row>
      <el-col :span="24">
        <div class="page-header">
          <div class="header-left">
            <h2>自定义代码实验室</h2>
            <div class="header-subtitle">
              在此可以自由编写和测试数据分析代码，探索金融大数据分析
            </div>
          </div>
          <div class="header-actions">
            <el-button type="primary" icon="el-icon-s-home" @click="$router.push('/')">返回首页</el-button>
            <el-button icon="el-icon-help" @click="showHelp">帮助</el-button>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row>
      <el-col :span="24">
        <custom-code-editor />
      </el-col>
    </el-row>

    <el-dialog
      title="代码编辑器使用帮助"
      :visible.sync="helpDialogVisible"
      width="60%">
      <div class="help-content">
        <h3>自定义代码实验室使用指南</h3>
        
        <div class="help-section">
          <h4>功能介绍</h4>
          <p>自定义代码实验室允许您编写和运行Python代码，进行数据分析、可视化和建模，提供了以下功能:</p>
          <ul>
            <li>代码编辑器：使用Monaco编辑器提供语法高亮、自动补全等功能</li>
            <li>代码模板：提供多种常用模板快速开始</li>
            <li>代码执行：在安全的后端环境中执行您的Python代码</li>
            <li>图表可视化：自动显示matplotlib创建的图表</li>
            <li>代码保存：保存常用代码供日后使用</li>
          </ul>
        </div>
        
        <div class="help-section">
          <h4>可用的Python库</h4>
          <p>您可以使用以下预装的Python库:</p>
          <ul>
            <li><strong>pandas</strong>: 用于数据分析和操作</li>
            <li><strong>numpy</strong>: 用于科学计算</li>
            <li><strong>matplotlib</strong>: 用于数据可视化</li>
            <li><strong>scikit-learn</strong>: 用于机器学习</li>
          </ul>
        </div>
        
        <div class="help-section">
          <h4>使用示例</h4>
          <pre class="code-example">
# 创建简单的数据分析
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 创建示例数据
data = {
    '日期': pd.date_range(start='2023-01-01', periods=10),
    '价格': np.random.normal(100, 5, 10),
    '成交量': np.random.randint(1000, 5000, 10)
}

df = pd.DataFrame(data)

# 打印数据
print(df.head())

# 创建简单可视化
plt.figure(figsize=(10, 6))
plt.plot(df['日期'], df['价格'], 'b-', label='价格')
plt.title('价格趋势')
plt.xlabel('日期')
plt.ylabel('价格')
plt.legend()
plt.grid(True)
plt.show()
          </pre>
        </div>
        
        <div class="help-section">
          <h4>注意事项</h4>
          <ul>
            <li>每次代码执行有30秒的超时限制</li>
            <li>最大允许输出2MB的数据</li>
            <li>请勿执行可能导致安全问题的代码（如文件读写、网络请求等）</li>
            <li>如需使用其他库或需要更多资源，请联系管理员</li>
          </ul>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import CustomCodeEditor from '@/components/CustomCodeEditor.vue'

export default {
  name: 'CustomCode',
  components: {
    CustomCodeEditor
  },
  data() {
    return {
      helpDialogVisible: false
    }
  },
  methods: {
    showHelp() {
      this.helpDialogVisible = true
    }
  }
}
</script>

<style scoped>
.custom-code-view {
  padding: 20px;
  height: calc(100vh - 120px);
  display: flex;
  flex-direction: column;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #ebeef5;
}

.header-subtitle {
  color: #606266;
  font-size: 14px;
  margin-top: 5px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.help-content {
  line-height: 1.6;
}

.help-section {
  margin-bottom: 20px;
}

.help-section h4 {
  margin-bottom: 10px;
  color: #303133;
}

.code-example {
  background-color: #f5f7fa;
  padding: a5px;
  border-radius: 4px;
  overflow: auto;
  font-family: 'Courier New', Courier, monospace;
  font-size: 14px;
}

.el-row {
  margin-bottom: 20px;
}
</style> 