<template>
  <div class="setup-guide">
    <el-card class="guide-card">
      <div slot="header" class="guide-header">
        <span>实验环境搭建指南</span>
        <el-button
          size="mini"
          type="text"
          @click="expandAll"
          v-if="!allExpanded">
          全部展开
        </el-button>
        <el-button
          size="mini"
          type="text"
          @click="collapseAll"
          v-else>
          全部折叠
        </el-button>
      </div>
      
      <el-scrollbar class="guide-scrollbar">
        <el-collapse v-model="activeSections">
          <!-- 环境要求 -->
          <el-collapse-item name="requirements">
            <template slot="title">
              <div class="section-title">
                <i class="el-icon-s-operation"></i>
                系统环境要求
              </div>
            </template>
            <div class="section-content">
              <el-descriptions title="硬件要求" :column="1" border>
                <el-descriptions-item label="处理器">至少双核处理器，推荐四核及以上</el-descriptions-item>
                <el-descriptions-item label="内存">至少8GB RAM，推荐16GB及以上</el-descriptions-item>
                <el-descriptions-item label="存储">至少20GB可用空间</el-descriptions-item>
                <el-descriptions-item label="显示器">分辨率不低于1280 x 720</el-descriptions-item>
              </el-descriptions>
              
              <el-descriptions title="软件要求" :column="1" border style="margin-top: 15px;">
                <el-descriptions-item label="操作系统">
                  <ul class="requirements-list">
                    <li>Windows 10/11 64位</li>
                    <li>macOS 10.15及以上</li>
                    <li>Ubuntu 20.04 LTS 或其他主流Linux发行版</li>
                  </ul>
                </el-descriptions-item>
                <el-descriptions-item label="必需软件">
                  <ul class="requirements-list">
                    <li>Python 3.8 或更高版本</li>
                    <li>Anaconda (推荐) 或 Miniconda</li>
                    <li>Git</li>
                    <li>IDE (推荐 VS Code 或 PyCharm)</li>
                  </ul>
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </el-collapse-item>
          
          <!-- Python环境设置 -->
          <el-collapse-item name="python">
            <template slot="title">
              <div class="section-title">
                <i class="el-icon-s-platform"></i>
                Python环境设置
              </div>
            </template>
            <div class="section-content">
              <el-tabs type="border-card">
                <el-tab-pane label="Windows">
                  <h4>使用Anaconda安装</h4>
                  <ol class="setup-steps">
                    <li>
                      <p>下载 Anaconda 安装包:</p>
                      <el-link href="https://www.anaconda.com/products/distribution" target="_blank" type="primary">Anaconda官网下载</el-link>
                    </li>
                    <li>
                      <p>运行安装程序，按默认设置安装即可。建议勾选"Add Anaconda to my PATH environment variable"。</p>
                      <div class="step-image">
                        <img src="https://docs.anaconda.com/_images/win-install-options.png" alt="Anaconda安装选项">
                      </div>
                    </li>
                    <li>
                      <p>安装完成后，打开Anaconda Prompt或Windows命令提示符，输入以下命令验证安装:</p>
                      <div class="code-block">
                        <pre>python --version
conda --version</pre>
                      </div>
                    </li>
                  </ol>
                </el-tab-pane>
                
                <el-tab-pane label="macOS">
                  <h4>使用Anaconda安装</h4>
                  <ol class="setup-steps">
                    <li>
                      <p>下载 macOS版本的Anaconda安装包:</p>
                      <el-link href="https://www.anaconda.com/products/distribution" target="_blank" type="primary">Anaconda官网下载</el-link>
                    </li>
                    <li>
                      <p>双击下载的.pkg文件开始安装，按照指引完成安装。</p>
                    </li>
                    <li>
                      <p>安装完成后，打开Terminal，输入以下命令验证安装:</p>
                      <div class="code-block">
                        <pre>python --version
