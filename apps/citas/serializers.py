from rest_framework import serializers
import logging
from datetime import datetime
from .models import (
    Usuario, EstadoChat, Profesional, Cliente, Producto, 
    HistorialEstadoCita, Cita, ProductoProfesional,
    TipoDocumentoEnum, TipoUsuarioEnum, EstadoCitaEnum,
    ApiKey
)

# Logger específico para serializadores
logger = logging.getLogger(__name__)


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
    
    def to_representation(self, instance):
        """Personalizar la representación del cliente para incluir el nombre completo"""
        representation = super().to_representation(instance)
        # Quitar el ID del cliente y solo dejar el ID del modelo usuario
        representation.pop('id')
        return representation


class ProductoSerializer(serializers.ModelSerializer):
    """Serializador para el modelo Producto"""
    producto_id = serializers.IntegerField(source='id', read_only=True)
    profesionales = serializers.SerializerMethodField()
    
    class Meta:
        model = Producto
        fields = ['producto_id', 'nombre', 'descripcion', 'es_agendable_por_bot', 'duracion_minutos', 'profesionales']

    def get_profesionales(self, obj):
        """Obtener profesionales asignados a este producto"""
        # Ahora ProductoProfesional apunta directamente a Usuario
        usuarios_profesionales = Usuario.objects.filter(
            productoprofesional__producto=obj,
            tipo=TipoUsuarioEnum.PROFESIONAL
        ).select_related('profesional')
        return [{
            'profesional_id': usuario.id,
            'nombres': usuario.nombres,
            'apellidos': usuario.apellidos,
            'cargo': usuario.profesional.cargo if hasattr(usuario, 'profesional') else None,
            'numero_whatsapp': usuario.profesional.numero_whatsapp if hasattr(usuario, 'profesional') else None
        } for usuario in usuarios_profesionales]

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
    cita_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = HistorialEstadoCita
        fields = ['id', 'cita', 'cita_id', 'estado_cita', 'fecha_registro']
        read_only_fields = ['fecha_registro', 'cita']


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
    
    # Campos personalizados para fechas en formato dd/mm/aaaa hh:mm
    fecha_hora_inicio = serializers.CharField(write_only=True)
    fecha_hora_fin = serializers.CharField(write_only=True)
    
    class Meta:
        model = Cita
        fields = [
            'id', 'cliente', 'cliente_id', 'producto', 'producto_id',
            'profesional_asignado', 'profesional_asignado_id',
            'fecha_hora_inicio', 'fecha_hora_fin', 'google_calendar_event_id',
            'google_calendar_url_event', 'estado_actual', 'estado_actual_id',
            'observaciones'
        ]

    def to_representation(self, instance):
        """Personalizar la representación de salida"""
        data = super().to_representation(instance)
        
        # Agregar campos adicionales para mejor identificación
        data['cita_id'] = instance.id
        data['cliente_id'] = instance.cliente.id if instance.cliente else None
        data['profesional_id'] = instance.profesional_asignado.id if instance.profesional_asignado else None
        
        # Formatear fechas en la respuesta (dd/mm/aaaa hh:mm)
        if instance.fecha_hora_inicio:
            data['fecha_hora_inicio'] = instance.fecha_hora_inicio.strftime('%d/%m/%Y %H:%M')
        if instance.fecha_hora_fin:
            data['fecha_hora_fin'] = instance.fecha_hora_fin.strftime('%d/%m/%Y %H:%M')
            
        return data

    def validate_fecha_hora_inicio(self, value):
        """Validar y convertir fecha_hora_inicio desde formato dd/mm/aaaa hh:mm"""
        logger.info(f"=== VALIDACIÓN FECHA_HORA_INICIO - Valor: {value} ===")
        
        try:
            # Convertir desde formato dd/mm/aaaa hh:mm
            fecha_convertida = datetime.strptime(value, '%d/%m/%Y %H:%M')
            logger.info(f"Fecha convertida exitosamente: {fecha_convertida}")
            return fecha_convertida
        except ValueError as e:
            logger.error(f"Error de validación de fecha: {str(e)}")
            raise serializers.ValidationError(
                'El formato de fecha debe ser dd/mm/aaaa hh:mm (ejemplo: 20/07/2025 14:30)'
            )

    def validate_fecha_hora_fin(self, value):
        """Validar y convertir fecha_hora_fin desde formato dd/mm/aaaa hh:mm"""
        logger.info(f"=== VALIDACIÓN FECHA_HORA_FIN - Valor: {value} ===")
        
        try:
            # Convertir desde formato dd/mm/aaaa hh:mm
            fecha_convertida = datetime.strptime(value, '%d/%m/%Y %H:%M')
            logger.info(f"Fecha convertida exitosamente: {fecha_convertida}")
            return fecha_convertida
        except ValueError as e:
            logger.error(f"Error de validación de fecha: {str(e)}")
            raise serializers.ValidationError(
                'El formato de fecha debe ser dd/mm/aaaa hh:mm (ejemplo: 20/07/2025 15:30)'
            )

    def validate_cliente_id(self, value):
        """Validar que el cliente existe y es realmente un Cliente registrado"""
        logger.info(f"=== VALIDACIÓN CLIENTE_ID - ID: {value} ===")
        
        try:
            # Verificar que el usuario existe
            usuario = Usuario.objects.get(id=value)
            logger.info(f"Usuario encontrado - ID: {usuario.id}, Tipo: {usuario.tipo}")
            
            # Verificar que es de tipo CLIENTE
            if usuario.tipo != TipoUsuarioEnum.CLIENTE:
                logger.error(f"Error de validación: Usuario no es CLIENTE. Tipo: {usuario.tipo}")
                raise serializers.ValidationError(
                    f"El usuario debe ser de tipo CLIENTE. Tipo actual: {usuario.tipo}"
                )
            
            # Verificar que existe el registro Cliente relacionado
            if not hasattr(usuario, 'cliente'):
                logger.error(f"Error de validación: Usuario {usuario.id} no tiene perfil Cliente")
                raise serializers.ValidationError(
                    "El usuario no tiene un perfil de Cliente asociado"
                )
            
            logger.info(f"Validación cliente_id exitosa - Cliente ID: {usuario.cliente.id}")
            return value
        except Usuario.DoesNotExist:
            logger.error(f"Error de validación: Usuario {value} no existe")
            raise serializers.ValidationError("El cliente especificado no existe")

    def validate_profesional_asignado_id(self, value):
        """Validar que el profesional existe y es realmente un Profesional registrado"""
        if value is None:
            logger.info("Profesional asignado es None - validación OK")
            return value
            
        logger.info(f"=== VALIDACIÓN PROFESIONAL_ID - ID: {value} ===")
        
        try:
            # Verificar que el usuario existe
            usuario = Usuario.objects.get(id=value)
            logger.info(f"Usuario encontrado - ID: {usuario.id}, Tipo: {usuario.tipo}")
            
            # Verificar que es de tipo PROFESIONAL
            if usuario.tipo != TipoUsuarioEnum.PROFESIONAL:
                logger.error(f"Error de validación: Usuario no es PROFESIONAL. Tipo: {usuario.tipo}")
                raise serializers.ValidationError(
                    f"El usuario debe ser de tipo PROFESIONAL. Tipo actual: {usuario.tipo}"
                )
            
            # Verificar que existe el registro Profesional relacionado
            if not hasattr(usuario, 'profesional'):
                logger.error(f"Error de validación: Usuario {usuario.id} no tiene perfil Profesional")
                raise serializers.ValidationError(
                    "El usuario no tiene un perfil de Profesional asociado"
                )
            
            logger.info(f"Validación profesional_id exitosa - Profesional ID: {usuario.profesional.id}")
            return value
        except Usuario.DoesNotExist:
            logger.error(f"Error de validación: Usuario {value} no existe")
            raise serializers.ValidationError("El profesional especificado no existe")

    def validate_producto_id(self, value):
        """Validar que el producto existe"""
        logger.info(f"=== VALIDACIÓN PRODUCTO_ID - ID: {value} ===")
        
        try:
            producto = Producto.objects.get(id=value)
            logger.info(f"Producto encontrado - ID: {producto.id}, Nombre: {producto.nombre}")
            return value
        except Producto.DoesNotExist:
            logger.error(f"Error de validación: Producto {value} no existe")
            raise serializers.ValidationError("El producto especificado no existe")

    def validate(self, data):
        """Validaciones cruzadas"""
        logger.info("=== VALIDACIONES CRUZADAS CITA ===")
        
        fecha_inicio = data.get('fecha_hora_inicio')
        fecha_fin = data.get('fecha_hora_fin')
        
        # Validar fechas
        if fecha_inicio and fecha_fin:
            logger.info(f"Validando fechas - Inicio: {fecha_inicio}, Fin: {fecha_fin}")
            if fecha_inicio >= fecha_fin:
                logger.error("Error de validación: Fecha fin debe ser posterior a fecha inicio")
                raise serializers.ValidationError({
                    'fecha_hora_fin': 'La fecha de fin debe ser posterior a la fecha de inicio'
                })
        
        # Validar que el profesional pueda atender el producto
        profesional_id = data.get('profesional_asignado_id')
        producto_id = data.get('producto_id')
        
        if profesional_id and producto_id:
            logger.info(f"Validando relación Profesional-Producto - Profesional ID: {profesional_id}, Producto ID: {producto_id}")
            
            # Primero verificar que ambos existen (aunque ya se validaron individualmente)
            try:
                profesional = Usuario.objects.get(id=profesional_id)
                producto = Producto.objects.get(id=producto_id)
                logger.info(f"Verificación exitosa - Profesional: {profesional.nombres} {profesional.apellidos}, Producto: {producto.nombre}")
            except Usuario.DoesNotExist:
                logger.error(f"Error: Usuario profesional {profesional_id} no encontrado en validación cruzada")
                raise serializers.ValidationError({
                    'profesional_asignado_id': 'El profesional especificado no existe'
                })
            except Producto.DoesNotExist:
                logger.error(f"Error: Producto {producto_id} no encontrado en validación cruzada")
                raise serializers.ValidationError({
                    'producto_id': 'El producto especificado no existe'
                })
            
            # Verificar que existe una relación ProductoProfesional
            relacion_existe = ProductoProfesional.objects.filter(
                profesional_id=profesional_id,
                producto_id=producto_id
            ).exists()
            
            if not relacion_existe:
                logger.error(f"Error de validación: No existe relación ProductoProfesional para profesional {profesional_id} y producto {producto_id}")
                error_msg = f'El profesional {profesional.nombres} {profesional.apellidos} no está autorizado para atender el producto "{producto.nombre}"'
                logger.error(f"Error detallado: {error_msg}")
                raise serializers.ValidationError({
                    'profesional_asignado_id': error_msg
                })
            else:
                logger.info("Relación Profesional-Producto validada exitosamente")
        
        logger.info("=== VALIDACIONES CRUZADAS COMPLETADAS ===")
        return data


