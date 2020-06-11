本文用于介绍这个接口自动化框架的使用方法
### 一、文件意义    
这是一个基于 [python](https://www.python.org/) 的接口自动化测试框架，可生成 `xml` 和 `Allure` 测试报告      
### 二、环境搭建    
1、必须          
安装 [python](https://www.python.org/)            
2、非必须   
安装 [Allure](http://allure.qatools.ru/) 并完成环境变量配置      
`注：安装 Allure 用于生成 Allure 的测试报告，不安装可以直接使用 xml 格式的测试报告`           
### 三、使用方法    
1、将 `autotest` 目录保存到本地     
2、打开 `autotest` 目录下 `config.py` 文件修改定义的常量的值      
（1）修改 `base_url` 的值为测试目标的 `协议+IP` 或 `协议+域名`   
（2）修改  `username` 和 `password` 的值为测试目标的账号密码        
```
base_url = 'http://192.168.200.115:8989/'

username = "admin"
password = "admin"
```       
3、添加接口测试用例       
打开文件`apidata.py` 。`httpurl_data` 为存放测试用例的列表，列表每一个类型为字典的值表示一条测试用例，添加测试用例只需要按照模板添加字典类型的数据即可    
```
    # 1.登录接口 第一条用例
    {'tittle': '登录接口',  # 用例的名称
     'skip': False,  # 跳过用例，bool类型，False，空，0，不存在skip为不跳过，其余均为跳过
     'url': '{}siteapi/oneid/ucenter/login/'.format(base_url),
     'headers':{
         'Content-Type': 'application/json;charset=UTF-8'    
     },
     'payload': {
         'password': 'admin',
         'username': 'admin'
     },
     'type': 'post',  # 请求的类型，支持 get,post,options,head,delete,put,connect，不区分大小写，这条是 post 类型
     'time': 1 , # 用例等待的时间 int 类型 秒 1就是等待1秒后执行
     'assert':['admin']     #断言，列表类型，可添加多个判断条件，与接口返回值对比
     }
``` 
|用例属性|意义|备注|
|-----|-----------|----|
|tittle|测试用例标题|可以不存在|
|skip|跳过用例|bool类型，True为跳过，False不跳过，正常执行|
|url|接口地址|不存在时抛出异常|
|headers|接口请求头信息|可以不存在|
|payload|接口携带参数|可以不存在|
|type|请求类型|支持 get,post,options,head,delete,put,connect,不区分大小写，不存在时抛出异常|    
|time|执行用例前等待的时间|单位为秒,int类型|
|assert|断言|列表类型，可添加多个|

4、运行生成 `xml` 测试报告      
在 `autotest` 目录下运行 `start.py` 文件。运行完成后，会在当前目录生成名为 `junit` 的目录，在 `junit` 目录下 有 `xml` 格式的测试报告。若存在同名文件时，生成的目录名称会发生改变。也可自定义测试报告的存储路径和文件名，在 `junit.py` 中进行设置。
```
        files = ('junit',)
        # 创建文件夹
        for k in files:
            path = Path(k)
            index = '(0)'
            
            if path.is_file():
                for i in range(1,10):
                    if path.is_file():
                        index = '('+str(i)+')'
                        path = Path(k+index)
                    else:
                        break
            else:
                    path = Path(k)

            if not path.is_dir():
                path.mkdir()

        file = path / ('API' + '-' + 'ReportJunit@' + self.nowtime + '.xml')   #xml文件名
        f = open(file, 'w')
        self.doc.writexml(f, indent='\t', newl='\n', addindent='\t', encoding='gbk')
        f.close())
```
5、生成 `Allure` 格式的测试报告       
若安装 `Allure` 并配置好了环境变量，可在生成 `xml` 测试报告后，使用命令 `allure serve junit` 生成 `Allure` 格式的测试报告。命令中的 `junit` 为 `xml` 测试报告的路径，存在同名文件时目录名称会发生变化，具体要以实际生成的目录名为准。若在 `junit.py` 进行了修改，这里也需要做相应改变