from rest_framework.pagination import PageNumberPagination


class CustomUserPagination(PageNumberPagination):
    """Пагинация для юзеров."""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProductPagination(PageNumberPagination):
    """Пагинация для товаров."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
