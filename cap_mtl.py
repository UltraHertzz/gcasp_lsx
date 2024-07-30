import os

"""
注释.obj 文件中的.mtl文件
"""
def comment_mtl_and_group_references(obj_file_path):
    with open(obj_file_path, 'r') as file:
        lines = file.readlines()

    with open(obj_file_path, 'w') as file:
        for line in lines:
            if line.startswith('mtllib') or line.startswith('usemtl') or line.startswith('g ') or line.startswith('l '):
                file.write(f"# {line}")  # 注释掉该行
            else:
                file.write(line)

def process_directory(directory):
    for root, dirs, files in os.walk(directory):
        print(root)
        for file in files:
            if file.endswith('.obj'):
                obj_file_path = os.path.join(root, file)
                comment_mtl_and_group_references(obj_file_path)

# 处理包含 .obj 文件的目录
directory = './eval_datas/obj_models/train'
process_directory(directory)

print("Commented out .mtl and group references in .obj files")
