import mysql.connector


def query_users():
    try:
        # 注意：这里连的是 localhost，因为端口已经映射到 Windows 了
        conn = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='Root@123456',
            database='testdb'
        )
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users;")

        results = cursor.fetchall()

        print("\n--- 查询结果 ---")
        for row in results:
            # row 是一个元组，对应 (id, name, gender, age)
            print(f"ID: {row[0]}, 姓名: {row[1]}, 性别: {row[2]}, 年龄: {row[3]}")
        print("-----------------\n")

        conn.close()
    except Exception as e:
        print(f"查询失败: {e}")


if __name__ == "__main__":
    query_users()
