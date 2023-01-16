download

```shell
Open https://github.com/Dragon Turtle Technology/arkid/releases/tag/2.6.2 （Manual check the latest version，Clone's latest version tag）

download arkid.zip Decompress，Get the following file
```

- be262.tar.gz
- desktop266.tar.gz
- fe262.tar.gz
- portal.conf
- settings_local.py
- supervisord.conf
- Native Arkid deployment.md



Two machines

## A back end：

#### 1、Software Installation

- python 3.8

- mysql 5.7

- redis 5

- ```
  gettext xmlsec1 supervisor tree
  freetds-dev freetds-bin
  python-dev python-pip
  ```

#### 2、Install the ARKID back end

```shell
# rear end Penetrately.tar.gz Decompress，Put /was/arkid/

# Revise settings_local.py，Fill in the correct mysql information，MySQL needs to create a new empty database
DEBUG = False
# mysql database
MYSQLHOST = "localhost"
MYSQLPORT = "3306"
MYSQLDATABASE = "arkid"
MYSQLUSER = "root"
MYSQLPASSWORD = "root"

# Redis cache, Default port 6379
REDISHOST = "localhost"
REDISPASSWD = None




# Bundle settings_local.py and supervisord.conf Put /was/arkid/ Down

```



#### 3、Start the back end

```shell
# redis and mysql Need to keep start
# Enter/was/arkid/ Under contents

export PYTHONUSERBASE=/var/arkid/arkid_extensions 
export PATH=$PATH:/var/arkid/arkid_extensions/bin 
export ARKID_VERSION=2.6.2

pip install --disable-pip-version-check -r requirements.txt;

/usr/local/bin/python3.8 manage.py migrate

supervisord
```



## One front end：

#### 1、Software Installation

- nginx
#### 2、nginxConfiguration file

```shell
# Move the default configuration
mv /etc/nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf_back

# Modify portal.conf file，Bundle `http://be` Replace the address of the back -end deployment 
# Will portal.conf Put /etc/nginx/conf.d/portal.conf


```



#### 3、Install ARKID front end and desktop

```shell
# front end Falata.tar.gz Decompress，Put /usr/share/nginx/html/

# desktop desktop.tar.gz Decompress，Put /usr/share/nginx/html/desktop/

```

#### 4、Start the front end

```shell
nginx -t

nginx -s reload
```

5、access

```shell
http://Front -end machine IP
```





