from flask import Flask, render_template, request, redirect, url_for, session
import json
import random
import os
from dictation_practice import start_dictation

app = Flask(__name__)
app.secret_key = "your_secret_key"  # 用于 Flask 会话管理

USERS_FILE = "users.json"  # 存储用户注册信息
USERS_DIR = "users"        # 存储用户数据的目录

# 加载用户注册信息
def load_users():
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# 保存用户注册信息
def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

# 加载用户数据
def load_user_data(username):
    user_file = os.path.join(USERS_DIR, f"{username}.json")
    try:
        with open(user_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"words": [], "wrong_words": [], "review_words": []}

# 保存用户数据
def save_user_data(username, data):
    user_file = os.path.join(USERS_DIR, f"{username}.json")
    with open(user_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 首页，展示当前用户的单词本、错题本、巩固本
@app.route("/")
def index():
    if "username" not in session:
        return redirect(url_for("login"))
    
    username = session["username"]
    data = load_user_data(username)
    
    words = sorted(data['words'], key=lambda x: x['word'])
    wrong_words = sorted(data['wrong_words'], key=lambda x: x['word'])
    review_words = sorted(data['review_words'], key=lambda x: x['word'])
    
    return render_template("index.html", words=words, wrong_words=wrong_words, review_words=review_words)

# 用户登录
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        users = load_users()
        
        if username in users and users[username]["password"] == password:
            session["username"] = username
            return redirect(url_for("index"))
        else:
            return "用户名或密码错误，请重新登录。"
    
    return render_template("login.html")

# 用户注册
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        users = load_users()
        
        if username in users:
            return "用户名已存在，请选择其他用户名。"
        
        users[username] = {"password": password}
        save_users(users)
        
        # 创建一个用户的空数据文件
        save_user_data(username, {"words": [], "wrong_words": [], "review_words": []})
        
        session["username"] = username
        return redirect(url_for("index"))
    
    return render_template("register.html")

# 用户注销
@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

# 添加单词
@app.route("/add", methods=["GET", "POST"])
def add_word():
    if "username" not in session:
        return redirect(url_for("login"))
    
    username = session["username"]
    
    if request.method == "POST":
        word = request.form["word"]
        translation = request.form["translation"]
        data = load_user_data(username)
        data['words'].append({"word": word, "translation": translation})
        save_user_data(username, data)
        return redirect(url_for("index"))
    
    return render_template("add_word.html")

# 听写页面
@app.route("/dictation", methods=["GET", "POST"])
def dictation():
    if "username" not in session:
        return redirect(url_for("login"))
    
    username = session["username"]
    data = load_user_data(username)
    
    if request.method == "POST":
        dictation_result = request.form.to_dict()
        correct = 0
        for word, answer in dictation_result.items():
            word_info = next((item for item in data["words"] if item["word"] == word), None)
            if word_info and word_info["translation"] == answer:
                correct += 1
        return render_template("results.html", correct=correct, total=len(data['words']))
    
    dictation_data = start_dictation(data['words'])
    return render_template("dictation.html", dictation_data=dictation_data)

# 错题本
@app.route("/wrong_words")
def wrong_words():
    if "username" not in session:
        return redirect(url_for("login"))
    
    username = session["username"]
    data = load_user_data(username)
    return render_template("wrong_words.html", wrong_words=sorted(data['wrong_words'], key=lambda x: x['word']))

# 巩固本
@app.route("/review_words")
def review_words():
    if "username" not in session:
        return redirect(url_for("login"))
    
    username = session["username"]
    data = load_user_data(username)
    return render_template("review_words.html", review_words=sorted(data['review_words'], key=lambda x: x['word']))

if __name__ == "__main__":
    if not os.path.exists(USERS_DIR):
        os.makedirs(USERS_DIR)
    app.run(debug=True, host='0.0.0.0', port=8080)  # 更改网址和端口


