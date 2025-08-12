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
    PENDIENTE_24H_MSG_ENVIADO = 'Pendiente Primer Confirmación 24 Horas Mensaje Enviado', _('Pendiente Primer Confirmación 24 Horas Mensaje Enviado')
    PRIMER_CONFIRMADO = 'Primer Confirmado', _('Primer Confirmado')
    PENDIENTE_6H = 'Pendiente Segunda Confirmación 6 Horas', _('Pendiente Segunda Confirmación 6 Horas')
    PENDIENTE_6H_MSG_ENVIADO = 'Pendiente Segunda Confirmación 6 Horas Mensaje Enviado', _('Pendiente Segunda Confirmación 6 Horas Mensaje Enviado')
    SEGUNDO_CONFIRMADO = 'Segundo Confirmado', _('Segundo Confirmado')
    INFORMADO_AGENTE_3h = 'Informado Agente 3h', _('Informado Agente 3h')
    FINALIZADO = 'Finalizado', _('Finalizado')
    CANCELADO = 'Cancelado', _('Cancelado')
    NO_ASISTIO = 'No Asistió', _('No Asistió')


class Usuario(models.Model):
    nombres = models.CharField(max_length=255, db_index=True)
    apellidos = models.CharField(max_length=255, db_index=True)
    tipo_documento = models.CharField(max_length=30, choices=TipoDocumentoEnum.choices, db_index=True)
    numero_documento = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True)
    celular = models.CharField(max_length=20, db_index=True)
    tipo = models.CharField(max_length=20, choices=TipoUsuarioEnum.choices, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['nombres', 'apellidos'], name='usuario_nombre_completo_idx'),
            models.Index(fields=['tipo', 'nombres'], name='usuario_tipo_nombre_idx'),
            models.Index(fields=['tipo_documento', 'numero_documento'], name='usuario_documento_idx'),
        ]

    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.tipo})"


class EstadoChat(models.Model):
    numero_whatsapp = models.CharField(max_length=20, unique=True)  # Ahora es único
    estado_conversacion = models.JSONField()

    class Meta:
        indexes = [
            models.Index(fields=['numero_whatsapp'], name='estadochat_whatsapp_idx'),
        ]

    def __str__(self):
        return self.numero_whatsapp


class Profesional(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    numero_whatsapp = models.CharField(max_length=20, unique=True)
    cargo = models.CharField(max_length=150, null=True, blank=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['cargo'], name='profesional_cargo_idx'),
            models.Index(fields=['numero_whatsapp'], name='profesional_whatsapp_idx'),
        ]

    def __str__(self):
        return f"{self.usuario} - {self.cargo or 'Profesional'}"


class Cliente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    nombre_acudiente = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    edad = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    barrio = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    direccion = models.CharField(max_length=255, null=True, blank=True)
    remitido_colegio = models.BooleanField(default=False, null=True, blank=True, db_index=True)
    colegio = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    estado_chat = models.ForeignKey(EstadoChat, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        indexes = [
            models.Index(fields=['remitido_colegio', 'colegio'], name='cliente_colegio_idx'),
            models.Index(fields=['barrio'], name='cliente_barrio_idx'),
            models.Index(fields=['edad'], name='cliente_edad_idx'),
            models.Index(fields=['estado_chat'], name='cliente_estado_chat_idx'),
        ]

    def __str__(self):
        return f"{self.usuario}"


class Producto(models.Model):
    nombre = models.CharField(max_length=255, db_index=True)
    descripcion = models.TextField(null=True, blank=True)
    es_agendable_por_bot = models.BooleanField(default=True, db_index=True)
    duracion_minutos = models.PositiveIntegerField(db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['es_agendable_por_bot', 'nombre'], name='producto_agendable_nombre_idx'),
            models.Index(fields=['duracion_minutos'], name='producto_duracion_idx'),
        ]

    def __str__(self):
        return self.nombre


class HistorialEstadoCita(models.Model):
    cita = models.ForeignKey('Cita', related_name='historial_estados', on_delete=models.CASCADE, db_index=True)
    estado_cita = models.CharField(max_length=100, choices=EstadoCitaEnum.choices, db_index=True)
    fecha_registro = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['cita', 'fecha_registro'], name='historial_cita_fecha_idx'),
            models.Index(fields=['estado_cita', 'fecha_registro'], name='historial_estado_fecha_idx'),
            models.Index(fields=['-fecha_registro'], name='historial_fecha_desc_idx'),
        ]

    def __str__(self):
        return f"Cita {self.cita.id} - {self.estado_cita} - {self.fecha_registro}"


