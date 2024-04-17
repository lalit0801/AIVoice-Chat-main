from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',index_view,name='index'),
    path('call',call,name='call'),
    path('create_event', CreateEvent.as_view(), name='create_event'),
    path('chatbot/',ChatBotView.as_view(),name='chatbot'),
]
