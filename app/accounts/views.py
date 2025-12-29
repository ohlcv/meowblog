# 标准库导入
import logging

# Django 核心导入
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.core.paginator import Paginator
from django.contrib.auth import update_session_auth_hash, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.middleware.csrf import get_token

# 第三方库导入
# (目前没有第三方库导入)

# 本地应用导入
from app.blog.models import PostCategory, Post, Comment, UserFollow
from app.blog.forms import PostCategoryForm, PostForm
from app.blog.views import get_visible_posts
from .services import LoginService, FormErrorHandler
from .forms import CustomUserCreationForm, UserProfileForm, CustomPasswordChangeForm, CustomAuthenticationForm
from .models import UserProfile

# 获取日志记录器
logger = logging.getLogger('accounts')

# signup视图，注册成功后重定向避免刷新提示
def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            logger.info(f'新用户注册成功: {user.username}, IP: {request.META.get("REMOTE_ADDR", "unknown")}')
            messages.success(request, f'账户创建成功！欢迎加入 Meow Blog，{user.username}！')
            return redirect('accounts:login')
        else:
            logger.warning(f'用户注册失败: IP: {request.META.get("REMOTE_ADDR", "unknown")}, 错误: {form.errors}')
            # 显示表单验证错误
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})

# 重构后的登录视图 - 遵循模块化设计原则
def custom_login(request):
    """登录视图 - 使用服务类处理业务逻辑"""
    if request.method == 'POST':
        return _handle_login_post(request)
    else:
        return _handle_login_get(request)


def _handle_login_post(request):
    """处理POST请求的登录逻辑"""
    form = CustomAuthenticationForm(request, data=request.POST)
    
    if form.is_valid():
        user = form.get_user()
        if user:
            # 使用登录服务处理成功登录
            remember_me = form.cleaned_data.get('remember_me')
            LoginService.handle_successful_login(request, user, remember_me)
            return redirect('homepage')
    
    # 登录失败，存储错误信息并重定向
    LoginService.store_login_errors(request, form)
    return redirect('accounts:login')


def _handle_login_get(request):
    """处理GET请求的登录逻辑"""
    # 尝试恢复错误信息
    form = LoginService.restore_login_errors(request, CustomAuthenticationForm)
    
    # 如果没有错误信息，创建干净表单
    if form is None:
        form = FormErrorHandler.create_clean_form(CustomAuthenticationForm, request)
    
    return render(request, 'accounts/login.html', {'form': form})

# 自定义退出登录视图（不显示消息）
def custom_logout(request):
    """自定义退出登录视图，不显示消息提示"""
    logout(request)
    return redirect('homepage')

# 个人中心入口页面
@login_required
def profile_center(request):
    """自己的个人中心入口页面，展示基本信息和快速操作"""
    target_user = request.user
    is_own_page = True
    
    # 获取关注统计
    followers_count = UserFollow.objects.filter(following=target_user).count()
    following_count = UserFollow.objects.filter(follower=target_user).count()
    
    context = {
        'target_user': target_user,
        'is_own_page': is_own_page,
        'is_admin_view': False,
        'followers_count': followers_count,
        'following_count': following_count,
        'is_following': False,
    }
    
    return render(request, 'accounts/profile_center.html', context)

@login_required
def user_profile(request, user_id):
    """其他用户的个人中心页面"""
    target_user = get_object_or_404(User, id=user_id)
    is_own_page = request.user == target_user
    
    # 获取关注统计
    followers_count = UserFollow.objects.filter(following=target_user).count()
    following_count = UserFollow.objects.filter(follower=target_user).count()
    
    # 检查当前用户是否关注了目标用户
    is_following = False
    if request.user.is_authenticated and not is_own_page:
        is_following = UserFollow.objects.filter(follower=request.user, following=target_user).exists()
    
    # 移除管理员特权，所有用户查看别人时权限一致
    is_admin_view = False
    
    context = {
        'target_user': target_user,
        'is_own_page': is_own_page,
        'is_admin_view': is_admin_view,
        'followers_count': followers_count,
        'following_count': following_count,
        'is_following': is_following,
    }
    
    return render(request, 'accounts/profile_center.html', context)

