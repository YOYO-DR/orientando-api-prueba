from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import AnonymousUser
from .models import ApiKey


class ApiKeyAuthentication(BaseAuthentication):
    """
    Autenticación personalizada usando API Keys.
    
    Los clientes deben incluir el header: Authorization: Api-Key <tu-api-key>
    """
    keyword = 'Api-Key'
    
    def authenticate(self, request):
        """
        Autenticar usando API Key en el header Authorization
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        if not auth_header:
            return None
            
        auth_parts = auth_header.split()
        
        if len(auth_parts) != 2 or auth_parts[0] != self.keyword:
            return None
            
        api_key = auth_parts[1]
        
        try:
            key_obj = ApiKey.objects.get(key=api_key, is_active=True)
            # Actualizar estadísticas de uso
            key_obj.update_usage()
            
            # Retornar un usuario especial para API Keys
            api_user = ApiKeyUser(api_key=key_obj)
            return (api_user, key_obj)
            
        except ApiKey.DoesNotExist:
            raise AuthenticationFailed('API Key inválida o inactiva')
    
    def authenticate_header(self, request):
        """
        Retorna el header que el cliente debe usar para autenticación
        """
        return self.keyword


class ApiKeyUser:
    """
    Usuario especial para requests autenticados con API Key
    """
    def __init__(self, api_key):
        self.api_key = api_key
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False
        self.is_staff = False
        self.is_superuser = False
        self.username = f"api_key_{api_key.name}"
        self.id = None
    
    def __str__(self):
        return f"API Key User: {self.api_key.name}"
    
    def has_perm(self, perm, obj=None):
        """API Keys tienen permisos básicos para usar la API"""
        return True
    
    def has_perms(self, perm_list, obj=None):
        """API Keys tienen permisos básicos para usar la API"""
        return True
    
    def has_module_perms(self, module):
        """API Keys tienen permisos básicos para usar la API"""
        return True
    
    def get_username(self):
        return self.username
