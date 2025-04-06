<template>
  <div class="custom-code-editor">
    <el-card class="editor-card">
      <div slot="header" class="editor-header">
        <span>自定义代码编辑器</span>
        <div class="header-actions">
          <el-select v-model="selectedTemplate" placeholder="选择代码模板" size="small" @change="loadTemplate">
            <el-option
              v-for="item in codeTemplates"
              :key="item.id"
              :label="item.name"
              :value="item.id">
            </el-option>
          </el-select>
          <el-button-group>
            <el-button type="primary" size="small" @click="runCode" :loading="loading">
              <i class="el-icon-video-play"></i> 运行
            </el-button>
            <el-button type="info" size="small" @click="saveCode" :disabled="loading">
              <i class="el-icon-document-checked"></i> 保存
            </el-button>
            <el-button type="danger" size="small" @click="clearOutput" :disabled="loading">
              <i class="el-icon-delete"></i> 清除输出
            </el-button>
          </el-button-group>
        </div>
      </div>
      
      <div class="editor-container">
        <div class="code-editor" ref="codeEditor"></div>
        
        <div class="execution-output">
          <div class="output-header">
            <span>执行结果</span>
            <div class="output-actions">
              <el-switch
                v-model="autoScroll"
                active-text="自动滚动"
                inactive-text=""
                size="small">
              </el-switch>
            </div>
          </div>
          
          <div class="output-content" ref="outputContent">
            <pre v-if="output" v-html="formattedOutput"></pre>
            <div v-else class="empty-output">
              <i class="el-icon-info"></i>
              <span>运行代码后将在此处显示输出结果</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="visualization-container" v-if="visualization">
        <div class="visualization-header">
          <span>可视化结果</span>
          <el-button size="mini" type="text" @click="downloadVisualization">
            <i class="el-icon-download"></i> 下载
          </el-button>
        </div>
        <div class="visualization-content">
          <img :src="visualization" class="visualization-image" alt="Visualization" />
        </div>
      </div>
    </el-card>
    
    <!-- 保存代码对话框 -->
    <el-dialog
      title="保存代码"
      :visible.sync="saveDialogVisible"
      width="30%">
      <el-form :model="saveForm" label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="saveForm.name" placeholder="请输入代码名称"></el-input>
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            type="textarea"
            :rows="3"
            placeholder="请输入代码描述"
            v-model="saveForm.description">
          </el-input>
        </el-form-item>
        <el-form-item label="标签">
          <el-select
            v-model="saveForm.tags"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="请输入标签">
            <el-option
              v-for="item in tagOptions"
              :key="item"
              :label="item"
              :value="item">
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="saveDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitSaveCode">确定</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import CodeMirror from 'codemirror'
import 'codemirror/lib/codemirror.css'
import 'codemirror/theme/monokai.css'
import 'codemirror/mode/python/python'
import axios from 'axios'

