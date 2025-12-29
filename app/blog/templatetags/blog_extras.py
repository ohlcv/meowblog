from django import template
from django.urls import reverse

register = template.Library()

@register.simple_tag
def get_post_url(post):
    """
    根据文章信息生成正确的URL
    返回格式：/user/<user_id>/post/<post_id>/ 或 /user/<user_id>/category/<category_id>/post/<post_id>/
    """
    if post.category:
        return reverse('blog:post_detail_with_category', kwargs={
            'user_id': post.author.id,
            'category_id': post.category.id,
            'post_id': post.id
        })
    else:
        return reverse('blog:post_detail', kwargs={
            'user_id': post.author.id,
            'post_id': post.id
        })
