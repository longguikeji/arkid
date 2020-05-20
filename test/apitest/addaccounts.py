import requests,urllib,demjson
import random,string
import json

localhost = '192.168.200.115:8989'

def login():         #提取登录后的token
    url = 'http://'+ localhost + '/siteapi/oneid/ucenter/login/'

    headers = {
        'Content-Type': 'application/json;charset=UTF-8'
    }
    payload = {
        "password": "admin",
        "username": "admin"
    }

    data=json.dumps(payload)

    response = requests.post(url, data=data, headers=headers)
    # 返回JSON中data数据的token
    token = response.json()['token']
    return token

def create_email(randomlength=10):
    #生成邮箱
    str_list = [random.choice(string.digits + string.ascii_lowercase) for i in range(randomlength)]      #所有数字和小写字母
    random_str = ''.join(str_list)        #生成列表
    email = random_str + "@163.com"
    return email

def create_phone():
    #生成手机号
    second = [3, 4, 5, 7, 8][random.randint(0, 4)]  #第二位数字

    third = {                                    #第三位
        3: random.randint(0, 9),
        4: [5, 7, 9][random.randint(0, 2)],
        5: [i for i in range(10) if i != 4][random.randint(0, 8)],
        7: [i for i in range(10) if i not in [4, 9]][random.randint(0, 7)],
        8: random.randint(0, 9),
    }[second]

    # 最后八位数字
    suffix = random.randint(9999999,100000000)

    # 拼接手机号
    phonenum =  "1{}{}{}".format(second, third, suffix)

    return phonenum

def create_username(randomlength=6):
    #生成用户名
    str_list = [random.choice(string.digits + string.ascii_lowercase) for i in range(randomlength)]      #所有数字和小写字母
    username = ''.join(str_list)        #生成列表
    return username

def getd_root():

    token = login()
    url = 'http://'+ localhost + '/siteapi/oneid/node/d_root/list/'

    headers = {
        'Authorization': "token " + token,
    }

    r = requests.get(url = url,headers = headers)
    a = r.json()
    root = []
    for i in range(1,len(a)): 
        root.append(a[i]["node_uid"])
    return root

def getg_role():
    token = login()
    url = 'http://'+ localhost + '/siteapi/oneid/node/g_role/list/'

    headers = {
        'Authorization': "token " + token,
    }

    r = requests.get(url = url,headers = headers)
    a = r.json()
    role = []
    for i in range(1,len(a)): 
        role.append(a[i]["node_uid"])
    
    return role

def getg_label():
    token = login()
    url = 'http://'+ localhost + '/siteapi/oneid/node/g_label/list/'

    headers = {
        'Authorization': "token " + token,
    }

    r = requests.get(url = url,headers = headers)
    a = r.json()
    label = []
    for i in range(1,len(a)): 
        label.append(a[i]["node_uid"])
    
    return label

def getg_personal():
    token = login()
    url = 'http://'+ localhost + '/siteapi/oneid/meta/node/'

    headers = {
        'Authorization': "token " + token,
    }

    r = requests.get(url = url,headers = headers)
    a = r.json()
    b = a[1]["nodes"]

    zidingyi = []
    for i in range(0,len(b)):
        zidingyi.append(b[i]["node_uid"])
    return zidingyi

node = getg_personal()

def getPergroup(node, x):
    token = login()
    url = 'http://'+ localhost + '/siteapi/oneid/node/'+node[x]+'/list/'

    headers = {
        'Authorization': "token " + token,
    }

    r = requests.get(url = url,headers = headers)
    a = r.json()
    
    b = []

    for i in range(1,len(a)): 
        b.append(a[i]["node_uid"])

    return b

pergroup = []
for x in range(0,len(node)):
    pergroup += getPergroup(node, x)

def select_uids():      #随机选择分组

    root = getd_root()
    role = getg_role()
    label = getg_label()

    uidroot = root
    #a1 = random.choice(uidroot)
    a11 = random.sample(uidroot, 1)
    b1 = random.sample(uidroot, 2)
    c1 = random.sample(uidroot, 3)
    d1 = [a11,b1,c1]
    d11 = random.choice(d1)
        #部门分类组合

    uidrole = role          #角色分类
    a2 = random.choice(uidrole)
    a22 = random.sample(uidrole,1)

    uidlabel = label       #标签分类
    a3 = random.choice(uidlabel)
    a31 = random.sample(uidlabel,1)
    b3 = random.sample(uidlabel,2)
    c3 = random.sample(uidlabel,3)
    d3 = random.sample(uidlabel,4)
    e3 = random.sample(uidlabel,5)

    uidpergroup = pergroup                 #自定义分类
    z = len(uidpergroup)

    if z == 1:
        a4 = random.sample(uidpergroup, 1)
        b4 = []
        c4 = []
    elif 1 < z <= 3:
        a4 = random.sample(uidpergroup, 1)
        b4 = random.sample(uidpergroup, 2)
        c4 = []
    elif z >  3:
        a4 = random.sample(uidpergroup, 1)
        b4 = random.sample(uidpergroup, 2)
        c4 = random.sample(uidpergroup, 3)
    else :
        a4 = []

        
    uid = [a2,a3]
    uid1 = random.sample(uid,1)
    uid2 = random.sample(uid, 2)

    uids = [a22,a31,a31,b3,c3,d3,e3,a4,b4,c4,uid,uid1,uid2]
    node_uids = random.choice(uids) + d11

    return node_uids

def addAccounts():

    token = login()

    email = create_email()

    phonenum = create_phone()

    username = create_username()

    node_uids = select_uids()

    url = 'http://' + localhost + '/siteapi/oneid/user/'

    headers = {
        'Authorization': "token " + token,
        'Content-Type': 'application/json;charset=UTF-8',
    }

    params = {
        "node_uids": node_uids,
        "user":{
        "avatar": "",
        "depts": "null",
        "email": email,
        "employee_number": "",
        "gender": "0",
        "has_password": "true",
        "is_settled": "false",
        "mobile": phonenum,
        "name": username,
        "nodes":"",
        "password": "111111",
        "position": "",
        "private_email": "",
        "require_reset_password": "false",
        "roles": "null",
        "username": username
        }
    }

    data = demjson.encode(params)

    r = requests.post(url = url,data = data,headers = headers)
    return r
    
for i in range(0,3):      #循环调用函数，添加账号,添加的账号数为range函数的第二个参数值
    addAccounts()
