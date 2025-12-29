# 标准库导入
import logging

# Django 核心导入
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Q

# 第三方库导入
# (目前没有第三方库导入)

# 本地应用导入
from .forms import CommentForm
from .models import Post, Comment, PostLike, CommentLike, PostFavorite, UserFollow

# 获取日志记录器
logger = logging.getLogger('blog')


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


def get_visible_posts(user):
    """
    根据用户权限获取可见的文章
    """
    if not user.is_authenticated:
        # 未登录用户只能看到公开文章
        return Post.objects.filter(visibility='public')
    
    # 获取用户关注的人
    following_users = set(UserFollow.objects.filter(follower=user).values_list('following', flat=True))
    # 获取关注用户的人
    followers_users = set(UserFollow.objects.filter(following=user).values_list('follower', flat=True))
    
    # 计算互相关注的用户（交集）
    mutual_follow_users = following_users & followers_users
    
    # 构建查询条件
    
    # 公开文章 + 互关文章（双方都关注了对方） + 用户自己的文章
    visible_posts = Post.objects.filter(
        Q(visibility='public') |  # 公开文章
        Q(visibility='mutual', author__in=mutual_follow_users) |  # 互关文章（双方互相关注）
        Q(author=user)  # 用户自己的文章
    )
    
    return visible_posts


def can_view_post(post, user):
    """
    检查用户是否可以查看指定文章
    """
    if not user.is_authenticated:
        return post.visibility == 'public'
    
    # 用户自己的文章总是可见
    if post.author == user:
        return True
    
    # 公开文章
    if post.visibility == 'public':
        return True
    
    # 互关文章 - 需要双方都关注了对方
    if post.visibility == 'mutual':
        # 检查用户是否关注了作者
        user_follows_author = UserFollow.objects.filter(follower=user, following=post.author).exists()
        # 检查作者是否关注了用户
        author_follows_user = UserFollow.objects.filter(follower=post.author, following=user).exists()
        # 只有双方都关注了对方才能看到
        return user_follows_author and author_follows_user
    
    # 私密文章
    return False

# 新增：发布新文章的视图

# 新增：编辑文章的视图


# post_list 视图，添加分页和搜索功能
def post_list(request):
    # 获取排序参数
    sort_by = request.GET.get('sort', 'default')
    # 获取搜索参数
    search_query = request.GET.get('search', '').strip()
    
    # 根据用户权限获取可见文章
    posts = get_visible_posts(request.user)
    
    # 搜索功能
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |  # 标题包含搜索词
            Q(content__icontains=search_query) |  # 内容包含搜索词
            Q(author__username__icontains=search_query)  # 作者用户名包含搜索词
        )
    
    # 根据排序参数设置排序方式
    if sort_by == 'created':
        posts = posts.order_by('-created_at')
    elif sort_by == 'updated':
        posts = posts.order_by('-updated_at')
    elif sort_by == 'likes':
        posts = posts.order_by('-likes_count', '-created_at')
    else:  # default - 按点赞数排序
        posts = posts.order_by('-likes_count', '-created_at')
    
    # 为每个文章添加收藏数统计和关注状态
    for post in posts:
        post.favorites_count = PostFavorite.objects.filter(post=post).count()
        # 添加关注状态 - 改进逻辑
        if request.user.is_authenticated and request.user != post.author:
            post.is_following = UserFollow.objects.filter(follower=request.user, following=post.author).exists()
        else:
            post.is_following = False
    
    # 分页
    paginator = Paginator(posts, 10)  # 每页显示10篇文章
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    context = {
        'posts': posts,
        'current_sort': sort_by,
        'search_query': search_query
    }
    
    return render(request, 'blog/post_list.html', context)


