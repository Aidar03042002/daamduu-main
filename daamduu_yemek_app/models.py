from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random
from django.core.validators import MinValueValidator

# Create your models here.

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=20, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(default=timezone.now)
    card_last_four = models.CharField(max_length=4)
    qr_code_data = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=[('active', 'Active'), ('used', 'Used')], default='active')

    def __str__(self):
        return f"Order {self.order_number} - {self.user.username}"

    @classmethod
    def generate_order_number(cls):
        """Generate a unique order number"""
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        random_suffix = ''.join([str(random.randint(0, 9)) for _ in range(4)])
        return f"ORD-{timestamp}-{random_suffix}"

class Dish(models.Model):
    name = models.CharField(max_length=100)
    calories = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    image = models.ImageField(upload_to='dishes/')

    def __str__(self):
        return self.name

class DailyMenu(models.Model):
    date = models.DateField(unique=True)
    dish1 = models.ForeignKey(Dish, related_name='menu_dish1', on_delete=models.CASCADE)
    dish2 = models.ForeignKey(Dish, related_name='menu_dish2', on_delete=models.CASCADE)
    dish3 = models.ForeignKey(Dish, related_name='menu_dish3', on_delete=models.CASCADE)
    dish4 = models.ForeignKey(Dish, related_name='menu_dish4', on_delete=models.CASCADE)

    def __str__(self):
        return f"Меню на {self.date}"
