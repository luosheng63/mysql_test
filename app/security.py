import hashlib
import secrets
import os
from datetime import datetime, timedelta, timezone
import jwt

def generate_salt():
    """生成随机盐值"""
    return secrets.token_hex(16)

def hash_password(password, salt):
    """使用PBKDF2加密密码"""
    return hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000  # 迭代次数
    ).hex()

def verify_password(password, stored_hash, salt):
    """验证密码"""
    return hash_password(password, salt) == stored_hash

def generate_token(user_id):
    """生成JWT Token（修复弃用警告）"""
    # 使用 timezone.utc 替代 utcnow()
    payload = {
        'user_id': user_id,
        'exp': datetime.now(timezone.utc) + timedelta(days=30),
        'iat': datetime.now(timezone.utc)  # 签发时间
    }
    secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-me')
    return jwt.encode(payload, secret_key, algorithm='HS256')

def decode_token(token):
    """解码JWT Token"""
    try:
        secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-me')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None