<template>
  <div class="workflow-editor">
    <!-- 组件面板 -->
    <div class="component-panel">
      <h3>算法组件</h3>
      <div v-for="(group, groupName) in groupedComponents" :key="groupName">
        <h4>{{ groupNameMap[groupName] }}</h4>
        <div 
          v-for="component in group" 
          :key="component.id" 
          class="component-item"
          draggable="true"
          @dragstart="handleDragStart($event, component)"
        >
          {{ component.name }}
        </div>
      </div>
    </div>
    
    <!-- 工作流画布 -->
    <div class="workflow-canvas" 
      @drop="handleDrop"
      @dragover="handleDragOver"
    >
      <svg ref="svg" width="100%" height="100%">
        <!-- 连线 -->
        <path 
          v-for="edge in workflow.edges" 
          :key="edge.id"
          :d="calculatePath(edge)"
          stroke="#666"
          stroke-width="2"
          fill="none"
          marker-end="url(#arrowhead)"
        ></path>
        
        <!-- 箭头标记 -->
        <defs>
          <marker
            id="arrowhead"
            viewBox="0 0 10 10"
            refX="8"
            refY="5"
            markerWidth="6"
            markerHeight="6"
            orient="auto"
          >
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#666" />
          </marker>
        </defs>
      </svg>
      
      <!-- 节点 -->
      <div 
        v-for="node in workflow.nodes" 
        :key="node.id"
        class="node"
        :class="{ 'selected': selectedNode === node.id }"
        :style="{ left: node.x + 'px', top: node.y + 'px' }"
        @mousedown="handleNodeMouseDown($event, node)"
        @click="selectNode(node)"
      >
        <div class="node-header">{{ node.name }}</div>
        <div class="node-status" :class="node.status || 'idle'">
          {{ nodeStatusMap[node.status || 'idle'] }}
        </div>
        <div class="node-ports">
          <div class="input-ports">
            <div 
              v-for="port in node.inputPorts" 
              :key="port.id"
              class="port input-port"
              @mousedown="handlePortMouseDown($event, node, port, 'input')"
            ></div>
          </div>
          <div class="output-ports">
            <div 
              v-for="port in node.outputPorts" 
              :key="port.id"
              class="port output-port"
              @mousedown="handlePortMouseDown($event, node, port, 'output')"
            ></div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 属性面板 -->
    <div class="property-panel" v-if="selectedNode">
      <h3>组件属性</h3>
      <div v-if="selectedNodeData">
        <div class="property-item">
          <label>名称:</label>
          <input v-model="selectedNodeData.name" />
        </div>
        <div class="property-item">
          <label>类型:</label>
          <span>{{ groupNameMap[selectedNodeData.type] }}</span>
        </div>
        <div class="property-item">
          <label>代码:</label>
          <div class="code-editor-container">
            <code-editor v-model="selectedNodeData.code" language="python" />
          </div>
        </div>
        <div class="property-buttons">
          <button @click="saveNodeProperties">保存</button>
          <button @click="deleteSelectedNode" class="delete-btn">删除</button>
        </div>
      </div>
    </div>
    
    <!-- 底部工具栏 -->
    <div class="toolbar">
      <button @click="saveWorkflow">保存工作流</button>
      <button @click="runWorkflow" :disabled="isRunning">运行</button>
      <button @click="stopWorkflow" :disabled="!isRunning">停止</button>
    </div>
  </div>
</template>

<script>
import CodeEditor from './CodeEditor.vue';
import { v4 as uuidv4 } from 'uuid';

