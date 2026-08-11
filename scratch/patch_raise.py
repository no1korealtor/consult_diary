with open('trade_viewer.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(len(lines)):
    if "except Exception as e:" in lines[i]:
        lines[i] = "    except Exception as e:\n        import traceback; traceback.print_exc(); raise e\n"

with open('trade_viewer.py', 'w', encoding='utf-8') as f:
    f.write(''.join(lines))
