#!/usr/bin/env python
"""
创建Django超级用户脚本
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meowsite.settings_production')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# 检查管理员用户是否存在
if User.objects.filter(username='admin').exists():
    print('EXIST')
else:
    # 创建管理员用户
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('CREATE')
