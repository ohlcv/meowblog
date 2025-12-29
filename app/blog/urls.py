from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.post_list, name='post_list'),
    
    # 新的文章URL结构 - 更语义化
    path('user/<int:user_id>/post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('user/<int:user_id>/category/<int:category_id>/post/<int:post_id>/', views.post_detail, name='post_detail_with_category'),
    
    # 保持向后兼容的旧URL
    path('post/<int:pk>/', views.post_detail, name='post_detail_legacy'),
    
    # 新增：评论相关URL
    path('comment/delete/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    # 新增：管理员功能
    path('admin/post/delete/<int:pk>/', views.admin_delete_post, name='admin_delete_post'),
    # 新增：点赞功能
    path('post/<int:post_id>/like/', views.post_like, name='post_like'),
    path('comment/<int:comment_id>/like/', views.comment_like, name='comment_like'),
    # 新增：收藏功能
    path('post/<int:post_id>/favorite/', views.post_favorite, name='post_favorite'),
    # 新增：关注功能
    path('user/<int:user_id>/follow/', views.follow_user, name='follow_user'),
    path('user/<int:user_id>/unfollow/', views.unfollow_user, name='unfollow_user'),
    path('user/<int:user_id>/follow-status/', views.get_follow_status, name='get_follow_status'),
]