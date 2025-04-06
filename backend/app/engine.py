import json
import networkx as nx
from compute_engine.kernel_manager import KernelManager

class WorkflowEngine:
    """工作流执行引擎"""
    def __init__(self):
        self.kernel_manager = KernelManager()
        
    def execute_workflow(self, workflow_data, user_id, experiment_id):
        """执行整个工作流"""
        # 解析工作流
        nodes = workflow_data.get('nodes', [])
        edges = workflow_data.get('edges', [])
        
        # 创建有向图
        G = nx.DiGraph()
        
        # 添加节点
        for node in nodes:
            G.add_node(node['id'], data=node)
        
        # 添加边
        for edge in edges:
            G.add_edge(edge['source'], edge['target'])
        
        # 检查是否有环
        if not nx.is_directed_acyclic_graph(G):
            return {
                "success": False,
                "message": "工作流不是有向无环图，无法执行"
            }
        
        # 获取拓扑排序
        topological_order = list(nx.topological_sort(G))
        
        # 创建内核
        kernel_id = self.kernel_manager.create_kernel(user_id, experiment_id)
        
        results = {}
        # 按拓扑排序执行节点
        try:
            for node_id in topological_order:
                node_data = G.nodes[node_id]['data']
                component_code = node_data.get('code', '')
                
                # 准备输入
                input_vars = {}
                for pred in G.predecessors(node_id):
                    input_vars[pred] = results.get(pred, {})
                
                # 准备执行代码
                exec_code = f"""
# 输入数据
input_data = {json.dumps(input_vars)}
                
# 组件代码
{component_code}
                
# 输出结果
print("<<<RESULT_START>>>")
print(json.dumps(result))
print("<<<RESULT_END>>>")
"""
                
                # 执行代码
                execution_result = self.kernel_manager.execute_code(kernel_id, exec_code)
                
                if execution_result['exit_code'] != 0:
                    return {
                        "success": False,
                        "message": f"节点 {node_id} 执行失败",
                        "error": execution_result['output']
                    }
                
                # 解析结果
                output = execution_result['output']
                result_start = output.find("<<<RESULT_START>>>") + len("<<<RESULT_START>>>")
                result_end = output.find("<<<RESULT_END>>>")
                
                if result_start > 0 and result_end > result_start:
                    result_json = output[result_start:result_end].strip()
                    results[node_id] = json.loads(result_json)
                else:
                    results[node_id] = {"output": output}
            
            return {
                "success": True,
                "results": results
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }
        finally:
            # 终止内核
            self.kernel_manager.terminate_kernel(kernel_id)
