from django.db import models

# Create your models here.
class Products(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class Category(models.Model):
    name = models.CharField(max_length=100)
 

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    size = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=50, blank=True)
    prepayment_price = models.DecimalField(max_digits=12, decimal_places=2)
    remaining_price = models.DecimalField(max_digits=12, decimal_places=2)
    

    

    @property
    def total_price(self):
        return self.prepayment_price + self.remaining_price

    def __str__(self):
        return f"{self.name} - {self.total_price} so‘m"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')  # media/products/ ichida saqlanadi

    def __str__(self):
        return f"Rasm - {self.product.name}"

# Telegram foydalanuvchisi
class TelegramUser(models.Model):
    telegram_id = models.BigIntegerField(unique=True)
    full_name = models.CharField(max_length=255)
    username = models.CharField(max_length=150, blank=True, null=True)
    phone = models.CharField(max_length=20)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.telegram_id})"



class Order(models.Model):
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    product_list = models.TextField()
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    prepayment_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    remaining_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    
    # Lokatsiyani alohida saqlash
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    phone_number = models.CharField(max_length=20)
    payment_screenshot = models.ImageField(upload_to='payments/', blank=True, null=True)
    admin_reply = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Kutilmoqda'),
        ('confirmed', 'Tasdiqlandi'),
        ('delivered', 'Yetkazildi'),
        ('archived', 'Arxiv'),
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.total_price and (self.prepayment_amount is None or self.remaining_amount is None):
            self.prepayment_amount = self.total_price * 0.3
            self.remaining_amount = self.total_price * 0.7
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Buyurtma #{self.id} - {self.user.full_name}"

# Feedback (Fikr)
# models.py
from django.db import models
import requests

TELEGRAM_BOT_TOKEN = "7580989162:AAFqEAG7Fb-pMmTI_rCQW-45ZpEzD7MvD70"  # Bot tokeningiz
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

class Feedback(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='feedbacks')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Admin javob yozganda botga yuborish
        chat_id = self.order.user.telegram_id
        text = f"📢 Sizning buyurtmangiz bo‘yicha javob:\n\n{self.message}"
        requests.post(TELEGRAM_API_URL, data={"chat_id": chat_id, "text": text})

    def __str__(self):
        return f"Feedback for Order #{self.order.id}"



# savat
class Cart(models.Model):
    user = models.ForeignKey('TelegramUser', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    color = models.CharField(max_length=50, null=True, blank=True)
    size = models.CharField(max_length=50, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return self.quantity * self.product.total_price

    def __str__(self):
        return f"{self.user.full_name} - {self.product.name} ({self.color}, {self.size}) x {self.quantity}"