conda --version</pre>
                      </div>
                    </li>
                  </ol>
                </el-tab-pane>
                
                <el-tab-pane label="Linux">
                  <h4>使用Anaconda安装</h4>
                  <ol class="setup-steps">
                    <li>
                      <p>下载Linux版本的Anaconda安装脚本:</p>
                      <el-link href="https://www.anaconda.com/products/distribution" target="_blank" type="primary">Anaconda官网下载</el-link>
                    </li>
                    <li>
                      <p>打开终端，运行以下命令安装:</p>
                      <div class="code-block">
                        <pre>bash ~/Downloads/Anaconda3-2023.XX-Linux-x86_64.sh</pre>
                      </div>
                      <p class="note">注意: 文件名请替换为实际下载的文件名</p>
                    </li>
                    <li>
                      <p>按照安装提示操作，建议在询问是否将conda添加到PATH时选择"yes"。</p>
                    </li>
                    <li>
                      <p>安装完成后，关闭并重新打开终端，或者运行<code>source ~/.bashrc</code>，然后输入以下命令验证安装:</p>
                      <div class="code-block">
                        <pre>python --version
conda --version</pre>
                      </div>
                    </li>
                  </ol>
                </el-tab-pane>
              </el-tabs>
              
              <div class="subsection">
                <h4>创建虚拟环境</h4>
                <p>创建一个专用于本实验平台的虚拟环境，保证依赖隔离:</p>
                <div class="code-block">
                  <pre>conda create -n finance_lab python=3.8
conda activate finance_lab</pre>
                </div>
              </div>
            </div>
          </el-collapse-item>
          
          <!-- 依赖安装 -->
          <el-collapse-item name="dependencies">
            <template slot="title">
              <div class="section-title">
                <i class="el-icon-s-management"></i>
                依赖库安装
              </div>
            </template>
            <div class="section-content">
              <p>使用以下命令安装实验所需的依赖库:</p>
              <div class="code-block">
                <pre>conda activate finance_lab
pip install numpy pandas matplotlib seaborn scikit-learn scipy jupyter
pip install tensorflow keras
pip install plotly dash
pip install yfinance pandas-datareader
pip install statsmodels
pip install ta  # 股票技术分析库</pre>
              </div>
              
              <div class="alternative">
                <h4>使用requirements.txt安装(推荐)</h4>
                <p>您也可以下载实验平台提供的<code>requirements.txt</code>文件，然后使用以下命令一次性安装所有依赖:</p>
                <div class="code-block">
                  <pre>conda activate finance_lab
pip install -r requirements.txt</pre>
                </div>
                <el-button size="small" type="primary" @click="downloadRequirements">下载requirements.txt</el-button>
              </div>
              
              <el-alert
                title="注意：部分库安装可能需要编译器支持"
                type="warning"
                description="在Windows上，您可能需要安装Visual C++ Build Tools; 在Linux上，您可能需要安装gcc和相关开发库。"
                show-icon
                :closable="false">
              </el-alert>
            </div>
          </el-collapse-item>
          
          <!-- 数据集准备 -->
          <el-collapse-item name="datasets">
            <template slot="title">
              <div class="section-title">
                <i class="el-icon-s-data"></i>
                数据集准备
              </div>
            </template>
            <div class="section-content">
              <p>您可以使用以下任一方式获取实验所需的数据集:</p>
              
              <div class="subsection">
                <h4>方法1: 在线直接获取(推荐)</h4>
                <p>在实验过程中，平台会自动为您准备相应的数据集，无需手动下载。您只需要按照实验指引进行操作即可。</p>
              </div>
              
              <div class="subsection">
                <h4>方法2: 手动下载数据集</h4>
                <p>如果您想在离线环境中进行实验，也可以提前下载以下数据集:</p>
                <el-table :data="datasets" style="width: 100%">
                  <el-table-column prop="name" label="数据集名称" width="180"></el-table-column>
                  <el-table-column prop="description" label="描述"></el-table-column>
                  <el-table-column label="操作" width="120">
                    <template slot-scope="scope">
                      <el-button 
                        size="mini" 
                        type="primary" 
                        @click="downloadDataset(scope.row)">
                        下载
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
              
              <div class="subsection">
                <h4>数据集存放位置</h4>
                <p>下载的数据集请存放在项目目录下的<code>data/</code>文件夹中:</p>
                <div class="code-block">
                  <pre>project_root/
