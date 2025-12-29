"""
生产环境配置文件
用于在服务器上运行Meow Blog博客系统
支持生产环境DEBUG模式，同时保持正常跨域设置
"""
import os
from .settings import *

# =============================================================================
# 生产环境特定设置
# =============================================================================

# 生产环境DEBUG模式（可通过环境变量控制）
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# 生产环境允许的主机
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,meowsite.cn,www.meowsite.cn,101.32.161.229').split(',')
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS if host.strip()]

# =============================================================================
# CSRF和Origin配置
# =============================================================================

# CSRF信任的源
CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', 'http://localhost:8000,http://127.0.0.1:8000,https://meowsite.cn,https://www.meowsite.cn,http://101.32.161.229:80').split(',')
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in CSRF_TRUSTED_ORIGINS if origin.strip()]

# 调试信息输出
if DEBUG:
    print(f"DEBUG: CSRF_TRUSTED_ORIGINS = {CSRF_TRUSTED_ORIGINS}")
    print(f"DEBUG: ALLOWED_HOSTS = {ALLOWED_HOSTS}")
    print(f"DEBUG: DEBUG mode is enabled for production debugging")

# =============================================================================
# 日志配置 - 生产环境
# =============================================================================

# 日志目录配置 - 生产环境使用系统标准目录
LOGS_DIR = os.getenv('LOG_DIR', 'C:/var/log/meowsite')
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR, exist_ok=True)

# 更新日志配置中的文件路径
LOGGING['handlers']['file']['filename'] = os.path.join(LOGS_DIR, 'django.log')
LOGGING['handlers']['error_file']['filename'] = os.path.join(LOGS_DIR, 'error.log')

# =============================================================================
# 安全设置 - 生产环境
# =============================================================================

# CSRF相关设置 - 完全以.env文件为最高优先级
CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE', 'True').lower() == 'true'
CSRF_COOKIE_HTTPONLY = os.getenv('CSRF_COOKIE_HTTPONLY', 'True').lower() == 'true'
CSRF_COOKIE_SAMESITE = os.getenv('CSRF_COOKIE_SAMESITE', 'Lax')
CSRF_USE_SESSIONS = False
CSRF_COOKIE_AGE = 31449600  # 1年
CSRF_COOKIE_DOMAIN = None
CSRF_COOKIE_PATH = '/'
CSRF_FAILURE_VIEW = 'django.views.csrf.csrf_failure'

# nginx代理相关设置
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# SSL安全设置 - 由nginx处理SSL
SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'False').lower() == 'true'
SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '31536000'))  # 1年HSTS
SECURE_HSTS_INCLUDE_SUBDOMAINS = os.getenv('SECURE_HSTS_INCLUDE_SUBDOMAINS', 'True').lower() == 'true'
SECURE_HSTS_PRELOAD = os.getenv('SECURE_HSTS_PRELOAD', 'True').lower() == 'true'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# 会话配置 - 生产环境安全
SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'True').lower() == 'true'
SESSION_COOKIE_HTTPONLY = os.getenv('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true'
SESSION_COOKIE_SAMESITE = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')
SESSION_COOKIE_AGE = 60 * 60 * 24 * 30  # 30天

# =============================================================================
# 数据库配置 - 生产环境
# =============================================================================

# 生产环境数据库 - MySQL配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', 'meowsite_prod'),
        'USER': os.getenv('DB_USER', 'meow'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
        'TEST': {
            'CHARSET': 'utf8mb4',
            'COLLATION': 'utf8mb4_unicode_ci',
        }
    }
}

# 注释掉之前的SQLite配置
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'meowsite_prod',
#         'USER': 'meow_user',
#         'PASSWORD': 'your_password',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }

# =============================================================================
# 静态文件和媒体文件配置 - 生产环境
# =============================================================================

# 静态文件配置 - 使用环境变量
STATIC_ROOT = os.getenv('STATIC_ROOT', 'C:/var/www/meowsite.cn/staticfiles')
MEDIA_ROOT = os.getenv('MEDIA_ROOT', 'C:/var/www/meowsite.cn/media')
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# 静态文件URL配置
STATIC_URL = os.getenv('STATIC_URL', '/static/')
MEDIA_URL = os.getenv('MEDIA_URL', '/media/')

# 生产环境性能优化
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# =============================================================================
# 缓存配置 - 生产环境
# =============================================================================

# 缓存配置（可选，提高性能）
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# =============================================================================
# 邮件配置 - 生产环境
# =============================================================================

# 邮件配置（用于发送通知邮件）
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.qq.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'Meow Site <noreply@meowsite.cn>')

# DEBUG模式下的额外配置
if DEBUG:
    # DEBUG模式下启用Django调试工具栏（如果安装了）
    # INSTALLED_APPS += ['debug_toolbar']
    # MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    
    # DEBUG模式下显示SQL查询
    LOGGING['loggers']['django.db.backends'] = {
        'level': 'DEBUG',
        'handlers': ['console'],
    }
    
    print("DEBUG模式已启用 - 生产环境调试模式")
    print("详细日志已启用")
    print("安全设置保持生产级别")