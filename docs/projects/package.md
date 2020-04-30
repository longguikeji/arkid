# 项目打包

## 适用于django-arkid-0.1.0
- 此版本打包流程仅适用于开发人员对当前项目版本和结构进行打包时所需要采取的一系列必要操作.

## 要求

### ArkID框架打包要求以下内容：

- setuptools （46.1.3）
- fnmatch （0.0.8）
- toml （0.10.0）

## 打包

### 必要的参数设置

- （必要的）在确定的项目的顶层目录名称后，在 setup.py 中修改 BASE_DIR 的值.
- （必要的）开发人员在进行打包时，需要将 oneid.settings_setup.py 中的 SERVE_AS_PLUGIN 设置为 True ，以使得ArkID可作为插件为用户所使用；开发人员在进行开发时，务必将其值设置为 False .
- （可选的）在 setup.cfg 中配置license的类型以及安装的路径等.
- （可选的）如果您尝试减少或添加打包时所需的文件或文件夹，可以修改 setup.py 中的 STANDARD_EXCLUDE 值和 STANDARD_EXCLUDE_DIRECTORIES 值或者在 MANIFEST.in 文件中进行相应的改动.


### 总目录结构编排

- 将 setup.py , setup.cfg , MANIFEST.in , LICENSE.md 文件移动到与ArkID项目同一个顶层目录下.其目的在于将 ArkID 框架打包为一个整体对外提供服务.

### 执行打包命令

- 在顶层目录下执行 python setup.py sdist 命令，在生成的 dist 文件夹中可找到刚刚打包的安装包.


