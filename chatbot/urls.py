# chatbot/urls.py
from django.urls import path
from .views import chatbot_response

urlpatterns = [
    path('', chatbot_response, name='chatbot_root_response'),   # accept /chatbot/ directly
    path('get_response/', chatbot_response, name='chatbot_response'),
]
