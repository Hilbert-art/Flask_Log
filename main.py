import flask
from flask import *
import pymysql
import hashlib

# 创建Flask程序并定义模板位置
app = Flask(__name__,
            static_url_path='/static',
            static_folder='static',
            template_folder='templates'
            )


# 将所有对主页面的访问都跳转到登录框
@app.route('/', methods=['GET', 'POST'])
def index():
    return flask.redirect(flask.url_for('log_in'))


@app.route('/log_handle', methods=['POST'])
def log_handle():
    find_user = False
    if request.method == 'POST':
        # username和password是前端log_in.html的name字段里的字符
        username = request.form.get('username')
        password = request.form.get('password')
        # 对密码进行md5处理
        encrypass = hashlib.md5()
        encrypass.update(password.encode(encoding='utf-8'))
        password = encrypass.hexdigest()

    # 通过mysql进行存储
    db = pymysql.connect(host="localhost", user="root", password="root", db="www")

    # 创建数据库指针cursor
    cursor = db.cursor()

    sql = "SELECT * FROM users"

    # 执行数据库命令并将数据提取到cursor中
    cursor.execute(sql)
    # 确认命令
    db.commit()
    user_list = []
    for item in cursor.fetchall():
        dict_user = {'username': item[0], 'password': item[1]}
        user_list.append(dict_user)
    # 对数据库中所有的数据进行遍历,找出username
    for i in range(len(user_list)):
        if user_list[i]['username'] == username:
            if user_list[i]['password'] == password:
                find_user = True
                break
            else:
                break

    db.close()
    if not find_user:
        # 登录失败就跳转倒log_fail中并弹窗
        return flask.render_template("log_fail.html")

    else:
        # 登录成功就跳转log_success,并将用户名带入
        return flask.render_template("log_success.html", username=username)


# 处理注册
@app.route('/register_handle', methods=['POST'])
def register_handle():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        # 判断两次密码是否正确
        if password == confirm_password:
            # 对密码进行md5处理
            encrypass = hashlib.md5()
            encrypass.update(password.encode(encoding='utf-8'))
            password = encrypass.hexdigest()

            db = pymysql.connect(host="localhost", user="root", password="root", db="www")
            cursor = db.cursor()

            search_sql = "SELECT * FROM users"
            cursor.execute(search_sql)
            db.commit()
            user_list = []
            for item in cursor.fetchall():
                dict_user = {'username': item[0], 'password': item[1]}
                user_list.append(dict_user)
            for i in range(len(user_list)):
                # 判断是否存在相同用户名
                if user_list[i]['username'] != username:
                    # 将用户名和加密后的密码插入数据库
                    sql = "INSERT INTO users VALUES('%s','%s')" % (username, password)
                    cursor.execute(sql)
                    db.commit()
                else:
                    have_same_username = 1
                    return flask.render_template("register_fail.html", have_same_username=have_same_username)
        else:
            two_passwd_wrong = 1
            return flask.render_template("register_fail.html", two_passwd_wrong=two_passwd_wrong)
    db.close()
    return flask.redirect(flask.url_for('log_in'))


@app.route('/log_in', methods=['GET'])
def log_in():
    return render_template('log_in.html')


@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')


@app.route('/log_success')
def log_success():
    return render_template('log_success.html')


# 自定义404页面
@app.errorhandler(404)
def page_not_found(error):
    return flask.render_template("404.html"), 404


if __name__ == '__main__':
    # 调试时需要debug=True
    app.run()
