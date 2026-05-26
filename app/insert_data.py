import mysql.connector
import os
from mysql.connector import Error
from faker import Faker
import random

def create_connection():
    """建立数据库连接"""
    try:
        conn = mysql.connector.connect(
            host= os.getenv('DB_HOST', 'localhost'),
            user= os.getenv('DB_USER', 'root'),
            password= os.getenv('DB_PASS', 'Root@123456'),
            database= os.getenv('DB_NAME', 'testdb')  # 这次直接连 testdb 库
        )
        if conn.is_connected():
            print("✅ 数据库连接成功！")
            return conn
    except Error as e:
        print(f"❌ 连接失败: {e}")
        return None

def insert_fake_users(conn, num_users=10):
    """插入 10 条虚假用户数据"""
    fake = Faker('zh_CN')  # 使用中文数据生成器
    cursor = conn.cursor()
    
    # SQL 插入语句
    insert_query = """
    INSERT INTO users (name, gender, age) 
    VALUES (%s, %s, %s)
    """
    
    print(f"🚀 开始生成 {num_users} 条用户数据...")
    
    for i in range(num_users):
        # 生成随机数据
        name = fake.name()
        
        # 随机生成性别 (数据库里存的是 '男' 或 '女')
        gender = random.choice(['男', '女'])
        
        # 随机生成年龄 (18 到 60 岁之间)
        age = random.randint(18, 60)
        
        # 将数据打包成元组
        record = (name, gender, age)
        
        try:
            cursor.execute(insert_query, record)
            print(f"   [{i+1}] 插入成功: {name}, {gender}, {age}")
        except Error as e:
            print(f"   [{i+1}] 插入失败: {e}")
            
    # 提交事务（非常重要，不然数据不会真正存入数据库）
    conn.commit()
    print(f"🎉 数据插入完成！共插入 {cursor.rowcount} 条记录。")

if __name__ == "__main__":
    connection = create_connection()
    if connection:
        insert_fake_users(connection, 10)
        connection.close()
        print("🔌 数据库连接已关闭。")