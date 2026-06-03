# app/app.py
from flask import Flask, render_template, request, redirect, url_for
from database import get_all_users, add_user, delete_user, update_user, get_user_by_id

app = Flask(__name__, template_folder='templates')


@app.route('/')
def index():
    users = get_all_users()
    return render_template('index.html', users=users)


@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    gender = request.form.get('gender', '未知')  # 如果没有选择性别，默认为未知
    age = request.form['age']
    if name and age:
        add_user(name, gender, int(age))
    return redirect(url_for('index'))


@app.route('/delete/<int:user_id>')
def delete(user_id):
    delete_user(user_id)
    return redirect(url_for('index'))


@app.route('/edit/<int:user_id>', methods=['GET', 'POST'])
def edit(user_id):
    if request.method == 'POST':
        name = request.form['name']
        gender = request.form.get('gender', '未知')  # 如果没有选择性别，默认为未知
        age = request.form['age']
        update_user(user_id, name, gender, int(age))
        return redirect(url_for('index'))

    user = get_user_by_id(user_id)
    return render_template('edit.html', user=user)


if __name__ == '__main__':
    # 监听 0.0.0.0，这样容器外部也能访问
    app.run(host='0.0.0.0', port=5000, debug=True)
