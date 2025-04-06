from django.db import models
from django.contrib.auth.models import User
import uuid

class Experiment(models.Model):
    """实验模型"""
    CATEGORY_CHOICES = [
        ('bank', '银行模块'),
        ('securities', '证券模块'),
        ('insurance', '保险模块'),
    ]
    
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('running', '运行中'),
        ('completed', '已完成'),
        ('failed', '失败'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('实验名称', max_length=100)
    description = models.TextField('实验描述', blank=True)
    category = models.CharField('实验类别', max_length=20, choices=CATEGORY_CHOICES)
    template_id = models.ForeignKey('ExperimentTemplate', on_delete=models.SET_NULL, null=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='experiments')
    workflow_data = models.JSONField('工作流数据', default=dict)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '实验'
        verbose_name_plural = '实验'
        ordering = ['-updated_at']
        
    def __str__(self):
        return self.name
        
class ExperimentTemplate(models.Model):
    """实验模板模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('模板名称', max_length=100)
    description = models.TextField('模板描述', blank=True)
    category = models.CharField('模板类别', max_length=20, choices=Experiment.CATEGORY_CHOICES)
    workflow_data = models.JSONField('工作流数据', default=dict)
    is_public = models.BooleanField('是否公开', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '实验模板'
        verbose_name_plural = '实验模板'
        
    def __str__(self):
        return self.name
        
class Component(models.Model):
    """算法组件模型"""
    COMPONENT_TYPE_CHOICES = [
        ('data_prep', '数据准备'),
        ('data_explore', '数据探索'),
        ('data_clean', '数据清洗'),
        ('feature_eng', '特征工程'),
        ('modeling', '建模分析'),
        ('evaluation', '模型评价'),
        ('visualization', '可视化'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('组件名称', max_length=100)
    component_type = models.CharField('组件类型', max_length=20, choices=COMPONENT_TYPE_CHOICES)
    description = models.TextField('组件描述', blank=True)
    code = models.TextField('组件代码')
    is_system = models.BooleanField('是否系统组件', default=False)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='components', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '算法组件'
        verbose_name_plural = '算法组件'