├── data/
│   ├── stock_data.csv
│   ├── bank_credit.csv
│   └── insurance_data.csv
├── notebooks/
├── src/
└── ... (其他目录)</pre>
                </div>
              </div>
            </div>
          </el-collapse-item>
          
          <!-- 开发环境设置 -->
          <el-collapse-item name="ide">
            <template slot="title">
              <div class="section-title">
                <i class="el-icon-s-tools"></i>
                开发环境设置
              </div>
            </template>
            <div class="section-content">
              <el-tabs type="border-card">
                <el-tab-pane label="VS Code (推荐)">
                  <h4>安装VS Code</h4>
                  <ol class="setup-steps">
                    <li>
                      <p>从官网下载并安装VS Code:</p>
                      <el-link href="https://code.visualstudio.com/" target="_blank" type="primary">Visual Studio Code官网</el-link>
                    </li>
                    <li>
                      <p>安装必要的扩展:</p>
                      <ul>
                        <li>Python (Microsoft): Python语言支持</li>
                        <li>Jupyter: Jupyter Notebook支持</li>
                        <li>Python Indent: 自动缩进</li>
                        <li>autoDocstring: 文档字符串自动生成</li>
                      </ul>
                      <div class="step-image">
                        <img src="https://code.visualstudio.com/assets/docs/languages/python/python-extension.png" alt="VS Code Python扩展">
                      </div>
                    </li>
                    <li>
                      <p>配置Python解释器:</p>
                      <p>按下<code>Ctrl+Shift+P</code> (Windows/Linux) 或 <code>Cmd+Shift+P</code> (macOS)，输入"Python: Select Interpreter"，选择先前创建的conda环境。</p>
                    </li>
                  </ol>
                </el-tab-pane>
                
                <el-tab-pane label="PyCharm">
                  <h4>安装PyCharm</h4>
                  <ol class="setup-steps">
                    <li>
                      <p>从官网下载并安装PyCharm (社区版免费):</p>
                      <el-link href="https://www.jetbrains.com/pycharm/download/" target="_blank" type="primary">PyCharm官网</el-link>
                    </li>
                    <li>
                      <p>配置Anaconda解释器:</p>
                      <p>打开 File > Settings > Project > Python Interpreter，点击右上角齿轮图标，选择"Add..."，然后选择"Conda Environment"，找到先前创建的环境。</p>
                    </li>
                    <li>
                      <p>安装必要的插件:</p>
                      <p>File > Settings > Plugins，搜索并安装以下插件:</p>
                      <ul>
                        <li>Jupyter Notebook</li>
                        <li>CSV Editor</li>
                      </ul>
                    </li>
                  </ol>
                </el-tab-pane>
                
                <el-tab-pane label="Jupyter Notebook">
                  <h4>使用Jupyter Notebook</h4>
                  <ol class="setup-steps">
                    <li>
                      <p>安装Jupyter:</p>
                      <div class="code-block">
                        <pre>conda activate finance_lab
pip install jupyter notebook</pre>
                      </div>
                    </li>
                    <li>
                      <p>启动Jupyter Notebook:</p>
                      <div class="code-block">
                        <pre>jupyter notebook</pre>
                      </div>
                      <p>这将在您的默认浏览器中打开Jupyter Web界面。</p>
                    </li>
                    <li>
                      <p>创建新的笔记本:</p>
                      <p>点击右上角的"New"按钮，选择"Python 3"创建新的笔记本。</p>
                    </li>
                  </ol>
                </el-tab-pane>
              </el-tabs>
            </div>
          </el-collapse-item>
          
          <!-- 验证安装 -->
          <el-collapse-item name="verify">
            <template slot="title">
              <div class="section-title">
                <i class="el-icon-s-claim"></i>
                验证安装
              </div>
            </template>
            <div class="section-content">
              <p>完成以上步骤后，请运行以下测试代码来验证您的环境是否正确设置:</p>
              <div class="code-block">
                <pre>import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sklearn
