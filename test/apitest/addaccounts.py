import requests,urllib,demjson
import random,string

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

def select_uids():      #随机选择分组

    uidroot = ["d_longguikkeji","d_axiangmuqianduan3","d_fuwuqi","d_zhongjianjian4","d_diyixiaozu5","d_dierxiaozu2","d_yanfabubxiangmu2","d_achanpinzhenglixuqiu3","d_achanpinuisheji","d_bchanpin2","d_yizu4","d_erzu4","d_xingnengceshi","d_shouhoujishuzhichi2","d_xiaoshoubu","d_caiwubu","d_renliziyuanbu"]
    a1 = random.choice(uidroot)
    a11 = random.sample(uidroot, 1)
    b1 = random.sample(uidroot, 2)
    c1 = random.sample(uidroot, 3)

    uidrole = ["g_gm","g_chanpinjingli","g_jishuzongjian"]
    a2 = random.choice(uidrole)
    a22 = random.sample(uidrole,1)

    uidlabel1 = ["g_shixi","g_yinianyinei","g_yidaosannian","g_sannianyishang"]
    uidlabel2 = ["g_c","g_c1","g_java","g_php","g_django","g_python"]
    a31 = random.choice(uidlabel1)
    a311 = random.sample(uidlabel1,1)

    a32 = random.choice(uidlabel2)
    a321 = random.sample(uidlabel2,1)
    b32 = random.sample(uidlabel2,2)
    c32 = random.sample(uidlabel2,3)
    d32 = random.sample(uidlabel2,4)

    aa1 = a321.copy()
    aa1.insert(0,a31)
    aa2 = b32.copy()
    aa2.insert(0,a31)
    aa3 = c32.copy()
    aa3.insert(0,a31)
    aa4 = d32.copy()
    aa4.insert(0,a31)

    uidxingbie = ["g_nan","g_nv"]
    a4 = random.choice(uidxingbie)
    a44 = random.sample(uidxingbie, 1)

    uidzhengzhimianmao = ["g_tuanyuan","g_dangyuan","g_qunzhong"]
    a5 = random.choice(uidzhengzhimianmao)
    a55 = random.sample(uidzhengzhimianmao,1)

    uid = [a1,a2,a31,a32,a4,a5]
    uid1 = random.sample(uid, 2)
    uid2 = random.sample(uid, 3)
    uid3 = random.sample(uid, 4)
    uid4 = random.sample(uid,5)

    uids = [a11,b1,c1,a22,a311,a321,b32,c32,d32,aa1,aa2,aa3,aa4,a44,a55,uid,uid1,uid2,uid3,uid4]
    node_uids = random.choice(uids)

    return node_uids

def addAccounts():

    email = create_email()

    phonenum = create_phone()

    username = create_username()

    node_uids = select_uids()

    url = 'http://192.168.200.115:8989/siteapi/oneid/user/'

    headers = {
        'Authorization': 'token b149e74b33056bb7ffcd834e87fbe66dded240d8',
        'Content-Type': 'application/json;charset=UTF-8',
        'Cookie': 'csrftoken=W4hnIQKJaAQOfjcm12ycnxWUJWAP567UpHiPPLTWsAwAU6NDu4i8hSDF5jHSC0JI; spauthn=b149e74b33056bb7ffcd834e87fbe66dded240d8',
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
    
for i in range(1,3):      #循环调用函数，添加账号
    addAccounts()

