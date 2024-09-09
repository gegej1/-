import json
import tkinter as tk

with open("data_China.json", "r", encoding="utf-8") as file:
    data_China = json.load(file)
with open("data_Abroad.json", "r", encoding="utf-8") as file:
    data_Abroad = json.load(file)

def load_city_data(file_path="countries_states_cities.json"):
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data

def create_city_index(file_path="countries_states_cities.json"):
        data = load_city_data(file_path)
        city_index = {}
        for country in data:
            for state in country['states']:
                for city in state['cities']:
                    city_index[city['name'].lower()] = {
                        'latitude': float(city['latitude']),
                        'longitude': float(city['longitude']),
                        'state': state['name'],
                        'country': country['name']
                    }
        return city_index

def get_all_data_scope():
        # 获取所有层级的数据范围
        all_data = {}
        def traverse(data, prefix=""):
            for key, value in data.items():
                projectSet = value
                full_key = f"{prefix}/{key}" if prefix else key
                all_data[full_key] = projectSet  # value是一个省份的项目集合
                # 将城市信息添加到路径中
                for key,value in projectSet.items():
                    full_data = f"{full_key}/{value['地理位置']['城市']}/{key}"
                    all_data[full_data] = value

        traverse(data_China)
        traverse(data_Abroad)
        
        return all_data