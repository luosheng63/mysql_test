import mysql.connector
from sshtunnel import SSHTunnelForwarder
import time
import os

# --- 1. 配置信息 ---
DOCKER_DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'db'), # 在 Docker Compose 里运行时，DB_HOST 是 'db'
    'user': 'root',
    'password': 'Root@123456',
    'database': 'testdb',
    'charset': 'utf8mb4'
}

# VM 的 SSH 信息
SSH_CONFIG = {
    'ssh_address_or_host': ('192.168.227.128', 22),
    'ssh_username': 'luosheng',
    'ssh_password': '你的luosheng密码', # 或者改用私钥路径 ssh_pkey
    'remote_bind_address': ('127.0.0.1', 3306) # VM 本地的 MySQL
}

def sync_data():
    print(f"[{time.strftime('%H:%M:%S')}] 开始同步数据...")
    
    try:
        # 建立 SSH 隧道
        with SSHTunnelForwarder(
            ssh_address_or_host=SSH_CONFIG['ssh_address_or_host'],
            ssh_username=SSH_CONFIG['ssh_username'],
            ssh_password=SSH_CONFIG['ssh_password'],
            remote_bind_address=SSH_CONFIG['remote_bind_address']
        ) as tunnel:
            
            # 配置 VM 数据库连接（通过隧道本地端口）
            vm_db_config = {
                'host': '127.0.0.1',
                'port': tunnel.local_bind_port,
                'user': 'root',
                'password': 'Root@123456', # 注意：这是 VM 里 MySQL 的密码
                'database': 'testdb',
                'charset': 'utf8mb4'
            }
            
            # 连接 Docker 数据库（源）
            docker_conn = mysql.connector.connect(**DOCKER_DB_CONFIG)
            docker_cursor = docker_conn.cursor(dictionary=True)
            
            # 连接 VM 数据库（目标）
            vm_conn = mysql.connector.connect(**vm_db_config)
            vm_cursor = vm_conn.cursor()
            
            # 1. 查出 Docker 里的所有数据
            docker_cursor.execute("SELECT * FROM users ORDER BY id")
            source_rows = docker_cursor.fetchall()
            
            # 2. 查出 VM 里已有的 ID
            vm_cursor.execute("SELECT id FROM users")
            existing_ids = {row[0] for row in vm_cursor.fetchall()}
            
            count = 0
            # 3. 增量插入
            for row in source_rows:
                if row['id'] not in existing_ids:
                    sql = """INSERT INTO users (id, name, gender, age) 
                             VALUES (%s, %s, %s, %s)"""
                    val = (row['id'], row['name'], row['gender'], row['age'])
                    vm_cursor.execute(sql, val)
                    count += 1
            
            vm_conn.commit()
            print(f"[{time.strftime('%H:%M:%S')}] 同步完成！本次新增插入了 {count} 条数据。")
            
            # 关闭连接
            docker_cursor.close()
            docker_conn.close()
            vm_cursor.close()
            vm_conn.close()
            
    except Exception as e:
        print(f"同步出错: {e}")

# 每隔 60 秒自动执行一次（模拟实时同步）
if __name__ == '__main__':
    while True:
        sync_data()
        time.sleep(60)