# chatbot/urls.py
from django.urls import path
from .views import chatbot_response

urlpatterns = [
    path('get_response/', chatbot_response, name='chatbot_response'),
]
