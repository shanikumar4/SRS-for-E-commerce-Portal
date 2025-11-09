from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime
# from app.views import user_directory_path




class User(AbstractUser):
    username=None
    email = models.EmailField(unique=True)
    phone_No =models.CharField(max_length=10)
    GENDER_CHOICES = (
        ('Male', 'MALE'),
        ('Female', 'FEMALE'),
        ('Other', 'OTHER')
    )
    gender = models.CharField(max_length=15, choices=GENDER_CHOICES)
    profileImage = models.ImageField(upload_to="profileImg/")
    
    
 
    
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS=[]
    
    
    
class products(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=1000)
    price= models.IntegerField()
    stock = models.IntegerField()
    createAt= models.DateTimeField(auto_now_add=True)
    updateAt= models.DateTimeField(null= True, blank=True)
    deleteAt= models.DateTimeField(null= True, blank=True)
    active = models.BooleanField(default=True)
    productCategory =(
        ('Amber', 'Amber'),
        ('Floral', 'Floral'),
        ('Fresh', 'Fresh'),
        ('Woody', 'Woody'),
    ) 
    category = models.CharField(max_length=6, choices=productCategory)
    
    
    
class productImage(models.Model):
    products = models.ForeignKey(products,on_delete= models.CASCADE)
    image= models.ImageField(upload_to="images/")
    
    
    
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ForeignKey(products, on_delete=models.CASCADE)
    quantity  = models.IntegerField(default = 1)
    
    
    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    createAt= models.DateTimeField(auto_now_add=True)
    totalPrice = models.IntegerField()
    shippingAddress = models.TextField()
    
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(products, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.IntegerField()
    name = models.CharField(max_length=200, default=None)
    shippingAddress = models.TextField(default=None)
    status = models.CharField(max_length=200, default=None)
    
    

class SalesInsights(models.Model):
    productName = models.CharField(max_length=200)
    totalSales = models.IntegerField()
    revenue = models.ImageField()
    numberOfOrders = models.IntegerField()      