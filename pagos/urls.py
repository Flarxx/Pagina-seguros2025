from django.urls import path
from . import views

app_name = 'pagos'

urlpatterns = [
    path('registrar/<int:poliza_id>/', views.registrar_pago, name='registrar_pago'),
    path('mis-pagos/', views.mis_pagos, name='mis_pagos'),
    path('verificar/', views.verificar_pagos, name='verificar_pagos'),
]
    