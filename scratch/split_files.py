import os

CHUNK_SIZE = 9.5 * 1024 * 1024 # 9.5MB (safely under 10MB)

def split_file(file_path, output_dir):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
        
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    print(f"Splitting '{file_name}' ({file_size / (1024*1024):.2f} MB)...")
    
    chunks = []
    with open(file_path, 'rb') as f:
        chunk_num = 1
        while True:
            chunk_data = f.read(int(CHUNK_SIZE))
            if not chunk_data:
                break
            
            chunk_name = f"{file_name}.{chunk_num:03d}"
            chunk_path = os.path.join(output_dir, chunk_name)
            with open(chunk_path, 'wb') as chunk_file:
                chunk_file.write(chunk_data)
                
            print(f" -> Created: {chunk_name} ({len(chunk_data) / (1024*1024):.2f} MB)")
            chunks.append(chunk_name)
            chunk_num += 1
            
    # Generate the [복원하기].bat file content
    bat_name = f"[{file_name.replace('.zip', '')}_복원하기].bat"
    bat_path = os.path.join(output_dir, bat_name)
    
    plus_str = " + ".join([f'"{c}"' for c in chunks])
    cmd = f'copy /b {plus_str} "{file_name}"\n'
    
    with open(bat_path, 'w', encoding='cp949') as bat_file:
        bat_file.write("@echo off\n")
        bat_file.write("echo 분할된 파일 복원을 시작합니다...\n")
        bat_file.write(cmd)
        bat_file.write("echo 복원이 완료되었습니다! 압축파일(.zip)을 해제하고 사용하세요.\n")
        bat_file.write("pause\n")
        
    print(f" -> Created Batch Script: {bat_name}")
    print("-" * 50)

def main():
    import glob
    
    base_dir = r"d:\부동산업무\antigravity\consult_diary\scratch"
    output_dir = os.path.join(base_dir, "블로그_업로드용")
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Korealtor 배포용
    korealtor_zips = glob.glob(os.path.join(base_dir, "Korealtor배포용_*.zip"))
    if korealtor_zips:
        korealtor_path = max(korealtor_zips, key=os.path.getmtime)
        split_file(korealtor_path, output_dir)
    else:
        print("No Korealtor zip files found to split.")
    
    # 2. 부동산정보 조회기 배포용
    viewer_zips = glob.glob(os.path.join(base_dir, "부동산정보_조회기_배포용_*.zip"))
    if viewer_zips:
        viewer_path = max(viewer_zips, key=os.path.getmtime)
        split_file(viewer_path, output_dir)
    else:
        print("No viewer zip files found to split.")
    
    print(f"All files split successfully! Check directory: {output_dir}")

if __name__ == "__main__":
    main()
