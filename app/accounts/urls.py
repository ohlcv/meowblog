from django.urls import path
from django.contrib.auth import views as auth_views
from . import views  # 导入我们自己的views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.custom_login, name='login'),  # 使用自定义登录视图
    path('logout/', views.custom_logout, name='logout'),
    # 注册页面
    path('signup/', views.signup, name='signup'),
    
    # 个人中心相关
    path('profile/', views.profile_center, name='profile_center'),  # 自己的个人中心
    path('profile/user/<int:user_id>/', views.user_profile, name='user_profile'),  # 其他用户的个人中心
    path('dashboard/', views.dashboard, name='dashboard'),  # 重定向到个人中心
    
    # 稿件管理相关
    path('manuscripts/', views.manuscript_management, name='manuscript_management'),
    path('manuscripts/user/<int:user_id>/', views.manuscript_management, name='user_manuscript_management'),
    
    # 文章分类管理
    path('category/edit/<int:category_id>/', views.edit_category, name='edit_category'),
    path('category/delete/<int:category_id>/', views.delete_category, name='delete_category'),
    path('category/<int:category_id>/posts/', views.category_posts, name='category_posts'),  # 自己的分类文章
    path('user/<int:user_id>/category/<int:category_id>/posts/', views.category_posts, name='user_category_posts'),  # 别人的分类文章
    
    # 文章管理
    path('post/create/', views.create_post, name='create_post'),
    path('post/create/<int:category_id>/', views.create_post, name='create_post'),
    path('post/edit/<int:post_id>/', views.edit_post, name='edit_post'),
    path('post/delete/<int:post_id>/', views.delete_post, name='delete_post'),
    
    # 用户设置
    path('settings/', views.user_settings, name='user_settings'),
    path('settings/profile/', views.edit_profile, name='edit_profile'),
    path('settings/password/', views.change_password, name='change_password'),
    
    # 管理员功能
    path('admin/', views.admin_panel, name='admin_panel'),
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/user/delete/<int:user_id>/', views.admin_delete_user, name='admin_delete_user'),
    
    # 用户状态管理
    path('admin/user/mute/<int:user_id>/', views.admin_mute_user, name='admin_mute_user'),
    path('admin/user/unmute/<int:user_id>/', views.admin_unmute_user, name='admin_unmute_user'),
    path('admin/user/ban/<int:user_id>/', views.admin_ban_user, name='admin_ban_user'),
    path('admin/user/unban/<int:user_id>/', views.admin_unban_user, name='admin_unban_user'),
]