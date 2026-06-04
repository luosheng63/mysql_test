import random
import string
import mysql.connector
from datetime import datetime, timedelta, timezone
import os


def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', '127.0.0.1'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASS', 'Root@123456'),
        database=os.getenv('DB_NAME', 'testdb'),
        charset='utf8mb4'
    )


def generate_code(length=6):
    """生成6位数字验证码"""
    return ''.join(random.choices(string.digits, k=length))


def send_sms_code(phone, ip_address=None):
    """
    发送短信验证码（Mock 模式，不花钱）
    返回：(success, message, code)
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 1. 检查发送频率（同手机号每小时最多3次）
        one_hour_ago = datetime.now(timezone.utc).replace(
            tzinfo=None) - timedelta(hours=1)
        cursor.execute("""
            SELECT COUNT(*) FROM sms_verification_codes
            WHERE phone = %s AND created_at > %s
        """, (phone, one_hour_ago))

        count = cursor.fetchone()[0]
        if count >= 3:
            return False, "发送过于频繁，请1小时后再试", None

        # 2. 生成验证码
        code = generate_code()
        expires_at = datetime.now(timezone.utc).replace(
            tzinfo=None) + timedelta(minutes=5)

        # 3. 保存到数据库
        cursor.execute("""
            INSERT INTO sms_verification_codes
                    (phone, code, ip_address, expires_at)
            VALUES (%s, %s, %s, %s)
        """, (phone, code, ip_address, expires_at))

        conn.commit()

        # 4. Mock 发送（只打印到控制台，不花钱）
        print("\n" + "=" * 50)
        print("📱 短信验证码（Mock 模式）")
        print(f"手机号: {phone}")
        print(f"验证码: {code}")
        print("有效期: 5分钟")
        print(f"IP地址: {ip_address or '未知'}")
        print("=" * 50 + "\n")

        return True, "验证码已发送（请查看服务端控制台）", code

    except Exception as e:
        conn.rollback()
        return False, f"发送失败: {str(e)}", None
    finally:
        cursor.close()
        conn.close()


def verify_sms_code(phone, code):
    """
    验证短信验证码（不立即标记为已使用）
    返回：(success, message, code_id)
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # 1. 查找最新的未使用验证码
        cursor.execute("""
            SELECT id, code, expires_at, used FROM sms_verification_codes
            WHERE phone = %s AND used = 0
            ORDER BY created_at DESC LIMIT 1
        """, (phone,))

        record = cursor.fetchone()

        if not record:
            return False, "验证码不存在或已使用", None

        # 2. 检查是否过期
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        if record['expires_at'] < now:
            return False, "验证码已过期", None

        # 3. 检查验证码是否正确
        if record['code'] != code:
            return False, "验证码错误", None

        # 4. 返回验证码ID，但不标记为已使用
        return True, "验证成功", record['id']

    except Exception as e:
        return False, f"验证失败: {str(e)}", None
    finally:
        cursor.close()
        conn.close()
