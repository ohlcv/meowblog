#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MySQL数据库初始化脚本
用于自动创建Meow Blog博客系统所需的数据库和用户

使用方法:
1. 确保已安装mysql-connector-python: pip install mysql-connector-python
2. 运行脚本: python setup_mysql.py
3. 按提示输入MySQL root用户密码和要创建的用户密码
4. 脚本会自动创建数据库、用户并设置权限
"""

import mysql.connector
from mysql.connector import Error
import getpass

def create_database_and_user():
    """创建数据库和用户"""
    
    # 数据库配置（可根据需要修改）
    db_config = {
        'host': 'localhost',
        'port': 3306,
        'database_name': 'meowsite_prod',
        'username': 'meow',
        'charset': 'utf8mb4'
    }
    
    print("=== Meow Blog MySQL数据库初始化脚本 ===\n")
    
    # 获取MySQL root用户密码
    print("请输入MySQL root用户的密码:")
    root_password = getpass.getpass("Root密码: ")
    
    # 获取要创建的数据库用户密码
    print(f"\n请输入要创建的数据库用户 '{db_config['username']}' 的密码:")
    user_password = getpass.getpass("用户密码: ")
    confirm_password = getpass.getpass("确认密码: ")
    
    if user_password != confirm_password:
        print("❌ 错误: 两次输入的密码不一致!")
        return False
    
    if not user_password:
        print("❌ 错误: 密码不能为空!")
        return False
    
    # 保存配置信息用于后续提示
    db_config['password'] = user_password
    
    try:
        # 连接到MySQL服务器（使用root用户）
        print(f"\n正在连接到MySQL服务器 ({db_config['host']}:{db_config['port']})...")
        connection = mysql.connector.connect(
            host=db_config['host'],
            port=db_config['port'],
            user='root',
            password=root_password
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # 创建数据库
            print(f"正在创建数据库 '{db_config['database_name']}'...")
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_config['database_name']}` "
                          f"CHARACTER SET {db_config['charset']} COLLATE {db_config['charset']}_unicode_ci")
            
            # 创建用户并授权
            print(f"正在创建用户 '{db_config['username']}' 并授权...")
            cursor.execute(f"CREATE USER IF NOT EXISTS '{db_config['username']}'@'localhost' "
                          f"IDENTIFIED WITH mysql_native_password BY %s", (user_password,))
            cursor.execute(f"GRANT ALL PRIVILEGES ON `{db_config['database_name']}`.* "
                          f"TO '{db_config['username']}'@'localhost'")
            
            # 刷新权限
            print("正在刷新权限...")
            cursor.execute("FLUSH PRIVILEGES")
            
            # 验证数据库和用户创建成功
            cursor.execute("SHOW DATABASES LIKE %s", (db_config['database_name'],))
            db_exists = cursor.fetchone()
            
            cursor.execute("SELECT User FROM mysql.user WHERE User=%s AND Host='localhost'", 
                          (db_config['username'],))
            user_exists = cursor.fetchone()
            
            if db_exists and user_exists:
                print("\n✅ 数据库和用户创建成功!")
                print(f"   数据库名称: {db_config['database_name']}")
                print(f"   用户名: {db_config['username']}")
                print(f"   主机: {db_config['host']}")
                print(f"   端口: {db_config['port']}")
                print(f"   字符集: {db_config['charset']}")
                
                # 生成环境变量配置提示
                print("\n📋 请在您的 .env 文件中添加以下配置:")
                print(f"DB_NAME={db_config['database_name']}")
                print(f"DB_USER={db_config['username']}")
                print(f"DB_PASSWORD={user_password}")
                print(f"DB_HOST={db_config['host']}")
                print(f"DB_PORT={db_config['port']}")
                
                return True
            else:
                print("❌ 数据库或用户创建失败!")
                return False
                
    except Error as e:
        print(f"❌ MySQL连接错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 脚本执行错误: {e}")
        return False
    finally:
        # 关闭连接
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("\nMySQL连接已关闭")

def main():
    """主函数"""
    try:
        success = create_database_and_user()
        if success:
            print("\n🎉 MySQL数据库初始化完成!")
            print("接下来请执行以下步骤:")
            print("1. 在项目根目录下运行: pip install PyMySQL cryptography")
            print("2. 在项目根目录下运行: python manage.py migrate --settings=meowsite.settings_production")
            print("3. 启动服务器: python manage.py runserver --settings=meowsite.settings_production")
        else:
            print("\n💥 MySQL数据库初始化失败，请检查错误信息并重试!")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  用户取消操作")
    except Exception as e:
        print(f"\n💥 脚本执行出错: {e}")

if __name__ == "__main__":
    main()