class ProductoProfesionalSerializer(serializers.ModelSerializer):
    """Serializador para el modelo ProductoProfesional"""
    producto = ProductoSerializer(read_only=True)
    producto_id = serializers.IntegerField(write_only=True)
    profesional = UsuarioSerializer(read_only=True)
    profesional_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = ProductoProfesional
        fields = ['id', 'producto', 'producto_id', 'profesional', 'profesional_id']

    def validate_profesional_id(self, value):
        """Validar que el profesional existe y es de tipo PROFESIONAL"""
        logger.info(f"=== VALIDACIÓN PROFESIONAL_ID en ProductoProfesional - ID: {value} ===")
        
        try:
            # Verificar que el usuario existe
            usuario = Usuario.objects.get(id=value)
            logger.info(f"Usuario encontrado - ID: {usuario.id}, Tipo: {usuario.tipo}")
            
            # Verificar que es de tipo PROFESIONAL
            if usuario.tipo != TipoUsuarioEnum.PROFESIONAL:
                logger.error(f"Error de validación: Usuario no es PROFESIONAL. Tipo: {usuario.tipo}")
                raise serializers.ValidationError(
                    f"El usuario debe ser de tipo PROFESIONAL. Tipo actual: {usuario.tipo}"
                )
            
            logger.info(f"Validación profesional_id exitosa en ProductoProfesional - Usuario ID: {usuario.id}")
            return value
        except Usuario.DoesNotExist:
            logger.error(f"Error de validación: Usuario {value} no existe")
            raise serializers.ValidationError("El profesional especificado no existe")

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
    producto_id = serializers.IntegerField(source='id', read_only=True)
    profesionales = serializers.SerializerMethodField()
    
    class Meta:
        model = Producto
        fields = ['producto_id', 'nombre', 'duracion_minutos', 'es_agendable_por_bot', 'profesionales']

    def get_profesionales(self, obj):
        """Obtener profesionales asignados a este producto"""
        # Ahora ProductoProfesional apunta directamente a Usuario
        usuarios_profesionales = Usuario.objects.filter(
            productoprofesional__producto=obj,
            tipo=TipoUsuarioEnum.PROFESIONAL
        ).select_related('profesional')
        return [{
            'profesional_id': usuario.id,
            'nombres': usuario.nombres,
            'apellidos': usuario.apellidos,
            'cargo': usuario.profesional.cargo if hasattr(usuario, 'profesional') else None,
            'numero_whatsapp': usuario.profesional.numero_whatsapp if hasattr(usuario, 'profesional') else None
        } for usuario in usuarios_profesionales]