class Cita(models.Model):
    cliente = models.ForeignKey(Usuario, related_name='citas', on_delete=models.CASCADE, db_index=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, db_index=True)
    profesional_asignado = models.ForeignKey(Usuario, null=True, blank=True, related_name='citas_asignadas', on_delete=models.SET_NULL, db_index=True)
    fecha_hora_inicio = models.DateTimeField(db_index=True)
    fecha_hora_fin = models.DateTimeField(db_index=True)
    google_calendar_event_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    google_calendar_url_event = models.CharField(max_length=255, null=True, blank=True)
    estado_actual = models.ForeignKey(HistorialEstadoCita, null=True, blank=True, related_name='cita_con_este_estado', on_delete=models.SET_NULL, db_index=True)
    observaciones = models.TextField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['fecha_hora_inicio', 'fecha_hora_fin'], name='cita_horario_idx'),
            models.Index(fields=['cliente', 'fecha_hora_inicio'], name='cita_cliente_fecha_idx'),
            models.Index(fields=['profesional_asignado', 'fecha_hora_inicio'], name='cita_profesional_fecha_idx'),
            models.Index(fields=['producto', 'fecha_hora_inicio'], name='cita_producto_fecha_idx'),
            models.Index(fields=['estado_actual', 'fecha_hora_inicio'], name='cita_estado_fecha_idx'),
            models.Index(fields=['-fecha_hora_inicio'], name='cita_fecha_desc_idx'),
            models.Index(fields=['google_calendar_event_id'], name='cita_calendar_event_idx'),
        ]

    def save(self, *args, **kwargs):
        """Override save para crear estado inicial en citas nuevas"""
        is_new = self.pk is None
        
        # Guardar la cita primero
        super().save(*args, **kwargs)
        
        # Si es una cita nueva y no tiene estado actual, crear el primer estado
        if is_new and not self.estado_actual:
            primer_estado = HistorialEstadoCita.objects.create(
                cita=self,
                estado_cita=EstadoCitaEnum.AGENDADO
            )
            # Actualizar la cita con el primer estado (sin triggerar save otra vez)
            Cita.objects.filter(pk=self.pk).update(estado_actual=primer_estado)
            self.estado_actual = primer_estado

    def cambiar_estado(self, nuevo_estado, observaciones_adicionales=None):
        """
        Método para cambiar estado y registrar automáticamente en historial
        
        Args:
            nuevo_estado: El nuevo estado de la cita (debe ser un valor válido de EstadoCitaEnum)
            observaciones_adicionales: Observaciones opcionales para agregar
            
        Returns:
            HistorialEstadoCita: El registro de historial creado
        """
        # Validar que el nuevo estado es válido
        estados_validos = [choice[0] for choice in EstadoCitaEnum.choices]
        if nuevo_estado not in estados_validos:
            raise ValueError(f"Estado '{nuevo_estado}' no es válido. Estados válidos: {estados_validos}")
        
        # Crear registro en historial
        historial = HistorialEstadoCita.objects.create(
            cita=self,
            estado_cita=nuevo_estado
        )
        
        # Actualizar estado actual de la cita
        self.estado_actual = historial
        
        # Agregar observaciones adicionales si se proporcionan
        if observaciones_adicionales:
            if self.observaciones:
                self.observaciones += f"\n--- {historial.fecha_registro.strftime('%Y-%m-%d %H:%M')} ---\n{observaciones_adicionales}"
            else:
                self.observaciones = f"--- {historial.fecha_registro.strftime('%Y-%m-%d %H:%M')} ---\n{observaciones_adicionales}"
        
        # Guardar solo los campos necesarios para evitar recursión
        self.save(update_fields=['estado_actual', 'observaciones'])
        
        return historial

    def get_estado_actual_nombre(self):
        """Obtener el nombre del estado actual"""
        return self.estado_actual.estado_cita if self.estado_actual else "Sin estado"

    def get_historial_completo(self):
        """Obtener todo el historial de estados ordenado por fecha"""
        return self.historial_estados.all().order_by('fecha_registro')

    def __str__(self):
        return f"Cita de {self.cliente} el {self.fecha_hora_inicio}"


class ProductoProfesional(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, db_index=True)
    profesional = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_index=True)

    class Meta:
        unique_together = ('producto', 'profesional')
        indexes = [
            models.Index(fields=['producto', 'profesional'], name='producto_profesional_idx'),
        ]

    def __str__(self):
        return f"{self.producto} - {self.profesional}"


class ApiKey(models.Model):
    """Modelo para gestionar API Keys para chatbots y servicios externos"""
    name = models.CharField(max_length=100, help_text="Nombre descriptivo para la API Key", db_index=True)
    key = models.CharField(max_length=64, unique=True, editable=False)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    last_used = models.DateTimeField(null=True, blank=True, db_index=True)
    usage_count = models.PositiveIntegerField(default=0, db_index=True)
    description = models.TextField(blank=True, help_text="Descripción del uso de esta API Key")
    
    class Meta:
        verbose_name = "API Key"
        verbose_name_plural = "API Keys"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active', 'name'], name='apikey_active_name_idx'),
            models.Index(fields=['-created_at'], name='apikey_created_desc_idx'),
            models.Index(fields=['-last_used'], name='apikey_last_used_desc_idx'),
            models.Index(fields=['-usage_count'], name='apikey_usage_desc_idx'),
        ]
    
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
