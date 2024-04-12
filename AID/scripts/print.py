import os

folder_path = 'C:/Users/40382/Desktop/NewPyCG/SDK_dataset/pyfritzhome'  # 将路径替换为你想要检查的文件夹路径

def print_py_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.abspath(os.path.join(root, file))
                print(file_path)

# 用法示例：

print_py_files(folder_path)