# 稿件管理页面
@login_required
@csrf_protect
def manuscript_management(request, user_id=None):
    """稿件管理页面，管理文章分类"""
    # 确定要查看的用户
    if user_id:
        target_user = get_object_or_404(User, id=user_id)
        is_own_page = request.user == target_user
    else:
        target_user = request.user
        is_own_page = True
    
    # 获取目标用户的分类
    categories = PostCategory.objects.filter(owner=target_user).order_by('name')
    
    # 获取目标用户的文章（根据权限过滤）
    if is_own_page:
        # 查看自己的文章，显示所有文章
        user_posts = Post.objects.filter(author=target_user)
    else:
        # 查看别人的文章，根据权限过滤
        user_posts = get_visible_posts(request.user).filter(author=target_user)
    
    total_posts = user_posts.count()
    total_categories = PostCategory.objects.filter(owner=target_user).count()
    
    # 计算总字数
    total_words = sum(post.word_count for post in user_posts)
    
    # 计算未分类文章数量和字数
    uncategorized_posts = user_posts.filter(category__isnull=True)
    uncategorized_posts_count = uncategorized_posts.count()
    uncategorized_word_count = sum(post.word_count for post in uncategorized_posts)
    
    # 为每个分类计算字数
    categories_with_stats = []
    for category in categories:
        category_posts = user_posts.filter(category=category)
        category_word_count = sum(post.word_count for post in category_posts)
        categories_with_stats.append({
            'category': category,
            'post_count': category_posts.count(),
            'word_count': category_word_count
        })
    
    # 获取关注统计
    followers_count = UserFollow.objects.filter(following=target_user).count()
    following_count = UserFollow.objects.filter(follower=target_user).count()
    
    # 计算总点赞数、收藏数、评论数
    total_likes = sum(post.likes_count for post in user_posts)
    total_favorites = sum(post.favorites_count for post in user_posts)
    total_comments = sum(post.comments.count() for post in user_posts)
    
    # 检查当前用户是否关注了目标用户
    is_following = False
    if request.user.is_authenticated and not is_own_page:
        is_following = UserFollow.objects.filter(follower=request.user, following=target_user).exists()
    
    if request.method == 'POST' and is_own_page:
        if 'create_category' in request.POST:
            category_form = PostCategoryForm(request.POST)
            if category_form.is_valid():
                try:
                    new_category = category_form.save(commit=False)
                    new_category.owner = request.user
                    new_category.save()
                    messages.success(request, f'文章分类「{new_category.name}」创建成功！')
                    return redirect('accounts:manuscript_management')
                except IntegrityError:
                    messages.error(request, f'分类名称「{category_form.cleaned_data["name"]}」已存在，请使用其他名称。')
            else:
                messages.error(request, '创建失败，请检查输入内容。')
    else:
        category_form = PostCategoryForm() if is_own_page else None
    
    # 确保CSRF token是最新的
    csrf_token = get_token(request)
    
    context = {
        'categories': categories,
        'categories_with_stats': categories_with_stats,
        'category_form': category_form,
        'total_posts': total_posts,
        'total_categories': total_categories,
        'total_words': total_words,
        'total_likes': total_likes,
        'total_favorites': total_favorites,
        'total_comments': total_comments,
        'uncategorized_posts': uncategorized_posts_count,
        'uncategorized_word_count': uncategorized_word_count,
        'csrf_token': csrf_token,
        'target_user': target_user,
        'is_own_page': is_own_page,
        'followers_count': followers_count,
        'following_count': following_count,
        'is_following': is_following,
    }
    return render(request, 'accounts/manuscript_management.html', context)

