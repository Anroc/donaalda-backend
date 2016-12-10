import itertools

from rest_framework import pagination
from rest_framework.utils.urls import replace_query_param

class GeneratorPagination(pagination.LimitOffsetPagination):
    """
    A pagination style for "querysets" that are actually cached generator
    functions.

    The thing that differentiates this from a standard LimitOffsetPagination
    style is that with a generator, you don't know the count before evaluating
    the whole generator (which would probably be quite expensive).

    An alternative base for this would have been CursorPagination but that
    one uses to many features that are specific to django querysets to be useful
    for us.
    """
    def paginate_queryset(self, queryset, request, view=None):
        self.limit = self.get_limit(request)
        if self.limit is None:
            return None

        self.offset = self.get_offset(request)
        self.request = request

        ret = list(itertools.islice(
                queryset, self.offset, self.offset + self.limit))

        self.count = len(ret)
        if self.count > self.limit and self.template is not None:
            self.display_page_controls = True

        return ret

    def get_next_link(self):
        if self.limit > self.count:
            return None

        url = self.request.build_absolute_uri()
        url = replace_query_param(url, self.limit_query_param, self.limit)

        offset = self.offset + self.limit
        return replace_query_param(url, self.offset_query_param, offset)


class SuggestionsPagination(GeneratorPagination):
    default_limit = 6
