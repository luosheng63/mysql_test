from flask import Flask, render_template, request, redirect, session, flash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-me')

# 延迟导入蓝图


def register_blueprints():
    from auth import auth_bp
    from profile import profile_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)


@app.route('/')
def index():
    return render_template('login.html')


@app.route('/register')
def register_page():
    return render_template('register.html')


@app.route('/login')
def login_page():
    return render_template('login.html')


@app.route('/profile')
def profile_page():
    # 检查是否登录
    token = request.cookies.get('token') or request.headers.get(
        'Authorization', '').replace('Bearer ', '')
    if not token:
        return redirect('/login')

    from security import decode_token
    payload = decode_token(token)
    if not payload:
        return redirect('/login')

    # 获取用户信息
    from profile import get_user_info
    user = get_user_info(payload['user_id'])
    if not user:
        return redirect('/login')

    return render_template('profile.html', user=user)


@app.route('/logout')
def logout():
    # 清除 session 和 cookie
    session.clear()
    response = redirect('/login')
    response.delete_cookie('token')
    flash('您已成功退出登录', 'success')
    return response


if __name__ == '__main__':
    from database import setup_database_and_tables
    setup_database_and_tables()

    register_blueprints()

    app.run(host='0.0.0.0', port=5000, debug=True)
