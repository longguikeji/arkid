# Pip依赖

当插件需要额外的依赖包时，只需要将插件的requirements.txt文件生成并放在根目录下即可

ArkID会在加载插件之前自动安装requirements.txt文件中的所有依赖包。

```txt title='requirements.txt'
alibabacloud-dysmsapi20170525==2.0.9

```