export default {
  components: {
    CodeEditor
  },
  props: {
    experimentId: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      components: [],
      workflow: {
        nodes: [],
        edges: []
      },
      selectedNode: null,
      selectedNodeData: null,
      isDrawingLine: false,
      startPort: null,
      startNode: null,
      portType: null,
      isRunning: false,
      groupNameMap: {
        'data_prep': '数据准备',
        'data_explore': '数据探索',
        'data_clean': '数据清洗',
        'feature_eng': '特征工程',
        'modeling': '建模分析',
        'evaluation': '模型评价',
        'visualization': '可视化'
      },
      nodeStatusMap: {
        'idle': '未运行',
        'running': '运行中',
        'completed': '已完成',
        'failed': '失败'
      }
    };
  },
  computed: {
    groupedComponents() {
      const grouped = {};
      this.components.forEach(component => {
        if (!grouped[component.component_type]) {
          grouped[component.component_type] = [];
        }
        grouped[component.component_type].push(component);
      });
      return grouped;
    }
  },
  mounted() {
    this.fetchComponents();
    this.fetchWorkflow();
    
    // 添加事件监听
    document.addEventListener('mousemove', this.handleMouseMove);
    document.addEventListener('mouseup', this.handleMouseUp);
  },
  beforeDestroy() {
    // 移除事件监听
    document.removeEventListener('mousemove', this.handleMouseMove);
    document.removeEventListener('mouseup', this.handleMouseUp);
  },
  methods: {
    async fetchComponents() {
      try {
        const response = await this.$http.get('/api/components/');
        this.components = response.data;
      } catch (error) {
        console.error('加载组件失败', error);
        this.$message.error('加载组件失败');
      }
    },
    async fetchWorkflow() {
      try {
        const response = await this.$http.get(`/api/experiments/${this.experimentId}/`);
        if (response.data.workflow_data) {
          this.workflow = response.data.workflow_data;
        }
      } catch (error) {
        console.error('加载工作流失败', error);
        this.$message.error('加载工作流失败');
      }
    },
    handleDragStart(event, component) {
      event.dataTransfer.setData('componentId', component.id);
    },
    handleDragOver(event) {
      event.preventDefault();
    },
    handleDrop(event) {
      event.preventDefault();
      const componentId = event.dataTransfer.getData('componentId');
      if (!componentId) return;
      
      const component = this.components.find(c => c.id === componentId);
      if (!component) return;
      
      const rect = event.currentTarget.getBoundingClientRect();
      const x = event.clientX - rect.left;
      const y = event.clientY - rect.top;
      
      // 创建新节点
      const newNode = {
        id: uuidv4(),
        name: component.name,
        type: component.component_type,
        componentId: component.id,
        code: component.code,
        x,
        y,
        inputPorts: [{ id: uuidv4() }],
        outputPorts: [{ id: uuidv4() }],
        status: 'idle'
      };
      
      this.workflow.nodes.push(newNode);
    },
    handleNodeMouseDown(event, node) {
      if (this.isDrawingLine) return;
      
      this.isDraggingNode = true;
      this.draggedNode = node;
      this.dragStartX = event.clientX;
      this.dragStartY = event.clientY;
      this.nodeStartX = node.x;
      this.nodeStartY = node.y;
    },
    handlePortMouseDown(event, node, port, type) {
      event.stopPropagation();
      
      this.isDrawingLine = true;
      this.startNode = node;
      this.startPort = port;
      this.portType = type;
    },
    handleMouseMove(event) {
      if (this.isDraggingNode) {
        const dx = event.clientX - this.dragStartX;
        const dy = event.clientY - this.dragStartY;
        
        this.draggedNode.x = this.nodeStartX + dx;
        this.draggedNode.y = this.nodeStartY + dy;
      }
      
      if (this.isDrawingLine) {
        // 更新临时连线
        // 实现略...
      }
    },
    handleMouseUp(event) {
      if (this.isDraggingNode) {
        this.isDraggingNode = false;
        this.draggedNode = null;
      }
      
      if (this.isDrawingLine) {
        this.isDrawingLine = false;
        
        // 查找目标端口
        // 如果找到并且类型相符，创建新的边
        // 实现略...
      }
    },
    selectNode(node) {
      this.selectedNode = node.id;
      this.selectedNodeData = { ...node };
    },
    saveNodeProperties() {
      const index = this.workflow.nodes.findIndex(n => n.id === this.selectedNode);
      if (index !== -1) {
        this.workflow.nodes[index] = { ...this.selectedNodeData };
        this.$message.success('保存成功');
      }
    },
    deleteSelectedNode() {
      if (!this.selectedNode) return;
      
      // 删除关联的边
      this.workflow.edges = this.workflow.edges.filter(edge => 
        edge.source !== this.selectedNode && edge.target !== this.selectedNode
      );
      
      // 删除节点
      this.workflow.nodes = this.workflow.nodes.filter(node => 
        node.id !== this.selectedNode
      );
      
      this.selectedNode = null;
      this.selectedNodeData = null;
    },
    calculatePath(edge) {
      // 计算连线路径
      // 实现略...
      return "M0,0 L100,100"; // 占位
    },
    async saveWorkflow() {
      try {
        await this.$http.patch(`/api/experiments/${this.experimentId}/`, {
          workflow_data: this.workflow
        });
        this.$message.success('工作流保存成功');
      } catch (error) {
        console.error('保存工作流失败', error);
        this.$message.error('保存工作流失败');
      }
    },
    async runWorkflow() {
      try {
        this.isRunning = true;
        
        // 更新所有节点状态为idle
        this.workflow.nodes.forEach(node => {
          node.status = 'idle';
        });
        
        // 调用后端API运行工作流
        const response = await this.$http.post(`/api/experiments/${this.experimentId}/run/`);
        const taskId = response.data.task_id;
        
        // 开始轮询结果
        this.pollWorkflowStatus(taskId);
      } catch (error) {
        console.error('运行工作流失败', error);
        this.$message.error('运行工作流失败');
        this.isRunning = false;
      }
    },
    stopWorkflow() {
      // 停止工作流
      this.isRunning = false;
      // 实际实现需调用后端API
    },
    async pollWorkflowStatus(taskId) {
      // 定时轮询工作流状态
      // 实现略...
    }
  }
};
</script>