# 新增：文章详情页的视图（包含评论功能）
def post_detail(request, pk=None, post_id=None, user_id=None, category_id=None):
    """
    这个视图负责显示单篇文章的详情和评论功能
    支持新的URL结构：/user/<user_id>/post/<post_id>/ 或 /user/<user_id>/category/<category_id>/post/<post_id>/
    """
    # 1. 根据URL参数获取文章
    if post_id is not None:
        # 新URL结构：使用post_id
        post = get_object_or_404(Post, pk=post_id)
        
        # 验证用户ID是否匹配（如果提供了user_id）
        if user_id is not None and post.author.id != user_id:
            messages.error(request, '文章与用户不匹配。')
            return redirect('blog:post_list')
        
        # 验证分类ID是否匹配（如果提供了category_id）
        if category_id is not None:
            if category_id == 0:
                # 未分类文章
                if post.category is not None:
                    messages.error(request, '文章分类不匹配。')
                    return redirect('blog:post_list')
            else:
                # 有分类的文章
                if post.category is None or post.category.id != category_id:
                    messages.error(request, '文章分类不匹配。')
                    return redirect('blog:post_list')
    else:
        # 旧URL结构：使用pk（向后兼容）
        post = get_object_or_404(Post, pk=pk)
    
    # 2. 检查用户是否有权限查看该文章
    if not can_view_post(post, request.user):
        messages.error(request, '您没有权限查看这篇文章。')
        return redirect('blog:post_list')
    
    # 3. 获取该文章的所有评论，按时间顺序排列
    comments = post.comments.all().order_by('created_at')
    
    # 4. 处理评论表单提交
    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            # 创建新评论但不立即保存
            new_comment = comment_form.save(commit=False)
            new_comment.post = post  # 设置评论所属文章
            new_comment.author = request.user  # 设置评论作者
            new_comment.save()
            
            messages.success(request, '评论发表成功！')
            # 重定向到当前文章页面，使用新的URL结构
            if post_id is not None:
                if category_id is not None:
                    return redirect('blog:post_detail_with_category', user_id=post.author.id, category_id=category_id, post_id=post_id)
                else:
                    return redirect('blog:post_detail', user_id=post.author.id, post_id=post_id)
            else:
                return redirect('blog:post_detail_legacy', pk=pk)
        else:
            messages.error(request, '评论发表失败，请检查输入内容。')
    else:
        comment_form = CommentForm()
    
    # 4. 检查用户是否已点赞该文章
    is_post_liked = False
    if request.user.is_authenticated:
        is_post_liked = PostLike.objects.filter(user=request.user, post=post).exists()
    
    # 5. 检查用户是否已收藏该文章
    is_post_favorited = False
    if request.user.is_authenticated:
        is_post_favorited = PostFavorite.objects.filter(user=request.user, post=post).exists()
    
    # 6. 检查用户是否关注了文章作者
    is_following = False
    if request.user.is_authenticated and request.user != post.author:
        is_following = UserFollow.objects.filter(follower=request.user, following=post.author).exists()
    
    # 7. 检查用户对每个评论的点赞状态和关注状态
    comment_likes = set()
    if request.user.is_authenticated:
        liked_comment_ids = CommentLike.objects.filter(
            user=request.user, 
            comment__in=comments
        ).values_list('comment_id', flat=True)
        comment_likes = set(liked_comment_ids)
        
        # 为每个评论添加关注状态
        for comment in comments:
            if request.user != comment.author:
                comment.is_following = UserFollow.objects.filter(follower=request.user, following=comment.author).exists()
            else:
                comment.is_following = False
    
    # 8. 将文章、评论和表单传递给模板
    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'comments_count': comments.count(),
        'is_post_liked': is_post_liked,
        'is_post_favorited': is_post_favorited,
        'is_following': is_following,
        'comment_likes': comment_likes,
    }
    return render(request, 'blog/post_detail.html', context)

