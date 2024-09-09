import tkinter as tk
from tkinter import messagebox, StringVar, Listbox, Scale, HORIZONTAL
from utils import get_all_data_scope

class Mode1:
    def __init__(self, root, app):
        self.root = root
        self.app = app

    def create_UI_elements(self):
        # 在同一行中放置搜索栏
        search_frame = tk.Frame(self.root)
        search_frame.place(x=790, y=255)  # 调整 x 和 y 以放置到合适位置
        # 创建搜索框
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=20)
        self.search_entry.bind('<KeyRelease>', lambda event: self.update_suggestions())  # 实时更新建议
        self.search_entry.bind('<Return>', self.perform_search)  # 绑定回车键

        # 创建搜索按钮
        self.search_button = tk.Button(search_frame, text="项目层级搜索", command=self.perform_search)
        self.search_button.pack(side=tk.LEFT, padx=20)
    
        # 创建联想提示列表框，动态显示联想提示
        self.suggestions_listbox = tk.Listbox(self.root, height=5, width=30)
        self.suggestions_listbox.place_forget()  # 初始状态下隐藏
        self.suggestions_listbox.bind("<<ListboxSelect>>", self.on_suggestion_click)

    def update_suggestions(self):
        # 获取搜索框中的输入
        query = self.search_var.get()
        if query:
            suggestions = self.get_suggestions(query)
            self.suggestions_listbox.delete(0, tk.END)  # 清空建议列表
            for suggestion in suggestions:
                self.suggestions_listbox.insert(tk.END, suggestion)  # 插入建议

            # 获取search_frame相对于主窗口的x和y坐标
            search_frame_x = self.search_entry.winfo_rootx() - self.root.winfo_rootx()
            search_frame_y = self.search_entry.winfo_rooty() - self.root.winfo_rooty()

            # 显示联想列表，放置在搜索框下方
            self.suggestions_listbox.place(x=search_frame_x, y=search_frame_y + self.search_entry.winfo_height())
            self.suggestions_listbox.lift()  # 确保列表在最前端显示
        
        if not query:
            self.suggestions_listbox.place_forget()  # 隐藏联想列表
            self.suggestions_listbox.delete(0, tk.END)

    def get_suggestions(self, query):
        # 获取匹配的建议列表
        suggestions = []
        current_data = get_all_data_scope()  # 改为全局数据范围
        for key in current_data:
            if query.lower() in key.lower():
                suggestions.append(key)
        return suggestions
    
    # def on_suggestion_click(self, event):
    #     # 处理用户点击联想提示的事件
    #     selection = self.suggestions_listbox.get(self.suggestions_listbox.curselection())
    #     self.search_var.set(selection)
    #     self.perform_search()
    #     self.suggestions_listbox.place_forget()  # 隐藏联想列表
    #     self.suggestions_listbox.delete(0, tk.END)
    #     # 清空当前界面
    #     for widget in self.root.winfo_children():
    #         # 排除 Toplevel 窗口
    #         if not isinstance(widget, tk.Toplevel):
    #             widget.pack_forget()
    #             widget.place_forget()

    #     # 重新创建基础UI
    #     self.app.update_UI()
    #     self.app.create_UI()
    def on_suggestion_click(self, event):
        # 检查是否有选中内容
        if not self.suggestions_listbox.curselection():
            return
        
        # 获取选中的内容
        selection = self.suggestions_listbox.get(self.suggestions_listbox.curselection())
        self.search_var.set(selection)
        self.perform_search()
        self.suggestions_listbox.place_forget()  # 隐藏联想列表
        self.suggestions_listbox.delete(0, tk.END)
        # 清空当前界面
        for widget in self.root.winfo_children():
            # 排除 Toplevel 窗口
            if not isinstance(widget, tk.Toplevel):
                widget.pack_forget()
                widget.place_forget()

        # 重新创建基础UI
        self.app.update_UI()

    def perform_search(self):
        search_query = self.search_var.get()
        all_data = get_all_data_scope()

        if search_query in all_data:
            path = search_query.split('/')
            if len(path) > 2:
                self.app.current_selection = path[:1] + path[2:]
                self.app.current_level = 4
            else:
                self.app.current_selection = path[:1]
                self.app.current_level = 3 # 设置当前层级

            self.app.update_UI()