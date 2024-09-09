import tkinter as tk
import json 
from tkinter import messagebox, StringVar, Listbox, Scale, HORIZONTAL
from mode1 import Mode1
from mode2 import Mode2
from mode3 import Mode3
from utils import create_city_index
from AI_Helper import main as ai_main
import os
import webbrowser

class IndexingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("沿海港口海洋动力信息查询")
        self.root.geometry("1200x700")
        self.current_level = 1
        self.current_selection = []  # 用来记录当前数据层级
        self.current_range = 500  # 初始化默认范围为500公里

        with open("data_China.json", "r", encoding="utf-8") as file:
            self.data_China = json.load(file)
        with open("data_Abroad.json", "r", encoding="utf-8") as file:
            self.data_Abroad = json.load(file)

        # 初始化城市数据
        self.city_index = create_city_index("countries_states_cities.json")

        # 初始化当前层级
        self.current_data = {**self.data_China, **self.data_Abroad}

        # 加载各模式的模块
        self.mode1 = Mode1(self.root, self)
        self.mode2 = Mode2(self.root, self)
        self.mode3 = Mode3(self.root, self)

        # 启动AI对话
        ai_main(self.root)
        
        # 初始化UI界面
        self.create_UI()
        self.update_UI()

    def create_UI(self):
        self.create_common_UI()
        self.mode1.create_UI_elements()
        self.mode2.create_UI_elements()
        self.mode3.create_UI_elements()
    
    def create_common_UI(self):
        # 创建基础UI组件（标题、主页按钮、搜索栏）
        self.label = tk.Label(self.root, text="海洋水动力信息查询系统", font=("Arial", 20))
        self.label.pack(pady=20)

        # 创建“主页”按钮
        self.home_button = tk.Button(
            self.root, 
            text="Home", 
            command=self.go_home, 
            font=("Arial", 14),  # 增加字体大小
            width=10,            # 调整按钮的宽度
            height=3,             # 调整按钮的高度
            bg="blue",      # 设置按钮背景色
            fg="red"           # 设置按钮前景色（文本颜色）
        )
        self.home_button.place(x=520, y=560)

        # 创建范围选择滑动条
        self.range_scale = Scale(
            self.root, 
            from_=10, 
            to=1500, 
            orient=HORIZONTAL, 
            label="选择搜索范围 (km)", 
            length=220, 
            font=("Arial", 12)
        )
        self.range_scale.set(self.current_range)  # 使用当前范围初始化滑块
        self.range_scale.place(x=460, y=110)

    def update_UI(self):
        # 清空当前界面
        for widget in self.root.winfo_children():
            # 排除 Toplevel 窗口
            if not isinstance(widget, tk.Toplevel):
                widget.pack_forget()
                widget.place_forget()

        # 重新创建基础UI
        self.create_UI()

        # 根据 current_level 显示不同的内容
        if self.current_level == 1:
            self.create_level1_UI()  # Level 1 的特定UI逻辑
        elif self.current_level > 1:
            # 创建“回退”按钮
            self.back_button = tk.Button(
                self.root, text="Back", 
                command=self.go_back, 
                font=("Arial", 14),  # 增加字体大小
                width=10,            # 调整按钮的宽度
                height=3,             # 调整按钮的高度
                bg="darkblue",      # 设置按钮背景色
                fg="red"           # 设置按钮前景色（文本颜色）
            )
            self.back_button.place(x=520, y=480)
            # 隐藏“中国”和“国外”按钮
            if hasattr(self, 'abroad_button'):
                self.abroad_button.place_forget()
            if hasattr(self, 'China_button'):
                self.China_button.place_forget()

        if self.current_level == 2:
            self.create_level2_UI()

        elif self.current_level == 3:
            self.load_City()

        elif self.current_level == 4:
            self.display_project_details(self.current_selection[-1])
    
    def create_level1_UI(self):
        # 创建国家选择按钮，仅在 Level 1 使用
        self.abroad_button = tk.Button(
            self.root,
            text="国外",
            command=self.go_abroad, 
            font=("Arial", 12),  # 增加字体大小
            width=8,            # 调整按钮的宽度
            height=3,             # 调整按钮的高度
            bg="lightblue",      # 设置按钮背景色
            fg="purple"           # 设置按钮前景色（文本颜色）
        )
        self.abroad_button.place(x=600, y=200)

        self.China_button = tk.Button(
            self.root, text="中国", 
            command=self.go_China,  
            font=("Arial", 12),  # 增加字体大小
            width=8,            # 调整按钮的宽度
            height=3,             # 调整按钮的高度
            bg="lightblue",      # 设置按钮背景色
            fg="purple"           # 设置按钮前景色（文本颜色）
        )
        self.China_button.place(x=480, y=200)

        # 创建一个文本框用于显示软件介绍
        intro_text = tk.Text(self.root, height=38, width=40, wrap=tk.WORD, bg="lightgrey", fg="black", font=("SimSun", 12))
        intro_text.place(x=20, y=10)

        # 配置加粗标签
        intro_text.tag_configure("bigBold", font=("SimHei", 14, "bold"))
        intro_text.tag_configure("bold", font=("SimHei", 12, "bold"))
        # 配置行距标签
        intro_text.tag_configure("spacing", spacing1=10, spacing2=5, spacing3=10)

        # 插入软件介绍内容
        intro_text.insert(tk.END, "欢迎使用沿海港口海洋动力信息查询系统！\n", "bigBold")
        intro_text.insert(tk.END, " 本软件旨在提供关于沿海港口的详细水动力信息，"
                                   "包括潮汐特征、波浪特征、流场特征等。\n"
                                   "您可以通过选择不同的层级，快速查询和访问相关项目的详细信息，并查看相关的文档。\n\n")
        intro_text.insert(tk.END, "功能介绍\n", "bigBold")
        intro_text.insert(tk.END, "Home: ", "bold")
        intro_text.insert(tk.END, "回到最初始层级\n")
        intro_text.insert(tk.END, "Back：", ("bold", "spacing"))
        intro_text.insert(tk.END, "返回上一层级\n")
        intro_text.insert(tk.END, "国家、省份及项目按钮: ", ("bold", "spacing"))
        intro_text.insert(tk.END, "选取对应按钮能进入下一层级，"
                          "选择国家中国或国外能够进入省份或外国国家，"
                          "继续点击可以继续访问，直到展开项目细节\n")
        intro_text.insert(tk.END, "AI小助手: ", ("bold", "spacing"))
        intro_text.insert(tk.END, "基于QWen2:7b模型，可以询问有关项目的相关的基础信息，也可以进行基本的沟通交流\n")
        intro_text.insert(tk.END, "项目层级搜索: ", ("bold", "spacing"))
        intro_text.insert(tk.END, "基于当前层级的搜索，对层级内的条目进行层级匹配，项目名、地名均可匹配\n")
        intro_text.insert(tk.END, "地名搜索附近项目：", ("bold", "spacing"))
        intro_text.insert(tk.END, "输入地名，展现改地名附近的项目。注意！对于英文地名，由于翻译区别，出现不匹配的情况，需要进行语料库微调\n")
        intro_text.insert(tk.END, "项目搜索附近项目：", ("bold", "spacing"))
        intro_text.insert(tk.END, "通过索引项目名，匹配输出其附近的项目名\n")
        intro_text.insert(tk.END, "搜索范围：", ("bold", "spacing"))
        intro_text.insert(tk.END, "通过拖动滑块搜索范围可以控制地名搜索和项目搜索匹配的范围")
        
        # 设置文本框为只读模式
        intro_text.config(state=tk.DISABLED)

    def create_level2_UI(self):
        # Level 2 的逻辑在此实现
        if "中国" in self.current_selection:
            self.select_China_province()
            
        elif "国外" in self.current_selection:
            self.select_abroad_country()

    def select_China_province(self):
        # 清空当前界面
        for widget in self.root.winfo_children():
            # 排除 Toplevel 窗口
            if isinstance(widget, tk.Toplevel):
                continue
            widget.pack_forget()

        self.create_UI()
        self.label = tk.Label(self.root, text="请选择省或直辖市", font=("Arial", 14))
        self.label.place(x=480,y=190)
        provinces = list(self.data_China.keys())

        # 创建省份列表
        self.provinceListBox = tk.Listbox(self.root, selectmode=tk.SINGLE)
        for province in provinces:
            self.provinceListBox.insert(tk.END, province)
        self.provinceListBox.place(x=500, y=220)

        # 创建确认按钮
        self.selectButton = tk.Button(self.root, text="确认", command=self.select_China_province_button)
        self.selectButton.place(x=548, y=410)

    def select_China_province_button(self):
        selectedIndice = self.provinceListBox.curselection()[0]
        selectedProvince = list(self.data_China.keys())[selectedIndice]
        self.current_selection.append(selectedProvince)
        self.current_level += 1
        self.update_UI()

    def select_abroad_country(self):
        # 清空当前界面
        for widget in self.root.winfo_children():
            # 排除 Toplevel 窗口
            if isinstance(widget, tk.Toplevel):
                continue
            widget.pack_forget()

        self.create_UI()
        self.label = tk.Label(self.root, text="请选择国家", font=("Arial", 14))
        self.label.place(x=515,y=190)
        countries = list(self.data_Abroad.keys())

        # 创建国家列表
        self.countryListBox = tk.Listbox(self.root, selectmode=tk.SINGLE)
        for country in countries:
            self.countryListBox.insert(tk.END, country)
        self.countryListBox.place(x=500, y=220)

        # 创建确认按钮
        self.selectButton = tk.Button(self.root, text="确认", command=self.select_abroad_country_button)
        self.selectButton.place(x=548, y=410)

    def select_abroad_country_button(self):
        selectedIndice = self.countryListBox.curselection()[0]
        selectedCountry = list(self.data_Abroad.keys())[selectedIndice]
        self.current_selection.append(selectedCountry)
        self.current_level += 1
        self.update_UI()

    def display_project_details(self, project_name, project_details=None):
        # 清空当前界面
        for widget in self.root.winfo_children():
            # 排除 Toplevel 窗口
            if not isinstance(widget, tk.Toplevel):
                widget.pack_forget()
                widget.place_forget()
                
        self.create_UI()

        # 获取项目的详细信息
        if not project_details:  # 如果从城市搜索进入的，需要获取项目细节
            project_details = self.current_data[self.current_selection[-2]][project_name]

        # 创建一个文本框用于显示项目详细信息
        details_text = tk.Text(self.root, height=38, width=42, wrap=tk.WORD, bg="lightgrey", fg="black", font=("SimSun", 12))
        details_text.place(x=20, y=10)

        # 配置行距
        details_text.tag_configure('custom_spacing', spacing1=5, spacing2=10, spacing3=5)
        details_text.tag_configure('section_title', font=("Arial", 14, "underline"))

        # 动态将项目详细信息添加到文本框中
        details_text.insert(tk.END, f"项目：{project_name}\n\n", 'custom_spacing')
        
        for section, details in project_details.items():
            details_text.insert(tk.END, f"{section}:\n", ('section_title', 'custom_spacing'))
            
            if isinstance(details, dict):
                for sub_key, sub_value in details.items():
                    details_text.insert(tk.END, f"  {sub_key}: {sub_value}\n", 'custom_spacing')
            else:
                details_text.insert(tk.END, f"{details}\n", 'custom_spacing')
        
        details_text.config(state=tk.DISABLED)  # 禁用编辑

        # 插入查看原文档按钮
        view_doc_button = tk.Button(self.root, text="查看原文档", command=lambda: self.open_project_document(project_name))
        view_doc_button.place(x=130, y=635)


    def open_project_document(self, project_name):
        # 项目文件夹路径
        project_folder = "Projects"
        # 查找最大匹配字数的文件夹
        best_match_folder = None
        best_match_length = 0

        for folder_name in os.listdir(project_folder):
            if project_name in folder_name:
                match_length = len(os.path.commonprefix([project_name, folder_name]))
                if match_length > best_match_length:
                    best_match_folder = folder_name
                    best_match_length = match_length

        if best_match_folder:
            folder_path = os.path.join(project_folder, best_match_folder)
            files = os.listdir(folder_path)

            if files:
                # 创建一个新的窗口来展示文件列表
                file_window = tk.Toplevel(self.root)
                file_window.title(f"{project_name} - 文件列表")
                file_window.geometry("700x450")

                file_label = tk.Label(file_window, text=f"项目 '{project_name}' 的相关文件：", font=("Arial", 12))
                file_label.pack(pady=10)

                for file_name in files:
                    file_path = os.path.join(folder_path, file_name)
                    file_button = tk.Button(file_window, text=file_name, command=lambda path=file_path: self.open_file(path))
                    file_button.pack(anchor="w", padx=20, pady=5)
            else:
                messagebox.showinfo("信息", f"文件夹 '{best_match_folder}' 中没有找到文件。")
        else:
            messagebox.showerror("错误", f"找不到与项目 '{project_name}' 关联的文件夹。")

    def open_file(self, file_path):
        # 使用默认程序打开文件
        if os.path.exists(file_path):
            webbrowser.open(file_path)
        else:
            messagebox.showerror("错误", f"找不到文件 '{file_path}'。")

    def load_City(self):
        # 判断是否为省份或者直辖市/特区
        print(self.current_selection)
        if len(self.current_selection) > 1:
            selected_location = self.current_selection[1]
        else:
            selected_location = self.current_selection[0]

        self.label = tk.Label(self.root, text=f"请选择 {selected_location} 的项目", font=("Arial", 14))
        self.label.place(x=495,y=190)
        self.selectCityButton = tk.Button(self.root, text="确认", command=self.select_City)
        self.selectCityButton.pack(pady=10)
        self.load_projects(selected_location)

    def select_City(self):
        selectedIndice = self.cityListBox.curselection()[0]
        selectedCity = list(self.current_data[self.current_selection[-1]].keys())[selectedIndice]
        self.current_selection.append(selectedCity)
        self.current_level += 1
        self.update_UI()

    def load_projects(self, location):
        # 清空当前界面
        for widget in self.root.winfo_children():
            # 排除 Toplevel 窗口
            if isinstance(widget, tk.Toplevel):
                continue
            widget.pack_forget()

        self.create_UI()

        projects = self.current_data[self.current_selection[-1]].keys()

        self.projectListBox = tk.Listbox(self.root, selectmode=tk.SINGLE)
        for project in projects:
            self.projectListBox.insert(tk.END, project)
        self.projectListBox.place(x=500, y=220)

        self.selectProjectButton = tk.Button(self.root, text="确认", command=self.select_Project)
        self.selectProjectButton.place(x=543, y=410)
    
    def select_Project(self):
        selectedIndice = self.projectListBox.curselection()[0]
        selectedProject = list(self.current_data[self.current_selection[-1]].keys())[selectedIndice]
        self.current_selection.append(selectedProject)
        self.current_level += 1
        self.update_UI()
        
    def go_back(self):
        self.current_level -= 1
        if self.current_selection:
            popedSelection = self.current_selection.pop()
            if not self.current_selection and popedSelection in self.data_China:
                self.current_selection.append("中国")
            if not self.current_selection and popedSelection in self.data_Abroad:
                self.current_selection.append("国外")
        self.update_UI()  # 更新UI，返回上一级

    def go_home(self):
        self.reset()
        self.update_UI()  # 更新UI，返回到首页

    def go_abroad(self):
        self.current_level += 1
        self.current_selection.append("国外")
        self.update_UI()

    def go_China(self):
        self.current_level += 1
        self.current_selection.append("中国")
        self.update_UI()

    def reset(self):
        self.current_level = 1
        self.current_selection = []
        self.update_UI()

# 创建主窗口并运行应用程序
root = tk.Tk()
app = IndexingApp(root)
root.mainloop()