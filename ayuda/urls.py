from django.urls import path, include
from . import views

app_name = 'ayuda'

urlpatterns = [
    path('', views.ayuda_index, name='index'),
    path('faq/<int:pk>/', views.faq_detail, name='faq_detail'),
    path('contacto/', views.contacto, name='contacto'),
    path('ticket/crear/', views.crear_ticket, name='crear_ticket'),
    path('mis-tickets/', views.mis_tickets, name='mis_tickets'),
    path('ticket/<int:pk>/', views.ticket_detail, name='ticket_detail'),
]
