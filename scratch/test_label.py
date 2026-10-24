
from trade_viewer import get_size_category_label, get_apartment_size_groups

items = [
    {'excluUseAr': 59.7},
    {'excluUseAr': 84.9},
    {'excluUseAr': 114.9}
]
groups = get_apartment_size_groups(items)
print(groups)
label1 = get_size_category_label(59.7, '아파트', groups)
label2 = get_size_category_label(84.9, '아파트', groups)
label3 = get_size_category_label(None, '아파트', groups)
print('label1:', label1)
print('label2:', label2)
print('label3:', label3)

