import mysql.connector
import os


def check_table():
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', '127.0.0.1'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASS', 'Root@123456'),
            database=os.getenv('DB_NAME', 'testdb')
        )
        cursor = conn.cursor()

        print("🔍 检查 users 表结构...")
        cursor.execute("DESC users;")
        rows = cursor.fetchall()

        if not rows:
            print("❌ users 表不存在或为空")
        else:
            print("✅ users 表字段如下：")
            for row in rows:
                nullable = 'NULL' if row[2] == 'YES' else 'NOT NULL'
                print(f"  {row[0]:<20} {row[1]:<15} {nullable}")

        cursor.close()
        conn.close()

    except mysql.connector.Error as e:
        print(f"❌ 数据库连接失败: {e}")


if __name__ == "__main__":
    check_table()
