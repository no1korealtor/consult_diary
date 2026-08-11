import sys

def patch_moa(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if "def check_moatown_and_redev(" not in content:
        moa_func = """
def check_moatown_and_redev(addr):
    return {"moatown": False, "moatown_name": "", "redev": False, "redev_name": ""}
"""
        content = moa_func + "\n" + content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Patched {file_path}")
    else:
        print(f"Already patched {file_path}")

patch_moa('trade_viewer.py')
