import mysql.connector
import os
from datetime import datetime, timezone  # 添加 timezone

# --- 配置读取 ---
DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASS = os.getenv('DB_PASS', 'Root@123456')
DB_NAME = os.getenv('DB_NAME', 'testdb')

def get_connection():
    """获取数据库连接"""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME,
            charset='utf8mb4'
        )
        return conn
    except mysql.connector.Error as e:
        print(f"❌ 连接数据库失败: {e}")
        return None

def create_connection_no_db():
    """连接MySQL服务器（不指定数据库）"""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS
        )
        return conn
    except mysql.connector.Error as e:
        print(f"❌ 连接服务器失败: {e}")
        return None

def setup_database_and_tables():
    conn = create_connection_no_db()
    if not conn:
        return

    cursor = conn.cursor()
    
    # 1. 创建数据库
    cursor.execute("CREATE DATABASE IF NOT EXISTS testdb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    cursor.execute("USE testdb;")
    
    # 2. 创建 users 表（完整结构）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            phone VARCHAR(20) UNIQUE NOT NULL COMMENT '手机号',
            password_hash VARCHAR(255) COMMENT '加密密码',
            salt VARCHAR(32) COMMENT '盐值',
            nickname VARCHAR(50) DEFAULT '用户' COMMENT '昵称',
            avatar_url VARCHAR(255) DEFAULT NULL COMMENT '头像地址',
            gender TINYINT DEFAULT 0 COMMENT '0未知 1男 2女',
            birthday DATE DEFAULT NULL COMMENT '生日',
            status TINYINT DEFAULT 1 COMMENT '1正常 0冻结',
            login_fail_count INT DEFAULT 0 COMMENT '登录失败次数',
            locked_until DATETIME DEFAULT NULL COMMENT '锁定截止时间',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_phone (phone)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    
    # 3. 创建短信验证码表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sms_verification_codes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            phone VARCHAR(20) NOT NULL COMMENT '手机号',
            code VARCHAR(6) NOT NULL COMMENT '验证码',
            ip_address VARCHAR(45) DEFAULT NULL COMMENT '请求IP',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at DATETIME NOT NULL COMMENT '过期时间',
            used TINYINT DEFAULT 0 COMMENT '0未使用 1已使用',
            INDEX idx_phone (phone),
            INDEX idx_expires (expires_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ 数据库和表初始化完成！")

if __name__ == "__main__":
    setup_database_and_tables()