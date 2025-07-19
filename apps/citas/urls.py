from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EstadoChatViewSet,
    ProfesionalViewSet,
    ClienteViewSet,
    ProductoViewSet,
    HistorialEstadoCitaViewSet,
    CitaViewSet,
    ProductoProfesionalViewSet,
    ApiKeyViewSet
)

router = DefaultRouter()

# Registrar todos los ViewSets
router.register(r'estados-chat', EstadoChatViewSet)
router.register(r'profesionales', ProfesionalViewSet)
router.register(r'clientes', ClienteViewSet)
router.register(r'productos', ProductoViewSet)
router.register(r'historial-estados', HistorialEstadoCitaViewSet)
router.register(r'citas', CitaViewSet)
router.register(r'producto-profesional', ProductoProfesionalViewSet)
router.register(r'api-keys', ApiKeyViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
