import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy.settings')
django.setup()

from store.models import CartItem, Medicine

print(f"Total Medicines: {Medicine.objects.count()}")
print(f"Total CartItems: {CartItem.objects.count()}")

for item in CartItem.objects.all():
    print(f"Item: {item.medicine.name}, Qty: {item.quantity}")
