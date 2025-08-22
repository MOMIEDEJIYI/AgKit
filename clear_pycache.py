import os
import shutil
import stat

def remove_readonly(func, path, excinfo):
    # 修改权限后重试
    os.chmod(path, stat.S_IWRITE)
    func(path)

def delete_dirs_and_files(root_path: str, targets: list[str]):
    for root, dirs, files in os.walk(root_path, topdown=False):
        # 删除目录
        for name in dirs:
            dir_path = os.path.join(root, name)
            if name in targets:
                try:
                    shutil.rmtree(dir_path, onerror=remove_readonly)
                    print(f"Deleted directory: {dir_path}")
                except Exception as e:
                    print(f"Failed to delete {dir_path}: {e}")

        # 删除文件（针对特定后缀或文件名）
        for name in files:
            file_path = os.path.join(root, name)
            for target in targets:
                if name == target or name.endswith(target):
                    try:
                        os.chmod(file_path, stat.S_IWRITE)
                        os.remove(file_path)
                        print(f"Deleted file: {file_path}")
                    except Exception as e:
                        print(f"Failed to delete {file_path}: {e}")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    delete_dirs_and_files(current_dir, ["__pycache__", "runtime", "build", "conversation"])