import tensorflow as tf
import yfinance as yf

# 打印各库版本
print(f"NumPy: {np.__version__}")
print(f"Pandas: {pd.__version__}")
print(f"Scikit-learn: {sklearn.__version__}")
print(f"TensorFlow: {tf.__version__}")

# 简单的数据获取测试
try:
    data = yf.download("AAPL", period="5d")
    print("\n成功获取苹果股票数据:")
    print(data.head())
    
    # 简单的可视化测试
    plt.figure(figsize=(10, 5))
    plt.plot(data.index, data['Close'])
    plt.title('Apple Stock Price')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.show()
    
    print("\n恭喜! 您的环境设置已成功完成。")
except Exception as e:
    print(f"\n出现错误: {str(e)}")
    print("请检查您的网络连接和依赖库安装情况。")</pre>
              </div>
              
              <el-button type="success" @click="copyVerificationCode">复制验证代码</el-button>
              
              <el-alert
                v-if="verificationSuccess"
                title="验证成功"
                type="success"
                description="恭喜！您的环境设置已完成，现在可以开始进行实验了。"
                show-icon
                :closable="false"
                style="margin-top: 15px;">
              </el-alert>
            </div>
          </el-collapse-item>
          
          <!-- 故障排除 -->
          <el-collapse-item name="troubleshooting">
            <template slot="title">
              <div class="section-title">
                <i class="el-icon-warning-outline"></i>
                常见问题与故障排除
              </div>
            </template>
            <div class="section-content">
              <el-collapse>
                <el-collapse-item title="依赖库安装失败" name="1">
                  <p>可能的原因和解决方案:</p>
                  <ul>
                    <li>
                      <strong>网络问题</strong>: 尝试使用镜像源安装，例如:
                      <div class="code-block">
                        <pre>pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple</pre>
                      </div>
                    </li>
                    <li>
                      <strong>缺少编译器</strong>: 部分库需要编译器支持
                      <ul>
                        <li>Windows: 安装 <a href="https://visualstudio.microsoft.com/visual-cpp-build-tools/" target="_blank">Visual C++ Build Tools</a></li>
                        <li>Linux: <code>sudo apt-get install build-essential</code> (Ubuntu/Debian) 或 <code>sudo yum groupinstall "Development Tools"</code> (CentOS/RHEL)</li>
                        <li>macOS: <code>xcode-select --install</code></li>
                      </ul>
                    </li>
                    <li>
                      <strong>使用Conda安装</strong>: 某些库在pip安装困难时，可以尝试用conda安装:
                      <div class="code-block">
                        <pre>conda install numpy pandas scikit-learn</pre>
                      </div>
                    </li>
                  </ul>
                </el-collapse-item>
                
                <el-collapse-item title="导入库时出现错误" name="2">
                  <p>如果在导入库时出现错误:</p>
                  <ul>
                    <li>
                      <strong>确认虚拟环境已激活</strong>: 确保在运行代码前已激活正确的conda环境:
                      <div class="code-block">
                        <pre>conda activate finance_lab</pre>
                      </div>
                    </li>
                    <li>
                      <strong>检查包版本兼容性</strong>: 某些库的版本可能不兼容，尝试安装特定版本:
                      <div class="code-block">
                        <pre>pip install tensorflow==2.6.0</pre>
                      </div>
                    </li>
                    <li>
                      <strong>检查Python版本</strong>: 确保使用的Python版本与库兼容，推荐使用Python 3.8。</li>
                  </ul>
                </el-collapse-item>
                
                <el-collapse-item title="数据访问或下载问题" name="3">
                  <p>如果无法访问或下载数据:</p>
                  <ul>
                    <li>
                      <strong>检查网络连接</strong>: 确保您能够访问互联网，特别是在使用yfinance等在线数据源时。
                    </li>
                    <li>
                      <strong>使用代理</strong>: 如果您的网络环境需要代理，设置环境变量:
                      <div class="code-block">
                        <pre># Windows (CMD)
