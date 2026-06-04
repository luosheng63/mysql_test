# profile.py
from flask import Blueprint, request, jsonify
import mysql.connector
import os
from datetime import datetime, timezone
from security import decode_token
from schemas import UpdateProfileSchema
from marshmallow import ValidationError

profile_bp = Blueprint('profile', __name__)

def get_db_connection():
    try:
        return mysql.connector.connect(
            host=os.getenv('DB_HOST', '127.0.0.1'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASS', 'Root@123456'),
            database=os.getenv('DB_NAME', 'testdb'),
            charset='utf8mb4'
        )
    except mysql.connector.Error as err:
        raise Exception(f"数据库连接失败: {err}")

def get_user_info(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT id, phone, nickname, avatar_url, gender, birthday, created_at
            FROM users WHERE id = %s
        """, (user_id,))
        user = cursor.fetchone()
        if user and user['phone']:
            phone = user['phone']
            user['phone'] = phone[:3] + '****' + phone[-4:]
        return user
    finally:
        cursor.close()
        conn.close()

# 获取个人资料（GET）
@profile_bp.route('/api/profile', methods=['GET'])
def get_profile():
    token = request.cookies.get('token') or request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return jsonify({"error": "未授权"}), 401
    
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Token无效或已过期"}), 401
    
    user = get_user_info(payload['user_id'])
    if not user:
        return jsonify({"error": "用户不存在"}), 404
    
    return jsonify({"data": user}), 200

# ✅ 更新个人资料（PUT）—— 这就是你要的功能！
@profile_bp.route('/api/profile', methods=['PUT'])
def update_profile():
    token = request.cookies.get('token') or request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return jsonify({"error": "未授权"}), 401
    
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Token无效或已过期"}), 401

    schema = UpdateProfileSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    user_id = payload['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        update_fields = []
        params = []
        
        if 'nickname' in data:
            update_fields.append("nickname = %s")
            params.append(data['nickname'])
        
        if 'gender' in data:
            update_fields.append("gender = %s")
            params.append(data['gender'])
        
        if 'birthday' in data:
            update_fields.append("birthday = %s")
            params.append(data['birthday'])
        
        if not update_fields:
            return jsonify({"error": "没有要更新的字段"}), 400
        
        update_fields.append("updated_at = NOW()")
        params.append(user_id)
        
        sql = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s"
        cursor.execute(sql, params)
        conn.commit()
        
        return jsonify({"message": "更新成功"}), 200
        
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"更新失败: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()