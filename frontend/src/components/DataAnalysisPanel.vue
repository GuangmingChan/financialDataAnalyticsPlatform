<template>
  <div class="data-analysis-panel">
    <el-tabs v-model="activeTab" type="border-card">
      <!-- 数据预览 -->
      <el-tab-pane label="数据预览" name="preview">
        <div class="panel-content">
          <div class="controls">
            <el-select v-model="selectedDataSource" placeholder="选择数据源" @change="loadData">
              <el-option
                v-for="source in dataSources"
                :key="source.id"
                :label="source.name"
                :value="source.id">
              </el-option>
            </el-select>
            <el-button type="primary" size="small" @click="refreshData">刷新</el-button>
          </div>
          
          <div v-if="loading" class="loading-container">
            <el-skeleton :rows="5" animated />
          </div>
          
          <div v-else>
            <div class="data-stats">
              <el-card shadow="hover" class="stat-card">
                <div slot="header">数据基本信息</div>
                <div v-if="currentData">
                  <p><strong>行数:</strong> {{ dataStats.rows }}</p>
                  <p><strong>列数:</strong> {{ dataStats.columns }}</p>
                  <p><strong>缺失值:</strong> {{ dataStats.missing }}</p>
                </div>
              </el-card>
            </div>
            
            <el-table
              v-if="currentData"
              :data="currentData.slice(0, previewRows)"
              border
              style="width: 100%"
              height="400"
              :cell-class-name="highlightMissingValues">
              <el-table-column
                v-for="column in dataColumns"
                :key="column"
                :prop="column"
                :label="column"
                sortable>
              </el-table-column>
            </el-table>
            
            <div v-else class="no-data">
              <p>请选择数据源以加载数据</p>
            </div>
          </div>
        </div>
      </el-tab-pane>
      
      <!-- 数据探索 -->
      <el-tab-pane label="数据探索" name="explore">
        <div class="panel-content">
          <div class="controls">
            <el-select v-model="selectedColumn" placeholder="选择列">
              <el-option
                v-for="column in dataColumns"
                :key="column"
                :label="column"
                :value="column">
              </el-option>
            </el-select>
            
            <el-select v-model="selectedAnalysis" placeholder="选择分析方法">
              <el-option label="基本统计量" value="basic_stats"></el-option>
              <el-option label="分布图" value="distribution"></el-option>
              <el-option label="箱线图" value="boxplot"></el-option>
              <el-option label="时间序列" value="timeseries"></el-option>
            </el-select>
            
            <el-button type="primary" @click="runAnalysis">分析</el-button>
          </div>
          
          <div v-if="analysisLoading" class="loading-container">
            <el-skeleton :rows="3" animated />
          </div>
          
          <div v-else-if="analysisResult" class="analysis-result">
            <!-- 基本统计量 -->
            <el-card v-if="selectedAnalysis === 'basic_stats'" shadow="hover">
              <div slot="header">基本统计量分析 - {{ selectedColumn }}</div>
              <el-table
                :data="[analysisResult]"
                border
                style="width: 100%">
                <el-table-column prop="count" label="计数"></el-table-column>
                <el-table-column prop="mean" label="均值"></el-table-column>
                <el-table-column prop="std" label="标准差"></el-table-column>
                <el-table-column prop="min" label="最小值"></el-table-column>
                <el-table-column prop="q25" label="25%分位数"></el-table-column>
                <el-table-column prop="median" label="中位数"></el-table-column>
                <el-table-column prop="q75" label="75%分位数"></el-table-column>
                <el-table-column prop="max" label="最大值"></el-table-column>
              </el-table>
            </el-card>
            
            <!-- 分布图/直方图 -->
            <el-card v-else-if="selectedAnalysis === 'distribution'" shadow="hover">
              <div slot="header">分布分析 - {{ selectedColumn }}</div>
              <div class="chart-container" ref="distributionChart"></div>
            </el-card>
            
            <!-- 箱线图 -->
            <el-card v-else-if="selectedAnalysis === 'boxplot'" shadow="hover">
              <div slot="header">箱线图分析 - {{ selectedColumn }}</div>
              <div class="chart-container" ref="boxplotChart"></div>
            </el-card>
            
            <!-- 时间序列图 -->
            <el-card v-else-if="selectedAnalysis === 'timeseries'" shadow="hover">
              <div slot="header">时间序列分析 - {{ selectedColumn }}</div>
              <div class="chart-container" ref="timeseriesChart"></div>
            </el-card>
          </div>
        </div>
      </el-tab-pane>
      
      <!-- 数据清洗 -->
      <el-tab-pane label="数据清洗" name="clean">
        <div class="panel-content">
          <div class="controls">
            <el-select v-model="cleaningAction" placeholder="选择操作">
              <el-option label="处理缺失值" value="missing_values"></el-option>
              <el-option label="处理异常值" value="outliers"></el-option>
              <el-option label="数据标准化" value="normalize"></el-option>
              <el-option label="特征编码" value="encode"></el-option>
            </el-select>
            
            <template v-if="cleaningAction === 'missing_values'">
              <el-select v-model="missingStrategy" placeholder="处理策略">
                <el-option label="删除" value="drop"></el-option>
                <el-option label="均值填充" value="mean"></el-option>
                <el-option label="中位数填充" value="median"></el-option>
                <el-option label="众数填充" value="mode"></el-option>
                <el-option label="固定值填充" value="constant"></el-option>
              </el-select>
              
              <el-input 
                v-if="missingStrategy === 'constant'" 
                v-model="constantValue" 
                placeholder="填充值">
              </el-input>
            </template>
            
            <el-button type="primary" @click="applyDataCleaning">应用</el-button>
          </div>
          
          <div v-if="cleaningLoading" class="loading-container">
            <el-skeleton :rows="3" animated />
          </div>
          
          <div v-else-if="cleaningResult" class="cleaning-result">
            <el-alert
              :title="cleaningResult.message"
              :type="cleaningResult.success ? 'success' : 'error'"
              :description="cleaningResult.details"
              show-icon>
            </el-alert>
            
            <el-table
              v-if="cleaningResult.previewData"
              :data="cleaningResult.previewData"
              border
              style="width: 100%; margin-top: 20px;"
              height="300">
              <el-table-column
                v-for="column in Object.keys(cleaningResult.previewData[0] || {})"
                :key="column"
                :prop="column"
                :label="column">
              </el-table-column>
            </el-table>
            
            <div class="action-buttons">
              <el-button @click="downloadCleanedData" type="success" :disabled="!cleaningResult.success">
                下载清洗后数据
              </el-button>
              <el-button @click="applyAndContinue" type="primary" :disabled="!cleaningResult.success">
                应用并继续
              </el-button>
            </div>
          </div>
        </div>
      </el-tab-pane>
      
      <!-- 可视化 -->
      <el-tab-pane label="可视化" name="visualize">
        <div class="panel-content">
          <div class="controls">
            <el-select v-model="visualizationType" placeholder="选择图表类型">
              <el-option label="折线图" value="line"></el-option>
              <el-option label="柱状图" value="bar"></el-option>
              <el-option label="散点图" value="scatter"></el-option>
              <el-option label="饼图" value="pie"></el-option>
              <el-option label="热力图" value="heatmap"></el-option>
            </el-select>
            
            <el-select 
              v-model="visualizationColumns" 
              multiple 
              collapse-tags 
              placeholder="选择数据列">
              <el-option
                v-for="column in dataColumns"
                :key="column"
                :label="column"
                :value="column">
              </el-option>
            </el-select>
            
            <el-button type="primary" @click="generateVisualization">生成图表</el-button>
          </div>
          
          <div v-if="visualizationLoading" class="loading-container">
            <el-skeleton :rows="5" animated />
          </div>
          
          <div v-else-if="visualizationResult" class="visualization-result">
            <div class="chart-container" ref="visualizationChart"></div>
            
            <div class="action-buttons">
              <el-button @click="exportVisualization" type="success">
                导出图表
              </el-button>
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
import axios from 'axios';
import * as echarts from 'echarts';

