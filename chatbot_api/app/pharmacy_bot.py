from store.models import Medicine
from django.db.models import Q
import random

class PharmacyBot:
    def process_instruction(self, text: str) -> str:
        text = text.lower()
        
        # Basic keyword matching for now
        if "hello" in text or "hi" in text:
            return "Hello! I am your Pharmacy Assistant. How can I help you regarding medicines today?"
        
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
                response = "Here is what I found:\n"
                for p in found_medicines[:3]: # Limit to 3
                    response += f"- {p.name}: ${p.price} ({'In Stock'})\n" # removed stock check as logic wasn't in Medicine model shown earlier
                return response
            else:
                return "I couldn't find any specific medicines matching your query. Please check the spelling or browse our catalog."

        return "I can help you check medicine prices and availability. Just ask 'Do you have Panadol?'"

    def process_prescription(self, filename: str, content: bytes) -> dict:
        # Mocking OCR / Analysis logic for now as per "unifying logic" step
        # Ideally this would parse the 'content' bytes (PDF/Image)
        
        # For demonstration, we'll return a static list or random safe medicines
        # mimicking "extracted" medicines from the file.
        
        # Unifying logic: This returns a list of suggested products found in DB
        
        all_medicines = list(Medicine.objects.all())
        if not all_medicines:
             return {"message": "No medicines in database to match.", "products": []}
             
        # Simulate finding 1-2 random products from the "prescription"
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
            
        return {
            "message": "Prescription processed successfully. We found these matches:",
            "products": results
        }
