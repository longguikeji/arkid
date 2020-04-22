# 插件机制

目前主要主持两种形式的插件，周期性任务与中间件。


## crontab
插件必须在 /plugins/crontab/tasks.py 中以 Celery Task 的形式实现，且名称以 `_plugin` 结尾。

可以通过接口启用或关闭插件，以及设置此插件运行周期。

添加插件需重启 celery 服务。

## middleware
插件必须是 function 的形式，且名称以 `_plugin` 结尾。

具体实现，参考文档 https://docs.djangoproject.com/en/2.2/topics/http/middleware/#writing-your-own-middleware

对插件做修改后需要重启 web server。

所有插件性质的 middleware 与 arkid 其他 middleware 相比，优先级最低。

这里维护的插件之间的顺序，与直接在 settings.py `MIDDLEWARE` 末尾按顺序添加的效果一致。

综上，即先执行 arkid 其他 middleware 的 pre-request，再按升序执行插件的 pre-request，然后再按降序执行插件的 post-request，最后执行 arkid 其他 middleware 的 post-request。
