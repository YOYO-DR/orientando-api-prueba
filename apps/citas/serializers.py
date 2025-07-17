from rest_framework import serializers
from .models import (
    Usuario, EstadoChat, Profesional, Cliente, Producto, 
    HistorialEstadoCita, Cita, ProductoProfesional,
    TipoDocumentoEnum, TipoUsuarioEnum, EstadoCitaEnum,
    ApiKey
)


class UsuarioSerializer(serializers.ModelSerializer):
    """Serializador para el modelo Usuario"""
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'nombres', 'apellidos', 'tipo_documento', 
            'numero_documento', 'email', 'celular', 'tipo'
        ]
        extra_kwargs = {
            'numero_documento': {'required': True},
            'celular': {'required': True},
            'email': {'required': False, 'allow_null': True, 'allow_blank': True}
        }

    def validate_email(self, value):
        """Validar formato de email"""
        if value and not value.strip():
            return None
        return value

    def validate_celular(self, value):
        """Validar formato de celular"""
        if not value.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise serializers.ValidationError("El celular debe contener solo números, espacios, guiones o signo +")
        return value


class EstadoChatSerializer(serializers.ModelSerializer):
    """Serializador para el modelo EstadoChat"""
    
    class Meta:
        model = EstadoChat
        fields = ['id', 'numero_whatsapp', 'estado_conversacion']

    def validate_numero_whatsapp(self, value):
        """Validar formato de número WhatsApp"""
        if not value.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise serializers.ValidationError("El número de WhatsApp debe contener solo números, espacios, guiones o signo +")
        return value


class ProfesionalSerializer(serializers.ModelSerializer):
    """Serializador para el modelo Profesional"""
    usuario = UsuarioSerializer(read_only=True)
    usuario_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Profesional
        fields = ['id', 'usuario', 'usuario_id', 'numero_whatsapp', 'cargo']
        
    def validate_usuario_id(self, value):
        """Validar que el usuario existe y es de tipo Profesional"""
        try:
            usuario = Usuario.objects.get(id=value)
            if usuario.tipo != TipoUsuarioEnum.PROFESIONAL:
                raise serializers.ValidationError("El usuario debe ser de tipo Profesional")
            return value
        except Usuario.DoesNotExist:
            raise serializers.ValidationError("El usuario especificado no existe")

    def validate_numero_whatsapp(self, value):
        """Validar formato de número WhatsApp"""
        if not value.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise serializers.ValidationError("El número de WhatsApp debe contener solo números, espacios, guiones o signo +")
        return value


class ClienteSerializer(serializers.ModelSerializer):
    """Serializador para el modelo Cliente"""
    usuario = UsuarioSerializer(read_only=True)
    usuario_id = serializers.IntegerField(write_only=True)
    estado_chat = EstadoChatSerializer(read_only=True)
    estado_chat_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = Cliente
        fields = [
            'id', 'usuario', 'usuario_id', 'nombre_acudiente', 'edad', 
            'barrio', 'direccion', 'remitido_colegio', 'colegio', 
            'estado_chat', 'estado_chat_id'
        ]

    def validate_usuario_id(self, value):
        """Validar que el usuario existe y es de tipo Cliente"""
        try:
            usuario = Usuario.objects.get(id=value)
            if usuario.tipo != TipoUsuarioEnum.CLIENTE:
                raise serializers.ValidationError("El usuario debe ser de tipo Cliente")
            return value
        except Usuario.DoesNotExist:
            raise serializers.ValidationError("El usuario especificado no existe")

    def validate_edad(self, value):
        """Validar que la edad sea razonable"""
        if value is not None and (value < 0 or value > 120):
            raise serializers.ValidationError("La edad debe estar entre 0 y 120 años")
        return value


class ProductoSerializer(serializers.ModelSerializer):
    """Serializador para el modelo Producto"""
    
    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'descripcion', 'es_agendable_por_bot', 'duracion_minutos']

    def validate_duracion_minutos(self, value):
        """Validar que la duración sea positiva"""
        if value <= 0:
            raise serializers.ValidationError("La duración debe ser mayor a 0 minutos")
        return value

    def validate_nombre(self, value):
        """Validar que el nombre no esté vacío"""
        if not value.strip():
            raise serializers.ValidationError("El nombre del producto no puede estar vacío")
        return value.strip()


class HistorialEstadoCitaSerializer(serializers.ModelSerializer):
    """Serializador para el modelo HistorialEstadoCita"""
    
    class Meta:
        model = HistorialEstadoCita
        fields = ['id', 'estado_cita', 'fecha_registro']
        read_only_fields = ['fecha_registro']


