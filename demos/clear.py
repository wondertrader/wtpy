import os
import sys
import shutil

clear_names = [
    "Logs",
    "BtLogs",
    "DtLogs",
    "outputs_bt",
    "generated",
    "CTPMDFlow",
    "CTPTDFlow",
    "CTPFlow",
    "__pycache__",
    "his",
    "rt",
    "cache.dmb"
]

clear_exts = [".log", ".xlsx", ".membin"]

def clear_temp(root_dir):
    folders = os.listdir(root_dir)
    for fname in folders:
        _,ext = os.path.splitext(fname)
        if ext.lower() in clear_exts:
            full_path = os.path.join(root_dir, fname)
            print('Deleting file:', full_path)
            os.remove(full_path)
            continue

        if fname not in clear_names:
            continue
        
        full_path = os.path.join(root_dir, fname)
        if os.path.isdir(full_path):
            print('Deleting folder:', full_path)
            shutil.rmtree(full_path)
        else:
            print('Deleting file:', full_path)
            os.remove(full_path)

if __name__ == "__main__":
    root = os.getcwd()
    if sys.argv.__len__() > 1:
        root = sys.argv[1]

    root = os.path.abspath(root)
    print(f"Clearing temp files in {root}...")

    if not os.path.exists(root):
        print('Path not exists:', root)
        exit(0)

    if not os.path.isdir(root):
        print('Path isnot dir:', root)
        exit(0)
    
    folders = os.listdir(root)
    for folder in folders:

        full_path = os.path.join(root, folder)

        if not os.path.isdir(full_path):
            continue

        clear_temp(full_path)