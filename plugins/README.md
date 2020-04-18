# 插件机制

目前主要主持两种形式的插件，周期性任务与中间件。


## crontab


## middleware

具体实现，参考文档 https://docs.djangoproject.com/en/2.2/topics/http/middleware/#writing-your-own-middleware

所有插件性质的 middleware 与 arkid 其他 middleware 相比，优先级最低。

这里维护的插件之间的顺序，与直接在 settings.py `MIDDLEWARE` 末尾按顺序添加的效果一致。

综上，即先执行 arkid 其他 middleware 的 pre-request，再按升序执行插件的 pre-request，然后再按降序执行插件的 post-request，最后执行 arkid 其他 middleware 的 post-request。
