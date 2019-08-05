# DingManifest

设计一系列中间文件用于描述钉钉的结构性数据，数据双向同步基于这些文件展开，先保证结构正确，之后再逐个同步详细信息。  
一共三份文件，分别由钉钉导出、OneID导出以及前两者的差异描述文件。  
均以JSON格式描述。


## DingManifest
由钉钉导出一份结构描述文件，格式如下

### User
+ d_id (string)
+ name (string)

### Dept
+ d_id (string)
+ name (string)
+ children (array[Dept])
+ users (array[User])

### Role
+ d_id (string)
+ name (string)
+ children (array[Role])
+ users (array[User])

### Label
+ d_id (string) - 标签组没有id, 用拼音代替
+ name (string)
+ children (array[Label])
+ users (array[User])

### DingManifest - 钉钉导出的结构
+ dept (array[Dept])
+ role (arrya[Role])
+ label (array[Label])

## OneIDDingManifest

由OneID面向钉钉导出一份结构描述文件，格式如下：  
与钉钉导出文件的差异主要在于，多了uid字段，而d_id可能没有

### OneIDUser
+ uid (string) - oneid uid，即username
+ d_id (string, optional)
+ name (string)

### OneIDDept
+ uid (string) - oneid uid
+ d_id (string, optional)
+ name (string)
+ children (array[OneIDDept])
+ users (array[OneIDUser])

### OneIDRole
+ uid (string) - oneid uid
+ d_id (string, optional)
+ name (string)
+ children (array[OneIDRole])
+ users (array[OneIDUser])

### OneIDLabel
+ uid (string) - oneid uid
+ d_id (string, optional) - 标签组没有id, 用拼音代替
+ name (string)
+ children (array[OneIDLabel])
+ users (array[OneIDUser])

### OneIDDingManifest - OneID导出的结构
+ dept (array[OneIDDept])
+ role (arrya[OneIDRole])
+ label (array[OneIDLabel])

## DingDiffManifest

描述DingManifest与OneIDDingManifest之间的差异

### 数据覆盖算法

将user，dept，role，label视为点，从属关系视为线。  
先根据d_id进行匹配，匹配即双方共有，剩下部分即各自特有。  

修改时按以下顺序：

- 把少的点加上
- 把多的线去掉
- 把少的线加上
- 把多的点去掉

name的差异会被忽略，展示时按主动方的name为准。  
对user进行比较时，只选取有ding_user数据的user。其他user不参与比较。  
如果oneid中，user参与比较，却又没匹配上，需要特殊处理。  
若某个点是一方特有的，那么其参与的所有线都会为该方所特有。  
只记录有差异的对象。

根据算法设计数据结构，但优先级还是低于数据的记录与展示。

### BaseNode (object)
+ uid
+ d_id
+ name

### BaseLine (array[BaseNode])  - 长度为2，后者是前者的父级

### BaseDiff
+ oneid (object) - OneID 特有
    + nodes (array[node]) 特有的节点及其参与的连线
        + node (object)
            + uid (string)
            + d_id (string)
            + parent (BaseNode)
            + children (array[BaseNode])
    + lines (array[BaseLine])
+ ding (object) - 钉钉特有
    + nodes (array[node]) 特有的节点及其参与的连线
        + node (object)
            + uid (string)
            + d_id (string)
            + parent (BaseNode)
            + children (array[BaseNode])
    + lines (array[BaseLine])

### DingDiffManifest
+ dept (BaseDiff)
+ role (BaseDiff)
+ label (BaseDiff)
+ user (BaseDiff)
