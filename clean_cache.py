import os
import shutil
import fnmatch  # 用于更强大的通配符匹配

# 要删除的缓存目录
CACHE_DIRS = [
    "__pycache__",
    # "venv", ".venv", "env", ".env",  # 虚拟环境目录
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".flake8_cache",
    ".coverage",  # 测试覆盖率缓存
    # "build", "dist",  # 打包产物
    "*.egg-info",  # Python包信息目录
    ".tox",  # tox测试环境
    ".idea", ".vscode",  # 编辑器缓存（可选，根据需求保留）
]

# 要删除的缓存文件（支持通配符）
CACHE_FILES = [
    # Python编译文件
    # "*.pyc", "*.pyo", "*.pyd",
    # C扩展模块
    "*.so",
    # 测试/覆盖率相关
    ".coverage", "coverage.xml",
    # 系统垃圾文件
    ".DS_Store",  # macOS
    "Thumbs.db",  # Windows
    "*.swp", "*.swo",  # Vim临时文件
    # 打包/安装残留
    "*.egg", "*.egg-info",
    # 日志文件（如果需要清理）
    "*.log",
]

def should_delete(path):
    """判断文件/目录是否需要删除"""
    name = os.path.basename(path)
    
    if os.path.isdir(path):
        # 检查目录是否匹配（支持通配符，如*__pycache__）
        return any(fnmatch.fnmatch(name, pattern) for pattern in CACHE_DIRS)
    
    # 检查文件是否匹配（支持通配符）
    return any(fnmatch.fnmatch(name, pattern) for pattern in CACHE_FILES)

def delete_cache(root):
    deleted = []
    # 从子目录开始删除，避免目录删除后影响父目录扫描
    for dirpath, dirnames, filenames in os.walk(root, topdown=False):
        # 处理文件
        for name in filenames:
            filepath = os.path.join(dirpath, name)
            if should_delete(filepath):
                try:
                    os.remove(filepath)
                    deleted.append(filepath)
                except Exception as e:
                    print(f"❌ 删除文件失败: {filepath} -> {e}")
        
        # 处理目录
        for name in dirnames:
            dirpath_full = os.path.join(dirpath, name)
            if should_delete(dirpath_full):
                try:
                    shutil.rmtree(dirpath_full)
                    deleted.append(dirpath_full)
                except Exception as e:
                    print(f"❌ 删除目录失败: {dirpath_full} -> {e}")
    return deleted

if __name__ == "__main__":
    print("🚀 开始清理缓存...")
    root_dir = os.getcwd()  # 当前目录
    deleted_items = delete_cache(root_dir)
    
    if deleted_items:
        print("\n✅ 已删除以下项目：")
        for item in deleted_items:
            print(f"- {item}")
        print(f"\n📊 共删除 {len(deleted_items)} 个缓存项")
    else:
        print("\n✨ 没有需要清理的缓存项")