# 编辑文章分类
@login_required
def edit_category(request, category_id):
    """编辑文章分类"""
    category = get_object_or_404(PostCategory, id=category_id, owner=request.user)
    
    if request.method == 'POST':
        form = PostCategoryForm(request.POST, instance=category)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f'分类「{category.name}」修改成功！')
                return redirect('accounts:manuscript_management')
            except IntegrityError:
                messages.error(request, f'分类名称「{form.cleaned_data["name"]}」已存在，请使用其他名称。')
        else:
            messages.error(request, '修改失败，请检查输入内容。')
    else:
        form = PostCategoryForm(instance=category)
    
    context = {
        'form': form,
        'category': category
    }
    return render(request, 'accounts/edit_category.html', context)

# 删除文章分类
@login_required
def delete_category(request, category_id):
    """删除文章分类"""
    category = get_object_or_404(PostCategory, id=category_id, owner=request.user)
    
    if request.method == 'POST':
        category_name = category.name
        category.delete()
        # messages.success(request, f'分类「{category_name}」删除成功！')
        return redirect('accounts:manuscript_management')
    
    context = {
        'category': category
    }
    return render(request, 'accounts/delete_category.html', context)

# 分类详情页，管理该分类下的文章
@login_required
def category_posts(request, category_id, user_id=None):
    """分类详情页，管理该分类下的文章"""
    # 确定要查看的用户
    if user_id:
        target_user = get_object_or_404(User, id=user_id)
        is_own_page = request.user == target_user
    else:
        target_user = request.user
        is_own_page = True
    
    category = None
    if category_id != 0:  # 0 表示未分类文章
        # 确保分类属于目标用户
        category = get_object_or_404(PostCategory, id=category_id, owner=target_user)
        if is_own_page:
            posts = Post.objects.filter(category=category, author=target_user).order_by('-created_at')
        else:
            # 查看别人的文章，根据权限过滤
            user_posts = get_visible_posts(request.user).filter(category=category, author=target_user).order_by('-created_at')
    else:
        # 未分类文章 - 只显示目标用户的未分类文章
        if is_own_page:
            posts = Post.objects.filter(category__isnull=True, author=target_user).order_by('-created_at')
        else:
            # 查看别人的文章，根据权限过滤
            posts = get_visible_posts(request.user).filter(category__isnull=True, author=target_user).order_by('-created_at')
    
    # 分页
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'posts': posts,
        'target_user': target_user,
        'is_own_page': is_own_page,
    }
    return render(request, 'accounts/category_posts.html', context)

# 创建新文章
@login_required
def create_post(request, category_id=None):
    """创建新文章"""
    category = None
    if category_id:
        category = get_object_or_404(PostCategory, id=category_id, owner=request.user)
    
    if request.method == 'POST':
        form = PostForm(request.POST, user=request.user)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            messages.success(request, f'文章「{new_post.title}」创建成功！')
            # 重定向到文章详情页，让用户看到刚发布的文章
            # 使用新的URL结构：user_id和post_id
            return redirect('blog:post_detail', user_id=new_post.author.id, post_id=new_post.id)
    else:
        # 如果指定了分类，默认选中该分类
        initial_data = {'category': category} if category else {}
        form = PostForm(user=request.user, initial=initial_data)
    
    context = {
        'form': form,
        'category': category
    }
    return render(request, 'blog/post_form.html', context)

# 编辑文章
@login_required
def edit_post(request, post_id):
    """编辑文章"""
    # 管理员可以编辑任何文章，普通用户只能编辑自己的文章
    if request.user.is_superuser:
        post = get_object_or_404(Post, id=post_id)
    else:
        post = get_object_or_404(Post, id=post_id, author=request.user)
    
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'文章「{post.title}」修改成功！')
            # 重定向到文章详情页，让用户看到修改后的文章
            # 使用新的URL结构：user_id和post_id
            return redirect('blog:post_detail', user_id=post.author.id, post_id=post.id)
    else:
        form = PostForm(instance=post, user=request.user)
    
    context = {
        'form': form,
        'post': post
    }
    return render(request, 'blog/post_form.html', context)

