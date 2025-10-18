from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from store.models import Medicine
from .bots.pharmacy_bot import generate_bot_reply

@csrf_exempt
def chatbot_response(request):
    if request.method == "POST":
        user_message = request.POST.get("message", "").strip().lower()
        if not user_message:
            return JsonResponse({"response": "Please type something to ask."})

        # Try to find medicine in database first
        medicine = Medicine.objects.filter(name__icontains=user_message).first()
        if medicine:
            stock_status = "Available" if medicine else "Out of stock"
            bot_reply = (
                f"✅ Yes, we have <b>{medicine.name}</b> in stock.<br>"
                f"💰 Price: {medicine.price} AED<br>"
                f"📦 Stock: {stock_status}"
            )
        else:
            # Fallback to AI / corpus logic
            bot_reply = generate_bot_reply(user_message)

        return JsonResponse({"response": bot_reply})
    return JsonResponse({"response": "Invalid request."})
