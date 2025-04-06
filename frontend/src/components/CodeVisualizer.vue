<template>
  <div class="code-visualizer">
    <div class="toolbar">
      <el-button type="primary" @click="visualizeCode" :loading="loading">
        生成流程图
      </el-button>
      <el-button @click="exportImage" :disabled="!flowchart">
        导出图片
      </el-button>
    </div>
    
    <div class="content-area">
      <!-- 代码输入区域 -->
      <div class="code-section" :class="{'expanded': !flowchart}">
        <h3>Python代码</h3>
        <div class="code-editor" ref="codeEditor"></div>
      </div>
      
      <!-- 可视化流程图区域 -->
      <div class="visualizer-section" v-if="flowchart">
        <h3>流程图</h3>
        <div class="flowchart-container" ref="flowchartContainer"></div>
      </div>
    </div>
    
    <!-- 错误消息 -->
    <el-alert
      v-if="error"
      :title="error"
      type="error"
      show-icon
      :closable="true"
      @close="error = null">
    </el-alert>
  </div>
</template>

<script>
import CodeMirror from 'codemirror';
import 'codemirror/lib/codemirror.css';
import 'codemirror/theme/material.css';
import 'codemirror/mode/python/python';
import axios from 'axios';
import * as d3 from 'd3';
import dagreD3 from 'dagre-d3';

