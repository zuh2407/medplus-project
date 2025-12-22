from chatbot_api.app.router_model import RouterModel

def test():
    router = RouterModel()
    queries = [
        "Can I take Aspirin if I am pregnant?",
        "symptoms of flu",
        "We have this in store",
        "Aspirin",
        "I'll take 2",
        "Can I take this with food?",
        "Is it safe for pregnancy?"
    ]
    
    print(f"{'QUERY':<40} | {'INTENT':<10} | {'SCORES (P/H/M)'}")
    print("-" * 70)
    
    for q in queries:
        msg = q.lower()
        p_score = sum(1 for k in router.pharmacy_keywords if k in msg)
        h_score = sum(1 for k in router.health_keywords if k in msg)
        m_score = sum(1 for k in router.medical_context_keywords if k in msg)
        
        intent = router.route_query(q)
        print(f"{q:<40} | {intent:<10} | {p_score}/{h_score}/{m_score}")

if __name__ == "__main__":
    test()