# 新增：删除评论的视图（增强管理员权限）
@login_required
def delete_comment(request, comment_id):
    """删除评论（评论作者、文章作者或超级管理员可以删除）"""
    comment = get_object_or_404(Comment, id=comment_id)
    
    # 检查权限：评论作者、文章作者或超级管理员可以删除
    if not (request.user == comment.author or request.user == comment.post.author or request.user.is_superuser):
        messages.error(request, '您没有权限删除这条评论。')
        # 使用新的URL结构：user_id和post_id
        return redirect('blog:post_detail', user_id=comment.post.author.id, post_id=comment.post.id)
    
    if request.method == 'POST':
        post_id = comment.post.id
        post_author_id = comment.post.author.id
        comment_author = comment.author.username
        comment_content = comment.content[:50] + '...' if len(comment.content) > 50 else comment.content
        comment.delete()
        
        # 记录删除日志
        if request.user.is_superuser and request.user != comment.author:
            logger.info(f'管理员 {request.user.username} 删除了用户 {comment_author} 的评论: 「{comment_content}」')
            messages.success(request, f'管理员操作：已删除用户 {comment_author} 的评论。')
        else:
            logger.info(f'用户 {request.user.username} 删除了评论: 「{comment_content}」')
            messages.success(request, '评论删除成功！')
        # 使用新的URL结构：user_id和post_id
        return redirect('blog:post_detail', user_id=post_author_id, post_id=post_id)
    
    # GET请求显示确认页面
    context = {
        'comment': comment
    }
    return render(request, 'blog/delete_comment.html', context)

# 新增：管理员删除文章功能
@login_required
def admin_delete_post(request, pk):
    """管理员删除任意文章（超级管理员或文章作者可以使用）"""
    post = get_object_or_404(Post, pk=pk)
    
    # 检查权限：超级管理员或文章作者可以删除
    if not (request.user.is_superuser or request.user == post.author):
        messages.error(request, '您没有权限删除这篇文章。')
        # 使用新的URL结构：user_id和post_id
        return redirect('blog:post_detail', user_id=post.author.id, post_id=post.id)
    
    if request.method == 'POST':
        post_title = post.title
        post_author = post.author.username
        post_id = post.pk
        post_author_id = post.author.id
        post.delete()
        
        # 记录删除日志
        if request.user.is_superuser and request.user != post.author:
            logger.info(f'管理员 {request.user.username} 删除了用户 {post_author} 的文章: 「{post_title}」 (ID: {post_id})')
            messages.success(request, f'管理员操作：已删除用户 {post_author} 的文章「{post_title}」。')
        else:
            logger.info(f'用户 {request.user.username} 删除了文章: 「{post_title}」 (ID: {post_id})')
            messages.success(request, f'文章「{post_title}」删除成功！')
        # 使用新的URL结构：user_id和post_id
        return redirect('blog:post_detail', user_id=post_author_id, post_id=post_id)
    
    context = {
        'post': post,
        'is_admin_delete': request.user.is_superuser and request.user != post.author
    }
    return render(request, 'blog/admin_delete_post.html', context)


@require_POST
@login_required
def post_like(request, post_id):
    """文章点赞/取消点赞"""
    post = get_object_or_404(Post, id=post_id)
    user = request.user
    
    try:
        # 检查是否已经点赞
        like, created = PostLike.objects.get_or_create(user=user, post=post)
        
        if created:
            # 新点赞
            post.likes_count += 1
            post.save()
            is_liked = True
            message = ''
        else:
            # 已点赞，检查用户权限
            if user.is_superuser:
                # 管理员可以重复点赞
                post.likes_count += 1
                post.save()
                is_liked = True
                message = ''
            else:
                # 普通用户取消点赞
                like.delete()
                post.likes_count -= 1
                post.save()
                is_liked = False
                message = ''
        
        return JsonResponse({
            'success': True,
            'is_liked': is_liked,
            'likes_count': post.likes_count,
            'message': message
        })
        
    except Exception as e:
        logger.error(f'文章点赞失败: {e}')
        return JsonResponse({
            'success': False,
            'message': '操作失败，请重试'
        })


@require_POST
@login_required
def comment_like(request, comment_id):
    """评论点赞/取消点赞"""
    comment = get_object_or_404(Comment, id=comment_id)
    user = request.user
    
    try:
        # 检查是否已经点赞
        like, created = CommentLike.objects.get_or_create(user=user, comment=comment)
        
        if created:
            # 新点赞
            comment.likes_count += 1
            comment.save()
            is_liked = True
            message = ''
        else:
            # 已点赞，检查用户权限
            if user.is_superuser:
                # 管理员可以重复点赞
                comment.likes_count += 1
                comment.save()
                is_liked = True
                message = ''
            else:
                # 普通用户取消点赞
                like.delete()
                comment.likes_count -= 1
                comment.save()
                is_liked = False
                message = ''
        
        return JsonResponse({
            'success': True,
            'is_liked': is_liked,
            'likes_count': comment.likes_count,
            'message': message
        })
        
    except Exception as e:
        logger.error(f'评论点赞失败: {e}')
        return JsonResponse({
            'success': False,
            'message': '操作失败，请重试'
        })


