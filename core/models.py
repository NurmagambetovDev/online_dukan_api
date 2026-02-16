from django.db import models
from django.contrib.auth.models import AbstractUser

#(USERS)
class User(AbstractUser):
    ADMIN = 'admin'
    CLIENT = 'client'
    
    ROLE_CHOICES = (
        (ADMIN, 'Admin'),
        (CLIENT, 'Client')
    )
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=CLIENT)
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.username

#  KATEGORIYALAR
class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    #parent
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class Meta:
        verbose_name_plural = 'Categories' 

    def __str__(self):
        return self.name

#(PRODUCTS)
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2) 
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    
    # teris san bolmawi ushin positiveinteger 
    stock = models.PositiveIntegerField(default=0) 
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# Sevet (CART)
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} seveti"

# models.py

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1) 

    @property
    def total_price(self):
        # Eger productta discount_price bolsa, sonı esapqa alamız
        if self.product.discount_price:
            return self.product.discount_price * self.quantity
        return self.product.price * self.quantity


    def __str__(self):
        return f"{self.product.name} ({self.quantity})"

#  BUYURTPALAR (ORDERS) 
class Order(models.Model):
    
    STATUS_CHOICES = (
        ('pending', 'Kutilmekte'),
        ('paid', "To'lendi"),
        ('shipped', 'Jiberildi'),
        ('canceled', 'Biykar etildi'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    # eger product oship ketse tariyxta qaliw ushin (SET_NULL)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        product_name = self.product.name if self.product else "O'shirilgen product"
        return f"{self.order.id} - {product_name}"
    

# comment (REVIEWS) 
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(1, 6)]) 
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # bir adam bir comment qaldiradi
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} - {self.rating}"


