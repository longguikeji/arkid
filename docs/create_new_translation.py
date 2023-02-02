import os
from google_trans_new import google_translator
import shutil
import string
  
translator = google_translator() 

dir_path = "zh/"
target_dir_path = "en/"
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

def is_chinese(checking_str:str):
    for ch in checking_str:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False

def translate_file(target_dir,source_dir,file_name,suffix):
    translated_filename = file_name
    if is_chinese(file_name):
        translated_filename = translator.translate(file_name,target_lang)

    if os.path.exists(os.path.join(target_dir,translated_filename+"."+suffix)):
        return

    translated_text = ""
    with open(os.path.join(source_dir,file_name+"."+suffix),'r') as src, open(os.path.join(target_dir,translated_filename+"."+suffix),'w') as tgt:
        lines = []
        for line in src.readlines():

            if is_chinese(line):
                count = 0
                for ch in line:
                    if u'\u4e00' <= ch <= u'\u9fff':
                        break
                    count += 1
                translated_text = line[:count] + translator.translate(line[count:],target_lang)
                lines.append(translated_text)
            else:
                lines.append(line)

        tgt.writelines(lines)

    with open(os.path.join(target_dir,translated_filename+"."+suffix),'w') as f:
        f.write(translated_text)

def read_translating_files_tree(target_dir,tree, p_translate_dir=''):
    # print(f"开始读取{target_dir}")
    for file in os.listdir(target_dir):
        # 忽略软连接目录
        if file in ['assets', 'overrides', 'stylesheets',"bin","__pycache__"]:
            continue
        source_file_path = os.path.join(target_dir,file)
        if os.path.isdir(source_file_path):
            f_name = translator.translate(file,target_lang).title() if is_chinese(file) else file
            f_name = f_name[:-1] if f_name.endswith(' ') else f_name

            if file.startswith(' '):
                count = 0
                for ch in file:
                    if ch != " ":
                        break
                    count += 1
                f_name = " "*count + f_name

            traslated_dir_path = os.path.join(p_translate_dir,f_name)
            tree[file] = {
                "name": f_name,
                "subfiles": {},
                "is_dir": True,
                "source": source_file_path,
                "target": traslated_dir_path
            }
            read_translating_files_tree(source_file_path,tree[file]["subfiles"],traslated_dir_path)
        else:
            if ".md" in file:
                f_name = file
                if is_chinese(file):
                    f_name = translator.translate(file.replace(".md",""),target_lang).title()
                    f_name = f_name.replace(" ","")+".md"
                tree[file] = {
                    "name": f_name,
                    "source": source_file_path,
                    "target": os.path.join(p_translate_dir,f_name),
                    "is_dir": False,
                }
            else:
                tree[file] = {
                    "name": file,
                    "source": source_file_path,
                    "target": os.path.join(p_translate_dir,file),
                    "is_dir": False,
                }


def translate_line(line):
    text = ""
    rs = ""
    for ch in line:
        # print(ch)
        if u'\u4e00' <= ch <= u'\u9fff' or ch in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789()[]{}":
            text += ch            
        else:
            # print(ch, ",",text)
            transed_text = translator.translate(text,target_lang)

            if transed_text.endswith(' '):
                transed_text = transed_text[:-1]

            rs += transed_text
            rs += ch
            text = ""

    if text:
        transed_text = translator.translate(text,target_lang)

        if transed_text.endswith(' '):
            transed_text = transed_text[:-1]

        rs += transed_text

    return rs


def copy_or_trans_file(source_file:str,target_file:str):
    if target_file.endswith(".py"):
        # python文件  直接复制
        shutil.copyfile(source_file,target_file)
    elif target_file.endswith(".md"):
        # md文件内容发起翻译后写入
        translated_text = ""
        with open(source_file,'r') as src, open(target_file,'w') as tgt:
            lines = []
            for line in src.readlines():

                if is_chinese(line):
                    count = 0
                    for ch in line:
                        if u'\u4e00' <= ch <= u'\u9fff':
                            break
                        count += 1
                    translated_text = line[:count] + translate_line(line[count:])
                    lines.append(translated_text if '\n' in translated_text else translated_text + '\n')
                else:
                    lines.append(line if line and '\n' in line else (line or '') + '\n')

            tgt.writelines(lines)

def copy_or_translate_doc(tree,force_translate=False):
    for k,v in tree.items():
        print(k,v)
        if v["is_dir"]:
            # 创建目录
            if not os.path.exists(v["target"]):
                os.mkdir(v["target"])
            copy_or_translate_doc(v["subfiles"])
        else:
            if  not os.path.exists(v["target"]) or force_translate:
                copy_or_trans_file(v["source"],v["target"])

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

    read_translating_files_tree(docs_template_dir,file_tree,p_translate_dir=os.path.join(target_dir_path,'docs'))

    copy_or_translate_doc(file_tree)