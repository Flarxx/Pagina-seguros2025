from django.urls import path
from . import views

urlpatterns = [
    path('registrar/<int:poliza_id>/', views.registrar_pago, name='registrar_pago'),
    path('mis-pagos/', views.mis_pagos, name='mis_pagos'),
    path('admin/verificar-pagos/', views.verificar_pagos, name='verificar_pagos'),
]
    