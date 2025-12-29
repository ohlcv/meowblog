"""
日志管理Django命令
提供日志清理、归档等功能

使用方法:
python manage.py logmanage --clean        # 清理旧日志
python manage.py logmanage --archive      # 归档日志
python manage.py logmanage --status       # 查看日志状态
"""
from django.core.management.base import BaseCommand
from django.conf import settings
import os
import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path


class Command(BaseCommand):
    help = '管理应用日志文件'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clean',
            action='store_true',
            help='清理30天前的日志文件',
        )
        parser.add_argument(
            '--archive',
            action='store_true',
            help='压缩归档7天前的日志文件',
        )
        parser.add_argument(
            '--status',
            action='store_true',
            help='显示日志文件状态',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='清理多少天前的日志文件 (默认: 30)',
        )

    def handle(self, *args, **options):
        log_dir = getattr(settings, 'LOG_DIR', Path(settings.BASE_DIR) / 'logs')
        
        if not log_dir.exists():
            self.stdout.write(
                self.style.WARNING(f'日志目录不存在: {log_dir}')
            )
            return

        if options['status']:
            self.show_log_status(log_dir)
        elif options['clean']:
            self.clean_old_logs(log_dir, options['days'])
        elif options['archive']:
            self.archive_logs(log_dir)
        else:
            self.stdout.write(
                self.style.WARNING('请指定操作: --clean, --archive 或 --status')
            )

    def show_log_status(self, log_dir):
        """显示日志文件状态"""
        self.stdout.write(
            self.style.SUCCESS('=== 日志文件状态 ===')
        )
        
        log_files = ['app.log', 'error.log', 'security.log', 'db.log']
        total_size = 0
        
        for log_file in log_files:
            log_path = log_dir / log_file
            if log_path.exists():
                file_size = log_path.stat().st_size
                file_size_mb = file_size / (1024 * 1024)
                total_size += file_size
                
                # 获取文件修改时间
                mtime = datetime.fromtimestamp(log_path.stat().st_mtime)
                
                self.stdout.write(
                    f"📁 {log_file}: {file_size_mb:.2f} MB "
                    f"(修改时间: {mtime.strftime('%Y-%m-%d %H:%M:%S')})"
                )
                
                # 统计最近的日志条目
                try:
                    with open(log_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        recent_lines = lines[-100:] if len(lines) > 100 else lines
                        error_count = sum(1 for line in recent_lines if 'ERROR' in line)
                        warning_count = sum(1 for line in recent_lines if 'WARNING' in line)
                        
                        if error_count > 0 or warning_count > 0:
                            self.stdout.write(
                                f"   最近100条: {error_count} 错误, {warning_count} 警告"
                            )
                except Exception:
                    pass
            else:
                self.stdout.write(f"📁 {log_file}: 不存在")
        
        total_size_mb = total_size / (1024 * 1024)
        self.stdout.write(f"\n总大小: {total_size_mb:.2f} MB")
        
        # 检查归档文件
        archive_files = list(log_dir.glob('*.log.*.gz'))
        if archive_files:
            self.stdout.write(f"\n归档文件: {len(archive_files)} 个")

    def clean_old_logs(self, log_dir, days):
        """清理旧日志文件"""
        cutoff_date = datetime.now() - timedelta(days=days)
        cleaned_count = 0
        
        self.stdout.write(
            self.style.WARNING(f'清理 {days} 天前的日志文件...')
        )
        
        # 清理归档文件
        for archive_file in log_dir.glob('*.log.*.gz'):
            try:
                file_time = datetime.fromtimestamp(archive_file.stat().st_mtime)
                if file_time < cutoff_date:
                    archive_file.unlink()
                    cleaned_count += 1
                    self.stdout.write(f"已删除: {archive_file.name}")
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"删除失败 {archive_file.name}: {e}")
                )
        
        if cleaned_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'已清理 {cleaned_count} 个旧日志文件')
            )
        else:
            self.stdout.write('没有找到需要清理的旧日志文件')

    def archive_logs(self, log_dir):
        """归档日志文件"""
        archive_date = datetime.now() - timedelta(days=7)
        archived_count = 0
        
        self.stdout.write('归档7天前的日志文件...')
        
        log_files = ['app.log', 'error.log', 'security.log', 'db.log']
        
        for log_file in log_files:
            log_path = log_dir / log_file
            if not log_path.exists():
                continue
                
            try:
                file_time = datetime.fromtimestamp(log_path.stat().st_mtime)
                if file_time < archive_date and log_path.stat().st_size > 0:
                    # 创建归档文件名
                    timestamp = file_time.strftime('%Y%m%d_%H%M%S')
                    archive_name = f"{log_file}.{timestamp}.gz"
                    archive_path = log_dir / archive_name
                    
                    # 压缩文件
                    with open(log_path, 'rb') as f_in:
                        with gzip.open(archive_path, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    
                    # 清空原文件
                    log_path.write_text('')
                    
                    archived_count += 1
                    self.stdout.write(f"已归档: {log_file} -> {archive_name}")
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"归档失败 {log_file}: {e}")
                )
        
        if archived_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'已归档 {archived_count} 个日志文件')
            )
        else:
            self.stdout.write('没有找到需要归档的日志文件')
