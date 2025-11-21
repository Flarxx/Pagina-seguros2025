from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('usuarios.urls')),
    path('polizas/', include('polizas.urls')),
    path('pagos/', include('pagos.urls')),
    path('ayuda/', include('ayuda.urls')),
    path('api/polizas/', include('polizas.api_urls')),   # separar APIs
    path('api/crm/', include('crm.api_urls')),           # separar APIs
    path('crm/', include(('crm.urls', 'crm'), namespace='crm')),  # rutas normales del CRM
    path('reclamos/', include('reclamos.urls', namespace='reclamos')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
