import mysql.connector
import os
from mysql.connector import Error

def create_connection_no_db():
    """先连接 MySQL 服务器（不指定具体数据库）"""
    try:
        conn = mysql.connector.connect(
            host= os.getenv('DB_HOST', 'localhost'), # 注意：这里没有 database 参数
            user= os.getenv('DB_USER', 'root'),
            password= os.getenv('DB_PASS', 'Root@123456')
        )
        if conn.is_connected():
            print("✅ 数据库连接成功！")
            return conn
    except Error as e:
        print(f"❌ 连接失败: {e}")
        return None

def setup_database_and_table(conn):
    """创建数据库和表"""
    try:
        cursor = conn.cursor()
        
        # 1. 创建数据库（如果不存在）
        print("🚀 正在创建数据库 'testdb'...")
        cursor.execute("CREATE DATABASE IF NOT EXISTS testdb;")
        
        # 2. 使用该数据库
        cursor.execute("USE testdb;")
        
        # 3. 创建用户表
        print("📝 正在创建表 'users'...")
        create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL COMMENT '姓名',
            gender ENUM('男', '女', '未知') DEFAULT '未知' COMMENT '性别',
            age INT COMMENT '年龄'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        cursor.execute(create_users_table)
        conn.commit()
        print("🎉 数据库和表创建成功！")
        
    except Error as e:
        print(f"❌ 操作失败: {e}")

if __name__ == "__main__":
    connection = create_connection_no_db()
    if connection:
        setup_database_and_table(connection)
        connection.close()
        print("🔌 连接已关闭。")