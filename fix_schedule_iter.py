import os

def replace_in_file(filepath, old_str, new_str):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.replace(old_str, new_str)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

replace_in_file('admin-global-deals.html', 'data.filter(deal => {', 'data.filter(schedule => {')
replace_in_file('admin-global-deals.html', 'data.forEach(deal => {', 'data.forEach(schedule => {')
replace_in_file('admin-global-deals.html', 'if (deal) {\n                const newMemo = (schedule.memo || \'\')', 'if (deal) {\n                const newMemo = (deal.memo || \'\')')

replace_in_file('deal-register.html', 'allDeals.forEach(deal => {', 'allDeals.forEach(schedule => {')
replace_in_file('deal-register.html', 'const li = createDealListItem(deal, !schedule.buildings && !schedule.building_id);', 'const li = createDealListItem(schedule, !schedule.buildings && !schedule.building_id);')

print("Fixed schedule iterator bugs")
