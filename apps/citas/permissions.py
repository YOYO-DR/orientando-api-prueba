from rest_framework.permissions import BasePermission
from .authentication import ApiKeyUser


class IsApiKeyAuthenticated(BasePermission):
    """
    Permite acceso solo a usuarios autenticados con API Key o usuarios regulares autenticados
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            (request.user.is_authenticated or isinstance(request.user, ApiKeyUser))
        )


class IsApiKeyOrAuthenticated(BasePermission):
    """
    Permite acceso a usuarios autenticados normalmente o con API Key
    """
    def has_permission(self, request, view):
        # Permitir acceso si es usuario regular autenticado
        if request.user and request.user.is_authenticated:
            return True
            
        # Permitir acceso si es usuario con API Key
        if isinstance(request.user, ApiKeyUser):
            return True
            
        return False


class ApiKeyReadOnly(BasePermission):
    """
    Permite solo operaciones de lectura para API Keys
    """
    def has_permission(self, request, view):
        # Si no es usuario con API Key, permitir todo
        if not isinstance(request.user, ApiKeyUser):
            return True
            
        # Si es usuario con API Key, solo permitir operaciones de lectura
        return request.method in ['GET', 'HEAD', 'OPTIONS']


class ApiKeyFullAccess(BasePermission):
    """
    Permite acceso completo para API Keys
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            (request.user.is_authenticated or isinstance(request.user, ApiKeyUser))
        )
