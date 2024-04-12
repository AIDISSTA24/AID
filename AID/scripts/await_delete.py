import os

# 指定文件夹路径
#directory = 'C:/Users/40382/Desktop/NewPyCG/scripts/test' 
directory = "C:/Users/40382/Desktop/NewPyCG/SDK_dataset/pyfritzhome"


def remove_await_in_files(directory):
    # 遍历文件夹内所有文件
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                # 读取文件内容并删除 await 关键字
                with open(file_path, 'r', encoding="utf-8") as f:
                    file_content = f.read()
                file_content = file_content.replace('await ', '')
                # 将修改后的内容重新写入文件
                with open(file_path, 'w', encoding="utf-8") as f:
                    f.write(file_content)

# 调用函数来执行操作
remove_await_in_files(directory)