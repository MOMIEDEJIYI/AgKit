import os
import shutil

def delete_dirs_and_files(root_path: str, targets: list[str]):
    for root, dirs, files in os.walk(root_path, topdown=False):
        # 删除目录
        for name in dirs:
            dir_path = os.path.join(root, name)
            if name in targets:
                try:
                    shutil.rmtree(dir_path)
                    print(f"Deleted directory: {dir_path}")
                except Exception as e:
                    print(f"Failed to delete {dir_path}: {e}")

        # 删除文件（如果你想删除特定后缀的 runtime 文件）
        for name in files:
            file_path = os.path.join(root, name)
            for target in targets:
                if name == target or name.endswith(target):
                    try:
                        os.remove(file_path)
                        print(f"Deleted file: {file_path}")
                    except Exception as e:
                        print(f"Failed to delete {file_path}: {e}")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 你可以添加更多需要删除的目标
    delete_dirs_and_files(current_dir, ["__pycache__", "runtime"])
