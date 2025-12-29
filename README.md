# 🐾 Meow Blog - Django 博客系统

一个功能完整、设计优雅的Django博客网站，支持用户注册、文章发布、评论互动等功能。

## ✨ 特性

### 🔐 用户系统
- **多方式登录**：支持用户名/邮箱/手机号登录
- **手机号注册**：11位中国手机号格式验证
- **用户协议**：注册时必须同意用户服务协议
- **记住登录**：支持30天免登录
- **权限管理**：用户封禁、禁言功能
- **个人中心**：完整的用户资料管理

### 📝 博客功能
- **Markdown支持**：完整的Markdown语法支持，包括代码高亮、表格、数学公式等
- **实时预览**：编辑时支持Markdown实时预览功能
- **文章管理**：创建、编辑、删除文章
- **分类系统**：用户自定义文章分类
- **评论系统**：支持文章评论和互动，现代化左右并列布局
- **点赞功能**：文章和评论点赞，支持权限控制
- **收藏功能**：文章收藏，方便用户管理喜欢的内容
- **分享功能**：一键复制文章链接分享
- **搜索功能**：支持按标题、内容、作者搜索文章
- **排序功能**：支持按创建时间、更新时间、点赞数排序
- **权限控制**：作者和管理员权限分离
- **分页显示**：优化大数据量展示
- **智能字数统计**：基于纯文本的准确字数统计
- **可见权限**：支持公开、互关、私密三种文章可见权限
- **用户关注**：用户可以关注其他用户，查看互关文章
- **稿件管理**：完整的个人稿件管理系统，支持分类管理
- **用户资料**：可查看其他用户的个人资料和文章列表
- **智能卡片**：整个文章卡片可点击跳转到详情页
- **头像系统**：统一的头像组件，集成关注功能
- **统计展示**：创作统计横幅，显示文章数、点赞数、收藏数等

### 🛡️ 管理员功能
- **超级权限**：管理员拥有最高删除和编辑权限
- **用户管理**：查看、封禁、解封用户
- **内容审核**：删除不当文章和评论
- **统计面板**：用户、文章、评论数据统计

### 📊 日志系统
- **分层日志**：应用日志、错误日志、安全日志、数据库日志
- **自动轮转**：日志文件大小控制和备份
- **性能监控**：请求响应时间和慢查询警告
- **安全审计**：用户操作和IP地址记录

### 🎨 界面设计
- **现代化设计**：粉色主题，参考哔哩哔哩设计理念
- **响应式设计**：支持PC和移动端
- **毛玻璃效果**：导航栏现代化质感
- **流畅动画**：使用 cubic-bezier 缓动函数
- **统一风格**：一致的确认页面和操作流程
- **组件化设计**：可复用的文章卡片和元数据组件
- **统一间距**：所有页面使用一致的视觉间距
- **现代化卡片**：圆角、阴影、悬停效果
- **粉色主题**：温暖、现代、符合年轻化趋势
- **智能交互**：整个文章卡片可点击跳转
- **头像系统**：统一的头像组件，支持关注功能

## 🛠️ 技术栈

- **后端框架**：Django 5.2.6
- **数据库**：SQLite（开发）/ MySQL/PostgreSQL（生产推荐）
- **前端**：HTML5 + CSS3 + JavaScript
- **设计系统**：CSS变量 + 现代化设计理念
- **动画系统**：CSS3 Transitions + cubic-bezier 缓动函数
- **Markdown处理**：Python-Markdown 3.5.1 + Pygments 2.17.2
- **AJAX交互**：原生JavaScript Fetch API
- **剪贴板API**：现代浏览器Clipboard API + 传统降级方案
- **Python版本**：Python 3.8+

## 📦 项目结构