@require_POST
@login_required
def post_favorite(request, post_id):
    """文章收藏/取消收藏"""
    post = get_object_or_404(Post, id=post_id)
    user = request.user
    
    try:
        # 检查是否已经收藏
        favorite, created = PostFavorite.objects.get_or_create(user=user, post=post)
        
        if created:
            # 新收藏
            post.favorites_count += 1
            post.save()
            is_favorited = True
            message = ''
        else:
            # 已收藏，取消收藏
            favorite.delete()
            post.favorites_count -= 1
            post.save()
            is_favorited = False
            message = ''
        
        return JsonResponse({
            'success': True,
            'is_favorited': is_favorited,
            'message': message
        })
        
    except Exception as e:
        logger.error(f'文章收藏失败: {e}')
        return JsonResponse({
            'success': False,
            'message': '操作失败，请重试'
        })


@require_POST
@login_required
def follow_user(request, user_id):
    """关注用户"""
    target_user = get_object_or_404(User, id=user_id)
    current_user = request.user
    
    
    # 不能关注自己
    if target_user == current_user:
        logger.warning(f'用户 {current_user.username} 尝试关注自己')
        return JsonResponse({
            'success': False,
            'message': '不能关注自己'
        })
    
    try:
        # 检查是否已经关注
        if UserFollow.objects.filter(follower=current_user, following=target_user).exists():
            return JsonResponse({
                'success': False,
                'message': '已经关注过该用户'
            })
        
        # 创建关注关系
        UserFollow.objects.create(
            follower=current_user,
            following=target_user
        )
        
        logger.info(f'用户 {current_user.username} 关注了 {target_user.username}')
        
        return JsonResponse({
            'success': True,
            'is_following': True,
            'message': f'已关注 {target_user.username}'
        })
        
    except Exception as e:
        logger.error(f'关注操作失败: {e}')
        return JsonResponse({
            'success': False,
            'message': '关注失败，请重试'
        })


@require_POST
@login_required
def unfollow_user(request, user_id):
    """取消关注用户"""
    target_user = get_object_or_404(User, id=user_id)
    current_user = request.user
    
    # 不能取消关注自己
    if target_user == current_user:
        return JsonResponse({
            'success': False,
            'message': '不能取消关注自己'
        })
    
    try:
        # 查找关注关系
        follow_relation = UserFollow.objects.filter(
            follower=current_user, 
            following=target_user
        ).first()
        
        if not follow_relation:
            return JsonResponse({
                'success': False,
                'message': '未关注该用户'
            })
        
        # 删除关注关系
        follow_relation.delete()
        
        logger.info(f'用户 {current_user.username} 取消关注了 {target_user.username}')
        
        return JsonResponse({
            'success': True,
            'is_following': False,
            'message': f'已取消关注 {target_user.username}'
        })
        
    except Exception as e:
        logger.error(f'取消关注操作失败: {e}')
        return JsonResponse({
            'success': False,
            'message': '取消关注失败，请重试'
        })


@login_required
def get_follow_status(request, user_id):
    """获取关注状态"""
    target_user = get_object_or_404(User, id=user_id)
    current_user = request.user
    
    if target_user == current_user:
        return JsonResponse({
            'success': False,
            'message': '不能关注自己'
        })
    
    try:
        is_following = UserFollow.objects.filter(
            follower=current_user, 
            following=target_user
        ).exists()
        
        return JsonResponse({
            'success': True,
            'is_following': is_following,
            'user_id': user_id,
            'username': target_user.username
        })
        
    except Exception as e:
        logger.error(f'获取关注状态失败: {e}')
        return JsonResponse({
            'success': False,
            'message': '获取关注状态失败'
        })

