import json
import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings

@require_POST
def chat_send(request):
    try:
        # Parse user message from JSON body
        data = json.loads(request.body)
        user_message = data.get('message', '')
        session_id = data.get('session_id', None)
        # Restriction: Only logged-in users
        if not request.user.is_authenticated:
            # Return as a normal message so the chatbot bubble displays it
            return JsonResponse({'response': 'Please log in or sign up to use the AI Assistant. 🔒'}, status=200)
        
        if not user_message:
            return JsonResponse({'error': 'Message is required'}, status=400)
        
        # Ensure session exists for anonymous users
        if not request.user.is_authenticated and not request.session.session_key:
            request.session.create()

        # Forward to FastAPI backend
        fastapi_url = f"{settings.FASTAPI_URL}/chat"

        payload = {
            'message': user_message, 
            'session_id': request.session.session_key if not request.user.is_authenticated else session_id,
            'user_id': request.user.id if request.user.is_authenticated else None
        }
        
        try:
            response = requests.post(fastapi_url, json=payload, timeout=60)
            response.raise_for_status()
            
            # Return FastAPI response to frontend
            return JsonResponse(response.json())
            
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection Error: Could not connect to Chatbot Service at {fastapi_url}")
            return JsonResponse({'error': 'Chat service unavailable'}, status=503)
        except requests.exceptions.RequestException as e:
            print(f"❌ Request Error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
