from django.contrib import admin
from django.utils.html import mark_safe
from .models import Post, PostCategory, Comment, PostLike, CommentLike, PostFavorite, UserFollow

# Register your models here.

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'visibility', 'created_at', 'word_count', 'likes_count', 'favorites_count']
    list_filter = ['created_at', 'category', 'author', 'visibility']
    search_fields = ['title', 'content']
    readonly_fields = ['content_html', 'created_at', 'updated_at', 'word_count', 'likes_count', 'favorites_count']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'author', 'category', 'visibility')
        }),
        ('内容', {
            'fields': ('content', 'content_html'),
            'description': '在content字段中输入Markdown格式的内容，系统会自动转换为HTML并显示在content_html字段中'
        }),
        ('统计信息', {
            'fields': ('likes_count', 'favorites_count'),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def word_count(self, obj):
        return f"{obj.word_count} 字"
    word_count.short_description = '字数'

@admin.register(PostCategory)
class PostCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'post_count']
    list_filter = ['owner']
    search_fields = ['name', 'owner__username']
    
    def post_count(self, obj):
        return obj.post_set.count()
    post_count.short_description = '文章数量'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'created_at', 'likes_count', 'content_preview']
    list_filter = ['created_at', 'post__author']
    search_fields = ['content', 'author__username', 'post__title']
    readonly_fields = ['likes_count']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = '评论内容预览'


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['user__username', 'post__title']
    readonly_fields = ['created_at']


@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'comment', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['user__username', 'comment__content']
    readonly_fields = ['created_at']


@admin.register(PostFavorite)
class PostFavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['user__username', 'post__title']
    readonly_fields = ['created_at']


@admin.register(UserFollow)
class UserFollowAdmin(admin.ModelAdmin):
    list_display = ['follower', 'following', 'created_at']
    list_filter = ['created_at', 'follower', 'following']
    search_fields = ['follower__username', 'following__username']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('follower', 'following')