# 删除文章
@login_required
def delete_post(request, post_id):
    """删除文章"""
    # 管理员可以删除任何文章，普通用户只能删除自己的文章
    if request.user.is_superuser:
        post = get_object_or_404(Post, id=post_id)
    else:
        post = get_object_or_404(Post, id=post_id, author=request.user)
    
    if request.method == 'POST':
        category_id = post.category.id if post.category else None
        post_title = post.title
        post.delete()
        # messages.success(request, f'文章「{post_title}」删除成功！')
        if category_id:
            return redirect('accounts:category_posts', category_id=category_id)
        else:
            return redirect('accounts:manuscript_management')

# 新增：获取用户关注状态的AJAX视图
@login_required
def get_user_follow_status(request, user_id):
    """获取用户关注状态"""
    target_user = get_object_or_404(User, id=user_id)
    
    # 检查当前用户是否关注了目标用户
    is_following = UserFollow.objects.filter(follower=request.user, following=target_user).exists()
    
    # 获取目标用户的资料
    try:
        profile = target_user.userprofile
        is_muted = profile.is_muted
        is_banned = profile.is_banned
    except UserProfile.DoesNotExist:
        is_muted = False
        is_banned = False
    
    return JsonResponse({
        'is_following': is_following,
        'is_muted': is_muted,
        'is_banned': is_banned
    })

# 保留原有的dashboard视图，但重定向到新的个人中心
@login_required
def dashboard(request):
    """重定向到新的个人中心"""
    return redirect('accounts:profile_center')

# ==================== 用户设置功能 ====================

@login_required
def user_settings(request):
    """用户设置主页"""
    # 获取要查看的用户ID（从URL参数）
    user_id = request.GET.get('user_id')
    
    if user_id:
        # 移除管理员特权，普通用户和管理员都不能查看别人的设置
        messages.error(request, '您没有权限查看其他用户的设置')
        return redirect('accounts:profile_center')
    else:
        # 查看自己的设置
        target_user = request.user
        is_own_page = True
    
    # 移除管理员特权
    is_admin_view = False
    
    context = {
        'target_user': target_user,
        'is_own_page': is_own_page,
        'is_admin_view': is_admin_view,
    }
    
    return render(request, 'accounts/user_settings.html', context)

@login_required
def edit_profile(request):
    """修改用户信息"""
    # 获取要修改的用户ID（从URL参数）
    user_id = request.GET.get('user_id')
    
    if user_id:
        # 移除管理员特权，普通用户和管理员都不能修改别人的信息
        messages.error(request, '您没有权限修改其他用户的信息')
        return redirect('accounts:profile_center')
    else:
        # 修改自己的信息
        target_user = request.user
        is_own_page = True
    
    # 移除管理员特权
    is_admin_view = False
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=target_user)
        
        if form.is_valid():
            form.save()
            messages.success(request, '个人信息修改成功！')
            return redirect('accounts:user_settings')
        else:
            messages.error(request, '修改失败，请检查输入内容。')
    else:
        form = UserProfileForm(instance=target_user)
    
    context = {
        'form': form,
        'target_user': target_user,
        'is_own_page': is_own_page,
        'is_admin_view': is_admin_view,
    }
    return render(request, 'accounts/edit_profile.html', context)

@login_required
def change_password(request):
    """修改密码"""
    # 获取要修改的用户ID（从URL参数）
    user_id = request.GET.get('user_id')
    
    if user_id:
        # 修改其他用户的密码（需要管理员权限）
        if not request.user.is_superuser:
            messages.error(request, '您没有权限修改其他用户的密码')
            return redirect('accounts:profile_center')
        
        target_user = get_object_or_404(User, id=user_id)
        is_own_page = request.user == target_user
    else:
        # 修改自己的密码
        target_user = request.user
        is_own_page = True
    
    # 管理员特权：管理员可以修改任何用户的密码
    is_admin_view = request.user.is_superuser and not is_own_page
    
    if request.method == 'POST':
        form = CustomPasswordChangeForm(target_user, request.POST)
        if form.is_valid():
            user = form.save()
            # 只有修改自己的密码时才保持登录状态
            if is_own_page:
                update_session_auth_hash(request, user)
            
            if is_admin_view:
                messages.success(request, f'管理员操作：已修改用户 {target_user.username} 的密码！')
            else:
                messages.success(request, '密码修改成功！')
            return redirect('accounts:user_settings' + (f'?user_id={user_id}' if user_id else ''))
        else:
            messages.error(request, '密码修改失败，请检查输入内容。')
    else:
        form = CustomPasswordChangeForm(target_user)
    
    context = {
        'form': form,
        'target_user': target_user,
        'is_own_page': is_own_page,
        'is_admin_view': is_admin_view,
    }
    return render(request, 'accounts/change_password.html', context)

