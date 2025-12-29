# Django 核心导入
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

# 本地应用导入
from .models import UserProfile

class UserStatusMiddleware(MiddlewareMixin):
    """
    用户状态检查中间件
    检查用户是否被封禁或禁言，并相应地限制其行为
    """
    
    def process_request(self, request):
        # 只对已登录用户进行检查
        if not request.user.is_authenticated:
            return None
            
        # 超级管理员不受限制
        if request.user.is_superuser:
            return None
            
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            # 如果用户没有profile，创建一个
            profile = UserProfile.objects.create(user=request.user)
        
        # 检查用户是否被封禁
        if profile.is_currently_banned:
            # 如果是AJAX请求，返回JSON响应
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': f'您的账户已被封禁。原因：{profile.ban_reason}',
                    'banned': True
                })
            
            # 对于POST请求（表单提交），显示错误信息并重定向
            if request.method == 'POST':
                messages.error(request, f'您的账户已被封禁，无法执行此操作。原因：{profile.ban_reason}')
                return redirect('homepage')
            
            # 对于GET请求，显示封禁页面
            return render(request, 'accounts/banned.html', {
                'ban_reason': profile.ban_reason,
                'ban_until': profile.ban_until,
                'banned_by': profile.banned_by
            })
        
        # 检查用户是否被禁言（只限制评论和发帖功能）
        if profile.is_currently_muted:
            # 禁言用户无法访问评论和发帖相关的URL
            forbidden_paths = [
                '/blog/post/create',
                '/accounts/post/create',
                '/accounts/manuscripts',
                '/accounts/category',
            ]
            
            # 检查是否是被禁止的路径
            for path in forbidden_paths:
                if request.path.startswith(path):
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': False,
                            'message': f'您已被禁言，无法发表内容。原因：{profile.mute_reason}',
                            'muted': True
                        })
                    
                    messages.error(request, f'您已被禁言，无法发表内容。原因：{profile.mute_reason}')
                    return redirect('homepage')
        
        return None