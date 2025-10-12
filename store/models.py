from django.db import models
from django.contrib.auth.models import User


class Medicine(models.Model):
    CATEGORY_CHOICES = [
        ('Vitamins', 'Vitamins'),
        ('Supplements', 'Supplements'),
        ('Personal Care', 'Personal Care'),
        ('Antibiotics', 'Antibiotics'),
        ('Painkiller', 'Painkillers'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='medicines/', blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    is_featured = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class CartItem(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.medicine.name} x {self.quantity}"

    def get_total_price(self):
        return self.medicine.price * self.quantity

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)
    default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.full_name} - {self.street}"