from rest_framework.pagination import CursorPagination, PageNumberPagination
from rest_framework.response import Response


class DefaultCursorPagination(CursorPagination):
    ordering = 'id'
    page_size_query_param = 'page_size'
    page_size = 10

    def get_paginated_response(self, data):
        next_url = self.get_next_link()
        previous_url = self.get_previous_link() if self.page else None
        headers = {'Prev': previous_url, 'Next': next_url, 'Page-Size': self.page_size}

        return Response(data, headers=headers)


class DefaultPageNumberPagination(PageNumberPagination):
    """Use when queryset ordering must be preserved (e.g. weight sort with Earth pinned last)."""

    page_size = 10
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response(
            data,
            headers={
                'Prev': self.get_previous_link(),
                'Next': self.get_next_link(),
                'Page-Size': self.page_size,
                'Total-Count': self.page.paginator.count,
            },
        )