class CitaSerializer(serializers.ModelSerializer):
    """Serializador para el modelo Cita"""
    cliente = UsuarioSerializer(read_only=True)
    cliente_id = serializers.IntegerField(write_only=True)
    producto = ProductoSerializer(read_only=True)
    producto_id = serializers.IntegerField(write_only=True)
    profesional_asignado = UsuarioSerializer(read_only=True)
    profesional_asignado_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    estado_actual = HistorialEstadoCitaSerializer(read_only=True)
    estado_actual_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = Cita
        fields = [
            'id', 'cliente', 'cliente_id', 'producto', 'producto_id',
            'profesional_asignado', 'profesional_asignado_id',
            'fecha_hora_inicio', 'fecha_hora_fin', 'google_calendar_event_id',
            'google_calendar_url_event', 'estado_actual', 'estado_actual_id',
            'observaciones'
        ]

    def validate_cliente_id(self, value):
        """Validar que el cliente existe y es de tipo Cliente"""
        try:
            usuario = Usuario.objects.get(id=value)
            if usuario.tipo != TipoUsuarioEnum.CLIENTE:
                raise serializers.ValidationError("El usuario debe ser de tipo Cliente")
            return value
        except Usuario.DoesNotExist:
            raise serializers.ValidationError("El cliente especificado no existe")

    def validate_profesional_asignado_id(self, value):
        """Validar que el profesional existe y es de tipo Profesional"""
        if value is None:
            return value
        try:
            usuario = Usuario.objects.get(id=value)
            if usuario.tipo != TipoUsuarioEnum.PROFESIONAL:
                raise serializers.ValidationError("El usuario debe ser de tipo Profesional")
            return value
        except Usuario.DoesNotExist:
            raise serializers.ValidationError("El profesional especificado no existe")

    def validate(self, data):
        """Validaciones cruzadas"""
        fecha_inicio = data.get('fecha_hora_inicio')
        fecha_fin = data.get('fecha_hora_fin')
        
        if fecha_inicio and fecha_fin:
            if fecha_inicio >= fecha_fin:
                raise serializers.ValidationError({
                    'fecha_hora_fin': 'La fecha de fin debe ser posterior a la fecha de inicio'
                })
        
        return data


class ProductoProfesionalSerializer(serializers.ModelSerializer):
    """Serializador para el modelo ProductoProfesional"""
    producto = ProductoSerializer(read_only=True)
    producto_id = serializers.IntegerField(write_only=True)
    profesional = ProfesionalSerializer(read_only=True)
    profesional_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = ProductoProfesional
        fields = ['id', 'producto', 'producto_id', 'profesional', 'profesional_id']

    def validate(self, data):
        """Validar que la combinación producto-profesional no exista"""
        if ProductoProfesional.objects.filter(
            producto_id=data['producto_id'],
            profesional_id=data['profesional_id']
        ).exists():
            raise serializers.ValidationError("Esta combinación de producto y profesional ya existe")
        return data


class ApiKeySerializer(serializers.ModelSerializer):
    """Serializador para el modelo ApiKey"""
    key = serializers.CharField(read_only=True)
    
    class Meta:
        model = ApiKey
        fields = ['id', 'name', 'key', 'is_active', 'created_at', 'last_used', 'usage_count', 'description']
        read_only_fields = ['key', 'created_at', 'last_used', 'usage_count']

    def validate_name(self, value):
        """Validar que el nombre no esté vacío"""
        if not value.strip():
            raise serializers.ValidationError("El nombre de la API Key no puede estar vacío")
        return value.strip()


class ApiKeyCreateSerializer(serializers.ModelSerializer):
    """Serializador para crear API Keys (muestra la key completa una sola vez)"""
    
    class Meta:
        model = ApiKey
        fields = ['id', 'name', 'key', 'is_active', 'description']
        read_only_fields = ['key']

    def validate_name(self, value):
        """Validar que el nombre no esté vacío"""
        if not value.strip():
            raise serializers.ValidationError("El nombre de la API Key no puede estar vacío")
        return value.strip()


class ApiKeyListSerializer(serializers.ModelSerializer):
    """Serializador simplificado para listados de API Keys (oculta la key completa)"""
    key_preview = serializers.SerializerMethodField()
    
    class Meta:
        model = ApiKey
        fields = ['id', 'name', 'key_preview', 'is_active', 'created_at', 'last_used', 'usage_count']
    
    def get_key_preview(self, obj):
        """Mostrar solo los primeros y últimos caracteres de la key"""
        if len(obj.key) > 8:
            return f"{obj.key[:4]}...{obj.key[-4:]}"
        return "****"


# Serializadores simplificados para listados
class UsuarioListSerializer(serializers.ModelSerializer):
    """Serializador simplificado para listados de usuarios"""
    
    class Meta:
        model = Usuario
        fields = ['id', 'nombres', 'apellidos', 'tipo', 'email', 'celular']


class ProductoListSerializer(serializers.ModelSerializer):
    """Serializador simplificado para listados de productos"""
    
    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'duracion_minutos', 'es_agendable_por_bot']


class CitaListSerializer(serializers.ModelSerializer):
    """Serializador simplificado para listados de citas"""
    cliente_nombre = serializers.CharField(source='cliente.nombres', read_only=True)
    cliente_apellidos = serializers.CharField(source='cliente.apellidos', read_only=True)
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    profesional_nombre = serializers.CharField(source='profesional_asignado.nombres', read_only=True)
    estado_cita = serializers.CharField(source='estado_actual.estado_cita', read_only=True)
    
    class Meta:
        model = Cita
        fields = [
            'id', 'fecha_hora_inicio', 'fecha_hora_fin',
            'cliente_nombre', 'cliente_apellidos', 'producto_nombre',
            'profesional_nombre', 'estado_cita'
        ]
