from django.db import models
from django.utils.translation import gettext_lazy as _
import secrets
import string


class TipoDocumentoEnum(models.TextChoices):
    CC = 'CC', _('Cédula de Ciudadanía')
    TI = 'TI', _('Tarjeta de Identidad')
    NIT = 'NIT', _('NIT')


class TipoUsuarioEnum(models.TextChoices):
    CLIENTE = 'Cliente', _('Cliente')
    PROFESIONAL = 'Profesional', _('Profesional')


class EstadoCitaEnum(models.TextChoices):
    AGENDADO = 'Agendado', _('Agendado')
    NOTIFICADO_PROFESIONAL = 'Notificado Profesional', _('Notificado Profesional')
    PENDIENTE_24H = 'Pendiente Primer Confirmación 24 Horas', _('Pendiente Primer Confirmación 24 Horas')
    PRIMER_CONFIRMADO = 'Primer Confirmado', _('Primer Confirmado')
    PENDIENTE_2H = 'Pendiente Segunda Confirmación 2 Horas', _('Pendiente Segunda Confirmación 2 Horas')
    SEGUNDO_CONFIRMADO = 'Segundo Confirmado', _('Segundo Confirmado')
    FINALIZADO = 'Finalizado', _('Finalizado')


class Usuario(models.Model):
    nombres = models.CharField(max_length=255)
    apellidos = models.CharField(max_length=255)
    tipo_documento = models.CharField(max_length=30, choices=TipoDocumentoEnum.choices)
    numero_documento = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True)
    celular = models.CharField(max_length=20, unique=True)
    tipo = models.CharField(max_length=20, choices=TipoUsuarioEnum.choices)

    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.tipo})"


class EstadoChat(models.Model):
    numero_whatsapp = models.CharField(max_length=20, unique=True)
    estado_conversacion = models.JSONField()

    def __str__(self):
        return self.numero_whatsapp


class Profesional(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    numero_whatsapp = models.CharField(max_length=20, unique=True)
    cargo = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return f"{self.usuario} - {self.cargo or 'Profesional'}"


class Cliente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    nombre_acudiente = models.CharField(max_length=255, null=True, blank=True)
    edad = models.PositiveIntegerField(null=True, blank=True)
    barrio = models.CharField(max_length=255, null=True, blank=True)
    direccion = models.CharField(max_length=255, null=True, blank=True)
    remitido_colegio = models.BooleanField(default=False)
    colegio = models.CharField(max_length=255, null=True, blank=True)
    estado_chat = models.ForeignKey(EstadoChat, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.usuario}"


class Producto(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(null=True, blank=True)
    es_agendable_por_bot = models.BooleanField(default=True)
    duracion_minutos = models.PositiveIntegerField()

    def __str__(self):
        return self.nombre


class HistorialEstadoCita(models.Model):
    estado_cita = models.CharField(max_length=100, choices=EstadoCitaEnum.choices)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.estado_cita} - {self.fecha_registro}"


class Cita(models.Model):
    cliente = models.ForeignKey(Usuario, related_name='citas', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    profesional_asignado = models.ForeignKey(Usuario, null=True, blank=True, related_name='citas_asignadas', on_delete=models.SET_NULL)
    fecha_hora_inicio = models.DateTimeField()
    fecha_hora_fin = models.DateTimeField()
    google_calendar_event_id = models.CharField(max_length=255, null=True, blank=True)
    google_calendar_url_event = models.CharField(max_length=255, null=True, blank=True)
    estado_actual = models.ForeignKey(HistorialEstadoCita, null=True, blank=True, on_delete=models.SET_NULL)
    observaciones = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Cita de {self.cliente} el {self.fecha_hora_inicio}"


class ProductoProfesional(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    profesional = models.ForeignKey(Profesional, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('producto', 'profesional')

    def __str__(self):
        return f"{self.producto} - {self.profesional}"


class ApiKey(models.Model):
    """Modelo para gestionar API Keys para chatbots y servicios externos"""
    name = models.CharField(max_length=100, help_text="Nombre descriptivo para la API Key")
    key = models.CharField(max_length=64, unique=True, editable=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)
    usage_count = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True, help_text="Descripción del uso de esta API Key")
    
    class Meta:
        verbose_name = "API Key"
        verbose_name_plural = "API Keys"
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        """Generar API Key automáticamente al crear"""
        if not self.key:
            self.key = self.generate_api_key()
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_api_key():
        """Generar una API Key aleatoria"""
        # Generar una clave de 48 caracteres (que será 64 en base64)
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(48))
    
    def update_usage(self):
        """Actualizar estadísticas de uso"""
        from django.utils import timezone
        self.last_used = timezone.now()
        self.usage_count += 1
        self.save(update_fields=['last_used', 'usage_count'])
    
    def __str__(self):
        return f"{self.name} ({'Activa' if self.is_active else 'Inactiva'})"
