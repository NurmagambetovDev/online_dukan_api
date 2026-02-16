from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework import viewsets, generics, status, filters, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination  
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .filters import ProductFilter, ReviewFilter
from .models import User, Category, Product, Cart, CartItem, Order, OrderItem, Review
from .serializers import (
    UserRegistrationSerializer, UserProfileSerializer,
    CategorySerializer, ProductSerializer,
    CartSerializer, AddToCartSerializer,
    OrderSerializer, CheckoutSerializer,
    ReviewSerializer
)
from .permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly

#  PAGINATION  
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

# 1. AUTHENTICATION

@extend_schema(tags=['Auth'])
class CustomTokenObtainPairView(TokenObtainPairView):
    pass

@extend_schema(tags=['Auth'])
class CustomTokenRefreshView(TokenRefreshView):
    pass

@extend_schema(tags=['Auth'])
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

#  PROFILE

@extend_schema(tags=['Profile'])
class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

#  CATEGORIES

@extend_schema(tags=['Categories'])
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

#  PRODUCTS

@extend_schema(tags=['Products'])
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination 
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at']

#  CART

@extend_schema(tags=['Cart'])
class CartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=CartSerializer)
    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @extend_schema(
        summary="Sebetga producti qosiw",
        request=AddToCartSerializer,
        responses={200: dict, 400: dict}
    )
    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']
        
        product = get_object_or_404(Product, id=product_id)

        if product.stock < quantity:
            return Response({"error": "Bazada producti jeterli emas"}, status=status.HTTP_400_BAD_REQUEST)

        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        
        cart_item.save()
        return Response({"message": "product sebetga qosildi"}, status=status.HTTP_200_OK)

@extend_schema(tags=['Cart'])
class CartItemDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses={204: None})
    def delete(self, request, pk):
        item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
        item.delete()
        return Response({"message": "O'shirildi"}, status=status.HTTP_204_NO_CONTENT)

# ORDERS

@extend_schema(tags=['Orders'])
class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

    @extend_schema(
        tags=['Orders'],
        summary="Tanlangan productilerdi tastiqlaw(Checkout)",
        request=CheckoutSerializer,
        responses=OrderSerializer
    )
    @action(detail=False, methods=['post'], serializer_class=CheckoutSerializer)
    def checkout(self, request):
        """
        tek addres ham itemlari arqali satip aliw
        """
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        address = serializer.validated_data['address']
        item_ids = serializer.validated_data['items'] 

        cart = get_object_or_404(Cart, user=user)
        
        #  tek sol userge tiyisli ham ID si tablitsada bar itemlarni alamiz
        items = CartItem.objects.filter(cart=cart, id__in=item_ids).select_related('product')

        # eger tabilgan itemler sani soralgan kem bolsa 
        if not items.exists() or items.count() != len(item_ids):
            return Response(
                {"error": "Tanlangan product qalmag'an yaki id qate"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Transaction
        with transaction.atomic():
            total_price = 0
            
            # bahasin tekseriw ha'm steck ti tekseriw
            for item in items:
                product = Product.objects.select_for_update().get(id=item.product.id)
                
                if product.stock < item.quantity:
                    return Response(
                        {"error": f"'{product.name}' bazada yetarli emas!"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                total_price += item.total_price

            # order jaratadi address penen 
            order = Order.objects.create(
                user=user,
                total_price=total_price,
                status='pending',
                address=address
            )

            # 4. OrderItem jaratiw va stockti kemeytiriw
            for item in items:
                product = item.product
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    price=product.price,
                    quantity=item.quantity
                )
                product.stock -= item.quantity
                product.save()

            # 5. tek satip aling'an productilerdi oshiredi qalg'anlari sevetde turadi
            items.delete()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

# REVIEWS

@extend_schema(tags=['Reviews'])
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filterset_class = ReviewFilter

    def perform_create(self, serializer):
        user = self.request.user
        product = serializer.validated_data['product']
        
        # paydalaniwshi productini rastanda satip alg'anlig'in tekseredi 
        has_bought = OrderItem.objects.filter(
            order__user=user, 
            product=product,
            order__status__in=['paid', 'shipped'] 
        ).exists()

        if not has_bought:
             # validatsiya ashiladi
             raise ValidationError("siz productti almagansiz yamasa tolem amelge asirilmagan.")
        
        if Review.objects.filter(user=user, product=product).exists():
             raise ValidationError("siz aldin bul productige comment qaldirg'ansiz.")

        serializer.save(user=user)