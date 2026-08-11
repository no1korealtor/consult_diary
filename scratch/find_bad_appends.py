import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

def main():
    p = r'D:\부동산업무\antigravity\consult_diary\scratch\중개수첩_오토봇.exe_extracted\PYZ.pyz_extracted\decompiled\building_viewer.py'
    lines = open(p, 'r', encoding='utf-8', errors='ignore').read().splitlines()
    for idx, line in enumerate(lines):
        if 'lines.append' in line:
            if '{"정보없음"}' in line or '{"일반건축물' in line:
                print(f'{idx+1}: {line}')

if __name__ == '__main__':
    main()
