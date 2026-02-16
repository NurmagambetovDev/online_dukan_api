import django_filters
from .models import Product, Review

class ProductFilter(django_filters.FilterSet):
    
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    category = django_filters.CharFilter(field_name="category__slug", lookup_expr="exact")

    class Meta:
        model = Product
        fields = ["category", "min_price", "max_price"]


class ReviewFilter(django_filters.FilterSet):
    product_id = django_filters.NumberFilter(field_name="product__id")

    class Meta:
        model = Review
        fields = ['product_id']

