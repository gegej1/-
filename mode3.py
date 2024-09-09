import tkinter as tk
from tkinter import messagebox, StringVar, Listbox, Scale, HORIZONTAL
from geopy.distance import geodesic
from utils import get_all_data_scope

class Mode3:
    def __init__(self, root, app):
        self.root = root
        self.app = app
        
    def create_UI_elements(self):

        # 在同一行中放置搜索栏
        search_frame = tk.Frame(self.root)
        search_frame.place(x=790, y=450)  # 调整 x 和 y 以放置到合适位置

        # 创建项目模糊搜索框
        self.search_var = StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=20)
        self.search_entry.bind('<KeyRelease>', lambda event: self.update_suggestions())  # 实时更新建议
        self.search_entry.bind('<Return>', self.perform_search)  # 绑定回车键

        # 创建项目模糊搜索按钮
        self.search_button = tk.Button(search_frame, text="模糊搜索附近项目", command=self.perform_search)
        self.search_button.pack(side=tk.LEFT, padx=20)
       
        # 创建联想提示列表框，动态显示联想提示
        self.suggestions_listbox = Listbox(self.root, height=5, width=30)
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
        # 获取项目模糊搜索的匹配建议
        suggestions = []
        current_data = get_all_data_scope()
        seen_names = set()  # 用于跟踪已经添加的项目名称

        for full_key in current_data:
            # full_key 是类似于 "省份/项目名称/城市名称" 这样的结构
            path_parts = full_key.split('/')
            
            # 确保项目名称部分是第二个元素，且不包含城市名
            if len(path_parts) > 1:
                project_name = path_parts[2]  # 获取项目名称部分
                
                # 检查项目名称是否包含查询字符串
                if query.lower() in project_name.lower() and project_name not in seen_names:
                    suggestions.append(project_name)
                    seen_names.add(project_name)  # 记录已添加的项目名称，避免重复
        
        return suggestions

    def perform_search(self, event=None):
        project_name = self.search_var.get()
        self.current_range = self.app.range_scale.get()  # 从滑动条获取范围大小并保存当前选择

        if not project_name:
            return

        nearby_projects = self.search_nearby_projects_P2P(project_name, self.current_range)

        if isinstance(nearby_projects, str):  # 如果返回的是错误信息
            messagebox.showwarning("Search Result", nearby_projects)
        else:
            self.display_nearby_projects(nearby_projects)

    def search_nearby_projects_P2P(self, project_name, radius_km=50):
        project_info = self.find_project_coordinates(project_name)
        if not project_info:
            return f"Project {project_name} not found."

        try:
            # 处理纬度
            latitude_str = project_info['地理位置']['纬度']
            if '°S' in latitude_str:
                latitude_str = '-' + latitude_str.replace('°S', '')
            else: 
                latitude_str = latitude_str.replace('°N', '')
            project_latitude = float(latitude_str)

            # 处理经度
            longitude_str = project_info['地理位置']['经度']
            if '°W' in longitude_str:
                longitude_str = '-' + longitude_str.replace('°W', '')
            else: 
                longitude_str = longitude_str.replace('°E', '')
            project_longitude = float(longitude_str)

            # 如果需要，继续处理project_coordinates
            project_coordinates = (project_latitude, project_longitude)
            
        except ValueError as e:
            print(f"Skipping project {pname} due to coordinate error: {str(e)}")

        nearby_projects = []

        for province, projects in self.app.current_data.items():
            for pname, project_details in projects.items():
                try:
                    # 提取并处理其他项目的纬度信息
                    latitude_str = project_details['地理位置']['纬度']
                    if '°S' in latitude_str:
                        latitude_str = '-' + latitude_str.replace('°S', '')
                    else: 
                        latitude_str = latitude_str.replace('°N', '')
                    other_project_latitude = float(latitude_str)

                    # 提取并处理其他项目的经度信息
                    longitude_str = project_details['地理位置']['经度']
                    if '°W' in longitude_str:
                        longitude_str = '-' + longitude_str.replace('°W', '')
                    else: 
                        longitude_str = longitude_str.replace('°E', '')
                    other_project_longitude = float(longitude_str)

                    other_project_coordinates = (other_project_latitude, other_project_longitude)

                    # 计算项目之间的距离
                    distance = geodesic(project_coordinates, other_project_coordinates).kilometers
                    if distance <= radius_km:
                        nearby_projects.append({
                            'name': pname,
                            'province': province,
                            'distance_km': round(distance, 2),
                            'details': project_details
                        })
                except ValueError as e:
                    print(f"Skipping project {pname} due to coordinate error: {str(e)}")
                    continue

        return sorted(nearby_projects, key=lambda x: x['distance_km'])

    def find_project_coordinates(self, project_name):
        all_data = get_all_data_scope()
        for full_key, project_details in all_data.items():
            if project_name.lower() in full_key.lower():
                return project_details
        return None

    def display_nearby_projects(self, nearby_projects):
        # 清空当前界面
        for widget in self.root.winfo_children():
            # 排除 Toplevel 窗口
            if not isinstance(widget, tk.Toplevel):
                widget.pack_forget()
                widget.place_forget()

        self.app.create_UI()

        self.label = tk.Label(self.root, text="Nearby Projects", font=("Arial", 16, "bold"))
        self.label.place(x=20, y=100)

        y = 150  # 初始y偏移，用于放置项目按钮
        for project in nearby_projects:
            project_button = tk.Button(
                self.root,
                text=f"{project['name']} - {project['distance_km']} km",
                font=("Arial", 10),
                command=lambda p=project: self.app.display_project_details(p['name'], p['details'])  # 调用app的方法
            )
            project_button.place(x=20, y=y)  # 将项目按钮放置在固定位置
            y += 40  # 增加y偏移以放置下一个按钮

    def on_suggestion_click(self, event):
        # 处理用户点击联想提示的事件
        selection = self.suggestions_listbox.get(self.suggestions_listbox.curselection())
        self.search_var.set(selection)
        self.suggestions_listbox.place_forget()  # 隐藏联想列表
        self.suggestions_listbox.delete(0, tk.END)
        self.perform_search()

