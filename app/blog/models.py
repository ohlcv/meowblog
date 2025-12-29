"""
博客模型模块
定义文章、评论、分类等数据模型

模块级别变量：
    __version__: 模块版本号
    __author__: 模块作者
    __all__: 公开API列表
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils.html import mark_safe
import markdown
from markdown.extensions import codehilite, fenced_code, tables, toc

# 模块级别特殊变量 - 遵循PEP8规范
__version__ = '1.0.0'
__author__ = 'Meow Site Development Team'
__all__ = ['PostCategory', 'Post', 'Comment']


class PostCategory(models.Model):
    """用户自定义的文章分类"""
    name = models.CharField(max_length=100)
    # 分类的拥有者，外键关联到User
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
    class Meta:
        app_label = 'blog'
        verbose_name = '文章分类'
        verbose_name_plural = '文章分类'
        unique_together = ['name', 'owner']  # 用户不能创建重名分类


class Post(models.Model):
    """文章"""
    # 可见权限选择
    VISIBILITY_CHOICES = [
        ('public', '公开'),
        ('mutual', '互关'),
        ('private', '私密'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField(verbose_name='Markdown内容')
    content_html = models.TextField(blank=True, verbose_name='HTML内容')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # 作者
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # 分类 (允许为空)
    category = models.ForeignKey(
        PostCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # 可见权限
    visibility = models.CharField(
        max_length=10,
        choices=VISIBILITY_CHOICES,
        default='public',
        verbose_name='可见权限'
    )
    
    # 点赞数
    likes_count = models.PositiveIntegerField(default=0, verbose_name='点赞数')
    # 收藏数
    favorites_count = models.PositiveIntegerField(default=0, verbose_name='收藏数')

    def __str__(self):
        return self.title

    class Meta:
        app_label = 'blog'
        verbose_name = '文章'
        verbose_name_plural = '文章'

    def save(self, *args, **kwargs):
        """保存时自动将Markdown转换为HTML"""
        if self.content:
            self.content_html = self.markdown_to_html(self.content)
        super().save(*args, **kwargs)

    @staticmethod
    def markdown_to_html(markdown_text):
        """将Markdown文本转换为HTML"""
        if not markdown_text:
            return ''
        
        # 配置Markdown扩展
        extensions = [
            'codehilite',      # 代码高亮
            'fenced_code',     # 围栏代码块
            'tables',          # 表格支持
            'toc',             # 目录生成
            'nl2br',           # 换行转换
            'extra',           # 额外功能
        ]
        
        # 配置代码高亮
        extension_configs = {
            'codehilite': {
                'css_class': 'highlight',
                'use_pygments': True,
                'noclasses': False,
            },
            'toc': {
                'permalink': True,
                'permalink_title': '永久链接',
            }
        }
        
        md = markdown.Markdown(
            extensions=extensions,
            extension_configs=extension_configs
        )
        
        return md.convert(markdown_text)

    @property
    def word_count(self):
        """计算字数（基于Markdown内容）"""
        if not self.content:
            return 0
        # 移除Markdown语法，计算纯文本字符数
        import re
        text = self.content
        # 移除代码块
        text = re.sub(r'```[\s\S]*?```', '', text)
        # 移除行内代码
        text = re.sub(r'`[^`]+`', '', text)
        # 移除链接，保留文本
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        # 移除图片
        text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', '', text)
        # 移除标题标记
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        # 移除粗体斜体标记
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        text = re.sub(r'\*([^*]+)\*', r'\1', text)
        # 移除列表标记
        text = re.sub(r'^[\s]*[-*+]\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'^[\s]*\d+\.\s+', '', text, flags=re.MULTILINE)
        # 移除引用标记
        text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
        # 移除水平线
        text = re.sub(r'^[-*_]{3,}$', '', text, flags=re.MULTILINE)
        # 移除多余的空格和换行
        text = re.sub(r'\s+', '', text)
        return len(text)
    
    @property
    def html_content(self):
        """获取HTML内容，如果没有则实时转换"""
        if self.content_html:
            return mark_safe(self.content_html)
        elif self.content:
            return mark_safe(self.markdown_to_html(self.content))
        return ''
    
    @property
    def text_preview(self):
        """获取纯文本预览，用于列表页显示"""
        import re
        # 移除Markdown语法，获取纯文本
        text = self.content
        
        # 移除标题标记
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        
        # 移除粗体和斜体标记
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        
        # 移除代码块
        text = re.sub(r'```[\s\S]*?```', '', text)
        text = re.sub(r'`(.*?)`', r'\1', text)
        
        # 移除链接，保留文本
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        
        # 移除图片
        text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', '', text)
        
        # 移除列表标记
        text = re.sub(r'^[\s]*[-*+]\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'^[\s]*\d+\.\s+', '', text, flags=re.MULTILINE)
        
        # 移除引用标记
        text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
        
        # 移除分割线
        text = re.sub(r'^[-*_]{3,}$', '', text, flags=re.MULTILINE)
        
        # 清理多余的空行
        text = re.sub(r'\n\s*\n', '\n', text)
        text = text.strip()
        
        return text
    
    class Meta:
        verbose_name = '文章'
        verbose_name_plural = '文章'
        ordering = ['-created_at']  # 默认按创建时间倒序排列

class Comment(models.Model):
    """文章评论"""
    # 评论所属的文章
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    # 评论的作者
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    # 评论内容
    content = models.TextField()
    # 评论时间
    created_at = models.DateTimeField(auto_now_add=True)
    # 点赞数
    likes_count = models.PositiveIntegerField(default=0, verbose_name='点赞数')

    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'
    
    class Meta:
        app_label = 'blog'
        verbose_name = '评论'
        verbose_name_plural = '评论'
        ordering = ['-created_at']  # 默认按创建时间倒序排列


class PostLike(models.Model):
    """文章点赞"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='点赞用户')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name='被点赞文章')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='点赞时间')

    def __str__(self):
        return f'{self.user.username} 点赞了 {self.post.title}'
    
    class Meta:
        app_label = 'blog'
        verbose_name = '文章点赞'
        verbose_name_plural = '文章点赞'
        unique_together = ['user', 'post']  # 同一用户对同一文章只能点赞一次


class CommentLike(models.Model):
    """评论点赞"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='点赞用户')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, verbose_name='被点赞评论')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='点赞时间')

    def __str__(self):
        return f'{self.user.username} 点赞了评论'
    
    class Meta:
        app_label = 'blog'
        verbose_name = '评论点赞'
        verbose_name_plural = '评论点赞'
        unique_together = ['user', 'comment']  # 同一用户对同一评论只能点赞一次


class PostFavorite(models.Model):
    """文章收藏"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='收藏用户')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name='被收藏文章')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='收藏时间')

    def __str__(self):
        return f'{self.user.username} 收藏了 {self.post.title}'
    
    class Meta:
        app_label = 'blog'
        verbose_name = '文章收藏'
        verbose_name_plural = '文章收藏'
        unique_together = ['user', 'post']  # 同一用户对同一文章只能收藏一次


class UserFollow(models.Model):
    """用户关注"""
    follower = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='following',
        verbose_name='关注者'
    )
    following = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='followers',
        verbose_name='被关注者'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='关注时间')

    def __str__(self):
        return f'{self.follower.username} 关注了 {self.following.username}'
    
    class Meta:
        app_label = 'blog'
        verbose_name = '用户关注'
        verbose_name_plural = '用户关注'
        unique_together = ['follower', 'following']  # 同一用户不能重复关注同一用户