from flask import Flask, render_template, request, redirect, session, flash
import os

app = Flask(__name__)
# 建议在生产环境中通过环境变量设置 SECRET_KEY
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-me')

# ==========================================
# 关键修改：在应用启动时立即注册蓝图
# 不能放在 if __name__ == '__main__': 里，否则 Docker/Gunicorn 无法加载
# ==========================================
from auth import auth_bp
from profile import profile_bp

app.register_blueprint(auth_bp)
app.register_blueprint(profile_bp)

# ==========================================
# 数据库初始化
# ==========================================
from database import setup_database_and_tables
setup_database_and_tables()

# ==========================================
# 路由定义
# ==========================================

@app.route('/')
def index():
    """根路径直接渲染登录页"""
    return render_template('login.html')

@app.route('/register')
def register_page():
    """注册页面"""
    return render_template('register.html')

@app.route('/login')
def login_page():
    """登录页面（GET请求）"""
    return render_template('login.html')

@app.route('/profile')
def profile_page():
    """个人资料页（需要鉴权）"""
    token = request.cookies.get('token') or \
            request.headers.get('Authorization', '').replace('Bearer ', '')
    
    if not token:
        return redirect('/login')

    # 延迟导入，避免循环依赖
    from security import decode_token
    payload = decode_token(token)
    
    if not payload:
        return redirect('/login')

    from profile import get_user_info
    user = get_user_info(payload['user_id'])
    
    if not user:
        return redirect('/login')

    return render_template('profile.html', user=user)

@app.route('/logout')
def logout():
    """退出登录"""
    session.clear()
    response = redirect('/login')
    response.delete_cookie('token')
    flash('您已成功退出登录', 'success')
    return response

# ==========================================
# 本地开发服务器启动入口
# ==========================================
if __name__ == '__main__':
    # 注意：Docker 启动走的是 command: python app.py
    # 这里的代码主要用于本地调试
    app.run(host='0.0.0.0', port=5000, debug=True)