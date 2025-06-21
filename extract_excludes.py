import os
import sys
import zipfile

def extract_modules_from_internal(internal_path):
    """
    从 PyInstaller 的 _internal 目录中提取打包模块名
    """
    modules = set()

    # 1. base_library.zip 中的模块
    zip_path = os.path.join(internal_path, 'base_library.zip')
    if os.path.exists(zip_path):
        with zipfile.ZipFile(zip_path) as zf:
            for name in zf.namelist():
                if name.endswith(('.py', '.pyc')) and not name.startswith('__pycache__'):
                    mod = name.replace('/', '.').rsplit('.', 1)[0]
                    top_mod = mod.split('.')[0]
                    modules.add(top_mod)

    # 2. lib-dynload 中的 .so 模块
    dyn_path = os.path.join(internal_path, 'lib-dynload')
    if os.path.isdir(dyn_path):
        for f in os.listdir(dyn_path):
            if f.endswith('.so'):
                mod = f.split('.')[0].split('-')[0].split('.')[0]
                modules.add(mod)

    # 3. 其他打包模块目录（如 PIL, wx, cv2）
    for item in os.listdir(internal_path):
        full = os.path.join(internal_path, item)
        if os.path.isdir(full) and item not in ['lib-dynload', 'gio_modules', 'gi_typelibs']:
            modules.add(item)

    return modules

def load_used_modules(path):
    """
    从 used_modules.txt 加载使用过的顶级模块名
    """
    with open(path, encoding='utf-8') as f:
        return set(line.strip().split('.')[0] for line in f if line.strip())

def main(internal_path, used_path='used_modules.txt', output_path='suggest_excludes.txt'):
    packaged = extract_modules_from_internal(internal_path)
    used = load_used_modules(used_path)
    unused = sorted(packaged - used)

    print(f"共发现打包模块 {len(packaged)} 个，实际使用 {len(used)} 个，未使用 {len(unused)} 个。")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# 建议排除的模块，可粘贴到 .spec 文件中 Analysis() 的 excludes 参数：\n")
        f.write(f"excludes = {unused}\n")

    print(f"\n✅ 已生成建议排除模块文件：{output_path}")
    print("\n以下为未使用的模块（供检查）：\n")
    for m in unused:
        print(m)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法：python extract_excludes_to_file.py dist/main_app/_internal [used_modules.txt]")
    else:
        internal_dir = sys.argv[1]
        used_path = sys.argv[2] if len(sys.argv) > 2 else 'used_modules.txt'
        main(internal_dir, used_path)