export default {
  name: 'CustomCodeEditor',
  data() {
    return {
      editor: null,
      code: '',
      output: '',
      loading: false,
      visualization: null,
      selectedTemplate: '',
      autoScroll: true,
      saveDialogVisible: false,
      saveForm: {
        name: '',
        description: '',
        tags: []
      },
      tagOptions: ['数据分析', '可视化', '机器学习', '金融分析', '风险预测'],
      codeTemplates: [
        {
          id: 'data_analysis',
          name: '数据分析模板',
          code: `# 数据分析模板
import pandas as pd
import numpy as np

# 创建示例数据
data = {
    '日期': pd.date_range(start='2023-01-01', periods=10),
    '收盘价': np.random.normal(100, 10, 10),
    '交易量': np.random.randint(1000, 5000, 10),
    '涨跌幅': np.random.normal(0, 0.02, 10)
}

# 创建DataFrame
df = pd.DataFrame(data)

# 数据分析
print("数据概览:")
print(df.head())

print("\\n基本统计信息:")
print(df.describe())

print("\\n缺失值检查:")
print(df.isnull().sum())
`
        },
        {
          id: 'visualization',
          name: '数据可视化模板',
          code: `# 数据可视化模板
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 创建示例数据
dates = pd.date_range(start='2023-01-01', periods=30)
prices = np.random.normal(100, 5, 30)
volumes = np.random.randint(1000, 5000, 30)

# 创建DataFrame
df = pd.DataFrame({
    '日期': dates,
    '价格': prices,
    '交易量': volumes
})

# 设置图表风格
plt.style.use('seaborn-v0_8-darkgrid')

# 创建子图
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

# 绘制价格线图
ax1.plot(df['日期'], df['价格'], color='blue', linewidth=2)
ax1.set_title('股票价格与交易量分析')
ax1.set_ylabel('价格')
ax1.grid(True)

# 绘制交易量柱状图
ax2.bar(df['日期'], df['交易量'], color='green', alpha=0.7)
ax2.set_xlabel('日期')
ax2.set_ylabel('交易量')
ax2.grid(True)

# 调整布局
plt.tight_layout()
plt.show()
`
        },
        {
          id: 'ml_model',
          name: '机器学习模型模板',
          code: `# 机器学习模型模板
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# 创建示例数据
np.random.seed(42)
X = np.random.rand(100, 1) * 10
y = 2 * X.squeeze() + 1 + np.random.randn(100) * 2

# 拆分数据集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 训练模型
model = LinearRegression()
model.fit(X_train, y_train)

# 预测
y_pred = model.predict(X_test)

# 评估模型
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"模型斜率: {model.coef_[0]:.4f}")
print(f"模型截距: {model.intercept_:.4f}")
print(f"均方误差 (MSE): {mse:.4f}")
print(f"决定系数 (R²): {r2:.4f}")

# 可视化结果
plt.figure(figsize=(10, 6))
plt.scatter(X_test, y_test, color='blue', alpha=0.5, label='实际值')
plt.plot(X_test, y_pred, color='red', linewidth=2, label='预测值')
plt.title('线性回归模型预测')
plt.xlabel('X')
plt.ylabel('y')
plt.legend()
plt.grid(True)
plt.show()
`
        },
        {
          id: 'financial_analysis',
          name: '金融分析模板',
          code: `# 金融分析模板
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 创建模拟股票数据
np.random.seed(42)
trading_days = 252  # 一年交易日
dates = pd.date_range('2023-01-01', periods=trading_days)
price = 100  # 初始价格
prices = [price]

# 模拟股价波动 (几何布朗运动)
returns = np.random.normal(0.0005, 0.015, trading_days-1)
for ret in returns:
    price *= (1 + ret)
    prices.append(price)

# 创建数据集
df = pd.DataFrame({
    '日期': dates,
    '收盘价': prices,
    '交易量': np.random.randint(1000000, 10000000, trading_days)
})

# 计算常用技术指标
df['日收益率'] = df['收盘价'].pct_change()
df['20日均线'] = df['收盘价'].rolling(window=20).mean()
df['50日均线'] = df['收盘价'].rolling(window=50).mean()
df['20日波动率'] = df['日收益率'].rolling(window=20).std() * np.sqrt(252) * 100

# 计算回报与风险指标
returns = df['日收益率'].dropna()
annual_return = returns.mean() * 252 * 100
annual_volatility = returns.std() * np.sqrt(252) * 100
sharpe_ratio = annual_return / annual_volatility

print(f"年化收益率: {annual_return:.2f}%")
print(f"年化波动率: {annual_volatility:.2f}%")
print(f"夏普比率: {sharpe_ratio:.4f}")

# 绘制股价走势和均线
plt.figure(figsize=(12, 8))
plt.plot(df['日期'], df['收盘价'], label='收盘价')
plt.plot(df['日期'], df['20日均线'], label='20日均线')
plt.plot(df['日期'], df['50日均线'], label='50日均线')
plt.title('股价走势与均线分析')
plt.xlabel('日期')
plt.ylabel('价格')
plt.legend()
plt.grid(True)
plt.show()
`
        }
      ]
    }
  },
  computed: {
    formattedOutput() {
      // 高亮输出中的错误信息
      if (!this.output) return '';
      
      return this.output
        .replace(/Error:/g, '<span class="output-error">Error:</span>')
        .replace(/Warning:/g, '<span class="output-warning">Warning:</span>');
    }
  },
  mounted() {
    this.initEditor();
  },
  beforeDestroy() {
    if (this.editor) {
      this.editor = null;
    }
  },
  methods: {
    initEditor() {
      // 初始化CodeMirror编辑器
      this.editor = CodeMirror(this.$refs.codeEditor, {
        value: '# 在此编写Python代码\nimport pandas as pd\nimport numpy as np\nimport matplotlib.pyplot as plt\n\n# 示例: 创建数据并打印\ndata = {"A": [1, 2, 3], "B": [4, 5, 6]}\ndf = pd.DataFrame(data)\nprint(df)\n',
        mode: 'python',
        theme: 'monokai',
        lineNumbers: true,
        indentUnit: 4,
        smartIndent: true,
        lineWrapping: true,
        matchBrackets: true,
        autoCloseBrackets: true,
        extraKeys: {"Tab": "indentMore", "Shift-Tab": "indentLess"}
      });
      
      // 监听编辑器内容变化
      this.editor.on('change', () => {
        this.code = this.editor.getValue();
      });
      
      // 初始赋值
      this.code = this.editor.getValue();
    },
    
    async runCode() {
      if (!this.code.trim()) {
        this.$message.warning('请输入代码后运行');
        return;
      }
      
      this.loading = true;
      this.output = '正在执行...\n';
      this.visualization = null;
      
      try {
        const response = await axios.post('/api/v1/execute-code/execute', {
          code: this.code
        });
        
        const result = response.data;
        this.output = result.output || '代码执行完成，无输出';
        
        if (result.visualization) {
          this.visualization = `data:image/png;base64,${result.visualization}`;
        }
        
        if (!result.success) {
          this.$message.error('代码执行出错，请查看输出信息');
        } else if (!this.output.trim() && !this.visualization) {
          this.$message.warning('代码执行完成，但没有输出结果');
        } else {
          this.$message.success('代码执行成功');
        }
      } catch (error) {
        console.error('执行代码失败', error);
        this.output = `执行失败: ${error.message || '未知错误'}\n\n${error.response?.data?.detail || ''}`;
        this.$message.error('请求失败，请检查网络连接');
      } finally {
        this.loading = false;
        
        // 自动滚动到输出底部
        if (this.autoScroll) {
          this.$nextTick(() => {
            if (this.$refs.outputContent) {
              this.$refs.outputContent.scrollTop = this.$refs.outputContent.scrollHeight;
            }
          });
        }
      }
    },
    
    clearOutput() {
      this.output = '';
      this.visualization = null;
    },
    
    loadTemplate() {
      if (!this.selectedTemplate) return;
      
      const template = this.codeTemplates.find(t => t.id === this.selectedTemplate);
      if (template) {
        // 确认是否覆盖当前代码
        if (this.code.trim() && this.code !== this.editor.getValue()) {
          this.$confirm('加载模板将覆盖当前代码，是否继续?', '提示', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }).then(() => {
            this.editor.setValue(template.code);
            this.code = template.code;
          }).catch(() => {});
        } else {
          this.editor.setValue(template.code);
          this.code = template.code;
        }
      }
    },
    
    saveCode() {
      if (!this.code.trim()) {
        this.$message.warning('代码不能为空');
        return;
      }
      
      // 显示保存对话框
      this.saveDialogVisible = true;
    },
    
    async submitSaveCode() {
      if (!this.saveForm.name.trim()) {
        this.$message.warning('请输入代码名称');
        return;
      }
      
      try {
        const response = await axios.post('/api/v1/execute-code/user_codes', {
          name: this.saveForm.name,
          description: this.saveForm.description,
          tags: this.saveForm.tags,
          code: this.code
        });
        
        if (response.data.success) {
          this.$message.success('代码保存成功');
          this.saveDialogVisible = false;
          
          // 清空表单
          this.saveForm = {
            name: '',
            description: '',
            tags: []
          };
        } else {
          this.$message.error('保存失败: ' + response.data.message);
        }
      } catch (error) {
        console.error('保存代码失败', error);
        this.$message.error('请求失败: ' + (error.response?.data?.detail || error.message || '未知错误'));
      }
    },
    
    downloadVisualization() {
      if (!this.visualization) return;
      
      // 创建下载链接
      const link = document.createElement('a');
      link.href = this.visualization;
      link.download = `visualization_${new Date().getTime()}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  }
}
</script>

<style scoped>
.custom-code-editor {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.editor-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.editor-container {
  display: flex;
  flex: 1;
  min-height: 600px;
  gap: 15px;
  margin-bottom: 15px;
}

.code-editor {
  flex: 6;
  height: 100%;
  min-height: 600px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}

.execution-output {
  flex: 4;
  display: flex;
  flex-direction: column;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}

.output-header {
  padding: 8px 12px;
  background-color: #f5f7fa;
  border-bottom: 1px solid #dcdfe6;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.output-content {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  background-color: #1e1e1e;
  color: #ffffff;
  font-family: 'Courier New', Courier, monospace;
  font-size: 14px;
  white-space: pre-wrap;
  word-break: break-all;
  height: 100%;
  min-height: 300px;
  max-height: 600px;
}

.empty-output {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #909399;
  gap: 10px;
}

.empty-output i {
  font-size: 24px;
}

.visualization-container {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 15px;
}

.visualization-header {
  padding: 8px 12px;
  background-color: #f5f7fa;
  border-bottom: 1px solid #dcdfe6;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.visualization-content {
  padding: 15px;
  display: flex;
  justify-content: center;
  background-color: #fff;
}

.visualization-image {
  max-width: 100%;
  max-height: 500px;
}

.output-error {
  color: #f56c6c;
  font-weight: bold;
}

.output-warning {
  color: #e6a23c;
  font-weight: bold;
}
</style> 