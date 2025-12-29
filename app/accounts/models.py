"""
用户模型模块
扩展Django用户模型，添加手机号、禁言、封禁等功能

模块级别变量：
    __version__: 模块版本号
    __author__: 模块作者
    __all__: 公开API列表
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# 信号处理器：当用户创建时自动创建UserProfile
from django.db.models.signals import post_save
from django.dispatch import receiver

# 模块级别特殊变量 - 遵循PEP8规范
__version__ = '1.0.0'
__author__ = 'Meow Site Development Team'
__all__ = ['UserProfile']

class UserProfile(models.Model):
    """用户扩展信息模型"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # 显示名称字段 - 可随时修改
    displayname = models.CharField(max_length=50, blank=True, null=True, verbose_name='显示名称')
    
    # 手机号字段
    phone = models.CharField(max_length=11, blank=True, null=True, unique=True, verbose_name='手机号')
    
    # 禁言相关字段
    is_muted = models.BooleanField(default=False, verbose_name='是否禁言')
    mute_until = models.DateTimeField(null=True, blank=True, verbose_name='禁言结束时间')
    mute_reason = models.TextField(blank=True, verbose_name='禁言原因')
    
    # 封禁相关字段
    is_banned = models.BooleanField(default=False, verbose_name='是否封禁')
    ban_until = models.DateTimeField(null=True, blank=True, verbose_name='封禁结束时间')
    ban_reason = models.TextField(blank=True, verbose_name='封禁原因')
    
    # 管理记录
    banned_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='banned_users',
        verbose_name='封禁操作者'
    )
    muted_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='muted_users',
        verbose_name='禁言操作者'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'accounts'
        verbose_name = '用户资料'
        verbose_name_plural = '用户资料'

    def __str__(self):
        return f'{self.user.username} 的资料'
    
    @property
    def identifier(self):
        """获取用户数据库ID - 不可修改"""
        return self.user.id

    @property
    def is_currently_muted(self):
        """检查用户是否当前被禁言"""
        if not self.is_muted:
            return False
        if self.mute_until and timezone.now() > self.mute_until:
            # 禁言期已过，自动解除禁言
            self.is_muted = False
            self.mute_until = None
            self.save()
            return False
        return True

    @property
    def is_currently_banned(self):
        """检查用户是否当前被封禁"""
        if not self.is_banned:
            return False
        if self.ban_until and timezone.now() > self.ban_until:
            # 封禁期已过，自动解除封禁
            self.is_banned = False
            self.ban_until = None
            self.save()
            return False
        return True

    def mute_user(self, duration_hours=None, reason='', muted_by=None):
        """禁言用户"""
        self.is_muted = True
        self.mute_reason = reason
        self.muted_by = muted_by
        
        if duration_hours:
            self.mute_until = timezone.now() + timezone.timedelta(hours=duration_hours)
        else:
            self.mute_until = None  # 永久禁言
        
        self.save()

    def unmute_user(self):
        """解除禁言"""
        self.is_muted = False
        self.mute_until = None
        self.mute_reason = ''
        self.muted_by = None
        self.save()

    def ban_user(self, duration_days=None, reason='', banned_by=None):
        """封禁用户"""
        self.is_banned = True
        self.ban_reason = reason
        self.banned_by = banned_by
        
        if duration_days:
            self.ban_until = timezone.now() + timezone.timedelta(days=duration_days)
        else:
            self.ban_until = None  # 永久封禁
        
        self.save()

    def unban_user(self):
        """解除封禁"""
        self.is_banned = False
        self.ban_until = None
        self.ban_reason = ''
        self.banned_by = None
        self.save()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """用户创建时自动创建对应的UserProfile"""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """保存用户时同时保存UserProfile"""
    if hasattr(instance, 'profile'):
        instance.profile.save()