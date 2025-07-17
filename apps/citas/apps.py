from django.apps import AppConfig


class CitasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.citas'
    verbose_name = 'Gestión de Citas'
    
    def ready(self):
        """Importar señales cuando la aplicación esté lista"""
        try:
            import apps.citas.signals  # noqa F401
        except ImportError:
            pass
