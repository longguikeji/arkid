# 缓存

本文档描述的缓存为部分计算结果，仅供服务端内部使用，不直接与客户端交互。

## 存储形式
目前存于redis中

## 存储数据

- 组的上溯路径

	**key**:   `oneid:node:$node_uid:upstream`
	
	**value**: [`$parent_node_uid`......]
	
	不包含节点自身，包含root。离节点近的节点在前，root 在最后。除 root 外，最后一项必为root，值为`d_root`或`g_root`

- 人直属节点

	**key**:   `oneid:user:{username}:parent_node`
	
	**value**: {`$node_uid`......}

- 人所属节点(直属或隶属)

	**key**:   `oneid:user:{username}:upstream_node`

	**value**: {`$node_uid`......}

* 实际存于redis中的键会受框架影响，还包括前缀和版本，格式为 `{prefix}:{version}:{key}`。默认前缀为空，版本为1。形如`:1:{key}`

## 缓存更新机制

- 移动节点后立即更新节点下子孙节点的上溯路径，子孙节点连同节点自身所有节点下属成员的直属节点、所属节点。
- 人员关系变动后立即更新该人的直属节点、所属节点。
- 缓存有效时间为3天。
- 用到时再生成，不预先生成。
