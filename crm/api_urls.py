from rest_framework import routers
from django.urls import path, include
from .api_views import InteraccionViewSet

router = routers.DefaultRouter()
router.register(r'interacciones', InteraccionViewSet, basename='interacciones')

urlpatterns = [
    path('api/', include(router.urls)),
]
