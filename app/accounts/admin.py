from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

# 创建内联管理类，将UserProfile嵌入到User管理页面
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    fk_name = 'user'  # 指定使用user字段作为外键关系
    can_delete = False
    verbose_name = '用户资料'
    verbose_name_plural = '用户资料'
    fields = ('phone', 'is_muted', 'mute_until', 'mute_reason', 'is_banned', 'ban_until', 'ban_reason', 'banned_by', 'muted_by')
    readonly_fields = ('created_at', 'updated_at')

# 扩展User管理类
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    
    # 在用户列表中添加手机号显示
    def get_phone(self, obj):
        return obj.profile.phone if hasattr(obj, 'profile') else '-'
    get_phone.short_description = '手机号'
    get_phone.admin_order_field = 'profile__phone'
    
    # 在用户列表中添加状态显示
    def get_status(self, obj):
        if hasattr(obj, 'profile'):
            if obj.profile.is_banned:
                return '封禁'
            elif obj.profile.is_muted:
                return '禁言'
            else:
                return '正常'
        return '正常'
    get_status.short_description = '状态'
    get_status.admin_order_field = 'profile__is_banned'
    
    # 重写list_display以包含新字段
    list_display = BaseUserAdmin.list_display + ('get_phone', 'get_status')
    list_filter = BaseUserAdmin.list_filter + ('profile__is_banned', 'profile__is_muted')

# 重新注册User模型
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# 单独注册UserProfile模型（可选）
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'is_muted', 'is_banned', 'created_at']
    list_filter = ['is_muted', 'is_banned', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'phone')
        }),
        ('禁言管理', {
            'fields': ('is_muted', 'mute_until', 'mute_reason', 'muted_by'),
            'classes': ('collapse',)
        }),
        ('封禁管理', {
            'fields': ('is_banned', 'ban_until', 'ban_reason', 'banned_by'),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')