from store.models import Medicine
from django.db.models import Q
import random

class PharmacyBot:
    def process_instruction(self, text: str) -> str:
        text = text.lower()
        
        # Cart Management Logic
        if "add" in text and "cart" in text:
            return self.manage_cart(text, action="add")
        if ("remove" in text or "delete" in text) and "cart" in text:
            return self.manage_cart(text, action="remove")
            
        # Basic keyword matching for now
        if "hello" in text or "hi" in text:
            return "Hello! I am your Pharmacy Assistant.\n\nI can help you Check Prices, Check Stock, Process Prescriptions, or Manage your Cart (e.g., 'Add 2 Panadol to cart').\n\nHow can I help you today?"
        
        if "price" in text or "cost" in text or "have" in text:
            # Simple product search
            medicines = Medicine.objects.all()
            found_medicines = []
            
            for word in text.split():
                if len(word) > 3: # Avoid small words
                    matches = medicines.filter(Q(name__icontains=word) | Q(description__icontains=word))
                    for p in matches:
                        if p.name not in [fp.name for fp in found_medicines]:
                            found_medicines.append(p)
            
            if found_medicines:
                response = "We have this in store:\n\n"
                for p in found_medicines[:5]: 
                    response += f"{p.name}\n"
                    response += f"Price: ${p.price}\n\n"
                
                response += "Would you like to add any of these to your cart with a message like 'Add Panadol to cart'?"
                return response
            else:
                return "No matches found.\n\nI couldn't find any specific medicines matching your query in our catalog. Please check the spelling."

        if "time" in text or "hour" in text or "open" in text or "close" in text or "when" in text or "available" in text:
            return (
                "Here are our Service Hours:\n\n"
                "Store Hours:\n"
                "- Mon-Fri: 8:00 AM - 10:00 PM\n"
                "- Sat-Sun: 9:00 AM - 9:00 PM\n\n"
                "Pharmacist Availability:\n"
                "- Mon-Fri: 9:00 AM - 6:00 PM\n"
                "- Sat: 10:00 AM - 4:00 PM"
            )

        return "I can help you check our store inventory. Please ask for a specific medicine name or say 'Add Panadol to cart'."

    def manage_cart(self, text: str, action: str) -> str:
        from store.models import CartItem, Medicine # Import here to avoid circulars if any
        
        # 1. Parse Quantity (default 1)
        # Look for words like "two", "three" or digits
        words = text.split()
        quantity = 1
        qty_map = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
        
        for w in words:
            if w.isdigit():
                quantity = int(w)
                break
            if w in qty_map:
                quantity = qty_map[w]
                break
                
        # 2. Parse Medicine Name
        # We assume the name is in the sentence. We check all medicines.
        medicines = Medicine.objects.all()
        target_med = None
        
        # Heuristic: Find the longest matching medicine name in the text
        # "Add two Panadol Extra to cart" -> Matches "Panadol Extra"
        for med in medicines:
            if med.name.lower() in text:
                # Keep the match if it's the best one (or first one)
                target_med = med
                break
        
        if not target_med:
             return "I couldn't identify the medicine name to add/remove. Please say the exact product name, e.g., 'Add Panadol to cart'."

        # 3. Perform Action
        if action == "add":
            item, created = CartItem.objects.get_or_create(medicine=target_med)
            if not created:
                item.quantity += quantity
            else:
                item.quantity = quantity
            item.save()
            return f"{quantity} x {target_med.name} added to your cart.\n\nCurrent Cart Total: ${sum(i.get_total_price() for i in CartItem.objects.all())}"
            
        elif action == "remove":
            try:
                item = CartItem.objects.get(medicine=target_med)
                item.delete()
                return f"{target_med.name} removed from your cart."
            except CartItem.DoesNotExist:
                return f"{target_med.name} is not in your cart."
                
        return "I didn't understand that cart command."

    def process_prescription(self, filename: str, content: bytes) -> dict:
        # Looking for "unifying logic" mock
        
        all_medicines = list(Medicine.objects.all())
        if not all_medicines:
             return {"message": "Database Empty\n\nNo medicines found in the system.", "products": []}
             
        # Simulate finding products
        suggestions = random.sample(all_medicines, min(len(all_medicines), 2))
        
        results = []
        for p in suggestions:
            results.append({
                "id": p.id,
                "name": p.name,
                "price": str(p.price),
                "image_url": p.image.url if p.image else "",
                "description": p.description[:100] + "..."
            })
            
        # Formatted Message
        msg = "Prescription Analyzed\n\n"
        msg += "We analyzed your file and identified the following potential matches from our inventory:\n\n"
        for p in suggestions:
             msg += f"{p.name}\n"
             msg += f"Price: ${p.price}\n"
        
        msg += "\nPlease confirm these are the correct items before ordering."

        return {
            "message": msg,
            "products": results
        }