export default {
  name: 'CodeVisualizer',
  props: {
    initialCode: {
      type: String,
      default: `import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 加载数据
data = pd.read_csv('data.csv')

# 数据处理
data = data.dropna()
data['new_feature'] = data['x'] * data['y']

# 建模
X = data[['x', 'y', 'new_feature']]
y = data['target']

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)

from sklearn.linear_model import LogisticRegression
model = LogisticRegression()
model.fit(X_train, y_train)

# 评估
predictions = model.predict(X_test)
from sklearn.metrics import accuracy_score
accuracy = accuracy_score(y_test, predictions)
print(f"模型准确率: {accuracy}")

# 可视化结果
plt.figure(figsize=(10, 6))
plt.bar(['Accuracy'], [accuracy])
plt.title('模型性能')
plt.ylim(0, 1)
plt.show()`
    }
  },
  data() {
    return {
      code: this.initialCode,
      flowchart: null,
      loading: false,
      error: null,
      codeEditor: null,
      graph: null,
      renderer: null,
      svg: null
    };
  },
  mounted() {
    this.initCodeEditor();
  },
  methods: {
    initCodeEditor() {
      this.codeEditor = CodeMirror(this.$refs.codeEditor, {
        value: this.code,
        mode: 'python',
        theme: 'material',
        lineNumbers: true,
        lineWrapping: true,
        indentUnit: 4,
        extraKeys: {
          'Tab': function(cm) {
            cm.replaceSelection('    ', 'end');
          }
        }
      });
      
      this.codeEditor.on('change', (cm) => {
        this.code = cm.getValue();
      });
    },
    
    async visualizeCode() {
      if (!this.code.trim()) {
        this.error = '请输入Python代码';
        return;
      }
      
      this.loading = true;
      this.error = null;
      
      try {
        // 实际项目中这里调用后端API
        // const response = await axios.post('/api/v1/analysis/visualize_code', {
        //   code: this.code
        // });
        // this.flowchart = response.data;
        
        // 由于后端API可能未实现，这里模拟一个解析结果
        await this.simulateCodeVisualization();
        
        this.$nextTick(() => {
          this.renderFlowchart();
        });
      } catch (error) {
        this.error = '代码可视化失败: ' + (error.response?.data?.detail || error.message);
      } finally {
        this.loading = false;
      }
    },
    
    simulateCodeVisualization() {
      return new Promise(resolve => {
        // 模拟500ms的处理时间
        setTimeout(() => {
          // 简单代码分析逻辑，实际项目中应当在后端实现更复杂的分析
          this.flowchart = this.parseCodeToGraph(this.code);
          resolve();
        }, 500);
      });
    },
    
    parseCodeToGraph(code) {
      // 简单的代码分析
      const lines = code.split('\n');
      const nodes = [];
      const edges = [];
      
      let currentBlock = null;
      let nodeId = 1;
      let importBlock = null;
      let dataBlock = null;
      
      lines.forEach((line, index) => {
        line = line.trim();
        if (!line || line.startsWith('#')) {
          // 空行或者注释，可能是一个新的代码块的开始
          if (currentBlock && currentBlock.content.length > 0) {
            nodes.push(currentBlock);
            currentBlock = null;
          }
          
          // 如果是注释，创建一个新的代码块
          if (line.startsWith('#')) {
            currentBlock = {
              id: `node${nodeId++}`,
              label: line.substring(1).trim(),
              type: 'comment',
              content: [],
              line: index + 1
            };
          }
        }
        else if (line.startsWith('import') || line.startsWith('from')) {
          // 导入语句
          if (!importBlock) {
            importBlock = {
              id: `node${nodeId++}`,
              label: '导入库',
              type: 'import',
              content: [line],
              line: index + 1
            };
            nodes.push(importBlock);
          } else {
            importBlock.content.push(line);
          }
        }
        else if (line.includes('=') && line.includes('pd.read_') || line.includes('pandas.read_')) {
          // 数据加载
          dataBlock = {
            id: `node${nodeId++}`,
            label: '数据加载',
            type: 'data_load',
            content: [line],
            line: index + 1
          };
          nodes.push(dataBlock);
          
          if (importBlock) {
            edges.push({
              source: importBlock.id,
              target: dataBlock.id
            });
          }
        }
        else if (currentBlock) {
          // 继续添加到当前块
          currentBlock.content.push(line);
        }
        else if (line.includes('model.fit')) {
          // 模型训练
          const modelBlock = {
            id: `node${nodeId++}`,
            label: '模型训练',
            type: 'model',
            content: [line],
            line: index + 1
          };
          nodes.push(modelBlock);
          
          if (dataBlock) {
            edges.push({
              source: dataBlock.id,
              target: modelBlock.id
            });
          }
          currentBlock = modelBlock;
        }
        else if (line.includes('predict')) {
          // 模型预测
          const predictBlock = {
            id: `node${nodeId++}`,
            label: '模型预测',
            type: 'predict',
            content: [line],
            line: index + 1
          };
          nodes.push(predictBlock);
          
          // 找最近的模型节点
          const modelNode = nodes.filter(n => n.type === 'model').pop();
          if (modelNode) {
            edges.push({
              source: modelNode.id,
              target: predictBlock.id
            });
          }
          currentBlock = predictBlock;
        }
        else if (line.includes('accuracy_score') || line.includes('classification_report')) {
          // 模型评估
          const evalBlock = {
            id: `node${nodeId++}`,
            label: '模型评估',
            type: 'evaluate',
            content: [line],
            line: index + 1
          };
          nodes.push(evalBlock);
          
          // 找最近的预测节点
          const predictNode = nodes.filter(n => n.type === 'predict').pop();
          if (predictNode) {
            edges.push({
              source: predictNode.id,
              target: evalBlock.id
            });
          }
          currentBlock = evalBlock;
        }
        else if (line.includes('plt.')) {
          // 可视化
          if (!currentBlock || currentBlock.type !== 'visualize') {
            const visBlock = {
              id: `node${nodeId++}`,
              label: '数据可视化',
              type: 'visualize',
              content: [line],
              line: index + 1
            };
            nodes.push(visBlock);
            
            // 找最近的评估节点或者数据节点
            const evalNode = nodes.filter(n => n.type === 'evaluate').pop();
            if (evalNode) {
              edges.push({
                source: evalNode.id,
                target: visBlock.id
              });
            } else if (dataBlock) {
              edges.push({
                source: dataBlock.id,
                target: visBlock.id
              });
            }
            currentBlock = visBlock;
          } else {
            currentBlock.content.push(line);
          }
        }
        else {
          // 其他代码行，归入数据处理类别
          if (!currentBlock || currentBlock.type === 'comment') {
            const processBlock = {
              id: `node${nodeId++}`,
              label: '数据处理',
              type: 'process',
              content: [line],
              line: index + 1
            };
            nodes.push(processBlock);
            
            if (dataBlock) {
              edges.push({
                source: dataBlock.id,
                target: processBlock.id
              });
            }
            currentBlock = processBlock;
          } else if (currentBlock.type !== 'import') {
            currentBlock.content.push(line);
          }
        }
      });
      
      // 最后的内容块
      if (currentBlock && currentBlock.content.length > 0 && !nodes.includes(currentBlock)) {
        nodes.push(currentBlock);
      }
      
      return { nodes, edges };
    },
    
    renderFlowchart() {
      if (!this.flowchart || !this.flowchart.nodes || this.flowchart.nodes.length === 0) {
        this.error = '没有可视化内容';
        return;
      }
      
      // 清除之前的图表
      const container = this.$refs.flowchartContainer;
      container.innerHTML = '';
      
      // 创建新的SVG元素
      const svg = d3.select(container).append('svg')
        .attr('width', '100%')
        .attr('height', '100%')
        .attr('class', 'flowchart-svg');
      
      this.svg = svg;
      
      // 创建图形和渲染器
      const g = new dagreD3.graphlib.Graph().setGraph({
        rankdir: 'TB',
        marginx: 20,
        marginy: 20,
        nodesep: 70,
        edgesep: 20,
        ranksep: 50,
        acyclicer: 'greedy'
      });
      
      // 添加节点
      this.flowchart.nodes.forEach(node => {
        const nodeClass = `node-type-${node.type}`;
        g.setNode(node.id, {
          label: node.label,
          class: nodeClass,
          rx: 5,
          ry: 5,
          padding: 10
        });
      });
      
      // 添加边
      this.flowchart.edges.forEach(edge => {
        g.setEdge(edge.source, edge.target, {
          label: '',
          arrowheadClass: 'arrowhead',
          curve: d3.curveBasis
        });
      });
      
      // 创建渲染器
      const render = new dagreD3.render();
      
      // 添加g元素以渲染图形
      const svgGroup = svg.append('g');
      
      // 运行渲染器
      render(svgGroup, g);
      
      // 居中显示
      const xCenterOffset = (container.clientWidth - g.graph().width) / 2;
      svgGroup.attr('transform', `translate(${xCenterOffset}, 20)`);
      
      // 设置SVG尺寸与图表尺寸一致
      svg.attr('height', g.graph().height + 40);
      
      // 添加缩放功能
      const zoom = d3.zoom().on('zoom', event => {
        svgGroup.attr('transform', event.transform);
      });
      
      svg.call(zoom);
      
      this.graph = g;
      this.renderer = render;
    },
    
    exportImage() {
      if (!this.svg) return;
      
      try {
        // 创建一个临时SVG序列化器
        const serializer = new XMLSerializer();
        const source = serializer.serializeToString(this.svg.node());
        
        // 添加SVG命名空间
        if(!source.match(/^<svg[^>]+xmlns="http\:\/\/www\.w3\.org\/2000\/svg"/)) {
          const svgSource = source.replace(/^<svg/, '<svg xmlns="http://www.w3.org/2000/svg"');
        }
        
        // 转换为URI
        const svgBlob = new Blob([source], {type: "image/svg+xml;charset=utf-8"});
        const url = URL.createObjectURL(svgBlob);
        
        // 创建下载链接
        const link = document.createElement('a');
        link.href = url;
        link.download = `code_flowchart_${Date.now()}.svg`;
        link.click();
        
        URL.revokeObjectURL(url);
      } catch (error) {
        this.error = '导出图片失败: ' + error.message;
      }
    }
  }
};
</script>

