import docker
import json
import uuid
import os
from datetime import datetime
import redis

class KernelManager:
    """Jupyter内核管理器"""
    def __init__(self):
        self.docker_client = docker.from_env()
        self.redis_client = redis.StrictRedis(host='redis', port=6379, db=0)
        self.kernels = {}
        
    def create_kernel(self, user_id, experiment_id):
        """为用户创建一个新的Jupyter内核"""
        kernel_id = str(uuid.uuid4())
        container_name = f"kernel-{user_id}-{kernel_id}"
        
        # 创建容器
        container = self.docker_client.containers.run(
            "jupyter/datascience-notebook",
            detach=True,
            name=container_name,
            environment={
                "JUPYTER_ENABLE_LAB": "yes",
                "GRANT_SUDO": "yes"
            },
            volumes={
                f"/data/user_{user_id}": {"bind": "/home/jovyan/work", "mode": "rw"},
            },
            mem_limit="2g",
            cpu_count=2,
            network="platform_network"
        )
        
        # 存储内核信息
        kernel_info = {
            "kernel_id": kernel_id,
            "container_id": container.id,
            "user_id": user_id,
            "experiment_id": experiment_id,
            "created_at": datetime.now().isoformat(),
            "status": "running"
        }
        
        self.kernels[kernel_id] = kernel_info
        self.redis_client.set(f"kernel:{kernel_id}", json.dumps(kernel_info))
        
        return kernel_id
        
    def execute_code(self, kernel_id, code):
        """在指定内核中执行代码"""
        if kernel_id not in self.kernels:
            # 从Redis恢复内核信息
            kernel_info_str = self.redis_client.get(f"kernel:{kernel_id}")
            if kernel_info_str:
                self.kernels[kernel_id] = json.loads(kernel_info_str)
            else:
                raise Exception(f"Kernel {kernel_id} not found")
        
        container_id = self.kernels[kernel_id]["container_id"]
        container = self.docker_client.containers.get(container_id)
        
        # 将代码写入临时文件
        script_path = f"/tmp/script_{uuid.uuid4()}.py"
        with open(script_path, "w") as f:
            f.write(code)
        
        # 将文件复制到容器
        os.system(f"docker cp {script_path} {container_id}:/home/jovyan/script.py")
        
        # 执行代码并获取结果
        exec_result = container.exec_run(
            "python /home/jovyan/script.py",
            user="jovyan"
        )
        
        os.remove(script_path)
        
        return {
            "exit_code": exec_result.exit_code,
            "output": exec_result.output.decode('utf-8')
        }
        
    def terminate_kernel(self, kernel_id):
        """终止内核"""
        if kernel_id not in self.kernels:
            kernel_info_str = self.redis_client.get(f"kernel:{kernel_id}")
            if kernel_info_str:
                self.kernels[kernel_id] = json.loads(kernel_info_str)
            else:
                return False
        
        container_id = self.kernels[kernel_id]["container_id"]
        try:
            container = self.docker_client.containers.get(container_id)
            container.stop(timeout=5)
            container.remove()
            
            self.kernels[kernel_id]["status"] = "terminated"
            self.redis_client.set(f"kernel:{kernel_id}", json.dumps(self.kernels[kernel_id]))
            return True
        except:
            return False
