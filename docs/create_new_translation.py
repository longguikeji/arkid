import os
from google_trans_new import google_translator
import shutil
  
translator = google_translator() 

dir_path = "zh/"
target_dir_path = "en-us/"
target_lang = 'en'

file_tree = {}

def create_template_dir(source_dir,target_dir):
    for file in os.listdir(source_dir):

        if ".md" in file or ".py" in file:
            # markdown 文档
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            shutil.copyfile(os.path.join(source_dir,file),os.path.join(target_dir,file))

        if file in ['assets', 'overrides', 'stylesheets',"bin","__pycache__","migrations","lib"]:
            continue

        if os.path.isdir(os.path.join(source_dir,file)):
            create_template_dir(os.path.join(source_dir,file),os.path.join(target_dir,file))

def translate_dir(path,dir_name):
    pass

def translate_file(target_dir,source_dir,file_name,suffix):
    translated_filename = file_name
    if target_lang not in translator.detect(file_name):
        print(file_name,target_lang)
        translated_filename = translator.translate(file_name,target_lang)

    if os.path.exists(os.path.join(target_dir,translated_filename+"."+suffix)):
        return

    translated_text = ""
    with open(os.path.join(source_dir,file_name+"."+suffix),'r') as f:
        text = f.read()
        translated_text = translator.translate(text,target_lang)
        print(translated_text)

    with open(os.path.join(target_dir,translated_filename+"."+suffix),'w') as f:
        f.write(translated_text)

def read_translating_files_tree(target_dir,tree):
    print(f"开始读取{target_dir}")
    for file in os.listdir(target_dir):
        # 忽略软连接目录
        if file in ['assets', 'overrides', 'stylesheets',"bin","__pycache__"]:
            continue
        translated_dir = translator.translate(file.replace(" ",""),target_lang).title()
        if os.path.isdir(os.path.join(target_dir,file)):
            tree[file] = {
                "name": translated_dir,
                "subfiles": {}
            }
            read_translating_files_tree(os.path.join(target_dir,file),tree[file]["subfiles"])
        else:
            tree[file] = {
                "name": translated_dir,
            }


if __name__ == "__main__":
    # 创建基础文件夹
    if not os.path.exists(target_dir_path):
        os.makedirs(target_dir_path)
        os.makedirs(os.path.join(target_dir_path,'docs'))
        # 创建软连接
        for soft_link in ['assets', 'overrides', 'stylesheets']:
            print(f"cd {os.path.join(target_dir_path,'docs')} && ln -s ../../{soft_link} ./{soft_link}")
            os.system(f"cd {os.path.join(target_dir_path,'docs')} && ln -s ../../{soft_link} ./{soft_link}")

    # 读取待翻译文件目录
    docs_dir_path = os.path.join(dir_path,'docs')
    dir_list = os.listdir(docs_dir_path)

    template_dir = "templates"
    docs_template_dir = "templates/docs"
    
    create_template_dir(docs_dir_path,docs_template_dir)

    read_translating_files_tree(docs_template_dir,file_tree)
    print(file_tree)

    # for dir in dir_list:
    #     if dir in ['assets', 'overrides', 'stylesheets']:
    #         continue

    #     if os.path.isdir(os.path.join(docs_dir_path,dir)):
    #         translated_dir = translator.translate(dir.replace(" ",""),target_lang).title()
    #         print(translated_dir)
    #     else:
    #         translated_text = ""
    #         with open(os.path.join(docs_dir_path,dir),'r') as f:
    #             text = f.read()
    #             translated_text = translator.translate(text,target_lang)
    #             print(translated_text)
    #         with open(os.path.join(target_dir_path+'/docs',dir),'w') as f:
    #             f.write(translated_text)
