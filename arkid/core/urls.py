
urlpatterns = []


def register(urls):
    temp_urls = []
    for url in urls:
        temp_urls.append(url)
        for urlpattern in urlpatterns:
            if url.namespace == urlpattern.namespace:
                urlpattern.url_patterns.extend(url.url_patterns)
                urlpattern.urlconf_module.extend(url.urlconf_module)
                urlpattern.urlconf_name.extend(url.urlconf_name)
                temp_urls.remove(url)
                break
    urlpatterns.extend(temp_urls)


def unregister(urls):
    for url in urls:
        if url in urlpatterns:
            urlpatterns.remove(url)
        else:
            for urlpattern in urlpatterns:
                if url.namespace == urlpattern.namespace:
                    urlpattern.url_patterns.remove(url.url_patterns)
                    urlpattern.urlconf_module.remove(url.urlconf_module)
                    urlpattern.urlconf_name.remove(url.urlconf_name)
                    break