export default {
  name: 'DataAnalysisPanel',
  props: {
    experimentId: {
      type: [String, Number],
      required: false
    }
  },
  data() {
    return {
      activeTab: 'preview',
      dataSources: [
        { id: 'stock', name: '股票数据' },
        { id: 'bank', name: '银行信贷数据' },
        { id: 'insurance', name: '保险数据' }
      ],
      selectedDataSource: '',
      loading: false,
      currentData: null,
      previewRows: 10,
      dataColumns: [],
      dataStats: { rows: 0, columns: 0, missing: 0 },
      
      // 数据探索
      selectedColumn: '',
      selectedAnalysis: 'basic_stats',
      analysisLoading: false,
      analysisResult: null,
      
      // 数据清洗
      cleaningAction: 'missing_values',
      missingStrategy: 'mean',
      constantValue: '0',
      cleaningLoading: false,
      cleaningResult: null,
      
      // 可视化
      visualizationType: 'line',
      visualizationColumns: [],
      visualizationLoading: false,
      visualizationResult: null,
      
      // 图表实例
      distributionChart: null,
      boxplotChart: null,
      timeseriesChart: null,
      visualizationChart: null
    };
  },
  methods: {
    async loadData() {
      if (!this.selectedDataSource) return;
      
      this.loading = true;
      try {
        let endpoint = '';
        switch(this.selectedDataSource) {
          case 'stock':
            endpoint = '/api/v1/analysis/get_stock_data';
            break;
          case 'bank':
            endpoint = '/api/v1/analysis/get_credit_data';
            break;
          case 'insurance':
            endpoint = '/api/v1/analysis/get_car_insurance_data';
            break;
        }
        
        const response = await axios.get(endpoint);
        this.currentData = response.data;
        
        if (this.currentData && this.currentData.length > 0) {
          this.dataColumns = Object.keys(this.currentData[0]);
          this.calculateDataStats();
        }
      } catch (error) {
        this.$message.error('加载数据失败: ' + error.message);
      } finally {
        this.loading = false;
      }
    },
    
    refreshData() {
      this.loadData();
    },
    
    calculateDataStats() {
      if (!this.currentData) return;
      
      const rows = this.currentData.length;
      const columns = this.dataColumns.length;
      
      let missingCount = 0;
      this.currentData.forEach(row => {
        Object.values(row).forEach(value => {
          if (value === null || value === undefined || value === '') {
            missingCount++;
          }
        });
      });
      
      this.dataStats = {
        rows,
        columns,
        missing: missingCount
      };
    },
    
    highlightMissingValues({ row, column }) {
      const value = row[column.property];
      if (value === null || value === undefined || value === '') {
        return 'missing-value-cell';
      }
      return '';
    },
    
    // 数据探索方法
    async runAnalysis() {
      if (!this.selectedColumn || !this.selectedAnalysis || !this.currentData) return;
      
      this.analysisLoading = true;
      try {
        // 后端API调用
        const response = await axios.post('/api/v1/analysis/get_data_basic_stats', {
          data: this.currentData,
          columns: [this.selectedColumn]
        });
        
        this.analysisResult = response.data[this.selectedColumn];
        
        // 渲染图表
        this.$nextTick(() => {
          if (this.selectedAnalysis === 'distribution') {
            this.renderDistributionChart();
          } else if (this.selectedAnalysis === 'boxplot') {
            this.renderBoxplotChart();
          } else if (this.selectedAnalysis === 'timeseries') {
            this.renderTimeseriesChart();
          }
        });
      } catch (error) {
        this.$message.error('分析失败: ' + error.message);
      } finally {
        this.analysisLoading = false;
      }
    },
    
    renderDistributionChart() {
      if (this.distributionChart) {
        this.distributionChart.dispose();
      }
      
      const chartDom = this.$refs.distributionChart;
      this.distributionChart = echarts.init(chartDom);
      
      const data = this.currentData.map(item => parseFloat(item[this.selectedColumn])).filter(val => !isNaN(val));
      
      const option = {
        title: {
          text: `${this.selectedColumn} 分布图`,
          left: 'center'
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        xAxis: {
          type: 'category',
          data: this.generateHistogramBins(data, 10)
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            data: this.calculateHistogram(data, 10),
            type: 'bar'
          }
        ]
      };
      
      this.distributionChart.setOption(option);
    },
    
    generateHistogramBins(data, binCount) {
      const min = Math.min(...data);
      const max = Math.max(...data);
      const step = (max - min) / binCount;
      
      return Array.from({ length: binCount }, (_, i) => {
        const binStart = min + i * step;
        const binEnd = min + (i + 1) * step;
        return `${binStart.toFixed(2)}-${binEnd.toFixed(2)}`;
      });
    },
    
    calculateHistogram(data, binCount) {
      const min = Math.min(...data);
      const max = Math.max(...data);
      const step = (max - min) / binCount;
      
      const bins = Array(binCount).fill(0);
      
      data.forEach(value => {
        const binIndex = Math.min(Math.floor((value - min) / step), binCount - 1);
        bins[binIndex]++;
      });
      
      return bins;
    },
    
    renderBoxplotChart() {
      if (this.boxplotChart) {
        this.boxplotChart.dispose();
      }
      
      const chartDom = this.$refs.boxplotChart;
      this.boxplotChart = echarts.init(chartDom);
      
      const data = this.currentData.map(item => parseFloat(item[this.selectedColumn])).filter(val => !isNaN(val));
      
      // 计算箱线图数据
      data.sort((a, b) => a - b);
      const len = data.length;
      const q1 = data[Math.floor(len * 0.25)];
      const median = data[Math.floor(len * 0.5)];
      const q3 = data[Math.floor(len * 0.75)];
      const iqr = q3 - q1;
      const min = Math.max(q1 - 1.5 * iqr, data[0]);
      const max = Math.min(q3 + 1.5 * iqr, data[len - 1]);
      
      const boxplotData = [[min, q1, median, q3, max]];
      
      const option = {
        title: {
          text: `${this.selectedColumn} 箱线图`,
          left: 'center'
        },
        tooltip: {
          trigger: 'item',
          axisPointer: {
            type: 'shadow'
          }
        },
        xAxis: {
          type: 'category',
          data: [this.selectedColumn]
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            name: 'boxplot',
            type: 'boxplot',
            data: boxplotData
          }
        ]
      };
      
      this.boxplotChart.setOption(option);
    },
    
    renderTimeseriesChart() {
      if (this.timeseriesChart) {
        this.timeseriesChart.dispose();
      }
      
      const chartDom = this.$refs.timeseriesChart;
      this.timeseriesChart = echarts.init(chartDom);
      
      // 假设数据中有日期字段
      const dateColumn = this.dataColumns.find(col => 
        col.toLowerCase().includes('date') || 
        col.toLowerCase().includes('time')
      ) || 'index';
      
      let xData;
      let yData;
      
      if (dateColumn === 'index') {
        xData = this.currentData.map((_, i) => i + 1);
      } else {
        xData = this.currentData.map(item => item[dateColumn]);
      }
      
      yData = this.currentData.map(item => parseFloat(item[this.selectedColumn])).filter(val => !isNaN(val));
      
      const option = {
        title: {
          text: `${this.selectedColumn} 时间序列图`,
          left: 'center'
        },
        tooltip: {
          trigger: 'axis'
        },
        xAxis: {
          type: 'category',
          data: xData
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            data: yData,
            type: 'line',
            smooth: true
          }
        ]
      };
      
      this.timeseriesChart.setOption(option);
    },
    
    // 数据清洗方法
    async applyDataCleaning() {
      if (!this.currentData || !this.cleaningAction) return;
      
      this.cleaningLoading = true;
      try {
        let endpoint = '';
        let params = {};
        
        switch(this.cleaningAction) {
          case 'missing_values':
            endpoint = '/api/v1/analysis/handle_missing_values';
            params = {
              data: this.currentData,
              strategy: this.missingStrategy
            };
            if (this.missingStrategy === 'constant') {
              params.fill_value = this.constantValue;
            }
            break;
          case 'outliers':
            endpoint = '/api/v1/analysis/handle_outliers';
            params = {
              data: this.currentData
            };
            break;
          case 'normalize':
            endpoint = '/api/v1/analysis/normalize_data';
            params = {
              data: this.currentData,
              method: 'minmax'
            };
            break;
          case 'encode':
            endpoint = '/api/v1/analysis/encode_categorical';
            params = {
              data: this.currentData,
              method: 'onehot'
            };
            break;
        }
        
        const response = await axios.post(endpoint, params);
        
        this.cleaningResult = {
          success: true,
          message: '数据处理成功',
          details: `共处理 ${this.currentData.length} 行数据`,
          previewData: response.data.slice(0, 10)
        };
      } catch (error) {
        this.cleaningResult = {
          success: false,
          message: '数据处理失败',
          details: error.message
        };
      } finally {
        this.cleaningLoading = false;
      }
    },
    
    downloadCleanedData() {
      if (!this.cleaningResult || !this.cleaningResult.success) return;
      
      const dataStr = JSON.stringify(this.cleaningResult.previewData);
      const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
      
      const exportFileDefaultName = `cleaned_data_${this.selectedDataSource}_${Date.now()}.json`;
      
      const linkElement = document.createElement('a');
      linkElement.setAttribute('href', dataUri);
      linkElement.setAttribute('download', exportFileDefaultName);
      linkElement.click();
    },
    
    applyAndContinue() {
      if (!this.cleaningResult || !this.cleaningResult.success) return;
      
      // 更新当前数据为清洗后的数据
      this.currentData = this.cleaningResult.previewData;
      this.cleaningResult = null;
      this.calculateDataStats();
      
      this.$message.success('已应用清洗结果到当前数据');
    },
    
    // 可视化方法
    async generateVisualization() {
      if (!this.currentData || !this.visualizationType || this.visualizationColumns.length === 0) {
        this.$message.warning('请选择图表类型和数据列');
        return;
      }
      
      this.visualizationLoading = true;
      try {
        const response = await axios.post('/api/v1/analysis/generate_data_visualization', {
          data: this.currentData,
          visualization_type: this.visualizationType,
          columns: this.visualizationColumns
        });
        
        this.visualizationResult = response.data;
        
        this.$nextTick(() => {
          this.renderVisualizationChart();
        });
      } catch (error) {
        this.$message.error('生成图表失败: ' + error.message);
      } finally {
        this.visualizationLoading = false;
      }
    },
    
    renderVisualizationChart() {
      if (this.visualizationChart) {
        this.visualizationChart.dispose();
      }
      
      const chartDom = this.$refs.visualizationChart;
      this.visualizationChart = echarts.init(chartDom);
      
      let option = {};
      
      switch(this.visualizationType) {
        case 'line':
          option = this.generateLineChartOption();
          break;
        case 'bar':
          option = this.generateBarChartOption();
          break;
        case 'scatter':
          option = this.generateScatterChartOption();
          break;
        case 'pie':
          option = this.generatePieChartOption();
          break;
        case 'heatmap':
          option = this.generateHeatmapOption();
          break;
      }
      
      this.visualizationChart.setOption(option);
    },
    
    generateLineChartOption() {
      const series = this.visualizationColumns.map(column => {
        return {
          name: column,
          type: 'line',
          data: this.currentData.map(item => parseFloat(item[column])).filter(val => !isNaN(val)),
          smooth: true
        };
      });
      
      return {
        title: {
          text: '多变量折线图',
          left: 'center'
        },
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: this.visualizationColumns,
          top: 30
        },
        xAxis: {
          type: 'category',
          data: this.currentData.map((_, i) => i + 1)
        },
        yAxis: {
          type: 'value'
        },
        series
      };
    },
    
    generateBarChartOption() {
      const series = this.visualizationColumns.map(column => {
        return {
          name: column,
          type: 'bar',
          data: this.currentData.map(item => parseFloat(item[column])).filter(val => !isNaN(val))
        };
      });
      
      return {
        title: {
          text: '多变量柱状图',
          left: 'center'
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        legend: {
          data: this.visualizationColumns,
          top: 30
        },
        xAxis: {
          type: 'category',
          data: this.currentData.map((_, i) => i + 1)
        },
        yAxis: {
          type: 'value'
        },
        series
      };
    },
    
    generateScatterChartOption() {
      if (this.visualizationColumns.length < 2) {
        this.$message.warning('散点图需要至少选择两个变量');
        return {};
      }
      
      const data = this.currentData.map(item => [
        parseFloat(item[this.visualizationColumns[0]]),
        parseFloat(item[this.visualizationColumns[1]])
      ]).filter(pair => !pair.some(isNaN));
      
      return {
        title: {
          text: `散点图: ${this.visualizationColumns[0]} vs ${this.visualizationColumns[1]}`,
          left: 'center'
        },
        tooltip: {
          trigger: 'item',
          formatter: function(params) {
            return `${params.seriesName}<br/>${params.value[0]}, ${params.value[1]}`;
          }
        },
        xAxis: {
          type: 'value',
          name: this.visualizationColumns[0]
        },
        yAxis: {
          type: 'value',
          name: this.visualizationColumns[1]
        },
        series: [
          {
            name: '数据点',
            type: 'scatter',
            data: data,
            symbolSize: 10
          }
        ]
      };
    },
    
    generatePieChartOption() {
      if (this.visualizationColumns.length < 1) {
        this.$message.warning('饼图需要至少选择一个变量');
        return {};
      }
      
      const column = this.visualizationColumns[0];
      const valueMap = {};
      
      this.currentData.forEach(item => {
        const value = item[column];
        if (value in valueMap) {
          valueMap[value]++;
        } else {
          valueMap[value] = 1;
        }
      });
      
      const data = Object.entries(valueMap).map(([name, value]) => ({ name, value }));
      
      return {
        title: {
          text: `饼图: ${column}`,
          left: 'center'
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b} : {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          left: 'left',
          data: Object.keys(valueMap)
        },
        series: [
          {
            name: column,
            type: 'pie',
            radius: '55%',
            center: ['50%', '60%'],
            data: data,
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            }
          }
        ]
      };
    },
    
    generateHeatmapOption() {
      if (this.visualizationColumns.length < 2) {
        this.$message.warning('热力图需要至少选择两个变量');
        return {};
      }
      
      // 创建相关性矩阵
      const matrix = [];
      const columns = this.visualizationColumns;
      
      columns.forEach((rowCol, i) => {
        const row = [];
        columns.forEach((colCol, j) => {
          // 简单计算相关系数
          const rowData = this.currentData.map(item => parseFloat(item[rowCol])).filter(val => !isNaN(val));
          const colData = this.currentData.map(item => parseFloat(item[colCol])).filter(val => !isNaN(val));
          
          const correlation = this.calculateCorrelation(rowData, colData);
          row.push([i, j, correlation.toFixed(2)]);
        });
        matrix.push(...row);
      });
      
      return {
        title: {
          text: '相关性热力图',
          left: 'center'
        },
        tooltip: {
          position: 'top',
          formatter: function (params) {
            return `${columns[params.value[0]]} 和 ${columns[params.value[1]]} 的相关性: ${params.value[2]}`;
          }
        },
        grid: {
          height: '50%',
          top: '10%'
        },
        xAxis: {
          type: 'category',
          data: columns,
          splitArea: {
            show: true
          }
        },
        yAxis: {
          type: 'category',
          data: columns,
          splitArea: {
            show: true
          }
        },
        visualMap: {
          min: -1,
          max: 1,
          calculable: true,
          orient: 'horizontal',
          left: 'center',
          bottom: '15%',
          inRange: {
            color: ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
          }
        },
        series: [{
          name: '相关性',
          type: 'heatmap',
          data: matrix,
          label: {
            show: true
          },
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }]
      };
    },
    
    calculateCorrelation(x, y) {
      if (x.length !== y.length || x.length === 0) return 0;
      
      const n = x.length;
      
      // 计算均值
      const xMean = x.reduce((a, b) => a + b, 0) / n;
      const yMean = y.reduce((a, b) => a + b, 0) / n;
      
      // 计算分子 (协方差)
      let numerator = 0;
      for (let i = 0; i < n; i++) {
        numerator += (x[i] - xMean) * (y[i] - yMean);
      }
      
      // 计算分母 (标准差的乘积)
      let xSS = 0;
      let ySS = 0;
      for (let i = 0; i < n; i++) {
        xSS += Math.pow(x[i] - xMean, 2);
        ySS += Math.pow(y[i] - yMean, 2);
      }
      
      const denominator = Math.sqrt(xSS * ySS);
      
      return denominator === 0 ? 0 : numerator / denominator;
    },
    
    exportVisualization() {
      if (!this.visualizationChart) return;
      
      const url = this.visualizationChart.getDataURL();
      
      const link = document.createElement('a');
      link.download = `visualization_${this.visualizationType}_${Date.now()}.png`;
      link.href = url;
      link.click();
    }
  },
  mounted() {
    if (this.experimentId) {
      this.dataSources.push({ id: 'experiment', name: '实验数据' });
    }
  },
  beforeDestroy() {
    // 销毁所有图表实例
    [this.distributionChart, this.boxplotChart, this.timeseriesChart, this.visualizationChart].forEach(chart => {
      if (chart) {
        chart.dispose();
      }
    });
  }
};
</script>

<style scoped>
.data-analysis-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.panel-content {
  padding: 15px;
  height: 100%;
  overflow-y: auto;
}

.controls {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center;
}

.data-stats {
  margin-bottom: 20px;
  display: flex;
  gap: 15px;
}

.stat-card {
  width: 200px;
}

.missing-value-cell {
  background-color: rgba(245, 108, 108, 0.1);
}

.loading-container {
  margin: 20px 0;
}

.no-data {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  border: 1px dashed #ccc;
  border-radius: 4px;
}

.chart-container {
  height: 400px;
  width: 100%;
}

.action-buttons {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.analysis-result, .cleaning-result, .visualization-result {
  margin-top: 20px;
}
</style> 