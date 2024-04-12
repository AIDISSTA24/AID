import os

#C:/Users/40382/Desktop/NewPyCG/pycg/examples/inherit
#C:\Users/40382\Desktop\NewPyCG\pycg\examples\jaraco.abode-5.1.0\jaraco\abode
directory = "C:/Users/40382/Desktop/NewPyCG/SDK_dataset/pyfritzhome"



def process_file(file_path):
    with open(file_path, 'r', encoding="utf-8") as file:
        lines = file.readlines()

    modified = False
    new_lines = []
    for line in lines:
        #from .X import Y格式的.删除
        #代码逻辑目前还是有问题
        if 'from .' in line and '. ' not in line:
            modified_line = line.replace('...','.').replace('..','.').replace('from .', 'from ')
            new_lines.append(modified_line)
            modified = True
        #from . import Y格式的from  .删除，还有from .. import Y的格式
        elif 'from . ' in line and '. ' in line:
            modified_line = line.replace('from .... ', '').replace('from ... ', '').replace('from .. ', '').replace('from . ', '')
            new_lines.append(modified_line)
            modified = True
        else:
            new_lines.append(line)



    if modified:
        with open(file_path, 'w', encoding="utf-8") as file:
            file.writelines(new_lines)

def process_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                process_file(file_path)

if __name__ == '__main__':
    process_directory(directory)
    print('已删除所有点号')