```
meowsite/
├── accounts/                 # 用户账户应用
│   ├── models.py            # 用户扩展模型
│   ├── views.py             # 用户相关视图
│   ├── forms.py             # 用户表单
│   ├── services.py          # 业务逻辑服务
│   ├── middleware.py        # 用户状态中间件
│   └── templates/           # 用户相关模板
├── blog/                    # 博客应用
│   ├── models.py            # 文章、评论、分类、关注模型
│   ├── views.py             # 博客视图
│   ├── forms.py             # 博客表单
│   └── templates/           # 博客模板
│       └── includes/        # 可复用组件
│           ├── post_card.html      # 文章卡片组件
│           └── post_metadata.html  # 文章元数据组件
├── core/                    # 核心应用
│   ├── views.py             # 首页等核心视图
│   ├── middleware.py        # 请求日志中间件
│   ├── management/          # Django管理命令
│   └── templates/           # 基础模板
├── meowsite/               # 项目配置
│   ├── settings.py          # 主配置文件
│   ├── logging_config.py    # 模块化日志配置
│   ├── settings_production.py # 生产环境配置
│   ├── settings_dev.py      # 开发环境配置
│   └── urls.py              # 主URL配置
├── logs/                    # 日志文件目录（运行时自动创建）
├── static/                  # 项目静态文件（源代码）
│   ├── css/                 # CSS样式文件
│   │   ├── base.css         # 基础样式和设计系统
│   │   ├── components.css   # 组件样式
│   │   ├── layout.css       # 布局样式
│   │   ├── pages.css        # 页面特定样式
│   │   ├── responsive.css   # 响应式样式
│   │   ├── markdown.css     # Markdown渲染样式
│   │   ├── avatar.css       # 头像组件样式
│   │   └── accounts.css     # 账户页面样式
│   ├── images/              # 项目图片资源
│   └── js/                  # JavaScript文件
├── staticfiles/             # 静态文件收集目录（运行时生成）
├── media/                   # 用户上传文件目录（运行时自动创建）
├── docs/                    # 项目文档
│   ├── mysql_setup_guide.md # MySQL设置指南
│   └── 用户使用指南.md       # 用户使用指南
├── deploy_clean.bat         # 智能部署脚本
├── start_dev_clean.bat      # 开发环境启动脚本
├── start_production_clean.bat # 生产环境启动脚本
├── meowsite_manager.py      # 跨平台管理脚本
├── env.development.example  # 开发环境配置示例
├── env.production.example   # 生产环境配置示例
├── nginx.conf               # Nginx配置文件
├── gunicorn.conf.py         # Gunicorn配置文件
├── log_viewer.py            # 日志查看工具
├── setup_mysql.py           # MySQL数据库初始化脚本
├── requirements.txt         # 依赖包列表
└── manage.py               # Django管理脚本
```

### 📁 重要文件夹说明

#### 🎨 **static/ 文件夹**
- **作用**：项目源代码中的静态文件
- **内容**：CSS、JavaScript、图片、favicon等
- **特点**：**不能删除**，这是源代码的一部分
- **用途**：开发时存放项目的静态资源

#### 📦 **staticfiles/ 文件夹**
- **作用**：`collectstatic` 命令收集静态文件的目标目录
- **内容**：所有静态文件的集合（包括Django Admin、第三方包、项目静态文件）
- **特点**：**可以删除**，运行时自动重新生成
- **生成方式**：运行 `python manage.py collectstatic` 时创建

#### 📁 **media/ 文件夹**
- **作用**：用户上传文件的存储目录
- **内容**：用户头像、文章图片、附件等
- **特点**：**可以删除**，用户上传时自动创建
- **权限**：需要写权限

#### 📝 **logs/ 文件夹**
- **作用**：应用程序日志文件
- **内容**：应用日志、错误日志、安全日志、数据库日志
- **特点**：**可以删除**，但建议保留历史日志
- **自动创建**：日志配置会自动创建目录

## 🚀 快速开始

### 方法一：使用部署脚本（推荐）

``bash
# 1. 克隆项目
git clone <repository-url>
cd meowblog

# 2. 一键部署（自动创建虚拟环境、安装依赖、数据库迁移）
deploy_clean.bat

# 3. 启动开发服务器
start_dev_clean.bat
```

### 方法二：手动部署

``bash
# 1. 克隆项目
git clone <repository-url>
cd meowblog

# 2. 创建虚拟环境
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量（可选）
copy env.development.example .env

# 5. 数据库迁移
python manage.py makemigrations
python manage.py migrate

# 6. 创建超级用户
python manage.py createsuperuser

# 7. 运行开发服务器
python manage.py runserver
```

