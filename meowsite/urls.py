from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from app.core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', core_views.homepage, name='homepage'),
    path('about/', core_views.about, name='about'),
    path('terms/', core_views.terms_of_service, name='terms_of_service'),
    path('privacy/', core_views.privacy_policy, name='privacy_policy'),
    path('disclaimer/', core_views.disclaimer, name='disclaimer'),
    path('blog/', include('app.blog.urls', namespace='blog')),
    # 新增：包含accounts应用的URL
    path('accounts/', include('app.accounts.urls', namespace='accounts')),
]

# 开发环境静态文件服务
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)