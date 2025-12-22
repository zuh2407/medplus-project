import os
import django
import sys

sys.path.append('c:\\projects\\pharmacy_app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy.settings')
django.setup()

from store.models import Medicine, CartItem

with open('price_report.txt', 'w') as f:
    f.write("seeking medicines with 'ibuprofen' in name...\n")
    meds = Medicine.objects.filter(name__icontains='ibuprofen')
    if not meds.exists():
        f.write("No medicines found matching 'ibuprofen'.\n")
    else:
        for m in meds:
            f.write(f"ID: {m.id} | Name: {m.name} | Price: {m.price}\n")

    f.write("-" * 20 + "\n")
    f.write(f"Total Cart Items in DB: {CartItem.objects.count()}\n")

    # Optional: List all cart items to see if there's any active session with huge totals
    for item in CartItem.objects.all()[:10]:
         f.write(f"CartItem: {item.medicine.name} x {item.quantity} (Session: {item.session_id}) | Total: {item.get_total_price()}\n")
