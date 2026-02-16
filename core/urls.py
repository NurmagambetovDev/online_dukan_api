from django.urls import path, include
from rest_framework.routers import DefaultRouter


from .views import (
    RegisterView, 
    CustomTokenObtainPairView,
    CustomTokenRefreshView,    
    UserProfileView,
    CategoryViewSet, 
    ProductViewSet, 
    CartView, 
    CartItemDeleteView,
    OrderViewSet,
    ReviewViewSet
)


router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'orders', OrderViewSet, basename='orders')
router.register(r'reviews', ReviewViewSet, basename='reviews')

urlpatterns = [
    # 1. Routerdagi URLlar (Category, Product, Order, Review)
    path('', include(router.urls)),

    # 2. Authentication (Auth bo'limine jayg'asadi)
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'), # JWT aliw
    path('auth/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'), # Tokenni janalaydi
    
    # 3. Profile (Profile bo'limine jayg'asadi)
    path('profile/', UserProfileView.as_view(), name='user-profile'),

   
    path('cart/', CartView.as_view(), name='cart_detail'), # get ham post
    path('cart/remove/<int:pk>/', CartItemDeleteView.as_view(), name='cart_remove'), # delete 
]