'''
Продукты могут фильтроваться по категории по названию или описанию по цене ( дороже дешевле)

Заказы могут фильтроваться ( по продукту по дате по сумме )

'''
import django_filters
from django_filters.rest_framework import FilterSet
from django_filters.rest_framework import FilterSet

from .models import Product


class ProductFilter(FilterSet):
    title = django_filters.CharFilter(field_name='title',
                                      lookup_expr='icontains')
    desc = django_filters.CharFilter(field_name='description',
                                      lookup_expr='icontains')
    price_from = django_filters.NumberFilter(field_name='price',
                                             lookup_expr='gte')
    price_to = django_filters.NumberFilter(field_name='price',
                                           lookup_expr='lte')

    class Meta:
        model = Product
        fields = ('category', 'title', 'desc', 'price_from', 'price_to')


