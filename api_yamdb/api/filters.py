import django_filters
from reviews.models import Title


class WriteFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name='category__slug', lookup_expr='icontains')
    genre = django_filters.CharFilter(field_name='genre__slug', lookup_expr='icontains')
    year = django_filters.NumberFilter(field_name='year')

    class Meta:
        model = Title
        fields = ['category', 'genre', 'year']
