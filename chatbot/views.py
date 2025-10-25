from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from store.models import Medicine
from .bots.pharmacy_bot import generate_bot_reply
import json

@csrf_exempt
def chatbot_response(request):
    """
    Accept POST requests with form-encoded 'message' or JSON { "message": "..." }.
    Returns JSON: { "response": "..." }
    """
    if request.method != "POST":
        return JsonResponse({"response": "Invalid request."}, status=400)

    # Try form POST first
    user_message = request.POST.get("message", "")
    if not user_message:
        # try JSON body
        try:
            body = json.loads(request.body.decode('utf-8') or "{}")
            user_message = body.get("message", "")
        except Exception:
            user_message = ""

    user_message = (user_message or "").strip().lower()
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
        # Fallback to corpus logic
        try:
            bot_reply = generate_bot_reply(user_message)
        except Exception:
            # don't crash the view for bot logic errors
            bot_reply = "Sorry, I'm having trouble right now. Please try again later."

    return JsonResponse({"response": bot_reply})
