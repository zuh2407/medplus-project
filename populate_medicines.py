import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy.settings')
django.setup()

from store.models import Medicine

def populate():
    medicines = [
        # Painkillers
        {
            'name': 'Paracetamol 500mg',
            'description': 'Effective pain reliever and fever reducer. Suitable for headaches, muscle aches, and colds.',
            'price': 5.99,
            'category': 'Painkiller',
            'image': 'medicines/paracetamol.jpg'
        },
        {
            'name': 'Ibuprofen 400mg',
            'description': 'Anti-inflammatory drug used for treating pain, fever, and inflammation.',
            'price': 8.99,
            'category': 'Painkiller',
            'image': 'medicines/ibuprofen.jpg'
        },
        {
            'name': 'Aspirin 81mg',
            'description': 'Low dose aspirin for heart health regimen.',
            'price': 6.50,
            'category': 'Painkiller',
            'image': 'medicines/aspirin.jpg'
        },
        {
            'name': 'Naproxen Sodium 220mg',
            'description': 'Long-lasting pain relief for muscle aches and arthritis.',
            'price': 10.99,
            'category': 'Painkiller',
            'image': 'medicines/naproxen.jpg'
        },
        {
            'name': 'Diclofenac Gel',
            'description': 'Topical gel for relief of joint pain and inflammation.',
            'price': 14.50,
            'category': 'Painkiller',
            'image': 'medicines/diclofenac.jpg'
        },

        # Vitamins
        {
            'name': 'Vitamin C 1000mg',
            'description': 'Boosts immunity and promotes healthy skin. Essential for daily wellness.',
            'price': 12.50,
            'category': 'Vitamins',
            'image': 'medicines/vitaminc.jpg'
        },
        {
            'name': 'Multivitamin Complex',
            'description': 'Complete daily multivitamin for overall health and vitality.',
            'price': 18.50,
            'category': 'Vitamins',
            'image': 'medicines/multivitamin.jpg'
        },
        {
            'name': 'Vitamin D3 5000 IU',
            'description': 'Supports bone health and immune function. High potency softgels.',
            'price': 11.00,
            'category': 'Vitamins',
            'image': 'medicines/vitamind3.jpg'
        },
        {
            'name': 'Vitamin B12 1000mcg',
            'description': 'Supports energy production and nervous system health.',
            'price': 13.99,
            'category': 'Vitamins',
            'image': 'medicines/vitaminb12.jpg'
        },
        {
            'name': 'Zinc Picolinate 50mg',
            'description': 'Essential mineral for immune system support and enzyme function.',
            'price': 9.50,
            'category': 'Vitamins',
            'image': 'medicines/zinc.jpg'
        },

        # Antibiotics
        {
            'name': 'Amoxicillin 500mg',
            'description': 'Antibiotic used to treat a wide variety of bacterial infections.',
            'price': 15.00,
            'category': 'Antibiotics',
            'image': 'medicines/amoxicillin.jpg'
        },
        {
            'name': 'Azithromycin 250mg',
            'description': 'Antibiotic used for respiratory infections, skin infections, and more.',
            'price': 22.00,
            'category': 'Antibiotics',
            'image': 'medicines/azithromycin.jpg'
        },
        {
            'name': 'Doxycycline 100mg',
            'description': 'Broad-spectrum antibiotic for bacterial infections.',
            'price': 19.50,
            'category': 'Antibiotics',
            'image': 'medicines/doxycycline.jpg'
        },

        # Supplements
        {
            'name': 'Omega-3 Fish Oil',
            'description': 'Supports heart health and brain function. High quality fish oil capsules.',
            'price': 25.99,
            'category': 'Supplements',
            'image': 'medicines/omega3.jpg'
        },
        {
            'name': 'Calcium + Vitamin D3',
            'description': 'Promotes strong bones and teeth. Essential for bone health.',
            'price': 11.99,
            'category': 'Supplements',
            'image': 'medicines/calcium.jpg'
        },
        {
            'name': 'Probiotic Daily',
            'description': 'Supports digestive health and immune system balance.',
            'price': 22.00,
            'category': 'Supplements',
            'image': 'medicines/probiotic.jpg'
        },
        {
            'name': 'Melatonin 5mg',
            'description': 'Natural sleep aid to help regulate sleep cycles.',
            'price': 8.50,
            'category': 'Supplements',
            'image': 'medicines/melatonin.jpg'
        },
        {
            'name': 'Whey Protein Isolate',
            'description': 'High-quality protein for muscle recovery and growth.',
            'price': 45.00,
            'category': 'Supplements',
            'image': 'medicines/whey.jpg'
        },

        # Personal Care
        {
            'name': 'Cetaphil Gentle Cleanser',
            'description': 'Mild, non-irritating face cleanser for sensitive skin.',
            'price': 14.99,
            'category': 'Personal Care',
            'image': 'medicines/cetaphil.jpg'
        },
        {
            'name': 'Band-Aid Flexible Fabric',
            'description': 'Cover minor cuts and scrapes. Flexible protection that moves with you.',
            'price': 4.50,
            'category': 'Personal Care',
            'image': 'medicines/bandaid.jpg'
        },
        {
            'name': 'Cough Syrup',
            'description': 'Fast acting relief for cough and chest congestion.',
            'price': 9.99,
            'category': 'Personal Care',
            'image': 'medicines/coughsyrup.jpg'
        },
        {
            'name': 'Sunscreen SPF 50',
            'description': 'Broad spectrum protection against UVA and UVB rays.',
            'price': 16.99,
            'category': 'Personal Care',
            'image': 'medicines/sunscreen.jpg'
        },
        {
            'name': 'Hand Sanitizer 500ml',
            'description': 'Kills 99.9% of germs. With moisturizing aloe vera.',
            'price': 7.99,
            'category': 'Personal Care',
            'image': 'medicines/sanitizer.jpg'
        },
        {
            'name': 'Digital Thermometer',
            'description': 'Fast and accurate temperature reading.',
            'price': 12.99,
            'category': 'Personal Care',
            'image': 'medicines/thermometer.jpg'
        }
    ]

    print(f"Adding {len(medicines)} medicines...")

    for med_data in medicines:
        med, created = Medicine.objects.get_or_create(
            name=med_data['name'],
            defaults={
                'description': med_data['description'],
                'price': med_data['price'],
                'category': med_data['category'],
                'is_featured': random.choice([True, False]),
                'is_new': random.choice([True, False])
            }
        )
        if created:
            print(f"Created: {med.name}")
        else:
            print(f"Already exists: {med.name}")

if __name__ == '__main__':
    populate()
