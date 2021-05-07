from rest_framework import pagination


class DefaultListPaginator(pagination.PageNumberPagination):
    page_size_query_param = 'page_size'
    page_size = 1000
    max_page_size = 100
