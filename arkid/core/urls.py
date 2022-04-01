
urlpatterns = []


def register(urls):
    urlpatterns.extend(urls)


def unregister(urls):
    for url in urls:
        urlpatterns.remove(url)
