import mysql.connector
import os
from mysql.connector import Error

# --- 配置读取 ---
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_NAME = os.getenv('DB_NAME')

# 校验：确保环境变量存在
if not all([DB_HOST, DB_USER, DB_PASS, DB_NAME]):
    raise RuntimeError(
        "❌ 缺少数据库环境变量！请检查 DB_HOST, DB_USER, DB_PASS, DB_NAME"
    )

# --- 连接管理 ---
def get_connection():
    """获取数据库连接（针对 testdb 进行操作）"""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME,
            charset='utf8mb4'
        )
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"❌ 连接数据库 {DB_NAME} 失败: {e}")
        return None

def create_connection_no_db():
    """先连接 MySQL 服务器（不指定具体数据库，用于初始化）"""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS
        )
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"❌ 连接服务器失败: {e}")
        return None

# --- 初始化逻辑 ---
def setup_database_and_table(conn):
    """创建数据库和表（你原有的逻辑）"""
    try:
        cursor = conn.cursor()
        print("🚀 正在创建数据库 'testdb'...")
        cursor.execute("CREATE DATABASE IF NOT EXISTS testdb;")
        cursor.execute("USE testdb;")
        
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
        print("🎉 数据库和表就绪！")
    except Error as e:
        print(f"❌ 初始化失败: {e}")

# --- CRUD 业务操作 ---

def get_all_users():
    """[R] 读取：获取所有用户"""
    conn = get_connection()
    if not conn: return []
    try:
        cursor = conn.cursor(dictionary=True) # 返回字典，方便前端渲染
        cursor.execute("SELECT id, name, gender, age FROM users ORDER BY id DESC")
        return cursor.fetchall()
    except Error as e:
        print(f"查询失败: {e}")
        return []
    finally:
        if conn.is_connected(): conn.close()

def get_user_by_id(user_id):
    """[R] 读取：获取单个用户详情（用于编辑页）"""
    conn = get_connection()
    if not conn: return None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, gender, age FROM users WHERE id = %s", (user_id,))
        return cursor.fetchone()
    except Error as e:
        print(f"查询失败: {e}")
        return None
    finally:
        if conn.is_connected(): conn.close()

def add_user(name, gender, age):
    """[C] 创建：添加用户"""
    conn = get_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        # 注意：这里加了 gender 字段
        sql = "INSERT INTO users (name, gender, age) VALUES (%s, %s, %s)"
        cursor.execute(sql, (name, gender, age))
        conn.commit()
        return True
    except Error as e:
        print(f"添加失败: {e}")
        return False
    finally:
        if conn.is_connected(): conn.close()

def update_user(user_id, name, gender, age):
    """[U] 更新：修改用户"""
    conn = get_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        sql = "UPDATE users SET name=%s, gender=%s, age=%s WHERE id=%s"
        cursor.execute(sql, (name, gender, age, user_id))
        conn.commit()
        return True
    except Error as e:
        print(f"更新失败: {e}")
        return False
    finally:
        if conn.is_connected(): conn.close()

def delete_user(user_id):
    """[D] 删除：删除用户"""
    conn = get_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        sql = "DELETE FROM users WHERE id = %s"
        cursor.execute(sql, (user_id,))
        conn.commit()
        return True
    except Error as e:
        print(f"删除失败: {e}")
        return False
    finally:
        if conn.is_connected(): conn.close()

if __name__ == "__main__":
    # 本地测试初始化
    conn = create_connection_no_db()
    if conn:
        setup_database_and_table(conn)
        conn.close()