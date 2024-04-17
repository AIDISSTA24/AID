import subprocess
from compare import compare_json_files

def DECG_run(source_path, test_file, test_category):
    command = [
        "python",         
        source_path,  
        test_file,  
        "--package",         
        test_category,  
        "-o",                 
        "RQ3\cg.json"             
    ]
    return command

def PyCG_run(source_path, test_file, test_category):
    command = [
        "python",            
        source_path, 
        test_file,  
        "--package",          
        test_category,  
        "-o",                
        "RQ3\cg2.json"         
    ]
    return command

if __name__ == "__main__":

    DECG_path = r'AID\__main__.py'
    PyCG_path = r'pycg\__main__.py'
    test_path = r'micro-benchmark\kwargs'
    categories = [r'\assigned_call', r'\call', r'\chained_call']

    DECG_accuracy = 0
    PyCG_accuracy = 0

    for category in categories:
        
        test_category = test_path + category

        test_file = test_category + r'\main.py'
        
        file1_path = r'RQ3\cg.json'
        file2_path = r'RQ3\cg2.json'
        file3_path = test_category + r'\callgraph.json'

        result = subprocess.run(DECG_run(DECG_path, test_file, test_category), check=True)
        result2 = subprocess.run(PyCG_run(PyCG_path, test_file, test_category), check=True)

        result1 = compare_json_files(file1_path, file3_path)
        if result1:
            DECG_accuracy += 1

        result2 = compare_json_files(file2_path, file3_path)
        if result2:
            PyCG_accuracy += 1
        
        print("DECG Accuracy: " + str(DECG_accuracy) + "/" + str(len(categories)))
        print("PyCG Accuracy: " + str(PyCG_accuracy) + "/" + str(len(categories)))
        print("_________________")


    