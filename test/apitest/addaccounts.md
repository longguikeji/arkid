本文用于介绍 `addaccounts.py` 文件的使用                     
### 一、文件意义                   
&nbsp;&nbsp;&nbsp;&nbsp; `addaccounts.py` 是用于给ArkID添加账号的 [python](https://www.python.org/) 脚本文件，目的是产生大量数据用于接口性能测试        
### 二、使用条件      
&nbsp;&nbsp;&nbsp;&nbsp;安装 `python3`     
### 三、使用方法      
1. 将 `addaccounts.py` 文件保存到本地    
2. 打开文件，修改文件中常量 `localhost` 的值为本地 IP 或 ArkID 域名
```
localhost = '192.168.200.115:8989'
```  
3. 修改 `login` 函数中 `payload` 两个键 `password` 和 `username` 对应的值             
```
payload = {
        "password": "admin",
        "username": "admin"
    }
```
4. 修改文件最后的 `range` 函数的第二个参数值为想要添加的账号个数    
```
for i in range(0,2000):    #循环调用函数添加账号,添加的账号数为 range 函数的第二个参数值
    addAccounts()
```       
5. 在终端或者编辑器运行 `addaccounts.py` 文件

