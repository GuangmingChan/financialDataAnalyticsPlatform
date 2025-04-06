from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Experiment, ExperimentTemplate, Component
from .serializers import ExperimentSerializer, ExperimentTemplateSerializer, ComponentSerializer
from workflow_engine.engine import WorkflowEngine
import json

class ExperimentViewSet(viewsets.ModelViewSet):
    """实验视图集"""
    serializer_class = ExperimentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Experiment.objects.filter(creator=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)
        
    @action(detail=True, methods=['post'])
    def run(self, request, pk=None):
        """运行实验"""
        experiment = self.get_object()
        workflow_data = experiment.workflow_data
        
        # 更新实验状态
        experiment.status = 'running'
        experiment.save()
        
        # 创建工作流引擎
        workflow_engine = WorkflowEngine()
        
        # 异步执行工作流
        from .tasks import execute_workflow_task
        task = execute_workflow_task.delay(
            workflow_data, 
            request.user.id, 
            str(experiment.id)
        )
        
        return Response({
            "success": True,
            "message": "实验开始运行",
            "task_id": task.id
        })
        
    @action(detail=True, methods=['get'])
    def result(self, request, pk=None):
        """获取实验结果"""
        experiment = self.get_object()
        
        return Response({
            "id": experiment.id,
            "name": experiment.name,
            "status": experiment.status,
            "workflow_data": experiment.workflow_data,
            "created_at": experiment.created_at,
            "updated_at": experiment.updated_at
        })

class ExperimentTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """实验模板视图集"""
    queryset = ExperimentTemplate.objects.filter(is_public=True)
    serializer_class = ExperimentTemplateSerializer
    
    @action(detail=True, methods=['post'])
    def create_experiment(self, request, pk=None):
        """基于模板创建实验"""
        template = self.get_object()
        
        experiment = Experiment.objects.create(
            name=f"{template.name} - 副本",
            description=template.description,
            category=template.category,
            template_id=template,
            creator=request.user,
            workflow_data=template.workflow_data,
            status='draft'
        )
        
        return Response(ExperimentSerializer(experiment).data)

class ComponentViewSet(viewsets.ModelViewSet):
    """组件视图集"""
    serializer_class = ComponentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # 显示系统组件和用户自己创建的组件
        return Component.objects.filter(is_system=True) | Component.objects.filter(creator=self.request.user)
        
    def perform_create(self, serializer):
        serializer.save(creator=self.request.user, is_system=False)
