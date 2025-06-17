import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
import requests
import yaml
from flask import Flask, request
from flask_cors import CORS
import tkinter as tk
import webbrowser
import os
from check import start
app = Flask(__name__)
CORS(app)
@app.route('/api/login', methods=['POST'])
def login():
    global uid, token
    data = request.get_json()
    response = requests.post(
        url="https://api.kurobbs.com/user/sdkLogin",
        data={"mobile": data["mobile"], "code": data["code"]},
        headers={"devCode": "", "source": "android", "version": "2.5.0", "versionCode": "2500"}
    )
    response = response.json()
    if response["code"] == 200:
        uid = response["data"]["userId"]
        token = response["data"]["token"]
        uid_label.config(text=f"uid: {uid[:3]}***{uid[:-3]}")
        token_label.config(text=f"token: {token[:3]}***{token[:-3]}")
        with open("data.yaml", "w", encoding="utf-8") as w:
            yaml.dump({"uid": uid, "token": token}, w, default_flow_style=False, allow_unicode=True, sort_keys=False)
    return response
def start_local_http_server(port=8000, directory="."):
    os.chdir(directory)
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    httpd.serve_forever()


# 定义主窗口
root = tk.Tk()
root.title("鸣潮自动扫码器")
root.resizable(False, False)
root.iconbitmap("bg.ico")
window_width = 300
window_height = 170
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width // 2) - (window_width // 2)
y = (screen_height // 2) - (window_height // 2)
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

# 最顶部的提示标签（居中显示）
tip_label = tk.Label(
    root,
    text="首次运行先登录获取uid和token\n被扫码设备首次登录需要短信二次验证",
    fg="blue"
)
tip_label.pack(pady=(10, 5))
top_frame = tk.Frame(root)
top_frame.pack(pady=5)

# 登录按钮
def open_html():
    webbrowser.open("http://localhost:8000/login.html")
def run():
    if not uid:
        return
    root.withdraw()
    start(token)
    root.deiconify()

login_button = tk.Button(top_frame, text="  登录  ", command=open_html)
login_button.grid(row=0, column=0, padx=20)

# 新增 Frame 用于垂直排列 UID 和 Token
info_frame = tk.Frame(top_frame)
info_frame.grid(row=0, column=1, padx=20)

# 显示 UID 和 Token 的标签（垂直排列）
uid_label = tk.Label(info_frame, text="uid: ")
uid_label.pack(anchor='w')

token_label = tk.Label(info_frame, text="token: ")
token_label.pack(anchor='w')
start_button = tk.Button(root, text="  启动  ", command=run)
start_button.pack(pady=10)

if os.path.exists("data.yaml"):
    with open("data.yaml", "r", encoding="utf-8") as f:
        d = yaml.safe_load(f)
        uid = d.get("uid")
        token = d.get("token")
        uid_label.config(text=f"uid: {uid[:3]}***{uid[-3:]}")
        token_label.config(text=f"token: {token[:3]}***{token[-3:]}")
else:
    uid = ""
    token = ""
threading.Thread(target=start_local_http_server, args=(8000, os.getcwd()), daemon=True).start()
threading.Thread(target=lambda : app.run(debug=False), daemon=True).start()
root.mainloop()
