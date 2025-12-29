"""
账户表单模块
提供用户注册、登录、资料修改等表单功能

模块级别变量：
    __version__: 模块版本号
    __author__: 模块作者
    __all__: 公开API列表
"""
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django import forms
from .models import UserProfile
import re

# 模块级别特殊变量 - 遵循PEP8规范
__version__ = '1.0.0'
__author__ = 'Meow Site Development Team'
__all__ = [
    'CustomUserCreationForm',
    'UserProfileForm', 
    'AdminUserProfileForm',
    'CustomPasswordChangeForm',
    'CustomAuthenticationForm'
]

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label='邮箱地址',
        help_text='',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    displayname = forms.CharField(
        max_length=50,
        required=False,
        label='显示名称',
        help_text='可选，用于显示，可随时修改',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入显示名称（可选）'})
    )
    phone = forms.CharField(
        max_length=11,
        required=True,
        label='手机号',
        help_text='',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入11位手机号'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['username'].label = '标识名（用户名）'
        self.fields['username'].help_text = '用于登录，注册后不可修改'
        self.fields['password1'].label = '密码'
        self.fields['password1'].help_text = ''
        self.fields['password2'].label = '确认密码'
        self.fields['password2'].help_text = ''
        
        # 为所有字段添加CSS类
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        
        # 为密码字段添加占位符
        self.fields['password1'].widget.attrs['placeholder'] = '请输入密码'
        self.fields['password2'].widget.attrs['placeholder'] = '请再次输入密码'
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('这个用户名已经被使用了，请选择其他用户名。')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('这个邮箱地址已经被使用了，请使用其他邮箱。')
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # 手机号格式验证
            if not re.match(r'^1[3-9]\d{9}$', phone):
                raise forms.ValidationError('请输入11位的正确手机号码。')
            # 手机号唯一性验证
            if UserProfile.objects.filter(phone=phone).exists():
                raise forms.ValidationError('这个手机号已经被使用了，请使用其他手机号。')
        return phone
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # 保存显示名称和手机号到UserProfile
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.displayname = self.cleaned_data.get('displayname')
            profile.phone = self.cleaned_data.get('phone')
            profile.save()
        return user

# 用户信息修改表单
class UserProfileForm(forms.ModelForm):
    displayname = forms.CharField(
        max_length=50,
        required=False,
        label='显示名称',
        help_text='用于显示，可随时修改',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ['email']  # 只保留邮箱字段，移除first_name和last_name
        labels = {
            'email': '邮箱地址',
        }
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 初始化显示名称字段
        if self.instance and hasattr(self.instance, 'profile'):
            self.fields['displayname'].initial = self.instance.profile.displayname
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError('这个邮箱地址已经被使用了')
        return email
    
    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit and hasattr(user, 'profile'):
            # 保存显示名称到UserProfile
            user.profile.displayname = self.cleaned_data.get('displayname')
            user.profile.save()
        return user

# 管理员专用表单 - 允许修改用户名
class AdminUserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']  # 移除first_name和last_name字段
        labels = {
            'username': '用户名',
            'email': '邮箱地址',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
            raise forms.ValidationError('这个用户名已经被使用了')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError('这个邮箱地址已经被使用了')
        return email

# 自定义密码修改表单
class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].label = '当前密码'
        self.fields['new_password1'].label = '新密码'
        self.fields['new_password2'].label = '确认新密码'
        
        # 清空帮助文本
        for field in self.fields.values():
            field.help_text = ''
            field.widget.attrs['class'] = 'form-control'

# 基于Django AuthenticationForm的增强登录表单
class CustomAuthenticationForm(AuthenticationForm):
    # 覆盖用户名字段，支持多种登录方式
    username = forms.CharField(
        max_length=254,
        label='用户名/邮箱/手机号',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入用户名、邮箱或手机号'
        })
    )
    
    # 添加记住我功能
    remember_me = forms.BooleanField(
        required=False,
        initial=False,
        label='记住我（30天）',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    # 错误消息本地化
    error_messages = {
        'invalid_login': '用户名/邮箱/手机号或密码错误，请重新输入。',
        'inactive': '此账户已被禁用。',
    }
    
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        # 设置密码字段样式和标签
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '请输入密码'
        })
        self.fields['password'].label = '密码'
    
    def clean_username(self):
        """增强的用户名验证，支持多种登录方式"""
        username = self.cleaned_data.get('username')
        if not username:
            raise forms.ValidationError('请输入用户名、邮箱或手机号。')
        
        # 检查用户是否存在
        if not self._check_user_exists(username):
            raise forms.ValidationError('用户名、邮箱或手机号不存在。')
        
        return username
    
    def authenticate(self, username, password):
        """覆盖认证方法，支持多种登录方式"""
        # 使用统一的认证服务
        return self._multi_authenticate(username, password)
    
    def _multi_authenticate(self, username, password):
        """多种方式认证的具体实现"""
        # 1. 尝试用户名登录
        user = authenticate(self.request, username=username, password=password)
        if user:
            return user
        
        # 2. 尝试邮箱登录
        user = self._try_email_login(username, password)
        if user:
            return user
        
        # 3. 尝试手机号登录
        user = self._try_phone_login(username, password)
        if user:
            return user
        
        return None
    
    def _try_email_login(self, username, password):
        """尝试邮箱登录"""
        try:
            user_obj = User.objects.get(email=username)
            return authenticate(self.request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            return None
    
    def _try_phone_login(self, username, password):
        """尝试手机号登录"""
        try:
            profile = UserProfile.objects.get(phone=username)
            return authenticate(self.request, username=profile.user.username, password=password)
        except UserProfile.DoesNotExist:
            return None
    
    def clean(self):
        """表单级验证，使用Django AuthenticationForm的基础架构"""
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username is not None and password:
            # 使用我们的增强认证方法
            self.user_cache = self.authenticate(username, password)
            if self.user_cache is None:
                # 认证失败，在密码字段显示错误
                self.add_error('password', '密码错误。')
            else:
                # 检查用户状态
                self.confirm_login_allowed(self.user_cache)
        
        return self.cleaned_data
    
    def confirm_login_allowed(self, user):
        """检查用户登录权限"""
        # 调用父类方法检查基本状态
        super().confirm_login_allowed(user)
        
        # 检查用户是否被封禁
        if hasattr(user, 'profile') and user.profile.is_currently_banned:
            raise forms.ValidationError(
                '账户已被禁用或封禁。',
                code='banned',
            )
    
    def _check_user_exists(self, username):
        """检查用户是否存在（用户名/邮箱/手机号）"""
        
        # 检查用户名
        if User.objects.filter(username=username).exists():
            return True
        
        # 检查邮箱
        if User.objects.filter(email=username).exists():
            return True
        
        # 检查手机号
        if UserProfile.objects.filter(phone=username).exists():
            return True
        
        return False