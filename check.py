import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import ImageGrab
from pyzbar.pyzbar import decode
import threading
import ctypes
import json
import requests
scale_factor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100  # 返回百分比形式的缩放因子
sms_code = ""
headers = {
    "devCode": "",
    "source": "android",
    "version": "2.5.0",
    "versionCode": "2500",
    "token": "",
    "Content-Type": "application/x-www-form-urlencoded",
}

def start(t):
    global headers
    headers["token"] = t
    # 创建子窗口
    top = tk.Toplevel()
    top.title("扫码器")
    # 设置窗口大小
    window_width = 300
    window_height = 300
    screen_width = top.winfo_screenwidth()
    screen_height = top.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    top.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # 设置窗口背景为透明
    top.attributes("-transparentcolor", "white")
    top.configure(bg="white")
    top.attributes('-topmost', True)
    top.iconbitmap("bg.ico")
    # 创建 Canvas 绘制红色边框
    canvas = tk.Canvas(top, highlightthickness=0, bd=0, bg="white")
    canvas.pack(fill="both", expand=True)

    def draw_border(event=None):
        canvas.delete("border")
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        canvas.create_rectangle(0, 0, width, height, outline="red", width=15, tags="border")

    draw_border()
    canvas.bind("<Configure>", draw_border)

    # 拖动窗口
    def start_move(event):
        top.x = event.x
        top.y = event.y

    def stop_move(event):
        top.x = None
        top.y = None

    def do_move(event):
        deltax = event.x - top.x
        deltay = event.y - top.y
        x = top.winfo_x() + deltax
        y = top.winfo_y() + deltay
        top.geometry(f"+{x}+{y}")

    canvas.bind("<Button-1>", start_move)
    canvas.bind("<ButtonRelease-1>", stop_move)
    canvas.bind("<B1-Motion>", do_move)

    def show_sms_dialog(qr_code):
        global sms_code
        sms_code = simpledialog.askstring("验证码", "请输入收到的短信验证码：", parent=top)
        scan_login(qr_code)
    # 截图识别二维码逻辑
    def check_qr_code():
        try:
            while True:
                try:
                    x = int(top.winfo_rootx() * scale_factor)
                    y = int(top.winfo_rooty() * scale_factor)
                    width = int(top.winfo_width() * scale_factor)
                    height = int(top.winfo_height() * scale_factor)
                    img = ImageGrab.grab(bbox=(x, y, x + width, y + height))
                    decoded_objects = decode(img)
                    if decoded_objects:
                        qr_code = decoded_objects[0].data.decode("utf-8")
                        if "G152#KURO" in qr_code:
                            if login(qr_code):
                                scan_login(qr_code)
                                top.destroy()  # 关闭窗口
                                return
                except tk.TclError:
                    # 窗口被关闭时退出线程
                    return
                except Exception as e:
                    print("识别出错:", e)

        except tk.TclError:
            return  # 如果窗口已被关闭则退出线程

    def login(qr_code):
        try:
            response = requests.post(
                url="https://api.kurobbs.com/user/auth/roleInfos",
                data={"qrCode": qr_code},
                headers=headers
            )
            res = json.loads(response.text)
            print(res)
            if res.get("code") == 200:
                return True
            elif res.get("code") == 220:
                messagebox.showerror("错误", "登录已过期，请重新登录")
            elif res.get("code") == 2209:
                messagebox.showerror("错误", "二维码已过期，请重新扫码")
            return False
        except Exception as e:
            print("请求出错:", e)
            return False

    def scan_login(qr_code):
        try:
            response = requests.post(
                url="https://api.kurobbs.com/user/auth/scanLogin",
                data={
                    "autoLogin": "false",
                    "qrCode": qr_code,
                    "id": "",
                    "verifyCode": sms_code
                },
                headers=headers
            )
            print(response.text)
            res = json.loads(response.text)
            if res.get("code") == 200:
                messagebox.showinfo("成功", "登录成功!")
            elif res.get("code") == 2240:
                smsCode(qr_code)
        except Exception as e:
            print("请求出错:", e)

    def smsCode(qr_code):
        try:
            if not sms_code:
                response = requests.post(
                    url="https://api.kurobbs.com/user/sms/scanSms",
                    data="geeTestData=",
                    headers=headers
                )
                res = json.loads(response.text)
                print(res)
            top.after(0, lambda : show_sms_dialog(qr_code))
        except Exception as e:
            print("请求出错:", e)


    # 启动二维码检测线程
    threading.Thread(target=check_qr_code, daemon=True).start()

    # 阻塞等待窗口关闭
    top.wait_window()
