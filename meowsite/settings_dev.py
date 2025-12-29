"""
开发环境配置文件
用于本地开发，不强制HTTPS，启用调试功能
"""
import os
from .settings import *

# =============================================================================
# 开发环境特定设置
# =============================================================================

# 强制启用DEBUG模式
DEBUG = True

# 开发环境允许的主机
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '::1']

# =============================================================================
# 安全设置 - 开发环境放宽
# =============================================================================

# 不强制HTTPS
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# 会话和CSRF配置 - 开发环境不安全
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False  # 开发环境允许JavaScript访问
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_USE_SESSIONS = False
CSRF_COOKIE_AGE = 31449600  # 1年
CSRF_COOKIE_DOMAIN = None
CSRF_COOKIE_PATH = '/'

# CSRF信任的源 - 开发环境
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://0.0.0.0:8000',
    'http://::1:8000',
]

# 其他安全设置 - 开发环境放宽
SECURE_CONTENT_TYPE_NOSNIFF = False
SECURE_BROWSER_XSS_FILTER = False
X_FRAME_OPTIONS = 'SAMEORIGIN'  # 开发环境允许同源嵌入
SECURE_REFERRER_POLICY = None   # 开发环境不限制

# =============================================================================
# 开发环境特定配置
# =============================================================================

# 日志目录配置 - 统一使用项目目录下的logs
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# 更新日志配置中的文件路径
LOGGING['handlers']['file']['filename'] = LOGS_DIR / 'django.log'
LOGGING['handlers']['error_file']['filename'] = LOGS_DIR / 'error.log'

# 缓存配置 - 开发环境使用虚拟缓存
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# 邮件配置 - 开发环境使用控制台后端
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'Meow Site Dev <dev@meowsite.cn>'

# 日志配置 - 开发环境显示更多信息
LOGGING['handlers']['console']['level'] = 'DEBUG'
LOGGING['loggers']['django']['level'] = 'DEBUG'
LOGGING['loggers']['blog']['level'] = 'DEBUG'
LOGGING['loggers']['accounts']['level'] = 'DEBUG'
LOGGING['loggers']['core']['level'] = 'DEBUG'

# 添加数据库查询日志
LOGGING['loggers']['django.db.backends'] = {
    'level': 'DEBUG',
    'handlers': ['console'],
    'propagate': False,
}

# =============================================================================
# 开发环境调试工具
# =============================================================================

# 可以在这里添加调试工具栏等开发工具
# INSTALLED_APPS += ['debug_toolbar']
# MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

# =============================================================================
# 数据库配置 - 开发环境
# =============================================================================

# 支持通过环境变量配置数据库（默认使用SQLite）
# if os.getenv('DB_NAME'):
#     # 如果配置了DB_NAME，则使用MySQL
#     DATABASES = {
#         'default': {
#             'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.mysql'),
#             'NAME': os.getenv('DB_NAME'),
#             'USER': os.getenv('DB_USER'),
#             'PASSWORD': os.getenv('DB_PASSWORD'),
#             'HOST': os.getenv('DB_HOST', 'localhost'),
#             'PORT': os.getenv('DB_PORT', '3306'),
#             'OPTIONS': {
#                 'charset': 'utf8mb4',
#                 'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
#             },
#             'TEST': {
#                 'CHARSET': 'utf8mb4',
#                 'COLLATION': 'utf8mb4_unicode_ci',
#             }
#         }
#     }
# else:
#     # 默认使用SQLite
#     DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.sqlite3',
#             'NAME': BASE_DIR / 'db.sqlite3',
#         }
#     }

if DEBUG:
    print("开发环境配置已加载")
    print("详细日志已启用")
    print("🌐 允许的主机:", ALLOWED_HOSTS)
    print("🔓 安全设置已放宽（仅开发环境）")
