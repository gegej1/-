import tkinter as tk
from tkinter import messagebox, StringVar, Listbox, Scale, HORIZONTAL
from geopy.distance import geodesic

class Mode2:
    def __init__(self, root, app):
        self.root = root
        self.app = app

    def create_UI_elements(self):

        # 在同一行中放置搜索栏
        search_frame = tk.Frame(self.root)
        search_frame.place(x=790, y=130)  # 调整 x 和 y 以放置到合适位置

        # 创建城市搜索框
        self.city_search_var = StringVar()
        self.city_search_entry = tk.Entry(search_frame, textvariable=self.city_search_var, width=30)
        self.city_search_entry.pack(side=tk.LEFT, padx=20)
        self.city_search_entry.bind('<Return>', self.perform_search)  # 绑定回车键

        # 创建城市搜索按钮
        self.city_search_button = tk.Button(search_frame, text="地名搜索附近项目", command=self.perform_search)
        self.city_search_button.pack(side=tk.LEFT, padx=20)

    def perform_search(self, event=None):
        city_name = self.city_search_var.get()
        self.current_range = self.app.range_scale.get()  # 从滑动条获取范围大小并保存当前选择

        if not city_name:
            messagebox.showwarning("Search Result", "Please enter a city name.")
            return

        nearby_projects = self.search_nearby_projects(city_name, self.current_range)

        if isinstance(nearby_projects, str):  # 如果返回的是错误信息
            messagebox.showwarning("Search Result", nearby_projects)
        else:
            self.display_nearby_projects(nearby_projects)

    def search_nearby_projects(self, city_name, radius_km=50):
        return self.find_nearby_projects(city_name, self.app.current_data, radius_km)
    
    def find_nearby_projects(self, city_name, project_data, radius_km=50):
        city_info = self.find_city_coordinates(city_name)

        if not city_info:
            return f"City {city_name} not found."

        city_coordinates = (city_info['latitude'], city_info['longitude'])
        nearby_projects = []

        for province, projects in project_data.items():
            for project_name, project_details in projects.items():
                try:
                    # 提取并处理项目的纬度信息
                    latitude_str = project_details['地理位置']['纬度']
                    if '°S' in latitude_str:
                        latitude_str = '-' + latitude_str.replace('°S', '')
                    else: 
                        latitude_str = latitude_str.replace('°N', '')
                    project_latitude = float(latitude_str)

                    # 提取并处理项目的经度信息
                    longitude_str = project_details['地理位置']['经度']
                    if '°W' in longitude_str:
                        longitude_str = '-' + longitude_str.replace('°W', '')
                    else: 
                        longitude_str = longitude_str.replace('°E', '')
                    project_longitude = float(longitude_str)

                    project_coordinates = (project_latitude, project_longitude)

                    # 计算项目和城市之间的距离
                    distance = geodesic(city_coordinates, project_coordinates).kilometers
                    if distance <= radius_km:
                        nearby_projects.append({
                            'name': project_name,
                            'province': province,
                            'distance_km': round(distance, 2),
                            'details': project_details
                        })
                except ValueError as e:
                    print(f"Skipping project {project_name} due to coordinate error: {str(e)}")
                    continue

        return sorted(nearby_projects, key=lambda x: x['distance_km'])

    def find_city_coordinates(self, city_name):
        city_name_lower = city_name.lower()
        if city_name_lower in self.app.city_index:
            return self.app.city_index[city_name_lower]
        return None

    def display_nearby_projects(self, nearby_projects):
        # 清空当前界面
        for widget in self.root.winfo_children():
            # 排除 Toplevel 窗口
            if not isinstance(widget, tk.Toplevel):
                widget.pack_forget()
                widget.place_forget()

        self.app.create_UI()

        # 使用 place() 布局管理器
        label = tk.Label(self.root, text="Nearby Projects", font=("Arial", 16, "bold"))
        label.place(x=20, y=100)  # 将标题放在固定位置

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
