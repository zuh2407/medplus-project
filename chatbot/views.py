# chatbot/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from store.models import Medicine
from .bots.pharmacy_bot import generate_bot_reply
import json

@csrf_exempt
def chatbot_response(request):
    """
    Accept POST requests with JSON { "message": "..." }.
    Returns JSON: { "response": "..." }
    """
    if request.method != "POST":
        return JsonResponse({"response": "Invalid request."}, status=400)

    # Parse JSON body
    try:
        body = json.loads(request.body.decode('utf-8') or "{}")
        user_message = (body.get("message", "") or "").strip()
    except Exception:
        user_message = ""

    if not user_message:
        return JsonResponse({"response": "Please type something to ask."})

    # Check if medicine exists (simple contains match)
    medicine = Medicine.objects.filter(name__icontains=user_message).first()
    if medicine:
        bot_reply = (
            f"✅ Yes, we have <b>{medicine.name}</b> in stock.<br>"
            f"💰 Price: {medicine.price} AED<br>"
            f"📦 Stock: Available"
        )
    else:
        # Fallback to bot logic
        try:
            bot_reply = generate_bot_reply(user_message)
        except Exception:
            bot_reply = "Sorry, I'm having trouble right now. Please try again later."

    return JsonResponse({"response": bot_reply})
