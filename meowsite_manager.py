#!/usr/bin/env python3
"""
Meow Site 跨平台管理脚本
支持：初始化、启动开发服务器、启动生产服务器
兼容：Windows、Linux、macOS
"""

import os
import sys
import subprocess
import platform
import shutil
import signal
import time
import socket
from pathlib import Path
from typing import Optional, Dict, List


class Colors:
    """终端颜色输出"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


class MeowSiteManager:
    """Meow Blog 项目管理器"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.is_windows = platform.system() == 'Windows'
        self.is_linux = platform.system() == 'Linux'
        self.is_macos = platform.system() == 'Darwin'
        
        # 虚拟环境路径
        if self.is_windows:
            self.venv_path = self.project_root / '.venv' / 'Scripts'
            self.activate_script = self.venv_path / 'activate.bat'
            self.python_exe = self.venv_path / 'python.exe'
            self.pip_exe = self.venv_path / 'pip.exe'
        else:
            self.venv_path = self.project_root / '.venv' / 'bin'
            self.activate_script = self.venv_path / 'activate'
            self.python_exe = self.venv_path / 'python'
            self.pip_exe = self.venv_path / 'pip'
        
        # 环境变量文件
        self.env_file = self.project_root / '.env'
        self.env_prod_example = self.project_root / 'env.production.example'
        self.env_dev_example = self.project_root / 'env.development.example'
        
        # 默认配置
        self.default_config = {
            'EXTERNAL_HOST': '101.32.161.229',
            'EXTERNAL_PORT': '80',
            'PORT': '8000'
        }
    
    def print_header(self, title: str):
        """打印标题"""
        print(f"\n{Colors.CYAN}{'='*50}")
        print(f"{Colors.BOLD}{title}")
        print(f"{Colors.CYAN}{'='*50}{Colors.END}")
    
    def print_success(self, message: str):
        """打印成功消息"""
        print(f"{Colors.GREEN}✓ {message}{Colors.END}")
    
    def print_error(self, message: str):
        """打印错误消息"""
        print(f"{Colors.RED}✗ {message}{Colors.END}")
    
    def print_warning(self, message: str):
        """打印警告消息"""
        print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")
    
    def print_info(self, message: str):
        """打印信息消息"""
        print(f"{Colors.BLUE}ℹ {message}{Colors.END}")
    
    def run_command(self, command: List[str], cwd: Optional[Path] = None, 
                   capture_output: bool = False, check: bool = True, use_venv: bool = True) -> subprocess.CompletedProcess:
        """运行命令"""
        if cwd is None:
            cwd = self.project_root
        
        # 如果使用虚拟环境且命令是python相关，替换为虚拟环境中的python
        if use_venv and command and command[0] in ['python', 'python.exe']:
            command = [str(self.python_exe)] + command[1:]
        
        try:
            if capture_output:
                result = subprocess.run(
                    command, cwd=cwd, capture_output=True, text=True, check=check
                )
            else:
                result = subprocess.run(command, cwd=cwd, check=check)
            return result
        except subprocess.CalledProcessError as e:
            if not capture_output:
                self.print_error(f"命令执行失败: {' '.join(command)}")
                if e.stderr:
                    self.print_error(f"错误信息: {e.stderr}")
            raise e
        except FileNotFoundError as e:
            self.print_error(f"命令未找到: {' '.join(command)}")
            self.print_error(f"请确保相关程序已正确安装")
            raise e
    
    def check_python(self) -> bool:
        """检查Python是否安装"""
        try:
            # 优先检查虚拟环境中的Python
            if self.venv_path.exists() and self.python_exe.exists():
                result = self.run_command([str(self.python_exe), '--version'], capture_output=True, use_venv=False)
                version = result.stdout.strip()
                self.print_success(f"虚拟环境Python版本: {version}")
                return True
            else:
                # 回退到系统Python
                result = self.run_command([sys.executable, '--version'], capture_output=True, use_venv=False)
                version = result.stdout.strip()
                self.print_success(f"系统Python版本: {version}")
                return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.print_error("Python未安装或不在PATH中，请安装Python 3.8+")
            return False
    
    def create_virtual_environment(self) -> bool:
        """创建虚拟环境"""
        if self.venv_path.exists():
            # 检查虚拟环境是否可用
            if self.is_virtual_environment_valid():
                self.print_info("虚拟环境已存在且可用，跳过创建")
                return True
            else:
                self.print_warning("虚拟环境存在但不可用，重新创建...")
                self.remove_virtual_environment()
        
        try:
            self.print_info("创建Python虚拟环境...")
            self.run_command([sys.executable, '-m', 'venv', '.venv'])
            self.print_success("虚拟环境创建成功")
            return True
        except subprocess.CalledProcessError as e:
            self.print_error("虚拟环境创建失败")
            self.print_error("请检查Python安装和权限设置")
            return False
    
    def is_virtual_environment_valid(self) -> bool:
        """检查虚拟环境是否有效"""
        try:
            if not self.python_exe.exists():
                return False
            
            # 尝试运行Python命令
            result = self.run_command([str(self.python_exe), '--version'], capture_output=True)
            return result.returncode == 0
        except:
            return False
    
    def remove_virtual_environment(self):
        """删除虚拟环境"""
        try:
            if self.venv_path.exists():
                if self.is_windows:
                    self.run_command(['rmdir', '/s', '/q', str(self.venv_path)], capture_output=True)
                else:
                    import shutil
                    shutil.rmtree(self.venv_path)
                self.print_info("已删除旧的虚拟环境")
        except:
            self.print_warning("删除虚拟环境失败，请手动删除 .venv 目录")
    
    def install_dependencies(self) -> bool:
        """安装依赖"""
        try:
            self.print_info("安装项目依赖...")
            
            # 检查虚拟环境是否可用
            if not self.is_virtual_environment_valid():
                self.print_error("虚拟环境不可用，请重新创建")
                return False
            
            # 升级pip
            self.print_info("升级pip...")
            self.run_command([str(self.python_exe), '-m', 'pip', 'install', '--upgrade', 'pip'])
            
            # 安装requirements.txt
            requirements_file = self.project_root / 'requirements.txt'
            if requirements_file.exists():
                self.print_info("安装requirements.txt中的依赖...")
                self.run_command([str(self.pip_exe), 'install', '-r', 'requirements.txt'])
                self.print_success("依赖安装完成")
                return True
            else:
                self.print_error("requirements.txt文件不存在")
                return False
        except subprocess.CalledProcessError as e:
            self.print_error("依赖安装失败")
            self.print_error("请检查网络连接和Python环境")
            return False
        except Exception as e:
            self.print_error(f"安装过程中发生未知错误: {e}")
            return False
    
    def setup_environment_file(self, env_type: str = 'production') -> bool:
        """设置环境变量文件"""
        if self.env_file.exists():
            self.print_info(".env文件已存在，跳过创建")
            return True
        
        # 选择示例文件
        if env_type == 'development':
            example_file = self.env_dev_example
        else:
            example_file = self.env_prod_example
        
        if not example_file.exists():
            self.print_error(f"示例文件不存在: {example_file}")
            return False
        
        try:
            # 复制示例文件
            shutil.copy2(example_file, self.env_file)
            self.print_success(f".env文件已创建（基于{env_type}配置）")
            self.print_warning("请编辑.env文件中的SECRET_KEY等配置！")
            return True
        except Exception as e:
            self.print_error(f"创建.env文件失败: {e}")
            return False
    
    def load_environment_variables(self) -> Dict[str, str]:
        """加载环境变量"""
        env_vars = {}
        
        if self.env_file.exists():
            try:
                with open(self.env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            if '=' in line:
                                key, value = line.split('=', 1)
                                env_vars[key.strip()] = value.strip()
                                os.environ[key.strip()] = value.strip()
            except Exception as e:
                self.print_warning(f"加载.env文件失败: {e}")
        
        # 设置默认值
        for key, default_value in self.default_config.items():
            if key not in env_vars:
                env_vars[key] = default_value
                os.environ[key] = default_value
        
        return env_vars
    
    def check_port_availability(self, port: int) -> bool:
        """检查端口是否可用"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', port))
                return result != 0
        except Exception:
            return False
    
    def kill_process_on_port(self, port: int) -> bool:
        """终止占用端口的进程"""
        try:
            if self.is_windows:
                # Windows: 使用netstat和taskkill
                result = self.run_command(
                    ['netstat', '-ano'], capture_output=True
                )
                for line in result.stdout.split('\n'):
                    if f':{port}' in line and 'LISTENING' in line:
                        parts = line.split()
                        if len(parts) >= 5:
                            pid = parts[-1]
                            self.run_command(['taskkill', '/F', '/PID', pid], capture_output=True)
                            self.print_success(f"已终止进程 PID: {pid}")
                            return True
            else:
                # Linux/macOS: 使用lsof和kill
                result = self.run_command(
                    ['lsof', '-ti', f':{port}'], capture_output=True
                )
                if result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        self.run_command(['kill', '-9', pid], capture_output=True)
                        self.print_success(f"已终止进程 PID: {pid}")
                    return True
        except Exception as e:
            self.print_warning(f"终止进程失败: {e}")
        
        return False
    
    def run_database_migrations(self, settings: str) -> bool:
        """运行数据库迁移"""
        try:
            self.print_info("运行数据库迁移...")
            self.run_command([
                str(self.python_exe), 'manage.py', 'migrate',
                f'--settings={settings}', '--verbosity=1'
            ])
            self.print_success("数据库迁移完成")
            return True
        except subprocess.CalledProcessError as e:
            self.print_error("数据库迁移失败")
            self.print_error(f"错误详情: {e}")
            self.print_error("可能的原因:")
            self.print_error("1. 数据库服务未启动")
            self.print_error("2. 数据库用户或密码错误")
            self.print_error("3. 数据库用户权限不足")
            self.print_error("4. 数据库连接配置错误")
            self.print_info("解决方法:")
            self.print_info("- 确保MySQL服务正在运行")
            self.print_info("- 检查.env文件中的数据库配置")
            self.print_info("- 确保数据库用户存在且密码正确")
            self.print_info("- 运行以下SQL命令创建数据库和用户:")
            self.print_info("  CREATE DATABASE IF NOT EXISTS meowsite_prod CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            self.print_info("  CREATE USER IF NOT EXISTS 'meow_user'@'localhost' IDENTIFIED BY 'meow123456';")
            self.print_info("  GRANT ALL PRIVILEGES ON meowsite_prod.* TO 'meow_user'@'localhost';")
            self.print_info("  FLUSH PRIVILEGES;")
            return False
    
    def collect_static_files(self, settings: str) -> bool:
        """收集静态文件"""
        try:
            self.print_info("收集静态文件...")
            self.run_command([
                str(self.python_exe), 'manage.py', 'collectstatic',
                '--noinput', f'--settings={settings}', '--verbosity=0'
            ])
            self.print_success("静态文件收集完成")
            return True
        except subprocess.CalledProcessError:
            self.print_warning("静态文件收集失败，但继续启动服务器")
            return True
    
    def create_superuser(self) -> bool:
        """创建超级用户"""
        try:
            self.print_info("检查超级用户...")
            result = self.run_command([
                str(self.python_exe), 'create_admin.py'
            ], capture_output=True)
            
            if 'CREATE' in result.stdout:
                self.print_success("已创建默认超级用户: admin / admin123")
                self.print_warning("请立即登录管理面板修改密码！")
            else:
                self.print_info("超级用户已存在，跳过创建")
            return True
        except subprocess.CalledProcessError:
            self.print_warning("超级用户创建检查失败")
            return True
    
    def detect_server_type(self) -> tuple[str, List[str]]:
        """检测可用的服务器类型"""
        # 检查Waitress (Windows推荐)
        if self.is_windows:
            try:
                self.run_command([str(self.python_exe), '-c', 'import waitress'], capture_output=True)
                # 使用Python模块方式调用waitress
                return 'waitress', [str(self.python_exe), '-m', 'waitress', '--host=0.0.0.0', '--port=8000', 'meowsite.wsgi:application']
            except subprocess.CalledProcessError:
                pass
        
        # 检查Gunicorn (Linux/macOS推荐)
        try:
            self.run_command([str(self.python_exe), '-c', 'import gunicorn'], capture_output=True)
            return 'gunicorn', [str(self.python_exe), '-m', 'gunicorn', '-c', 'gunicorn.conf.py', 'meowsite.wsgi:application']
        except subprocess.CalledProcessError:
            pass
        
        # 回退到Django开发服务器
        self.print_warning("未找到生产级WSGI服务器，使用Django开发服务器")
        self.print_warning("生产环境不推荐使用开发服务器！")
        return 'django', [str(self.python_exe), 'manage.py', 'runserver', '0.0.0.0:8000', '--settings=meowsite.settings_production']
    
    def deploy(self) -> bool:
        """部署应用"""
        self.print_header("Meow Blog 部署")
        
        # 检查Python
        if not self.check_python():
            return False
        
        # 创建虚拟环境
        if not self.create_virtual_environment():
            return False
        
        # 安装依赖
        if not self.install_dependencies():
            return False
        
        # 设置环境文件
        if not self.setup_environment_file('production'):
            return False
        
        # 运行数据库迁移
        if not self.run_database_migrations('meowsite.settings_production'):
            return False
        
        # 收集静态文件
        self.collect_static_files('meowsite.settings_production')
        
        # 创建超级用户
        self.create_superuser()
        
        # 加载环境变量
        env_vars = self.load_environment_variables()
        
        self.print_header("部署完成")
        self.print_success(f"访问地址: http://{env_vars['EXTERNAL_HOST']}:{env_vars['EXTERNAL_PORT']}")
        self.print_success(f"管理面板: http://{env_vars['EXTERNAL_HOST']}:{env_vars['EXTERNAL_PORT']}/admin")
        self.print_info("下一步:")
        self.print_info("  开发环境: python meowsite_manager.py dev")
        self.print_info("  生产环境: python meowsite_manager.py prod")
        
        return True
    
    def start_development_server(self) -> bool:
        """启动开发服务器"""
        self.print_header("Meow Blog 开发服务器")
        
        # 检查虚拟环境
        if not self.venv_path.exists():
            self.print_error("虚拟环境不存在")
            self.print_info("请先运行: python meowsite_manager.py deploy")
            return False
        
        # 检查虚拟环境是否可用
        if not self.is_virtual_environment_valid():
            self.print_error("虚拟环境不可用")
            self.print_info("请重新运行: python meowsite_manager.py deploy")
            return False
        
        # 加载环境变量
        env_vars = self.load_environment_variables()
        port = int(env_vars['PORT'])
        
        # 检查端口
        if not self.check_port_availability(port):
            self.print_warning(f"端口 {port} 被占用，尝试释放...")
            if not self.kill_process_on_port(port):
                self.print_error(f"无法释放端口 {port}")
                return False
        
        # 运行数据库迁移
        self.run_database_migrations('meowsite.settings_dev')
        
        self.print_header("开发服务器启动")
        self.print_success(f"本地访问: http://127.0.0.1:{port}")
        self.print_success(f"外部访问: http://{env_vars['EXTERNAL_HOST']}:{env_vars['EXTERNAL_PORT']}")
        self.print_success(f"管理面板: http://127.0.0.1:{port}/admin")
        self.print_info("测试用户:")
        self.print_info("  Admin: admin / admin123")
        self.print_info("  User: meow / meow123")
        self.print_info("按 Ctrl+C 停止服务器")
        
        try:
            # 启动开发服务器
            self.run_command([
                str(self.python_exe), 'manage.py', 'runserver',
                f'0.0.0.0:{port}', '--settings=meowsite.settings_dev'
            ], check=False)
        except KeyboardInterrupt:
            self.print_info("服务器已停止")
        
        return True
    
    def start_production_server(self) -> bool:
        """启动生产服务器"""
        self.print_header("Meow Blog 生产服务器")
        
        # 检查虚拟环境
        if not self.venv_path.exists():
            self.print_error("虚拟环境不存在")
            self.print_info("请先运行: python meowsite_manager.py deploy")
            return False
        
        # 检查虚拟环境是否可用
        if not self.is_virtual_environment_valid():
            self.print_error("虚拟环境不可用")
            self.print_info("请重新运行: python meowsite_manager.py deploy")
            return False
        
        # 加载环境变量
        env_vars = self.load_environment_variables()
        port = int(env_vars['PORT'])
        
        # 检查端口
        if not self.check_port_availability(port):
            self.print_warning(f"端口 {port} 被占用，尝试释放...")
            if not self.kill_process_on_port(port):
                self.print_error(f"无法释放端口 {port}")
                return False
        
        # 运行数据库迁移
        if not self.run_database_migrations('meowsite.settings_production'):
            return False
        
        # 收集静态文件
        self.collect_static_files('meowsite.settings_production')
        
        # 检测服务器类型
        server_type, server_cmd = self.detect_server_type()
        
        self.print_header("生产服务器启动")
        self.print_success(f"服务器类型: {server_type}")
        self.print_success(f"本地访问: http://127.0.0.1:{port}")
        self.print_success(f"外部访问: http://{env_vars['EXTERNAL_HOST']}:{env_vars['EXTERNAL_PORT']} (via nginx)")
        self.print_success(f"管理面板: http://{env_vars['EXTERNAL_HOST']}:{env_vars['EXTERNAL_PORT']}/admin (via nginx)")
        self.print_info("重要提示:")
        self.print_info("- 生产环境使用HTTPS (via nginx)")
        self.print_info("- 静态文件由nginx提供")
        self.print_info("- 日志文件位置: logs/")
        if server_type == 'django':
            self.print_warning("- 警告: 使用开发服务器 - 生产环境不推荐！")
        self.print_info("按 Ctrl+C 停止服务器")
        
        try:
            # 启动生产服务器
            self.run_command(server_cmd, check=False)
        except KeyboardInterrupt:
            self.print_info("服务器已停止")
        
        return True


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print(f"""
{Colors.BOLD}Meow Blog 跨平台管理脚本{Colors.END}

{Colors.CYAN}用法:{Colors.END}
  python meowsite_manager.py <命令>

{Colors.CYAN}命令:{Colors.END}
  {Colors.GREEN}deploy{Colors.END}  - 部署应用（首次安装或重新部署）
  {Colors.GREEN}dev{Colors.END}    - 启动开发服务器
  {Colors.GREEN}prod{Colors.END}   - 启动生产服务器

{Colors.CYAN}示例:{Colors.END}
  python meowsite_manager.py deploy
  python meowsite_manager.py dev
  python meowsite_manager.py prod

{Colors.CYAN}支持平台:{Colors.END}
  Windows, Linux, macOS
        """)
        return 1
    
    manager = MeowSiteManager()
    command = sys.argv[1].lower()
    
    try:
        if command == 'deploy':
            success = manager.deploy()
        elif command == 'dev':
            success = manager.start_development_server()
        elif command == 'prod':
            success = manager.start_production_server()
        else:
            print(f"{Colors.RED}未知命令: {command}{Colors.END}")
            print(f"{Colors.YELLOW}可用命令: deploy, dev, prod{Colors.END}")
            return 1
        
        return 0 if success else 1
    
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}操作被用户中断{Colors.END}")
        return 1
    except Exception as e:
        print(f"\n{Colors.RED}发生错误: {e}{Colors.END}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
