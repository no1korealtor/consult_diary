import ast

def find_f_refs(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        source = file.read()
    
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == 'f':
            print(f"{filepath}:{node.lineno}: found reference to 'f', ctx: {type(node.ctx).__name__}")
        elif isinstance(node, ast.arg) and node.arg == 'f':
            print(f"{filepath}:{node.lineno}: found argument 'f'")

find_f_refs("d:/부동산업무/antigravity/consult_diary/scratch/building_viewer.py")
find_f_refs("d:/부동산업무/antigravity/consult_diary/scratch/trade_viewer.py")
