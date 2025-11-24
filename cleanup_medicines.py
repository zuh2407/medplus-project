import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy.settings')
django.setup()

from store.models import Medicine

def cleanup():
    medicines_to_remove = [
        'Paracetamol 500mg', 'Vitamin C 1000mg', 'Amoxicillin 500mg', 'Omega-3 Fish Oil',
        'Ibuprofen 400mg', 'Multivitamin Complex', 'Cetaphil Gentle Cleanser', 'Calcium + Vitamin D3',
        'Aspirin 81mg', 'Probiotic Daily', 'Band-Aid Flexible Fabric', 'Cough Syrup',
        'Naproxen Sodium 220mg', 'Diclofenac Gel', 'Vitamin D3 5000 IU', 'Vitamin B12 1000mcg',
        'Zinc Picolinate 50mg', 'Azithromycin 250mg', 'Doxycycline 100mg', 'Melatonin 5mg',
        'Whey Protein Isolate', 'Sunscreen SPF 50', 'Hand Sanitizer 500ml', 'Digital Thermometer'
    ]

    print(f"Attempting to remove {len(medicines_to_remove)} medicines...")
    
    count = 0
    for name in medicines_to_remove:
        deleted, _ = Medicine.objects.filter(name=name).delete()
        if deleted:
            print(f"Deleted: {name}")
            count += 1
        else:
            print(f"Not found: {name}")

    print(f"Successfully removed {count} medicines.")

if __name__ == '__main__':
    cleanup()