# ==================== 超级管理员功能 ====================

@login_required
def admin_panel(request):
    """超级管理员面板"""
    if not request.user.is_superuser:
        messages.error(request, '您没有管理员权限。')
        return redirect('accounts:profile_center')
    
    
    # 统计信息
    total_users = User.objects.count()
    total_posts = Post.objects.count()
    total_comments = Comment.objects.count()
    total_categories = PostCategory.objects.count()
    
    # 最近活动
    recent_users = User.objects.order_by('-date_joined')[:3]  # 显示3个最近注册用户
    recent_posts = Post.objects.order_by('-created_at')[:1]   # 显示1个最近文章
    recent_comments = Comment.objects.select_related('author', 'post').order_by('-created_at')[:2]  # 显示2个最近评论
    
    context = {
        'total_users': total_users,
        'total_posts': total_posts,
        'total_comments': total_comments,
        'total_categories': total_categories,
        'recent_users': recent_users,
        'recent_posts': recent_posts,
        'recent_comments': recent_comments,
    }
    return render(request, 'accounts/admin_panel.html', context)

@login_required
def admin_users(request):
    """管理所有用户"""
    if not request.user.is_superuser:
        messages.error(request, '您没有管理员权限。')
        return redirect('accounts:profile_center')
    
    
    # 获取所有用户并预加载profile信息
    users = User.objects.select_related('profile').all().order_by('-date_joined')
    
    # 为没有profile的用户创建profile
    for user in users:
        if not hasattr(user, 'profile'):
            UserProfile.objects.create(user=user)
    
    # 重新获取以确保所有用户都有profile
    users = User.objects.select_related('profile').all().order_by('-date_joined')
    
    # 分页
    paginator = Paginator(users, 20)  # 每页显示20个用户
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)
    
    context = {
        'users': users
    }
    return render(request, 'accounts/admin_users.html', context)

@login_required
def admin_delete_user(request, user_id):
    """管理员删除用户账户"""
    if not request.user.is_superuser:
        messages.error(request, '您没有管理员权限。')
        return redirect('accounts:profile_center')
    
    
    target_user = get_object_or_404(User, id=user_id)
    
    # 不能删除自己
    if target_user == request.user:
        messages.error(request, '不能删除自己的账户。')
        return redirect('accounts:admin_users')
    
    # 不能删除其他超级管理员
    if target_user.is_superuser:
        messages.error(request, '不能删除其他超级管理员账户。')
        return redirect('accounts:admin_users')
    
    if request.method == 'POST':
        username = target_user.username
        # 删除用户将自动删除其所有文章和评论（因为 CASCADE 外键）
        target_user.delete()
        messages.success(request, f'管理员操作：已删除用户 {username} 及其所有数据。')
        return redirect('accounts:admin_users')
    
    # 统计用户数据
    user_posts_count = Post.objects.filter(author=target_user).count()
    user_comments_count = Comment.objects.filter(author=target_user).count()
    user_categories_count = PostCategory.objects.filter(owner=target_user).count()
    
    context = {
        'target_user': target_user,
        'user_posts_count': user_posts_count,
        'user_comments_count': user_comments_count,
        'user_categories_count': user_categories_count,
    }
    return render(request, 'accounts/admin_delete_user.html', context)

# ==================== 用户状态管理功能 ====================