访问 http://127.0.0.1:8000 即可使用！

### 测试用户

项目已预置测试用户，可直接登录体验：

- **管理员用户**：
  - 用户名：`admin`
  - 密码：`admin123`
  - 权限：超级管理员，可管理所有内容

- **普通用户**：
  - 用户名：`meow`
  - 密码：`meow123`
  - 权限：普通用户，可创建和管理自己的内容

## 📝 Markdown功能说明

### 支持的Markdown语法

本博客系统支持完整的Markdown语法，包括：

#### 基础语法
- **标题**：`# 一级标题` 到 `###### 六级标题`
- **粗体**：`**粗体文本**` 或 `__粗体文本__`
- **斜体**：`*斜体文本*` 或 `_斜体文本_`
- **删除线**：`~~删除线文本~~`
- **链接**：`[链接文本](URL)`
- **图片**：`![图片描述](图片URL)`

#### 列表
- **无序列表**：`- 项目` 或 `* 项目` 或 `+ 项目`
- **有序列表**：`1. 项目`
- **任务列表**：`- [x] 已完成` 或 `- [ ] 未完成`

#### 代码
- **行内代码**：`` `代码` ``
- **代码块**：`` 代码块 ```（支持语法高亮）
- **围栏代码块**：支持多种编程语言语法高亮

#### 表格
```
| 列1 | 列2 | 列3 |
|-----|-----|-----|
| 内容1 | 内容2 | 内容3 |
```

#### 引用
```
> 这是引用内容
> 可以多行引用
```

#### 分割线
```
---
***
___
```

### 特色功能

1. **实时预览**：编辑文章时可以实时预览Markdown渲染效果
2. **语法帮助**：内置Markdown语法帮助面板
3. **代码高亮**：支持多种编程语言的语法高亮
4. **智能字数统计**：自动过滤Markdown语法，统计纯文本字数
5. **复制粘贴支持**：可以直接复制粘贴Markdown内容

### 使用示例

创建新文章时，在内容区域输入Markdown格式的内容：

```
# 我的第一篇博客

这是一篇使用 **Markdown** 编写的博客文章。

## 代码示例

```
def hello_world():
    print("Hello, Meow Blog!")
```

## 列表

- 功能1
- 功能2
- 功能3

> 这是一个引用块

