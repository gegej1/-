import tkinter as tk
from tkinter import scrolledtext
from threading import Thread
import requests

class AIChat:
    def __init__(self, root):
        self.root = root
        self.headers = {
            'accept': 'application/json',
            'AUTHORIZATION': 'application-49bc9791a723ee1f4513a629ce6de081'  # 这里是您的API key
        }
        self.profile_id = self.get_profile_id()
        self.create_chat_window()

    def create_chat_window(self):
        # 创建AI对话框窗口
        self.chat_window = tk.Toplevel(self.root)
        self.chat_window.title("AI Chat")
        self.chat_window.geometry("600x400")

        # 设置窗口位置为右下角
        self.chat_window.update_idletasks()
        x = self.root.winfo_screenwidth() - self.chat_window.winfo_width() - 10
        y = self.root.winfo_screenheight() - self.chat_window.winfo_height() - 10
        self.chat_window.geometry(f"+{x}+{y}")

        # 创建文本框用于显示AI响应
        self.text_area = scrolledtext.ScrolledText(self.chat_window, wrap=tk.WORD, state='disabled')
        self.text_area.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # 创建框架来容纳输入框和按钮
        input_frame = tk.Frame(self.chat_window)
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        # 创建输入框用于用户输入
        self.entry_box = tk.Text(input_frame, height=3, wrap=tk.WORD)
        self.entry_box.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 设置输入框的左对齐
        self.entry_box.tag_configure('left', justify='left')

        # 创建 "Enter" 按钮
        self.enter_button = tk.Button(input_frame, text="↩", command=self.send_message)
        self.enter_button.pack(side=tk.RIGHT)

        # 设置文本对齐和样式
        self.text_area.tag_configure('left', justify='left')
        self.text_area.tag_configure('right', justify='right')
        self.text_area.tag_configure('user', foreground='blue', font=('Arial', 10, 'bold'))
        self.text_area.tag_configure('ai', foreground='green', font=('Arial', 10, 'bold'))

        # 绑定回车键事件
        self.entry_box.bind('<Return>', self.send_message)

    def get_profile_id(self):
        profile_url = 'http://localhost:8080/api/application/profile'
        response = requests.get(profile_url, headers=self.headers)
        if response.status_code == 200:
            return response.json()['data']['id']
        else:
            print("获取profile id失败")
            return None

    def get_chat_id(self):
        if not self.profile_id:
            return None
        chat_open_url = f'http://localhost:8080/api/application/{self.profile_id}/chat/open'
        response = requests.get(chat_open_url, headers=self.headers)
        if response.status_code == 200:
            return response.json()['data']
        else:
            print("获取chat id失败")
            return None

    def send_chat_message(self, chat_id, payload):
        chat_message_url = f'http://localhost:8080/api/application/chat_message/{chat_id}'
        response = requests.post(chat_message_url, headers=self.headers, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"发送消息失败，状态码: {response.status_code}")
            return None

    def send_message(self, event=None):
        # 获取用户输入的消息
        user_message = self.entry_box.get("1.0", tk.END).strip()
        if user_message:
            # 清空输入框
            self.entry_box.delete("1.0", tk.END)
            
            # 显示用户消息
            self.display_message(f"User:\n", user_message, align="left", tag='user')
            
            # 启动线程处理AI响应
            Thread(target=self.get_ai_response, args=(user_message,)).start()

        # 阻止文本框默认的回车键行为
        return "break" if event else None

    def get_ai_response(self, user_message):
        chat_id = self.get_chat_id()
        if not chat_id:
            ai_response = "AI: 无法获取聊天ID，请检查API配置。"
        else:
            chat_message_payload = {
                "message": user_message,
                "re_chat": False,
                "stream": False
            }
            response = self.send_chat_message(chat_id, chat_message_payload)
            if response:
                ai_response = response.get('data', {}).get('content', "AI: 无法解析响应。")
            else:
                ai_response = "AI: 未能获取有效响应。"

        # 显示AI响应
        self.display_message(f"AI:\n", ai_response, align="right", tag='ai')

    def display_message(self, username, message, align="left", tag='user'):
        # 启用text_area编辑
        self.text_area.config(state='normal')

        # 插入用户名并设置颜色和加粗样式
        self.text_area.insert(tk.END, username, tag)

        # 对消息进行换行处理，并左对齐每一行
        lines = message.splitlines()
        for line in lines:
            self.text_area.insert(tk.END, f"{line}\n", 'left')

        # 插入额外的空行以分隔每条消息
        self.text_area.insert(tk.END, "\n")

        # 自动滚动到底部
        self.text_area.see(tk.END)

        # 禁用text_area编辑
        self.text_area.config(state='disabled')


def main(root):
    AIChat(root)
