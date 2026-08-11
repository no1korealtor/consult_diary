import os
import time

def print_unicode_paths():
    user_profile = os.environ.get('USERPROFILE', '')
    paths = [
        os.path.join(user_profile, 'OneDrive'),
        os.path.join(user_profile, 'Pictures'),
        os.path.join(user_profile, 'Downloads'),
        os.path.join(user_profile, 'Desktop')
    ]
    
    now = time.time()
    one_hour = 3600
    
    for base in paths:
        if not os.path.exists(base):
            continue
        for root, dirs, files in os.walk(base):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    full_path = os.path.join(root, file)
                    try:
                        mtime = os.path.getmtime(full_path)
                        # Look for files modified in the last 2 hours
                        if now - mtime < one_hour * 2:
                            print(f"Path: {repr(full_path)}, size: {os.path.getsize(full_path)}")
                    except Exception:
                        pass

if __name__ == '__main__':
    print_unicode_paths()
