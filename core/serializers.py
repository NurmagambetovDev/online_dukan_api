from rest_framework import serializers
from django.utils.text import slugify
from rest_framework.exceptions import ValidationError
from .models import User, Category, Product, Cart, CartItem, Order, OrderItem, Review

# USER SERIALIZERS

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name', 'phone_number', 'address']

    def create(self, validated_data):
        user = User.objects.create_user(
            first_name=validated_data['first_name'],  
            last_name=validated_data['last_name'],
            username=validated_data['username'],
            password=validated_data['password'],    
            phone_number=validated_data.get('phone_number'),
            address=validated_data.get('address')
        )
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'phone_number', 'address']
        read_only_fields = ['username']


# CATEGORY & PRODUCT
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'category', 'category_name', 'name', 'slug', 
            'description', 'price', 'discount_price', 'image', 'stock'
        ]
        read_only_fields = ['slug']

    def create(self, validated_data):
        if not validated_data.get('slug'):
            validated_data['slug'] = slugify(validated_data['name'])
        return super().create(validated_data)

# CART (Sevet)
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'subtotal']

    def get_subtotal(self, obj):
        return obj.total_price 

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_cart_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_cart_price']

    def get_total_cart_price(self, obj):
        return sum(item.total_price for item in obj.items.all())

class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)

# ORDER (BUYURTPA)
class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['product_name', 'price', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'status', 'total_price', 'address', 'created_at', 'items']


class CheckoutSerializer(serializers.Serializer):
    address = serializers.CharField(max_length=500, required=True)
    
    # tek idlarin qabillaydi
    items = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
        write_only=True,
        help_text="Satip alinajaq CartItem ID lari "
    )

# REVIEW (comment)
class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user', 'product', 'rating', 'comment', 'created_at']