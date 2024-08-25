import json
import re

# 假设route_shape是一个从数据库中读取的字符串
route_shape = "[{lon=-6.27347093024794, lat=53.3550173969283}, {lon=-6.2734795, lat=53.3550716}]"

# 首先，将等号（=）替换为冒号（:）
route_shape_temp_format = route_shape.replace("=", ":")

# 使用正则表达式来匹配所有键名，并在它们周围添加双引号
# 这里假设键名不包含特殊字符
route_shape_json_format = re.sub(r"(\w+)(:)", r'"\1"\2', route_shape_temp_format)

# 可以使用json.loads()来验证转换后的字符串是否为有效的JSON
try:
    valid_json = json.loads(route_shape_json_format)
    print("转换成功，有效的JSON格式。")
    print(valid_json)  # 美化打印JSON对象，仅用于验证
except json.JSONDecodeError as e:
    print(route_shape_json_format)
    print("转换失败，字符串不是有效的JSON格式。错误信息:", e)
