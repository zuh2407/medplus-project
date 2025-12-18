import sys
import os
import random
import django
from pathlib import Path
from django.db.models import Q

BASE_DIR = Path("C:/projects/pharmacy_app")
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy.settings')
django.setup()

from store.models import Medicine

def assign_images():
    print("--- Assigning Generic Images to Medicines ---")
    
    # Define our generic images available in media/medicines/
    images = {
        "bottle": "medicines/bottle.png",
        "pills": "medicines/pills.png",
        "blister": "medicines/blister.png",
        "cream": "medicines/cream.png"
    }
    
    # Filter medicines that probably have no image (empty string or None)
    # We also want to update the ones we imported which might have empty image fields
    meds = Medicine.objects.filter(Q(image="") | Q(image=None))
    
    print(f"Found {meds.count()} medicines without images.")
    count = 0
    
    for med in meds:
        # Simple heuristic to make it look somewhat correct
        name = med.name.lower()
        cat = med.category.lower()
        desc = med.description.lower()
        
        choice = "pills" # Default
        
        if "cream" in name or "gel" in name or "ointment" in name or "lotion" in name:
            choice = "cream"
        elif "syrup" in name or "liquid" in name or "solution" in name or "suspension" in name:
            choice = "bottle"
        elif "capsule" in name:
             choice = "pills" # The blue pills look like capsules
        elif "tablet" in name:
             choice = "blister"
        else:
            # Randomize for variety if no keyword matches
            choice = random.choice(list(images.keys()))
            
        med.image = images[choice]
        med.save()
        count += 1
        
    print(f"Updated {count} medicines with new images.")

if __name__ == "__main__":
    assign_images()
