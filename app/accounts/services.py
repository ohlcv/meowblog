"""
账户服务模块 - 遵循模块化设计原则
负责处理登录相关的业务逻辑
"""
from django.contrib.auth import login
from django.conf import settings
import logging

# 获取日志记录器
logger = logging.getLogger('accounts')


class LoginService:
    """登录服务类 - 处理登录相关业务逻辑"""
    
    @staticmethod
    def handle_successful_login(request, user, remember_me=False):
        """处理成功登录的逻辑"""
        # 记录登录成功日志
        ip_address = request.META.get('REMOTE_ADDR', 'unknown')
        user_agent = request.META.get('HTTP_USER_AGENT', 'unknown')
        logger.info(f'用户登录成功: {user.username}, IP: {ip_address}, User-Agent: {user_agent[:100]}...')
        
        # 执行登录
        login(request, user)
        
        # 处理"记住我"功能
        if remember_me:
            # 设置会话过期时间为30天
            request.session.set_expiry(settings.REMEMBER_ME_DURATION)
            logger.info(f'用户 {user.username} 启用了"记住我"功能')
        else:
            # 使用默认会话过期时间（浏览器关闭时过期）
            request.session.set_expiry(0)
    
    @staticmethod
    def store_login_errors(request, form):
        """存储登录错误信息到session"""
        if form.errors:
            # 记录登录失败日志
            ip_address = request.META.get('REMOTE_ADDR', 'unknown')
            username = request.POST.get('username', 'unknown')
            logger.warning(f'登录失败: 用户名 {username}, IP: {ip_address}, 错误: {form.errors}')
            
            request.session['login_errors'] = {
                'field_errors': {field: errors for field, errors in form.errors.items()},
                'form_data': request.POST.dict()
            }
    
    @staticmethod
    def restore_login_errors(request, form_class):
        """从session恢复登录错误信息"""
        login_errors = request.session.pop('login_errors', None)
        if login_errors:
            # 使用存储的表单数据创建绑定表单
            form = form_class(request, data=login_errors['form_data'])
            # 设置为绑定状态但不验证
            form.is_bound = True
            form._errors = {}
            # 恢复错误信息
            for field, errors in login_errors['field_errors'].items():
                if field in form.fields or field is None:
                    form._errors[field] = form.error_class(errors)
            return form
        return None


class FormErrorHandler:
    """表单错误处理器 - 专门处理表单错误显示逻辑"""
    
    @staticmethod
    def create_clean_form(form_class, request=None):
        """创建一个干净的表单实例"""
        return form_class(request) if request else form_class()