set HTTP_PROXY=http://proxy_server:port
set HTTPS_PROXY=http://proxy_server:port

# Linux/macOS
export HTTP_PROXY=http://proxy_server:port
export HTTPS_PROXY=http://proxy_server:port</pre>
                      </div>
                    </li>
                    <li>
                      <strong>使用离线数据</strong>: 如果在线数据访问持续失败，请下载我们提供的示例数据集，并使用本地加载方式。
                    </li>
                  </ul>
                </el-collapse-item>
                
                <el-collapse-item title="Jupyter Notebook问题" name="4">
                  <ul>
                    <li>
                      <strong>内核无法启动</strong>: 确保在Jupyter中选择了正确的内核，可能需要手动添加内核:
                      <div class="code-block">
                        <pre>python -m ipykernel install --user --name finance_lab --display-name "Python (finance_lab)"</pre>
                      </div>
                    </li>
                    <li>
                      <strong>内核崩溃</strong>: 可能是因为内存不足，尝试关闭其他应用程序，或者增加系统的交换空间。
                    </li>
                  </ul>
                </el-collapse-item>
                
                <el-collapse-item title="图形显示问题" name="5">
                  <ul>
                    <li>
                      <strong>matplotlib图形不显示</strong>: 在Jupyter中添加魔术命令:
                      <div class="code-block">
                        <pre>%matplotlib inline</pre>
                      </div>
                    </li>
                    <li>
                      <strong>中文字体显示为方块</strong>: 需要配置中文字体:
                      <div class="code-block">
                        <pre>import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False    # 用来正常显示负号</pre>
                      </div>
                    </li>
                  </ul>
                </el-collapse-item>
              </el-collapse>
              
              <div class="help-section">
                <h4>仍然需要帮助?</h4>
                <p>如果您遇到上述未覆盖的问题，请通过以下方式获取支持:</p>
                <ul>
                  <li>查阅<el-link type="primary" href="#" @click.prevent="openDocumentation">完整文档</el-link></li>
                  <li>在<el-link type="primary" href="#" @click.prevent="openForum">论坛</el-link>中提问</li>
                  <li>联系您的实验指导教师</li>
                </ul>
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>
      </el-scrollbar>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'SetupGuide',
  data() {
    return {
      activeSections: ['requirements'],
      verificationSuccess: false,
      datasets: [
        { 
          name: '股票市场数据', 
          description: '近5年主要股票市场指数和个股数据',
          url: '/api/v1/datasets/stock_market.zip'
        },
        { 
          name: '银行信贷数据', 
          description: '信用卡客户违约预测数据集',
          url: '/api/v1/datasets/credit_default.zip'
        },
        { 
          name: '保险客户数据', 
          description: '包含车险和健康保险客户数据',
          url: '/api/v1/datasets/insurance.zip'
        }
      ]
    };
  },
  computed: {
    allExpanded() {
      const allSections = ['requirements', 'python', 'dependencies', 'datasets', 'ide', 'verify', 'troubleshooting'];
      return allSections.every(section => this.activeSections.includes(section));
    }
  },
  methods: {
    expandAll() {
      this.activeSections = ['requirements', 'python', 'dependencies', 'datasets', 'ide', 'verify', 'troubleshooting'];
    },
    collapseAll() {
      this.activeSections = [];
    },
    downloadRequirements() {
      // 实际项目中应该提供一个真实的下载链接
      // window.open('/api/v1/setup/requirements.txt', '_blank');
      this.$message({
        message: '正在下载requirements.txt...',
        type: 'success'
      });
      
      // 模拟下载内容
      const content = `numpy==1.22.4
pandas==1.4.2
matplotlib==3.5.2
seaborn==0.11.2
scikit-learn==1.1.1
scipy==1.8.1
jupyter==1.0.0
tensorflow==2.9.1
keras==2.9.0
plotly==5.8.0
dash==2.5.1
yfinance==0.1.72
pandas-datareader==0.10.0
statsmodels==0.13.2
ta==0.10.1
`;
      
      const blob = new Blob([content], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'requirements.txt';
      link.click();
      URL.revokeObjectURL(url);
    },
    downloadDataset(dataset) {
      // 实际项目中应该提供真实的下载链接
      // window.open(dataset.url, '_blank');
      this.$message({
        message: `正在下载${dataset.name}...`,
        type: 'success'
      });
    },
    copyVerificationCode() {
      const verificationCode = `import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sklearn
import tensorflow as tf
import yfinance as yf

# 打印各库版本
print(f"NumPy: {np.__version__}")
print(f"Pandas: {pd.__version__}")
print(f"Scikit-learn: {sklearn.__version__}")
print(f"TensorFlow: {tf.__version__}")

# 简单的数据获取测试
try:
    data = yf.download("AAPL", period="5d")
    print("\\n成功获取苹果股票数据:")
    print(data.head())
    
    # 简单的可视化测试
    plt.figure(figsize=(10, 5))
    plt.plot(data.index, data['Close'])
    plt.title('Apple Stock Price')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.show()
    
    print("\\n恭喜! 您的环境设置已成功完成。")
except Exception as e:
    print(f"\\n出现错误: {str(e)}")
    print("请检查您的网络连接和依赖库安装情况。")`;
      
      navigator.clipboard.writeText(verificationCode).then(() => {
        this.$message({
          message: '验证代码已复制到剪贴板',
          type: 'success'
        });
        
        // 模拟验证成功
        setTimeout(() => {
          this.verificationSuccess = true;
        }, 2000);
      }).catch(() => {
        this.$message.error('复制失败，请手动复制代码');
      });
    },
    openDocumentation() {
      this.$message.info('文档正在建设中，敬请期待');
    },
    openForum() {
      this.$message.info('论坛正在建设中，敬请期待');
    }
  }
};
</script>