<style scoped>
.workflow-editor {
  display: flex;
  height: calc(100vh - 120px);
}

.component-panel {
  width: 250px;
  border-right: 1px solid #ddd;
  padding: 10px;
  overflow-y: auto;
}

.workflow-canvas {
  flex: 1;
  position: relative;
  background-color: #f5f5f5;
  overflow: hidden;
}

.property-panel {
  width: 300px;
  border-left: 1px solid #ddd;
  padding: 10px;
  overflow-y: auto;
}

.component-item {
  padding: 8px;
  margin: 5px 0;
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: move;
}

.component-item:hover {
  background-color: #f0f0f0;
}

.node {
  position: absolute;
  width: 150px;
  background-color: white;
  border: 1px solid #999;
  border-radius: 4px;
  padding: 10px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  cursor: move;
  z-index: 10;
}

.node.selected {
  border: 2px solid #1890ff;
}

.node-header {
  font-weight: bold;
  margin-bottom: 5px;
}

.node-status {
  font-size: 12px;
  padding: 2px 4px;
  border-radius: 2px;
  margin-bottom: 5px;
}

.node-status.idle {
  background-color: #e6f7ff;
  color: #1890ff;
}

.node-status.running {
  background-color: #fff7e6;
  color: #fa8c16;
}

.node-status.completed {
  background-color: #f6ffed;
  color: #52c41a;
}

.node-status.failed {
  background-color: #fff1f0;
  color: #f5222d;
}

.node-ports {
  display: flex;
  justify-content: space-between;
}

.port {
  width: 10px;
  height: 10px;
  background-color: #1890ff;
  border-radius: 50%;
  margin: 5px;
  cursor: crosshair;
}

.input-ports {
  display: flex;
  flex-direction: column;
}

.output-ports {
  display: flex;
  flex-direction: column;
}

.toolbar {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 50px;
  background-color: #f0f0f0;
  border-top: 1px solid #ddd;
  display: flex;
  align-items: center;
  padding: 0 20px;
}

.toolbar button {
  margin-right: 10px;
  padding: 5px 15px;
}

.property-item {
  margin-bottom: 10px;
}

.property-item label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.code-editor-container {
  height: 300px;
  border: 1px solid #ddd;
}

.property-buttons {
  margin-top: 15px;
  display: flex;
  justify-content: space-between;
}

.delete-btn {
  background-color: #ff4d4f;
  color: white;
}
</style> 