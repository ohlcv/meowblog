#!/usr/bin/env python3
"""
日志查看工具
用于快速查看和监控应用日志

使用方法:
python log_viewer.py                                    # 查看最近50条应用日志
python log_viewer.py --type error                       # 查看最近50条错误日志
python log_viewer.py --type security                    # 查看最近50条安全日志
python log_viewer.py --tail                            # 实时监控应用日志
python log_viewer.py --lines 100                       # 查看最近100条日志
python log_viewer.py --env dev                         # 查看开发环境日志
python log_viewer.py --env production                  # 查看生产环境日志
"""
import os
import argparse
import time
from pathlib import Path

def get_log_path(log_type='app', environment='dev'):
    """获取日志文件路径"""
    base_dir = Path(__file__).resolve().parent
    
    # 根据环境选择日志目录
    if environment == 'production':
        log_dir = Path('C:/var/log/meowsite')
    else:
        log_dir = base_dir / 'logs'  # 统一使用logs目录
    
    log_files = {
        'app': log_dir / 'django.log',
        'error': log_dir / 'error.log', 
        'security': log_dir / 'security.log',
        'db': log_dir / 'db.log'
    }
    
    return log_files.get(log_type, log_files['app'])

def read_log_lines(file_path, lines=50):
    """读取日志文件的最后N行"""
    if not file_path.exists():
        print(f"日志文件不存在: {file_path}")
        return []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            return all_lines[-lines:] if len(all_lines) > lines else all_lines
    except Exception as e:
        print(f"读取日志文件失败: {e}")
        return []

def tail_log(file_path):
    """实时监控日志文件"""
    if not file_path.exists():
        print(f"日志文件不存在: {file_path}")
        return
    
    print(f"正在监控日志文件: {file_path}")
    print("按 Ctrl+C 停止监控\n")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # 定位到文件末尾
            f.seek(0, 2)
            
            while True:
                line = f.readline()
                if line:
                    print(line.rstrip())
                else:
                    time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n监控已停止")
    except Exception as e:
        print(f"监控失败: {e}")

def format_log_output(lines, log_type):
    """格式化日志输出"""
    if not lines:
        print(f"没有找到 {log_type} 日志")
        return
    
    print(f"=== {log_type.upper()} 日志 (最近 {len(lines)} 条) ===\n")
    
    for line in lines:
        line = line.rstrip()
        if not line:
            continue
            
        # 根据日志级别添加颜色标识
        if 'ERROR' in line:
            print(f"🔴 {line}")
        elif 'WARNING' in line:
            print(f"🟡 {line}")
        elif 'INFO' in line:
            print(f"🔵 {line}")
        else:
            print(f"⚪ {line}")

def show_log_summary(environment='dev'):
    """显示日志文件摘要"""
    log_types = ['app', 'error', 'security', 'db']
    
    print(f"=== {environment.upper()} 环境日志文件状态摘要 ===\n")
    
    for log_type in log_types:
        log_path = get_log_path(log_type, environment)
        if log_path.exists():
            file_size = log_path.stat().st_size
            file_size_mb = file_size / (1024 * 1024)
            
            # 统计最近的错误和警告数量
            recent_lines = read_log_lines(log_path, 100)
            error_count = sum(1 for line in recent_lines if 'ERROR' in line)
            warning_count = sum(1 for line in recent_lines if 'WARNING' in line)
            
            print(f"📁 {log_type.upper()} 日志:")
            print(f"   路径: {log_path}")
            print(f"   文件大小: {file_size_mb:.2f} MB")
            print(f"   最近100条中 - 错误: {error_count}, 警告: {warning_count}")
            print()
        else:
            print(f"📁 {log_type.upper()} 日志: 文件不存在")
            print(f"   路径: {log_path}")
            print()

def main():
    parser = argparse.ArgumentParser(description='Django应用日志查看工具')
    parser.add_argument('--type', choices=['app', 'error', 'security', 'db'], 
                       default='app', help='日志类型 (默认: app)')
    parser.add_argument('--lines', type=int, default=50, 
                       help='显示的行数 (默认: 50)')
    parser.add_argument('--tail', action='store_true', 
                       help='实时监控日志')
    parser.add_argument('--summary', action='store_true',
                       help='显示所有日志文件的摘要信息')
    parser.add_argument('--env', choices=['dev', 'production'], 
                       default='dev', help='环境类型 (默认: dev)')
    
    args = parser.parse_args()
    
    if args.summary:
        show_log_summary(args.env)
        return
    
    log_path = get_log_path(args.type, args.env)
    
    if args.tail:
        tail_log(log_path)
    else:
        lines = read_log_lines(log_path, args.lines)
        format_log_output(lines, args.type)

if __name__ == '__main__':
    main()