<style scoped>
.setup-guide {
  height: 100%;
}

.guide-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.guide-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.guide-scrollbar {
  height: calc(100% - 50px);
}

.section-title {
  display: flex;
  align-items: center;
  font-weight: bold;
}

.section-title i {
  margin-right: 10px;
  color: #409EFF;
}

.section-content {
  padding: 10px 20px 20px;
}

.setup-steps {
  padding-left: 20px;
}

.setup-steps li {
  margin-bottom: 15px;
}

.step-image {
  margin: 10px 0;
  text-align: center;
}

.step-image img {
  max-width: 100%;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.subsection {
  margin-top: 20px;
}

.subsection h4 {
  margin-bottom: 10px;
  color: #303133;
}

.code-block {
  background-color: #f5f7fa;
  border-radius: 4px;
  padding: 10px;
  margin: 10px 0;
  overflow-x: auto;
}

.code-block pre {
  margin: 0;
  font-family: 'Courier New', Courier, monospace;
  white-space: pre-wrap;
}

.note {
  color: #909399;
  font-style: italic;
  font-size: 13px;
  margin-top: 5px;
}

.alternative {
  margin-top: 20px;
  padding: 15px;
  border: 1px dashed #dcdfe6;
  border-radius: 4px;
}

.help-section {
  margin-top: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.requirements-list {
  margin: 0;
  padding-left: 20px;
}

.requirements-list li {
  margin-bottom: 5px;
}
</style> 