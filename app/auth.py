# auth.py
from flask import Blueprint, request, jsonify, make_response
import mysql.connector
import os
from datetime import datetime, timezone, timedelta
from marshmallow import ValidationError

# 导入 Schema
from schemas import SendCodeSchema, RegisterSchema, LoginSchema
from security import (
    generate_salt,
    hash_password,
    verify_password,
    generate_token,
    decode_token)
from sms import send_sms_code, verify_sms_code

auth_bp = Blueprint('auth', __name__)


def get_db_connection():
    """安全的数据库连接获取"""
    try:
        return mysql.connector.connect(
            host=os.getenv('DB_HOST', '127.0.0.1'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASS', 'Root@123456'),
            database=os.getenv('DB_NAME', 'testdb'),
            charset='utf8mb4'
        )
    except mysql.connector.Error as err:
        # 在真实项目中，这里应该记录日志
        raise Exception(f"数据库连接失败: {err}")

# =======================
# 路由定义
# =======================


@auth_bp.route('/api/send-code', methods=['POST'])
def send_code():
    """发送短信验证码（Mock模式）"""
    schema = SendCodeSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    phone = data['phone']
    ip_address = request.remote_addr

    try:
        success, message, code = send_sms_code(phone, ip_address)
        if success:
            # 构造返回数据
            response_data = {"message": message}

            # ✅ 强制返回 _debug_code（无论什么环境）
            # 如果你担心安全问题，可以加个环境变量判断
            if code:
                response_data['_debug_code'] = code

            return jsonify(response_data), 200
        else:
            return jsonify({"error": message}), 400
    except Exception as e:
        print(f"发送验证码异常: {e}")
        return jsonify({"error": "服务器内部错误"}), 500


@auth_bp.route('/api/register', methods=['POST'])
def register():
    """用户注册接口"""
    schema = RegisterSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    phone = data['phone']
    code = data['code']
    password = data['password']

    # 1. 验证短信验证码
    success, message, code_id = verify_sms_code(phone, code)
    if not success:
        return jsonify({"error": message}), 400

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 2. 检查用户是否已存在
        cursor.execute("SELECT id FROM users WHERE phone = %s", (phone,))
        if cursor.fetchone():
            return jsonify({"error": "该手机号已注册"}), 409

        # 3. 创建用户
        salt = generate_salt()
        password_hash = hash_password(password, salt)
        nickname = f'用户{phone[-4:]}' if len(phone) >= 4 else '用户'

        cursor.execute("""
            INSERT INTO users (phone, password_hash, salt, nickname, status)
            VALUES (%s, %s, %s, %s, 1)
        """, (phone, password_hash, salt, nickname))

        conn.commit()
        user_id = cursor.lastrowid

        # 4. 标记验证码为已使用
        if code_id:
            cursor.execute(
                "UPDATE sms_verification_codes SET\
                    used = 1 WHERE id = %s", (code_id,))
            conn.commit()

        token = generate_token(user_id)

        return jsonify({
            "message": "注册成功",
            "token": token,
            "user_id": user_id,
            "nickname": nickname
        }), 201

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": f"注册失败: {str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@auth_bp.route('/api/login', methods=['POST'])
def login():
    """用户登录接口"""
    schema = LoginSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    phone = data['phone']
    password = data['password']

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, phone, password_hash, salt,
                status, login_fail_count, locked_until
            FROM users WHERE phone = %s
        """, (phone,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"error": "账号不存在"}), 404

        if user['status'] == 0:
            return jsonify({"error": "账号已被冻结"}), 403

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        if user['locked_until'] and user['locked_until'] > now:
            remaining = int((user['locked_until'] - now).total_seconds() // 60)
            return jsonify({"error": f"账号已锁定，请{remaining}分钟后再试"}), 403

        if not verify_password(password, user['password_hash'], user['salt']):
            # 登录失败，增加计数
            fail_count = user['login_fail_count'] + 1
            locked_until = None
            if fail_count >= 5:
                locked_until = now + timedelta(hours=1)

            cursor.execute("""
                UPDATE users SET login_fail_count = %s, locked_until = %s
                WHERE id = %s
            """, (fail_count, locked_until, user['id']))
            conn.commit()

            if fail_count >= 5:
                return jsonify({"error": "密码错误次数过多，账号已锁定1小时"}), 401
            else:
                return jsonify({"error": f"密码错误，还剩{5 - fail_count}次尝试机会"}), 401

        # 登录成功，重置失败计数
        cursor.execute("""
            UPDATE users SET login_fail_count = 0, locked_until = NULL
            WHERE id = %s
        """, (user['id'],))
        conn.commit()

        token = generate_token(user['id'])

        # 设置 HttpOnly Cookie (更安全)
        resp = make_response(jsonify({
            "message": "登录成功",
            "user_id": user['id'],
            "nickname": user.get('nickname', '用户')
        }))
        resp.set_cookie('token', token, httponly=True, path='/')

        return resp, 200

    except Exception as e:
        return jsonify({"error": f"登录失败: {str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# =======================
# 新增：验证 Token 有效性接口
# =======================


@auth_bp.route('/api/verify-token', methods=['GET'])
def verify_token():
    """
    验证 Token 是否有效
    用于 Postman 自动化测试或前端检查登录态
    """
    token = request.cookies.get('token') or request.headers.get(
        'Authorization', '').replace('Bearer ', '')

    if not token:
        return jsonify({"valid": False, "error": "未提供 Token"}), 401

    try:
        payload = decode_token(token)
        if not payload:
            return jsonify({"valid": False, "error": "Token 无效或已过期"}), 401

        # 可选：检查用户是否存在
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE id = %s",
                       (payload['user_id'],))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if not user:
            return jsonify({"valid": False, "error": "用户不存在"}), 404

        return jsonify({
            "valid": True,
            "user_id": payload['user_id'],
            "message": "Token 有效"
        }), 200

    except Exception as e:
        return jsonify({"valid": False, "error": f"验证失败: {str(e)}"}), 500
