from rest_framework.pagination import PageNumberPagination

class AdminProfileTablePagination(PageNumberPagination):
    """Controls how many user records load at once in your frontend dashboard."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100