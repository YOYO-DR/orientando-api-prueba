from django.contrib import admin
from .models import (
    Usuario, EstadoChat, Profesional, Cliente, Producto,
    HistorialEstadoCita, Cita, ProductoProfesional, ApiKey
)


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['nombres', 'apellidos', 'tipo', 'numero_documento', 'email', 'celular']
    list_filter = ['tipo', 'tipo_documento']
    search_fields = ['nombres', 'apellidos', 'numero_documento', 'email']
    ordering = ['nombres', 'apellidos']


@admin.register(EstadoChat)
class EstadoChatAdmin(admin.ModelAdmin):
    list_display = ['numero_whatsapp', 'estado_conversacion']
    search_fields = ['numero_whatsapp']


@admin.register(Profesional)
class ProfesionalAdmin(admin.ModelAdmin):
    list_display = ['get_nombre_completo', 'cargo', 'numero_whatsapp']
    search_fields = ['usuario__nombres', 'usuario__apellidos', 'cargo']
    
    def get_nombre_completo(self, obj):
        return f"{obj.usuario.nombres} {obj.usuario.apellidos}"
    get_nombre_completo.short_description = 'Nombre Completo'


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['get_nombre_completo', 'edad', 'barrio', 'remitido_colegio', 'colegio']
    list_filter = ['remitido_colegio', 'colegio']
    search_fields = ['usuario__nombres', 'usuario__apellidos', 'barrio']
    
    def get_nombre_completo(self, obj):
        return f"{obj.usuario.nombres} {obj.usuario.apellidos}"
    get_nombre_completo.short_description = 'Nombre Completo'


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'duracion_minutos', 'es_agendable_por_bot']
    list_filter = ['es_agendable_por_bot']
    search_fields = ['nombre', 'descripcion']


@admin.register(HistorialEstadoCita)
class HistorialEstadoCitaAdmin(admin.ModelAdmin):
    list_display = ['estado_cita', 'fecha_registro']
    list_filter = ['estado_cita', 'fecha_registro']
    ordering = ['-fecha_registro']


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ['get_cliente', 'get_producto', 'get_profesional', 'fecha_hora_inicio', 'get_estado']
    list_filter = ['producto', 'profesional_asignado', 'estado_actual__estado_cita', 'fecha_hora_inicio']
    search_fields = ['cliente__nombres', 'cliente__apellidos', 'observaciones']
    date_hierarchy = 'fecha_hora_inicio'
    
    def get_cliente(self, obj):
        return f"{obj.cliente.nombres} {obj.cliente.apellidos}"
    get_cliente.short_description = 'Cliente'
    
    def get_producto(self, obj):
        return obj.producto.nombre
    get_producto.short_description = 'Producto'
    
    def get_profesional(self, obj):
        if obj.profesional_asignado:
            return f"{obj.profesional_asignado.nombres} {obj.profesional_asignado.apellidos}"
        return "Sin asignar"
    get_profesional.short_description = 'Profesional'
    
    def get_estado(self, obj):
        return obj.estado_actual.estado_cita if obj.estado_actual else "Sin estado"
    get_estado.short_description = 'Estado'


@admin.register(ProductoProfesional)
class ProductoProfesionalAdmin(admin.ModelAdmin):
    list_display = ['get_producto', 'get_profesional']
    list_filter = ['producto', 'profesional']
    
    def get_producto(self, obj):
        return obj.producto.nombre
    get_producto.short_description = 'Producto'
    
    def get_profesional(self, obj):
        # Ahora profesional apunta directamente a Usuario
        return f"{obj.profesional.nombres} {obj.profesional.apellidos}"
    get_profesional.short_description = 'Profesional'


@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ['name', 'key_preview', 'is_active', 'created_at', 'last_used', 'usage_count']
    list_filter = ['is_active', 'created_at', 'last_used']
    search_fields = ['name', 'description']
    readonly_fields = ['key', 'created_at', 'last_used', 'usage_count']
    ordering = ['-created_at']
    
    def key_preview(self, obj):
        """Mostrar solo una vista previa de la key por seguridad"""
        if len(obj.key) > 8:
            return f"{obj.key[:4]}...{obj.key[-4:]}"
