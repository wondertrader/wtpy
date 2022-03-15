import os
import yaml
import json

def json_to_yaml(filename:str):
    f = open(filename,"r",encoding="utf8")
    content = f.read()
    f.close()
    obj = json.loads(content)

    f = open(filename[:-4]+"yaml", "w")
    yaml.dump(obj, f, indent=4, allow_unicode=True)
    f.close()

def yaml_to_json(filename:str):
    f = open(filename,"r",encoding="utf8")
    content = f.read()
    obj = yaml.full_load(content)
    f.close()

    f = open(filename[:-4]+"json", "w")
    content = json.dumps(obj, indent=4)
    f.write(content)
    f.close()

def scan_folder(folder:str):
    files = os.listdir(folder)
    for fname in files:
        ext = fname[-5:].lower()
        if ext != '.json':
            continue
        
        fpath = os.path.join(folder, fname)
        print(fpath)
        json_to_yaml(fpath)

if __name__ == "__main__":
    folder = "./"
    dirs = os.listdir(folder)
    for dname in dirs:        
        dpath = os.path.join(folder, dname)
        if not os.path.isdir(dpath):
            continue
        scan_folder(dpath)