class CitaListSerializer(serializers.ModelSerializer):
    """Serializador simplificado para listados de citas"""
    cita_id = serializers.IntegerField(source='id', read_only=True)
    cliente_id = serializers.IntegerField(source='cliente.id', read_only=True)
    cliente_nombre = serializers.CharField(source='cliente.nombres', read_only=True)
    cliente_apellidos = serializers.CharField(source='cliente.apellidos', read_only=True)
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    profesional_id = serializers.IntegerField(source='profesional_asignado.id', read_only=True)
    profesional_nombre = serializers.CharField(source='profesional_asignado.nombres', read_only=True)
    estado_cita = serializers.CharField(source='estado_actual.estado_cita', read_only=True)
    google_calendar_event_id = serializers.CharField(read_only=True)
    
    class Meta:
        model = Cita
        fields = [
            'cita_id', 'cliente_id', 'fecha_hora_inicio', 'fecha_hora_fin',
            'cliente_nombre', 'cliente_apellidos', 'producto_nombre',
            'profesional_id', 'profesional_nombre', 'estado_cita',
            'google_calendar_event_id'
        ]

    def to_representation(self, instance):
        """Personalizar la representación de salida con fechas en formato dd/mm/aaaa hh:mm"""
        data = super().to_representation(instance)
        
        # Formatear fechas en la respuesta (dd/mm/aaaa hh:mm)
        if instance.fecha_hora_inicio:
            data['fecha_hora_inicio'] = instance.fecha_hora_inicio.strftime('%d/%m/%Y %H:%M')
        if instance.fecha_hora_fin:
            data['fecha_hora_fin'] = instance.fecha_hora_fin.strftime('%d/%m/%Y %H:%M')
            
        return data