@login_required
@require_POST
def admin_mute_user(request, user_id):
    """管理员禁言用户"""
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'message': '您没有管理员权限。'})
    
    
    target_user = get_object_or_404(User, id=user_id)
    
    # 不能操作自己和其他超级管理员
    if target_user == request.user or target_user.is_superuser:
        return JsonResponse({'success': False, 'message': '无法操作该用户。'})
    
    duration_hours = request.POST.get('duration_hours')
    reason = request.POST.get('reason', '')
    
    try:
        duration = int(duration_hours) if duration_hours else None
        
        # 获取或创建用户配置
        profile, created = UserProfile.objects.get_or_create(user=target_user)
        
        if profile.is_currently_muted:
            return JsonResponse({'success': False, 'message': '该用户已被禁言。'})
        
        profile.mute_user(duration_hours=duration, reason=reason, muted_by=request.user)
        
        duration_text = f'{duration}小时' if duration else '永久'
        messages.success(request, f'用户 {target_user.username} 已被禁言 {duration_text}。')
        
        return JsonResponse({
            'success': True, 
            'message': f'用户 {target_user.username} 已被禁言 {duration_text}。'
        })
        
    except (ValueError, TypeError):
        return JsonResponse({'success': False, 'message': '无效的时间参数。'})

@login_required
@require_POST
def admin_unmute_user(request, user_id):
    """管理员解除禁言"""
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'message': '您没有管理员权限。'})
    
    
    target_user = get_object_or_404(User, id=user_id)
    
    try:
        profile = UserProfile.objects.get(user=target_user)
        
        if not profile.is_currently_muted:
            return JsonResponse({'success': False, 'message': '该用户未被禁言。'})
        
        profile.unmute_user()
        messages.success(request, f'用户 {target_user.username} 的禁言已解除。')
        
        return JsonResponse({
            'success': True, 
            'message': f'用户 {target_user.username} 的禁言已解除。'
        })
        
    except UserProfile.DoesNotExist:
        # 如果没有profile，说明用户未被禁言
        return JsonResponse({'success': False, 'message': '该用户未被禁言。'})

@login_required
@require_POST
def admin_ban_user(request, user_id):
    """管理员封禁用户"""
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'message': '您没有管理员权限。'})
    
    
    target_user = get_object_or_404(User, id=user_id)
    
    # 不能操作自己和其他超级管理员
    if target_user == request.user or target_user.is_superuser:
        return JsonResponse({'success': False, 'message': '无法操作该用户。'})
    
    duration_days = request.POST.get('duration_days')
    reason = request.POST.get('reason', '')
    
    try:
        duration = int(duration_days) if duration_days else None
        
        # 获取或创建用户配置
        profile, created = UserProfile.objects.get_or_create(user=target_user)
        
        if profile.is_currently_banned:
            return JsonResponse({'success': False, 'message': '该用户已被封禁。'})
        
        profile.ban_user(duration_days=duration, reason=reason, banned_by=request.user)
        
        duration_text = f'{duration}天' if duration else '永久'
        messages.success(request, f'用户 {target_user.username} 已被封禁 {duration_text}。')
        
        return JsonResponse({
            'success': True, 
            'message': f'用户 {target_user.username} 已被封禁 {duration_text}。'
        })
        
    except (ValueError, TypeError):
        return JsonResponse({'success': False, 'message': '无效的时间参数。'})

@login_required
@require_POST
def admin_unban_user(request, user_id):
    """管理员解除封禁"""
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'message': '您没有管理员权限。'})
    
    
    target_user = get_object_or_404(User, id=user_id)
    
    try:
        profile = UserProfile.objects.get(user=target_user)
        
        if not profile.is_currently_banned:
            return JsonResponse({'success': False, 'message': '该用户未被封禁。'})
        
        profile.unban_user()
        messages.success(request, f'用户 {target_user.username} 的封禁已解除。')
        
        return JsonResponse({
            'success': True, 
            'message': f'用户 {target_user.username} 的封禁已解除。'
        })
        
    except UserProfile.DoesNotExist:
        # 如果没有profile，说明用户未被封禁
        return JsonResponse({'success': False, 'message': '该用户未被封禁。'})