[访问官网](https://example.com)
```

## 💝 互动功能说明

### 点赞系统

#### 文章点赞
- **普通用户**：同一篇文章只能点赞一次，再次点击取消点赞
- **管理员**：可以无限点赞，每次点击赞数+1
- **实时更新**：点赞数实时显示在文章列表和详情页

#### 评论点赞
- **权限控制**：与文章点赞相同的权限规则
- **独立统计**：每个评论都有独立的点赞数统计

### 收藏系统
- **一键收藏**：点击收藏按钮即可收藏文章
- **状态同步**：收藏状态实时更新（⭐/☆）
- **个人管理**：收藏的文章可以在个人中心查看

### 分享功能
- **一键复制**：点击分享按钮自动复制文章链接
- **兼容性好**：支持现代浏览器和传统浏览器
- **用户反馈**：复制成功后显示提示信息

### 排序功能
- **多种排序**：支持按创建时间、更新时间、点赞数排序
- **智能排序**：点赞数相同时按创建时间排序
- **实时切换**：排序选项实时生效

### 权限控制
- **普通用户**：点赞/收藏操作有次数限制
- **管理员**：拥有特殊权限，可以重复点赞
- **未登录用户**：只能查看统计信息，无法操作

## 👥 社交功能说明

### 文章可见权限
- **🌐 公开**：所有用户都可以看到
- **🤝 互关**：只有互相关注的用户可以看到
- **🔒 私密**：只有作者自己可以看到

### 用户关注系统
- **关注功能**：用户可以关注其他用户
- **粉丝统计**：显示关注数和粉丝数
- **互关检测**：自动检测互相关注关系
- **权限控制**：只有互关用户才能看到"互关"权限的文章

### 稿件管理系统
- **个人稿件**：管理自己的所有文章
- **分类管理**：创建、编辑、删除文章分类
- **统计信息**：显示文章数、分类数、关注数、粉丝数
- **他人稿件**：查看其他用户的稿件管理页面
- **关注按钮**：在他人稿件页面可以关注/取消关注

### 用户资料页面
- **基本信息**：显示用户名、关注数、粉丝数
- **文章列表**：显示该用户的所有可见文章
- **关注操作**：可以关注/取消关注该用户
- **权限过滤**：只显示当前用户有权限查看的文章

### 组件化设计
- **文章卡片**：统一的文章显示组件，支持多种样式
- **元数据组件**：可复用的文章元数据显示组件
- **响应式布局**：适配不同屏幕尺寸
- **统一间距**：所有页面使用一致的视觉间距

## 🎨 现代化设计系统

Meow Blog采用了现代化的CSS设计系统，提供了统一的视觉语言和组件库：

### 设计原则
- **一致性**：所有组件遵循统一的设计语言
- **可复用性**：组件化设计，易于维护和扩展
- **响应式**：适配各种屏幕尺寸
- **可访问性**：良好的对比度和键盘导航支持

### 颜色系统
- **主色调**：粉色系（#fb7299），温暖现代
- **辅助色**：成功、警告、危险、信息色
- **中性色**：文本、背景、边框的标准色值

### 组件库
- **卡片系统**：现代化卡片设计，支持多种变体
- **按钮系统**：统一的按钮样式和交互效果
- **表单组件**：一致的表单控件样式
- **导航组件**：响应式导航栏和面包屑导航
- **头像组件**：统一的用户头像显示组件

### 动画系统
- **缓动函数**：使用cubic-bezier实现自然流畅的动画
- **过渡效果**：统一的过渡时间和缓动曲线
- **交互反馈**：悬停、点击等交互状态的视觉反馈

## 🔧 配置说明

### 环境变量

可选择创建 `.env` 文件配置环境变量：

```
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 日志配置

项目采用模块化日志配置，支持：

- **开发环境**：控制台输出 + 文件记录
- **生产环境**：仅关键信息记录
- **自动轮转**：文件大小超过5MB自动备份

### 数据库配置

#### 开发环境（SQLite）
默认使用SQLite，无需额外配置。

#### 生产环境（MySQL）
支持MySQL数据库，可通过自动化脚本或手动方式配置：

##### 自动化配置（推荐）
```bash
# 1. 安装MySQL依赖
pip install mysql-connector-python

# 2. 运行自动化配置脚本
python setup_mysql.py
```

##### 手动配置
```sql
-- 创建数据库
CREATE DATABASE meowsite_prod CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户并授权
CREATE USER 'meow_user'@'localhost' IDENTIFIED BY 'your_secure_password_here';
GRANT ALL PRIVILEGES ON meowsite_prod.* TO 'meow_user'@'localhost';

-- 刷新权限
FLUSH PRIVILEGES;
```

##### 环境变量配置
在 `.env` 文件中添加：
```
DB_NAME=meowsite_prod
DB_USER=meow_user
DB_PASSWORD=your_secure_password_here
DB_HOST=localhost
DB_PORT=3306
```

#### 安装数据库驱动

在生产环境中使用MySQL数据库时，需要安装PyMySQL驱动和加密库：

```
pip install PyMySQL cryptography
```

#### 生产环境（PostgreSQL）
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'meowsite_prod',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 📋 管理工具

### 日志管理

```
# 查看日志状态
python manage.py logmanage --status

# 清理30天前的日志
python manage.py logmanage --clean

# 清理指定天数前的日志
python manage.py logmanage --clean --days 15

# 归档7天前的日志
python manage.py logmanage --archive
```

### 日志查看

```
# 查看应用日志
python log_viewer.py

# 查看错误日志
python log_viewer.py --type error

# 实时监控
python log_viewer.py --tail

# 查看所有日志摘要
python log_viewer.py --summary
```

## 🔐 安全特性

- **CSRF保护**：所有表单都有CSRF令牌
- **SQL注入防护**：使用Django ORM
- **XSS防护**：模板自动转义
- **用户权限**：基于Django权限系统
- **密码安全**：使用Django内置密码验证
- **会话安全**：安全的会话配置

## 📱 功能模块

### 用户管理
- [x] 用户注册（用户名+邮箱+手机号）
- [x] 多方式登录（用户名/邮箱/手机号）
- [x] 个人资料管理
- [x] 密码修改
- [x] 用户状态管理（封禁/解封）

### 文章系统
- [x] 文章发布和编辑
- [x] Markdown语法支持（标题、列表、代码、表格、链接等）
- [x] 代码高亮显示
- [x] 实时Markdown预览
- [x] 文章分类管理
- [x] 文章删除（作者/管理员）
- [x] 文章列表和详情
- [x] 智能字数统计（基于纯文本）
- [x] 文章点赞功能（权限控制）
- [x] 文章收藏功能
- [x] 文章分享功能（复制链接）
- [x] 文章排序功能（时间、点赞数）
- [x] 文章可见权限（公开/互关/私密）
- [x] 内容预览功能（两行预览）
- [x] 组件化文章卡片设计

### 评论系统
- [x] 发表评论
- [x] 删除评论（作者/文章作者/管理员）
- [x] 评论列表显示
- [x] 评论点赞功能（权限控制）

### 用户互动
- [x] 用户关注系统
- [x] 互关文章可见性
- [x] 用户个人资料页面
- [x] 稿件管理系统
- [x] 关注/粉丝统计
- [x] 用户文章列表

### 管理功能
- [x] 超级管理员面板
- [x] 用户管理
- [x] 内容审核
- [x] 统计信息

## 🎯 开发规范

### PEP8 规范
- ✅ 所有模块包含 `__version__`、`__author__`、`__all__` 变量
- ✅ 函数使用 snake_case 命名
- ✅ 类使用 PascalCase 命名
- ✅ 导入语句按标准顺序排列

### 模块化设计
- ✅ 复杂功能按功能域拆分
- ✅ 业务逻辑封装在服务类中
- ✅ 表单验证逻辑独立管理
- ✅ 配置文件模块化

### Django 最佳实践
- ✅ 模型包含完整的 Meta 类配置
- ✅ 表单包含必要的验证逻辑
- ✅ 视图函数职责单一
- ✅ 模板继承和组件化

## 🚀 部署指南

### Windows 部署（推荐）

#### 使用部署脚本

```
# 1. 克隆项目
git clone <repository-url>
cd meowblog

# 2. 一键部署
deploy_clean.bat

# 3. 配置环境变量
copy env.production.example .env
# 编辑 .env 文件，设置正确的配置

# 4. 启动生产环境
start_production_clean.bat
```

#### 跨平台管理脚本

项目提供了 `meowsite_manager.py` 脚本，支持跨平台管理：

```
# 初始化项目
python meowsite_manager.py init

# 启动开发服务器
python meowsite_manager.py dev

# 启动生产服务器
python meowsite_manager.py prod
```

### Linux 部署

#### 1. 环境准备

```bash
# 安装系统依赖
sudo apt update
sudo apt install python3-pip python3-venv nginx postgresql

# 创建项目用户
sudo useradd -m -s /bin/bash meowsite
```

#### 2. 代码部署

```bash
# 切换到项目用户
sudo su - meowsite

# 克隆代码
git clone <repository-url> /home/meowsite/meowsite
cd /home/meowsite/meowsite

# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 3. 数据库配置

```bash
# 创建PostgreSQL数据库
sudo -u postgres createdb meowsite_prod
sudo -u postgres createuser --interactive meowsite

# 运行迁移
python manage.py migrate --settings=meowsite.settings_production
```

#### 4. 静态文件收集

```bash
python manage.py collectstatic --settings=meowsite.settings_production
```

#### 5. Web服务器配置

使用Nginx + Gunicorn的生产配置示例：

```
server {
    listen 80;
    server_name your-domain.com;
    
    location /static/ {
        alias /home/meowsite/meowsite/staticfiles/;
    }
    
    location /media/ {
        alias /home/meowsite/meowsite/media/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 6. 进程管理

使用systemd管理Gunicorn进程：

```
[Unit]
Description=Meow Blog Django App
After=network.target

[Service]
User=meowsite
Group=meowsite
WorkingDirectory=/home/meowsite/meowsite
Environment="PATH=/home/meowsite/meowsite/.venv/bin"
ExecStart=/home/meowsite/meowsite/.venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 meowsite.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

## 🐛 故障排除

### 常见问题

1. **数据库连接错误**
   - 检查数据库配置和连接权限
   - 确认数据库服务运行状态

2. **静态文件404**
   - 运行 `python manage.py collectstatic`
   - 检查STATIC_ROOT配置

3. **日志权限错误**
   - 确保logs目录存在且有写权限
   - 检查用户权限配置

4. **内存使用过高**
   - 调整Gunicorn worker数量
   - 检查数据库查询优化

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 👥 作者

- **量化交易喵** - *项目开发者和维护者*
  - 专注于量化交易策略开发
  - AgileGrid多级网格策略作者
  - 缠论机器学习量化框架开发者
  - 个人主页：[关于我](/about/)

## 🙏 致谢

- Django 框架团队
- 所有贡献者和测试用户
- 开源社区的支持

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- **GitHub**：[项目仓库](https://github.com/your-username/meowblog)
- **邮箱**：24369961@qq.com
- **Bilibili**：[量化交易喵](https://b23.tv/wOztNSS)
- **个人网站**：[关于我页面](/about/)

---

**📝 最后更新**：2025年10月2日

## 🆕 最新更新

### v2.5.0 - 用户体验优化版本
- ✅ 博客搜索功能：支持按标题、内容、作者搜索
- ✅ 评论系统重构：现代化左右并列布局设计
- ✅ 评论框自适应：固定宽度，高度自适应内容
- ✅ 文字对齐优化：评论内容左上角对齐
- ✅ 头像组件优化：统一显示，避免重复用户名
- ✅ 浅粉色背景系统：层次分明的视觉设计
- ✅ 管理后台增强：文章可见权限管理
- ✅ 响应式评论布局：移动端适配优化
- ✅ 用户体验提升：更直观的交互设计

### v2.4.0 - 现代化设计版本
- ✅ 粉色主题设计，参考哔哩哔哩设计理念
- ✅ 现代化卡片设计（圆角、阴影、悬停效果）
- ✅ 毛玻璃效果导航栏
- ✅ 流畅动画系统（cubic-bezier 缓动函数）
- ✅ 统一头像组件，集成关注功能
- ✅ 智能文章卡片（整个卡片可点击跳转）
- ✅ 创作统计横幅（文章数、点赞数、收藏数等）
- ✅ 现代化按钮和交互效果
- ✅ 紧凑布局优化（卡片间距调整）
- ✅ 统一设计语言和视觉层次

### v2.3.0 - 社交功能版本
- ✅ 文章可见权限系统（公开/互关/私密）
- ✅ 用户关注系统
- ✅ 互关文章可见性控制
- ✅ 用户个人资料页面
- ✅ 稿件管理系统增强
- ✅ 关注/粉丝统计功能
- ✅ 组件化文章卡片设计
- ✅ 统一页面间距和视觉效果
- ✅ 内容预览功能优化
- ✅ 发布文章后重定向优化

### v2.2.0 - 组件化版本
- ✅ 可复用的文章卡片组件
- ✅ 文章元数据组件
- ✅ 统一的文章显示样式
- ✅ 优化模板结构
- ✅ 改进代码可维护性

### v2.1.0 - 互动功能版本
- ✅ 文章和评论点赞功能
- ✅ 文章收藏功能
- ✅ 文章分享功能（复制链接）
- ✅ 文章排序功能（时间、点赞数）
- ✅ 权限控制系统（普通用户vs管理员）
- ✅ 优化文章列表布局
- ✅ 改进用户体验

### v2.0.0 - Markdown支持版本
- ✅ 完整的Markdown语法支持
- ✅ 实时预览功能
- ✅ 代码高亮显示
- ✅ 智能字数统计
- ✅ 优化用户界面
- ✅ 改进文章编辑体验