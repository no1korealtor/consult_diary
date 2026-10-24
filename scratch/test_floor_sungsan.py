import urllib.request
import urllib.parse
import json

from get_building_info import get_floor_data

sigunguCd = "11440"
bjdongCd = "12500"
bun = "0200"
ji = "0109"

# Let's say user entered '201호'
ho_name = "201"
# For '201호', floor is usually '2'.
floor_name = str(int(ho_name) // 100) # '2'

floor_data = get_floor_data(sigunguCd, bjdongCd, bun, ji, floor_name)
print("Floor Data for floor", floor_name, ":", floor_data)
