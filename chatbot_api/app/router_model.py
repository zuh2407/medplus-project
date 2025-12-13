class RouterModel:
    def __init__(self):
        # Pharmacy Intents (transactional, inventory)
        self.pharmacy_keywords = [
            "price", "cost", "how much", 
            "buy", "purchase", "order", "get",
            "stock", "available", "have", "do you have",
            "prescription", "store", "shop"
        ]
        
        # Health Intents (informational)
        self.health_keywords = [
            "what is", "what are", 
            "side effect", "symptom", "dose", "dosage",
            "treat", "cure", "usage", "use",
            "benefit", "risk", "pain", "fever", "flu"
        ]

    def route_query(self, message: str) -> str:
        message = message.lower()
        
        # Simple keyword scoring
        pharmacy_score = sum(1 for k in self.pharmacy_keywords if k in message)
        health_score = sum(1 for k in self.health_keywords if k in message)
        
        # Default behavior
        if pharmacy_score > 0:
            return "pharmacy"
        if health_score > 0:
            return "health"
            
        # Fallback / Context aware
        if "?" in message and len(message.split()) > 3:
            return "health" # Assume questions are health related if not explicitly buying
            
        return "pharmacy" # Default to pharmacy assistant
