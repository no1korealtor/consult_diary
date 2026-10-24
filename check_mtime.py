import os
import time

dir_name = "종합분석보고서"
with open("temp_mtime.txt", "w", encoding="utf-8") as f:
    for filename in os.listdir(dir_name):
        if "시세" in filename:
            path = os.path.join(dir_name, filename)
            mtime = time.ctime(os.path.getmtime(path))
            f.write(f"{filename}: {mtime}\n")
