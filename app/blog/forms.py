"""
博客表单模块
提供文章、评论、分类等表单功能

模块级别变量：
    __version__: 模块版本号
    __author__: 模块作者
    __all__: 公开API列表
"""
from django import forms
from .models import Post, PostCategory, Comment, UserFollow

# 模块级别特殊变量 - 遵循PEP8规范
__version__ = '1.0.0'
__author__ = 'Meow Site Development Team'
__all__ = ['PostForm', 'PostCategoryForm', 'CommentForm', 'FollowForm']


class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # 从kwargs中弹出user，因为它不是ModelForm的默认参数
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            if user.is_superuser:
                # 管理员可以选择任何用户的分类
                self.fields['category'].queryset = PostCategory.objects.all().order_by('owner__username', 'name')
            else:
                # 过滤分类字段的queryset，只显示当前用户的分类
                self.fields['category'].queryset = PostCategory.objects.filter(owner=user)
        
        # 为Markdown内容字段添加特殊样式和帮助文本
        self.fields['content'].widget.attrs.update({
            'class': 'form-control markdown-editor',
            'rows': 15,
            'placeholder': '在这里输入Markdown格式的内容...\n\n支持的功能：\n- 标题：# ## ###\n- 粗体：**文本**\n- 斜体：*文本*\n- 代码：`代码` 或 ```代码块```\n- 链接：[文本](URL)\n- 图片：![alt](URL)\n- 列表：- 或 1.\n- 表格：| 列1 | 列2 |\n- 引用：> 文本'
        })
        self.fields['content'].help_text = '支持Markdown语法，可以复制粘贴Markdown内容'

    class Meta:
        model = Post
        fields = ['title', 'category', 'content', 'visibility']
        labels = {
            'title': '标题',
            'category': '文章分类',
            'content': 'Markdown内容',
            'visibility': '可见权限',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入文章标题'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'visibility': forms.Select(attrs={
                'class': 'form-control'
            }),
        }

# 新增：分类表单
class PostCategoryForm(forms.ModelForm):
    class Meta:
        model = PostCategory
        fields = ['name']
        labels = {
            'name': '文章分类名称'
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': '输入分类名称，例如：技术教程、生活感悟',
                'maxlength': 100
            })
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name or not name.strip():
            raise forms.ValidationError('分类名称不能为空')
        return name.strip()

# 新增：评论表单
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        labels = {
            'content': '评论内容'
        }
        widgets = {
            'content': forms.Textarea(attrs={
                'placeholder': '写下你的评论...',
                'rows': 4,
                'class': 'form-control'
            })
        }
    
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if not content or not content.strip():
            raise forms.ValidationError('评论内容不能为空')
        if len(content.strip()) < 2:
            raise forms.ValidationError('评论内容至少需要2个字符')
        return content.strip()


# 新增：关注表单
class FollowForm(forms.ModelForm):
    class Meta:
        model = UserFollow
        fields = ['following']
        widgets = {
            'following': forms.HiddenInput()
        }