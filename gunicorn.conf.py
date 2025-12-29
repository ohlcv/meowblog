# Gunicorn 配置文件
import multiprocessing
import os

# 设置Django设置模块
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meowsite.settings_production")

# 服务器套接字
bind = "0.0.0.0:8000"
backlog = 2048

# Worker 进程
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 2

# 重启
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# 日志 - 使用生产环境日志目录
log_dir = os.getenv('LOG_DIR', 'C:/var/log/meowsite')
accesslog = os.path.join(log_dir, "gunicorn_access.log")
errorlog = os.path.join(log_dir, "gunicorn_error.log")
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# 进程命名
proc_name = "meowsite"

# 安全
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8090
