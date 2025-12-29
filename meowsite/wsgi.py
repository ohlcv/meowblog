"""
meowsite 项目的 WSGI 配置。

它将 WSGI 可调用对象作为名为 ``application`` 的模块级变量暴露出来。

关于此文件的更多信息，请参阅
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

# 将项目根目录添加到Python路径中
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 将app目录添加到Python路径中
app_path = project_root / 'app'
if str(app_path) not in sys.path:
    sys.path.insert(0, str(app_path))

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meowsite.settings_production")

application = get_wsgi_application()