<style scoped>
.code-visualizer {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.toolbar {
  padding: 10px;
  display: flex;
  gap: 10px;
  border-bottom: 1px solid #eee;
}

.content-area {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.code-section, .visualizer-section {
  flex: 1;
  padding: 10px;
  overflow: auto;
  display: flex;
  flex-direction: column;
}

.code-section.expanded {
  flex: 1;
}

.code-editor {
  flex: 1;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
}

h3 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #333;
}

.flowchart-container {
  flex: 1;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: auto;
  background-color: #f8f9fa;
}

/* 流程图节点样式 */
:deep(.node) {
  stroke: #333;
  fill: #fff;
  stroke-width: 1.5px;
}

:deep(.node-type-import) rect {
  fill: #e1f5fe;
}

:deep(.node-type-data_load) rect {
  fill: #e8f5e9;
}

:deep(.node-type-process) rect {
  fill: #fff8e1;
}

:deep(.node-type-model) rect {
  fill: #f3e5f5;
}

:deep(.node-type-predict) rect {
  fill: #e8eaf6;
}

:deep(.node-type-evaluate) rect {
  fill: #fbe9e7;
}

:deep(.node-type-visualize) rect {
  fill: #e0f2f1;
}

:deep(.node-type-comment) rect {
  fill: #f5f5f5;
  stroke-dasharray: 5, 5;
}

:deep(.edgePath path) {
  stroke: #333;
  fill: #333;
  stroke-width: 1.5px;
}

:deep(.arrowhead) {
  fill: #333;
}
</style> 