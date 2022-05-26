
urlpatterns = []


def register(urls):
    
    flag = False
    for url in urls:
        namespace = url.namespace
        for urlpattern in urlpatterns:
            pattern_namespace = urlpattern.namespace
            if namespace == pattern_namespace:
                urlpattern.url_patterns.extend(url.url_patterns)
                urlpattern.urlconf_module.extend(url.urlconf_module)
                urlpattern.urlconf_name.extend(url.urlconf_name)
                flag = True
                break
    if flag is False:
        urlpatterns.extend(urls)


def unregister(urls):
    for url in urls:
        urlpatterns.remove(url)
