from django.urls import path
from . import views

urlpatterns = [
    path('send/', views.chat_send, name='chat_send'),
]
