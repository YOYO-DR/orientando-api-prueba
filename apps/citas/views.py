from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view
import logging

# Logger específico para este módulo
logger = logging.getLogger(__name__)

from .models import (
    Usuario, EstadoChat, Profesional, Cliente, Producto,
    HistorialEstadoCita, Cita, ProductoProfesional,
    TipoUsuarioEnum, EstadoCitaEnum, ApiKey
)
from .serializers import (
    UsuarioSerializer, UsuarioListSerializer,
    EstadoChatSerializer,
    ProfesionalSerializer,
    ClienteSerializer,
    ProductoSerializer, ProductoListSerializer,
    HistorialEstadoCitaSerializer,
    CitaSerializer, CitaListSerializer,
    ProductoProfesionalSerializer,
    ApiKeySerializer, ApiKeyCreateSerializer, ApiKeyListSerializer
)
from .authentication import ApiKeyAuthentication
from .permissions import IsApiKeyOrAuthenticated, ApiKeyFullAccess

@extend_schema_view(
    list=extend_schema(description="Listar todos los estados de chat"),
    create=extend_schema(description="Crear un nuevo estado de chat"),
    retrieve=extend_schema(description="Obtener un estado de chat específico"),
    update=extend_schema(description="Actualizar un estado de chat"),
    partial_update=extend_schema(description="Actualizar parcialmente un estado de chat"),
    destroy=extend_schema(description="Eliminar un estado de chat")
)
class EstadoChatViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar estados de conversaciones WhatsApp.
    
    Permite gestionar el estado de las conversaciones de WhatsApp
    para cada número registrado.
    """
    queryset = EstadoChat.objects.all()
    serializer_class = EstadoChatSerializer
    permission_classes = [IsApiKeyOrAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['numero_whatsapp']

    @extend_schema(
        description="Buscar estado por número de WhatsApp",
        responses={200: EstadoChatSerializer}
    )
    @action(detail=False, methods=['get'])
    def por_numero(self, request):
        """Buscar estado de chat por número de WhatsApp"""
        numero = request.query_params.get('numero', None)
        if not numero:
            return Response({'error': 'Parámetro numero es requerido'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            estado_chat = EstadoChat.objects.get(numero_whatsapp=numero)
            serializer = self.get_serializer(estado_chat)
            return Response(serializer.data)
        except EstadoChat.DoesNotExist:
            return Response({'error': 'Estado de chat no encontrado'}, 
                          status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        description="Actualizar estado de chat por número de WhatsApp (enviado en JSON)",
        request=EstadoChatSerializer,
        responses={200: EstadoChatSerializer}
    )
    @action(detail=False, methods=['put', 'patch'], url_path='actualizar-por-numero')
    def actualizar_por_numero(self, request):
        """
        Actualizar estado de chat utilizando el número de WhatsApp enviado en el JSON
        
        Este endpoint permite al bot actualizar un estado de chat usando el número de WhatsApp
        enviado en el cuerpo de la petición, no en la URL.
        
        URL FIJA: /api/estados-chat/actualizar-por-numero/
        
        Estructura esperada del JSON:
        {
            "numero_whatsapp": "573001234567",
            "estado_conversacion": {
                "fase": "confirmacion_cita",
                "step": "seleccion_horario"
            }
        }
        """
        logger.info("=== INICIO - Actualizando estado de chat por número de WhatsApp (desde JSON) ===")
        
        data = request.data
        numero_whatsapp = data.get('numero_whatsapp')
        
        logger.info(f"Datos recibidos: {data}")
        logger.info(f"Número WhatsApp extraído del JSON: {numero_whatsapp}")
        
        if not numero_whatsapp:
            return Response({
                'error': 'numero_whatsapp es requerido en el JSON'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Buscar el estado de chat por número de WhatsApp
            estado_chat = EstadoChat.objects.get(numero_whatsapp=numero_whatsapp)
            logger.info(f"EstadoChat encontrado - ID: {estado_chat.id}, WhatsApp: {estado_chat.numero_whatsapp}")
            
            # Actualizar el estado de chat (excluir numero_whatsapp de los datos a procesar ya que es el identificador)
            datos_actualizacion = {key: value for key, value in data.items() if key != 'numero_whatsapp'}
            
            logger.info(f"Datos para actualización: {datos_actualizacion}")
            
            if not datos_actualizacion:
                return Response({
                    'error': 'No hay datos para actualizar'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            estado_chat_serializer = EstadoChatSerializer(
                estado_chat, 
                data=datos_actualizacion, 
                partial=True
            )
            
            if not estado_chat_serializer.is_valid():
                logger.error(f"Error validando estado chat: {estado_chat_serializer.errors}")
                return Response({
                    'error': 'Datos de estado chat inválidos', 
                    'detalles': estado_chat_serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            estado_chat_serializer.save()
            logger.info(f"EstadoChat actualizado exitosamente - ID: {estado_chat.id}")
            
            # Retornar el estado de chat actualizado
            estado_chat_actualizado = EstadoChat.objects.get(id=estado_chat.id)
            response_serializer = EstadoChatSerializer(estado_chat_actualizado)
            
            logger.info("=== FIN - Estado de chat actualizado exitosamente por número de WhatsApp ===")
            return Response({
                'message': 'Estado de chat actualizado exitosamente',
                'data': response_serializer.data
            })
            
        except EstadoChat.DoesNotExist:
            logger.error(f"Estado de chat no encontrado para número: {numero_whatsapp}")
            return Response({
                'error': 'Estado de chat no encontrado con ese número de WhatsApp'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error actualizando estado de chat por número: {str(e)}")
            return Response({
                'error': 'Error interno del servidor', 
                'detalles': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema_view(
    list=extend_schema(description="Listar todos los profesionales"),
    create=extend_schema(description="Crear un nuevo profesional"),
    retrieve=extend_schema(description="Obtener un profesional específico"),
    update=extend_schema(description="Actualizar un profesional"),
    partial_update=extend_schema(description="Actualizar parcialmente un profesional"),
    destroy=extend_schema(description="Eliminar un profesional")
)
class ProfesionalViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar profesionales.
    
    Maneja la información específica de los profesionales
    del sistema, incluyendo su cargo y número de WhatsApp.
    """
    queryset = Profesional.objects.select_related('usuario').all()
    serializer_class = ProfesionalSerializer
    permission_classes = [IsApiKeyOrAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['usuario__nombres', 'usuario__apellidos', 'cargo', 'numero_whatsapp']
    ordering_fields = ['usuario__nombres', 'cargo']
    ordering = ['usuario__nombres']

    @extend_schema(
        description="Obtener productos asignados a un profesional",
        responses={200: ProductoListSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def productos(self, request, pk=None):
        """Obtener productos asignados a un profesional"""
        profesional = self.get_object()
        productos = Producto.objects.filter(productoprofesional__profesional=profesional)
        serializer = ProductoListSerializer(productos, many=True)
        return Response(serializer.data)

    @extend_schema(
        description="Buscar profesional por ID de usuario (enviado en JSON)",
        responses={200: ProfesionalSerializer}
    )
    @action(detail=False, methods=['post'], url_path='por-id')
    def por_id(self, request):
        """
        Buscar profesional por ID de usuario enviado en el JSON
        
        Este endpoint permite buscar un profesional usando el ID del usuario
        enviado en el cuerpo de la petición, no en la URL.
        
        URL FIJA: /api/profesionales/por-id/
        
        Estructura esperada del JSON:
        {
            "profesional_id": 456
        }
        
        Respuesta exitosa:
        {
            "profesional_id": 456,
            "nombres": "Dr. Juan Carlos",
            "apellidos": "Pérez García",
            "tipo_documento": "CC",
            "numero_documento": "12345678",
            "email": "dr.juan@email.com",
            "celular": "3009876543",
            "tipo": "Profesional",
            "numero_whatsapp": "573001234567",
            "cargo": "Psicólogo Clínico"
        }
        """
        logger.info("=== INICIO - Buscando profesional por ID de usuario (desde JSON) ===")
        
        data = request.data
        profesional_id = data.get('profesional_id')  # Este es realmente el usuario_id
        
        logger.info(f"Datos recibidos: {data}")
        logger.info(f"Profesional ID (usuario_id) extraído del JSON: {profesional_id}")
        
        if not profesional_id:
            return Response({
                'error': 'profesional_id es requerido en el JSON'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Buscar el usuario (profesional_id es realmente el usuario_id)
            usuario = Usuario.objects.get(id=profesional_id)
            logger.info(f"Usuario encontrado - ID: {usuario.id}, Tipo: {usuario.tipo}")
            
            # Verificar que el usuario sea de tipo PROFESIONAL
            if usuario.tipo != TipoUsuarioEnum.PROFESIONAL:
                logger.warning(f"Tipo de usuario no válido: {usuario.tipo}")
                return Response({
                    'error': f'Solo se pueden consultar usuarios de tipo PROFESIONAL. Tipo actual: {usuario.tipo}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Buscar el profesional relacionado
            try:
                profesional = Profesional.objects.select_related('usuario').get(usuario=usuario)
                logger.info(f"Profesional encontrado - ID: {profesional.id}")
            except Profesional.DoesNotExist:
                logger.error(f"No se encontró profesional para usuario ID: {profesional_id}")
                return Response({
                    'error': 'No se encontró registro de profesional para este usuario'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Construir respuesta en formato flat (profesional_id = usuario.id)
            response_data = {
                'profesional_id': usuario.id,  # Retornar el ID del usuario como profesional_id
                'nombres': usuario.nombres,
                'apellidos': usuario.apellidos,
                'tipo_documento': usuario.tipo_documento,
                'numero_documento': usuario.numero_documento,
                'email': usuario.email,
                'celular': usuario.celular,
                'tipo': usuario.tipo,
                'numero_whatsapp': profesional.numero_whatsapp,
                'cargo': profesional.cargo
            }
            
            logger.info("=== FIN - Profesional encontrado y retornado en formato flat ===")
            return Response(response_data)
            
        except Usuario.DoesNotExist:
            logger.error(f"Usuario no encontrado con ID: {profesional_id}")
            return Response({
                'error': 'Usuario no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error buscando profesional por ID de usuario: {str(e)}")
            return Response({
                'error': 'Error interno del servidor', 
                'detalles': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema_view(
    list=extend_schema(description="Listar todos los clientes"),
    create=extend_schema(description="Crear un nuevo cliente"),
    retrieve=extend_schema(description="Obtener un cliente específico"),
    update=extend_schema(description="Actualizar un cliente"),
    partial_update=extend_schema(description="Actualizar parcialmente un cliente"),
    destroy=extend_schema(description="Eliminar un cliente")
)
class ClienteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar clientes.
    
    Maneja la información específica de los clientes,
    incluyendo datos personales y de contacto.
    """
    queryset = Cliente.objects.select_related('usuario', 'estado_chat').all()
    serializer_class = ClienteSerializer
    permission_classes = [IsApiKeyOrAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['remitido_colegio', 'colegio']
    search_fields = ['usuario__nombres', 'usuario__apellidos', 'barrio', 'colegio']
    ordering_fields = ['usuario__nombres', 'edad']
    ordering = ['usuario__nombres']

    def create(self, request, *args, **kwargs):
        """
        Crear cliente completo con usuario y estado de chat
        
        IMPORTANTE: La respuesta incluye el ID del Usuario (no del modelo Cliente)
        para que el bot use ese ID en futuras actualizaciones.
        
        Estructura esperada del JSON:
        {
            "nombres": "Juan Carlos",
            "apellidos": "Pérez García",
            "tipo_documento": "CC",
            "numero_documento": "12345678",
            "email": "juan.nuevo@email.com",
            "celular": "3009876543",
            "edad": 26,
            "barrio": "Zona Norte",
            "colegio": "Nuevo Colegio",
            "remitido_colegio": true,
            "nombre_acudiente": "María García",
            "direccion": "Calle 123 #45-67",
            "estado_chat": {
                "estado_conversacion": {
                    "fase": "confirmacion_cita",
                    "step": "seleccion_horario"
                },
                "numero_whatsapp": "57123465798"
            }
        }
        
        Respuesta exitosa:
        {
            "id": 123,  // ID del Usuario - usar este para actualizaciones
            "usuario": { ... },
            "edad": 25,
            "barrio": "Centro",
            // ... otros campos
        }
        """
        logger.info("=== INICIO - Creando cliente completo ===")
        
        data = request.data
        logger.info(f"Datos recibidos: {data}")
        
        try:
            from django.db import transaction
            
            with transaction.atomic():
                # 1. Separar datos de Usuario y Cliente
                campos_usuario = ['nombres', 'apellidos', 'tipo_documento', 'numero_documento', 'email', 'celular']
                campos_cliente = ['edad', 'barrio', 'colegio', 'remitido_colegio', 'nombre_acudiente', 'direccion']
                
                usuario_data = {key: value for key, value in data.items() if key in campos_usuario}
                cliente_data = {key: value for key, value in data.items() if key in campos_cliente}
                estado_chat_data = data.get('estado_chat')
                
                # Validar que al menos algunos datos de usuario estén presentes
                if not usuario_data.get('nombres') or not usuario_data.get('apellidos'):
                    return Response({'error': 'nombres y apellidos son requeridos'}, 
                                  status=status.HTTP_400_BAD_REQUEST)
                
                # Asegurar que el tipo de usuario sea CLIENTE
                usuario_data['tipo'] = TipoUsuarioEnum.CLIENTE
                
                logger.info(f"Datos usuario: {usuario_data}")
                logger.info(f"Datos cliente: {cliente_data}")
                logger.info(f"Datos estado_chat: {estado_chat_data}")
                
                # 2. Crear Usuario
                usuario_serializer = UsuarioSerializer(data=usuario_data)
                if not usuario_serializer.is_valid():
                    logger.error(f"Error validando usuario: {usuario_serializer.errors}")
                    return Response({'error': 'Datos de usuario inválidos', 'detalles': usuario_serializer.errors}, 
                                  status=status.HTTP_400_BAD_REQUEST)
                
                usuario = usuario_serializer.save()
                logger.info(f"Usuario creado - ID: {usuario.id}, Nombre: {usuario.nombres} {usuario.apellidos}")
                
                # 3. Crear o actualizar EstadoChat si se proporciona
                estado_chat = None
                if estado_chat_data:
                    numero_whatsapp = estado_chat_data.get('numero_whatsapp')
                    estado_conversacion = estado_chat_data.get('estado_conversacion')
                    
                    if not numero_whatsapp:
                        return Response({'error': 'numero_whatsapp es requerido en estado_chat'}, 
                                      status=status.HTTP_400_BAD_REQUEST)
                    
                    # Verificar si ya existe un EstadoChat con ese número
                    try:
                        estado_chat = EstadoChat.objects.get(numero_whatsapp=numero_whatsapp)
                        # Si existe, actualizar solo el estado_conversacion
                        if estado_conversacion is not None:
                            estado_chat.estado_conversacion = estado_conversacion
                            estado_chat.save()
                        logger.info(f"EstadoChat actualizado - ID: {estado_chat.id}, WhatsApp: {estado_chat.numero_whatsapp}")
                    except EstadoChat.DoesNotExist:
                        # Si no existe, crear uno nuevo
                        estado_chat_serializer = EstadoChatSerializer(data=estado_chat_data)
                        if not estado_chat_serializer.is_valid():
                            logger.error(f"Error validando estado chat: {estado_chat_serializer.errors}")
                            return Response({'error': 'Datos de estado chat inválidos', 'detalles': estado_chat_serializer.errors}, 
                                          status=status.HTTP_400_BAD_REQUEST)
                        
                        estado_chat = estado_chat_serializer.save()
                        logger.info(f"EstadoChat creado - ID: {estado_chat.id}, WhatsApp: {estado_chat.numero_whatsapp}")
                
                # 4. Crear Cliente
                cliente_data_final = {
                    'usuario_id': usuario.id,
                    **cliente_data,  # Incluir todos los campos de cliente
                    'estado_chat_id': estado_chat.id if estado_chat else None
                }
                
                cliente_serializer = ClienteSerializer(data=cliente_data_final)
                if not cliente_serializer.is_valid():
                    logger.error(f"Error validando cliente: {cliente_serializer.errors}")
                    return Response({'error': 'Datos de cliente inválidos', 'detalles': cliente_serializer.errors}, 
                                  status=status.HTTP_400_BAD_REQUEST)
                
                cliente = cliente_serializer.save()
                logger.info(f"Cliente creado - ID: {cliente.id}")
                
                # 5. Retornar cliente en estructura flat (igual a la trama recibida)
                cliente_completo = Cliente.objects.select_related('usuario', 'estado_chat').get(id=cliente.id)
                
                # Construir respuesta en estructura flat
                response_data = {
                    'usuario_id': cliente_completo.usuario.id,  # ID para futuras actualizaciones
                    'nombres': cliente_completo.usuario.nombres,
                    'apellidos': cliente_completo.usuario.apellidos,
                    'tipo_documento': cliente_completo.usuario.tipo_documento,
                    'numero_documento': cliente_completo.usuario.numero_documento,
                    'email': cliente_completo.usuario.email,
                    'celular': cliente_completo.usuario.celular,
                    'edad': cliente_completo.edad,
                    'barrio': cliente_completo.barrio,
                    'colegio': cliente_completo.colegio,
                    'remitido_colegio': cliente_completo.remitido_colegio,
                    'nombre_acudiente': cliente_completo.nombre_acudiente,
                    'direccion': cliente_completo.direccion,
                }
                
                # Agregar estado_chat si existe
                if cliente_completo.estado_chat:
                    response_data['estado_chat'] = {
                        'numero_whatsapp': cliente_completo.estado_chat.numero_whatsapp,
                        'estado_conversacion': cliente_completo.estado_chat.estado_conversacion,
                    }
                
                logger.info("=== FIN - Cliente completo creado exitosamente ===")
                return Response(response_data, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            logger.error(f"Error creando cliente completo: {str(e)}")
            return Response({'error': 'Error interno del servidor', 'detalles': str(e)}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        """
        Actualizar cliente completo con usuario y estado de chat
        
        Estructura esperada del JSON (estructura flat - todos los campos opcionales):
        {
            "nombres": "Juan Carlos",
            "apellidos": "Pérez García",
            "email": "juan.nuevo@email.com",
            "celular": "3009876543",
            "edad": 26,
            "barrio": "Zona Norte",
            "colegio": "Nuevo Colegio",
            "remitido_colegio": true,
            "nombre_acudiente": "María García",
            "direccion": "Calle 123 #45-67",
            "estado_chat": {
                "estado_conversacion": {
                    "fase": "confirmacion_cita",
                    "step": "seleccion_horario"
                },
                "numero_whatsapp": "57123465798"
            }
        }
        """
        logger.info("=== INICIO - Actualizando cliente completo ===")
        
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data
        
        logger.info(f"Actualizando cliente ID: {instance.id}")
        logger.info(f"Datos recibidos: {data}")
        
        try:
            from django.db import transaction
            
            with transaction.atomic():
                # 1. Separar datos de Usuario y Cliente
                campos_usuario = ['nombres', 'apellidos', 'tipo_documento', 'numero_documento', 'email', 'celular']
                campos_cliente = ['edad', 'barrio', 'colegio', 'remitido_colegio', 'nombre_acudiente', 'direccion']
                
                usuario_data = {key: value for key, value in data.items() if key in campos_usuario}
                cliente_data = {key: value for key, value in data.items() if key in campos_cliente}
                estado_chat_data = data.get('estado_chat')
                
                logger.info(f"Datos usuario: {usuario_data}")
                logger.info(f"Datos cliente: {cliente_data}")
                logger.info(f"Datos estado_chat: {estado_chat_data}")
                
                # 2. Actualizar Usuario si hay datos
                if usuario_data:
                    usuario_serializer = UsuarioSerializer(
                        instance.usuario, 
                        data=usuario_data, 
                        partial=True
                    )
                    if not usuario_serializer.is_valid():
                        logger.error(f"Error validando usuario: {usuario_serializer.errors}")
                        return Response({
                            'error': 'Datos de usuario inválidos', 
                            'detalles': usuario_serializer.errors
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    usuario_serializer.save()
                    logger.info(f"Usuario actualizado - ID: {instance.usuario.id}")
                
                # 3. Actualizar datos del cliente si hay
                if cliente_data:
                    # Para campos que pueden ser null, permitir explícitamente valores None
                    # Esto permite que el bot envíe "colegio": null para limpiar el campo
                    cliente_serializer = ClienteSerializer(
                        instance, 
                        data=cliente_data, 
                        partial=True
                    )
                    if not cliente_serializer.is_valid():
                        logger.error(f"Error validando cliente: {cliente_serializer.errors}")
                        return Response({
                            'error': 'Datos de cliente inválidos', 
                            'detalles': cliente_serializer.errors
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    cliente_serializer.save()
                    logger.info(f"Cliente actualizado - ID: {instance.id}")
                    logger.info(f"Campos actualizados: {list(cliente_data.keys())}")
                
                # 4. Actualizar EstadoChat si se proporciona
                if 'estado_chat' in data:  # Verificar si el campo está presente en la trama
                    if estado_chat_data is None:
                        # Si estado_chat es null, eliminar la relación
                        if instance.estado_chat:
                            logger.info(f"Eliminando relación con EstadoChat - ID: {instance.estado_chat.id}")
                            instance.estado_chat = None
                            instance.save()
                            logger.info("Relación con EstadoChat eliminada")
                    else:
                        # Si estado_chat tiene datos, crear o actualizar
                        if instance.estado_chat:
                            # Actualizar estado chat existente
                            estado_chat_serializer = EstadoChatSerializer(
                                instance.estado_chat, 
                                data=estado_chat_data, 
                                partial=True
                            )
                            if not estado_chat_serializer.is_valid():
                                logger.error(f"Error validando estado chat: {estado_chat_serializer.errors}")
                                return Response({
                                    'error': 'Datos de estado chat inválidos', 
                                    'detalles': estado_chat_serializer.errors
                                }, status=status.HTTP_400_BAD_REQUEST)
                            
                            estado_chat_serializer.save()
                            logger.info(f"EstadoChat actualizado - ID: {instance.estado_chat.id}")
                        else:
                            # Crear nuevo estado chat si no existe
                            estado_chat_serializer = EstadoChatSerializer(data=estado_chat_data)
                            if not estado_chat_serializer.is_valid():
                                logger.error(f"Error validando nuevo estado chat: {estado_chat_serializer.errors}")
                                return Response({
                                    'error': 'Datos de estado chat inválidos', 
                                    'detalles': estado_chat_serializer.errors
                                }, status=status.HTTP_400_BAD_REQUEST)
                            
                            nuevo_estado_chat = estado_chat_serializer.save()
                            instance.estado_chat = nuevo_estado_chat
                            instance.save()
                            logger.info(f"Nuevo EstadoChat creado - ID: {nuevo_estado_chat.id}")
                
                # 5. Retornar cliente actualizado en estructura flat (igual a la trama recibida)
                cliente_actualizado = Cliente.objects.select_related('usuario', 'estado_chat').get(id=instance.id)
                
                # Construir respuesta en estructura flat
                response_data = {
                    'usuario_id': cliente_actualizado.usuario.id,  # ID para futuras actualizaciones
                    'nombres': cliente_actualizado.usuario.nombres,
                    'apellidos': cliente_actualizado.usuario.apellidos,
                    'tipo_documento': cliente_actualizado.usuario.tipo_documento,
                    'numero_documento': cliente_actualizado.usuario.numero_documento,
                    'email': cliente_actualizado.usuario.email,
                    'celular': cliente_actualizado.usuario.celular,
                    'edad': cliente_actualizado.edad,
                    'barrio': cliente_actualizado.barrio,
                    'colegio': cliente_actualizado.colegio,
                    'remitido_colegio': cliente_actualizado.remitido_colegio,
                    'nombre_acudiente': cliente_actualizado.nombre_acudiente,
                    'direccion': cliente_actualizado.direccion,
                }
                
                # Agregar estado_chat si existe
                if cliente_actualizado.estado_chat:
                    response_data['estado_chat'] = {
                        'numero_whatsapp': cliente_actualizado.estado_chat.numero_whatsapp,
                        'estado_conversacion': cliente_actualizado.estado_chat.estado_conversacion,
                    }
                
                logger.info("=== FIN - Cliente completo actualizado exitosamente ===")
                return Response({
                    'message': 'Cliente actualizado exitosamente',
                    'data': response_data
                })
                
        except Exception as e:
            logger.error(f"Error actualizando cliente completo: {str(e)}")
            return Response({
                'error': 'Error interno del servidor', 
                'detalles': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        description="Actualizar cliente por ID de usuario (enviado en JSON)",
        request=ClienteSerializer,
        responses={200: ClienteSerializer}
    )
    @action(detail=False, methods=['put', 'patch'], url_path='actualizar-por-usuario')
    def actualizar_por_usuario(self, request):
        """
        Actualizar cliente utilizando el ID del usuario enviado en el JSON
        
        Este endpoint permite al bot actualizar un cliente usando el ID del usuario
        enviado en el cuerpo de la petición, no en la URL.
        
        URL FIJA: /api/clientes/actualizar-por-usuario/
        
        Estructura esperada del JSON (estructura flat - todos los campos opcionales excepto usuario_id):
        {
            "usuario_id": 123,
            "nombres": "Juan Carlos",
            "apellidos": "Pérez García",
            "email": "juan.nuevo@email.com",
            "celular": "3009876543",
            "edad": 26,
            "barrio": "Zona Norte",
            "colegio": "Nuevo Colegio",
            "remitido_colegio": true,
            "nombre_acudiente": "María García",
            "direccion": "Calle 123 #45-67",
            "estado_chat": {
                "estado_conversacion": {
                    "fase": "confirmacion_cita",
                    "step": "seleccion_horario"
                },
                "numero_whatsapp": "57123465798"
            }
        }
        """
        logger.info("=== INICIO - Actualizando cliente por ID de usuario (desde JSON) ===")
        
        data = request.data
        usuario_id = data.get('usuario_id')
        
        logger.info(f"Datos recibidos: {data}")
        logger.info(f"Usuario ID extraído del JSON: {usuario_id}")
        
        if not usuario_id:
            return Response({
                'error': 'usuario_id es requerido en el JSON'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Buscar el usuario
            usuario = Usuario.objects.get(id=usuario_id)
            logger.info(f"Usuario encontrado - ID: {usuario.id}, Tipo: {usuario.tipo}")
            
            # Verificar que sea un cliente
            if usuario.tipo != TipoUsuarioEnum.CLIENTE:
                logger.warning(f"Tipo de usuario no válido para actualización: {usuario.tipo}")
                return Response({
                    'error': f'Solo se pueden actualizar usuarios de tipo CLIENTE. Tipo actual: {usuario.tipo}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Buscar el cliente relacionado
            try:
                cliente = Cliente.objects.select_related('usuario', 'estado_chat').get(usuario=usuario)
                logger.info(f"Cliente encontrado - ID: {cliente.id}")
            except Cliente.DoesNotExist:
                logger.error(f"No se encontró cliente para usuario ID: {usuario_id}")
                return Response({
                    'error': 'No se encontró registro de cliente para este usuario'
                }, status=status.HTTP_404_NOT_FOUND)
            
            from django.db import transaction
            
            with transaction.atomic():
                # 1. Separar datos de Usuario y Cliente (excluir usuario_id de los datos a procesar)
                campos_usuario = ['nombres', 'apellidos', 'tipo_documento', 'numero_documento', 'email', 'celular']
                campos_cliente = ['edad', 'barrio', 'colegio', 'remitido_colegio', 'nombre_acudiente', 'direccion']
                
                usuario_data = {key: value for key, value in data.items() if key in campos_usuario}
                cliente_data = {key: value for key, value in data.items() if key in campos_cliente}
                estado_chat_data = data.get('estado_chat')
                
                logger.info(f"Datos usuario: {usuario_data}")
                logger.info(f"Datos cliente: {cliente_data}")
                logger.info(f"Datos estado_chat: {estado_chat_data}")
                
                # 2. Actualizar Usuario si hay datos
                if usuario_data:
                    usuario_serializer = UsuarioSerializer(
                        usuario, 
                        data=usuario_data, 
                        partial=True
                    )
                    if not usuario_serializer.is_valid():
                        logger.error(f"Error validando usuario: {usuario_serializer.errors}")
                        return Response({
                            'error': 'Datos de usuario inválidos', 
                            'detalles': usuario_serializer.errors
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    usuario_serializer.save()
                    logger.info(f"Usuario actualizado - ID: {usuario.id}")
                
                # 3. Actualizar datos del cliente si hay
                if cliente_data:
                    # Para campos que pueden ser null, permitir explícitamente valores None
                    # Esto permite que el bot envíe "colegio": null para limpiar el campo
                    cliente_serializer = ClienteSerializer(
                        cliente, 
                        data=cliente_data, 
                        partial=True
                    )
                    if not cliente_serializer.is_valid():
                        logger.error(f"Error validando cliente: {cliente_serializer.errors}")
                        return Response({
                            'error': 'Datos de cliente inválidos', 
                            'detalles': cliente_serializer.errors
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    cliente_serializer.save()
                    logger.info(f"Cliente actualizado - ID: {cliente.id}")
                    logger.info(f"Campos actualizados: {list(cliente_data.keys())}")
                
                # 4. Actualizar EstadoChat si se proporciona
                if 'estado_chat' in data:  # Verificar si el campo está presente en la trama
                    if estado_chat_data is None:
                        # Si estado_chat es null, eliminar la relación
                        if cliente.estado_chat:
                            logger.info(f"Eliminando relación con EstadoChat - ID: {cliente.estado_chat.id}")
                            cliente.estado_chat = None
                            cliente.save()
                            logger.info("Relación con EstadoChat eliminada")
                    else:
                        # Si estado_chat tiene datos, crear o actualizar
                        if cliente.estado_chat:
                            # Actualizar estado chat existente
                            estado_chat_serializer = EstadoChatSerializer(
                                cliente.estado_chat, 
                                data=estado_chat_data, 
                                partial=True
                            )
                            if not estado_chat_serializer.is_valid():
                                logger.error(f"Error validando estado chat: {estado_chat_serializer.errors}")
                                return Response({
                                    'error': 'Datos de estado chat inválidos', 
                                    'detalles': estado_chat_serializer.errors
                                }, status=status.HTTP_400_BAD_REQUEST)
                            
                            estado_chat_serializer.save()
                            logger.info(f"EstadoChat actualizado - ID: {cliente.estado_chat.id}")
                        else:
                            # Crear nuevo estado chat si no existe
                            estado_chat_serializer = EstadoChatSerializer(data=estado_chat_data)
                            if not estado_chat_serializer.is_valid():
                                logger.error(f"Error validando nuevo estado chat: {estado_chat_serializer.errors}")
                                return Response({
                                    'error': 'Datos de estado chat inválidos', 
                                    'detalles': estado_chat_serializer.errors
                                }, status=status.HTTP_400_BAD_REQUEST)
                            
                            nuevo_estado_chat = estado_chat_serializer.save()
                            cliente.estado_chat = nuevo_estado_chat
                            cliente.save()
                            logger.info(f"Nuevo EstadoChat creado - ID: {nuevo_estado_chat.id}")
                
                # 5. Retornar cliente actualizado en estructura flat (igual a la trama recibida)
                cliente_actualizado = Cliente.objects.select_related('usuario', 'estado_chat').get(id=cliente.id)
                
                # Construir respuesta en estructura flat
                response_data = {
                    'usuario_id': cliente_actualizado.usuario.id,  # ID para futuras actualizaciones
                    'nombres': cliente_actualizado.usuario.nombres,
                    'apellidos': cliente_actualizado.usuario.apellidos,
                    'tipo_documento': cliente_actualizado.usuario.tipo_documento,
                    'numero_documento': cliente_actualizado.usuario.numero_documento,
                    'email': cliente_actualizado.usuario.email,
                    'celular': cliente_actualizado.usuario.celular,
                    'edad': cliente_actualizado.edad,
                    'barrio': cliente_actualizado.barrio,
                    'colegio': cliente_actualizado.colegio,
                    'remitido_colegio': cliente_actualizado.remitido_colegio,
                    'nombre_acudiente': cliente_actualizado.nombre_acudiente,
                    'direccion': cliente_actualizado.direccion,
                }
                
                # Agregar estado_chat si existe
                if cliente_actualizado.estado_chat:
                    response_data['estado_chat'] = {
                        'numero_whatsapp': cliente_actualizado.estado_chat.numero_whatsapp,
                        'estado_conversacion': cliente_actualizado.estado_chat.estado_conversacion,
                    }
                
                logger.info("=== FIN - Cliente actualizado exitosamente por ID de usuario (desde JSON) ===")
                return Response({
                    'message': 'Cliente actualizado exitosamente',
                    'data': response_data
                })
                
        except Usuario.DoesNotExist:
            logger.error(f"Usuario no encontrado con ID: {usuario_id}")
            return Response({
                'error': 'Usuario no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error actualizando cliente por ID de usuario: {str(e)}")
            return Response({
                'error': 'Error interno del servidor', 
                'detalles': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        description="Obtener citas de un cliente",
        responses={200: CitaListSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def citas(self, request, pk=None):
        """Obtener todas las citas de un cliente"""
        cliente = self.get_object()
        citas = Cita.objects.filter(cliente=cliente.usuario).select_related(
            'cliente', 'producto', 'profesional_asignado', 'estado_actual'
        )
        serializer = CitaListSerializer(citas, many=True)
        return Response(serializer.data)

    @extend_schema(
        description="Buscar cliente por número de documento (cédula)",
        responses={200: ClienteSerializer}
    )
    @action(detail=False, methods=['get'])
    def por_documento(self, request):
        """Buscar cliente por número de documento"""
        logger.info("=== INICIO - Endpoint por_documento llamado ===")
        
        numero_documento = request.query_params.get('numero_documento', None)
        logger.info(f"Parámetro recibido - numero_documento: {numero_documento}")
        
        if not numero_documento:
            logger.warning("Error: Parámetro numero_documento es requerido pero no fue proporcionado")
            return Response({'error': 'Parámetro numero_documento es requerido'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Buscar cliente por número de documento del usuario relacionado
            cliente = Cliente.objects.select_related('usuario', 'estado_chat').get(
                usuario__numero_documento=numero_documento
            )
            logger.info(f"Cliente encontrado - ID: {cliente.id}, Usuario: {cliente.usuario.nombres} {cliente.usuario.apellidos}")
            
            # Construir respuesta en estructura flat (igual que create/update)
            response_data = {
                'usuario_id': cliente.usuario.id,  # ID para futuras actualizaciones
                'nombres': cliente.usuario.nombres,
                'apellidos': cliente.usuario.apellidos,
                'tipo_documento': cliente.usuario.tipo_documento,
                'numero_documento': cliente.usuario.numero_documento,
                'email': cliente.usuario.email,
                'celular': cliente.usuario.celular,
                'edad': cliente.edad,
                'barrio': cliente.barrio,
                'colegio': cliente.colegio,
                'remitido_colegio': cliente.remitido_colegio,
                'nombre_acudiente': cliente.nombre_acudiente,
                'direccion': cliente.direccion,
            }
            
            # Agregar estado_chat si existe
            if cliente.estado_chat:
                response_data['estado_chat'] = {
                    'numero_whatsapp': cliente.estado_chat.numero_whatsapp,
                    'estado_conversacion': cliente.estado_chat.estado_conversacion,
                }
            
            logger.info("=== FIN - Cliente encontrado y retornado en estructura flat ===")
            return Response(response_data)
            
        except Cliente.DoesNotExist:
            logger.warning(f"Cliente no encontrado para numero_documento: {numero_documento}")
            return Response({'error': 'Cliente no encontrado con ese número de documento'}, 
                          status=status.HTTP_404_NOT_FOUND)


@extend_schema_view(
    list=extend_schema(description="Listar todos los productos"),
    create=extend_schema(description="Crear un nuevo producto"),
    retrieve=extend_schema(description="Obtener un producto específico"),
    update=extend_schema(description="Actualizar un producto"),
    partial_update=extend_schema(description="Actualizar parcialmente un producto"),
    destroy=extend_schema(description="Eliminar un producto")
)
class ProductoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar productos/servicios.
    
    Permite gestionar los diferentes productos o servicios
    que se pueden agendar en el sistema.
    """
    queryset = Producto.objects.all()
    permission_classes = [IsApiKeyOrAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['es_agendable_por_bot']
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'duracion_minutos']
    ordering = ['nombre']

    def get_serializer_class(self):
        """Usar serializador simplificado para listados"""
        if self.action == 'list':
            return ProductoListSerializer
        return ProductoSerializer

    def list(self, request, *args, **kwargs):
        """Listar productos con profesionales incluidos"""
        logger.info("=== INICIO - Listando productos con profesionales ===")
        
        queryset = self.filter_queryset(self.get_queryset())
        
        # Optimizar consulta para incluir profesionales
        queryset = queryset.prefetch_related('productoprofesional_set__profesional')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            logger.info(f"Productos paginados con profesionales - Items: {len(page)}")
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        logger.info(f"=== FIN - {len(serializer.data)} productos listados con profesionales ===")
        return Response(serializer.data)

    @extend_schema(
        description="Consultar producto por ID con profesionales (enviado en JSON)",
        request=ProductoSerializer,
        responses={200: ProductoSerializer}
    )
    @action(detail=False, methods=['post'], url_path='obtener-por-id')
    def obtener_por_id(self, request):
        """
        Consultar producto específico con profesionales usando ID enviado en el JSON
        
        Este endpoint permite al bot obtener un producto completo con su lista
        de profesionales relacionados usando el ID enviado en el cuerpo de la petición.
        
        URL FIJA: /api/productos/obtener-por-id/
        
        Estructura esperada del JSON:
        {
            "producto_id": 45
        }
        
        Respuesta exitosa:
        {
            "id": 45,
            "nombre": "Consulta General",
            "descripcion": "Consulta psicológica general",
            "es_agendable_por_bot": true,
            "duracion_minutos": 50,
            "profesionales": [
                {
                    "id": 2,
                    "nombres": "Dr. Juan",
                    "apellidos": "Pérez",
                    "cargo": "Psicólogo Clínico",
                    "numero_whatsapp": "573001234567"
                }
            ]
        }
        """
        logger.info("=== INICIO - Consultando producto por ID con profesionales (desde JSON) ===")
        
        data = request.data
        producto_id = data.get('producto_id')
        
        logger.info(f"Datos recibidos: {data}")
        logger.info(f"Producto ID extraído del JSON: {producto_id}")
        
        if not producto_id:
            return Response({
                'error': 'producto_id es requerido en el JSON'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Buscar el producto con optimización para profesionales
            producto = Producto.objects.prefetch_related(
                'productoprofesional_set__profesional'
            ).get(id=producto_id)
            
            logger.info(f"Producto encontrado - ID: {producto.id}, Nombre: {producto.nombre}")
            
            # Usar ProductoSerializer que incluye profesionales
            serializer = ProductoSerializer(producto)
            response_data = serializer.data
            
            logger.info(f"Profesionales incluidos: {len(response_data.get('profesionales', []))}")
            logger.info("=== FIN - Producto encontrado y retornado con profesionales ===")
            
            return Response(response_data)
            
        except Producto.DoesNotExist:
            logger.error(f"Producto no encontrado con ID: {producto_id}")
            return Response({
                'error': 'Producto no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error consultando producto por ID: {str(e)}")
            return Response({
                'error': 'Error interno del servidor',
                'detalles': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        description="Buscar productos por nombre o descripción con profesionales",
        responses={200: ProductoListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def buscar(self, request):
        """
        Buscar productos por nombre o descripción e incluir profesionales
        
        Parámetros:
        - q: Término de búsqueda (busca en nombre y descripción)
        - agendable_bot: true/false para filtrar solo productos agendables por bot
        """
        logger.info("=== INICIO - Búsqueda de productos con profesionales ===")
        
        query = request.query_params.get('q', '')
        agendable_bot = request.query_params.get('agendable_bot', '')
        
        logger.info(f"Parámetros - q: '{query}', agendable_bot: '{agendable_bot}'")
        
        if not query.strip():
            return Response({
                'error': 'Parámetro q (término de búsqueda) es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Construir filtros
        from django.db.models import Q
        filtros = Q(nombre__icontains=query) | Q(descripcion__icontains=query)
        
        if agendable_bot.lower() == 'true':
            filtros = filtros & Q(es_agendable_por_bot=True)
        elif agendable_bot.lower() == 'false':
            filtros = filtros & Q(es_agendable_por_bot=False)
        
        # Ejecutar búsqueda con profesionales incluidos
        productos = Producto.objects.filter(filtros).prefetch_related(
            'productoprofesional_set__profesional__usuario'
        ).order_by('nombre')
        
        logger.info(f"Productos encontrados: {productos.count()}")
        
        serializer = ProductoListSerializer(productos, many=True)
        
        logger.info("=== FIN - Búsqueda de productos completada con profesionales ===")
        return Response({
            'query': query,
            'total_encontrados': len(serializer.data),
            'productos': serializer.data
        })

    @extend_schema(
        description="Obtener productos agendables por bot con profesionales",
        responses={200: ProductoListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def agendables_bot(self, request):
        """Obtener solo productos agendables por bot con profesionales incluidos"""
        logger.info("=== INICIO - Obteniendo productos agendables por bot ===")
        
        productos = self.queryset.filter(es_agendable_por_bot=True).prefetch_related(
            'productoprofesional_set__profesional__usuario'
        ).order_by('nombre')
        
        serializer = ProductoListSerializer(productos, many=True)
        
        logger.info(f"=== FIN - {len(serializer.data)} productos agendables por bot encontrados ===")
        return Response({
            'total_agendables': len(serializer.data),
            'productos': serializer.data
        })

    @extend_schema(
        description="Obtener profesionales asignados a un producto",
        responses={200: ProfesionalSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def profesionales(self, request, pk=None):
        """Obtener profesionales asignados a un producto"""
        producto = self.get_object()
        profesionales = Profesional.objects.filter(
            productoprofesional__producto=producto
        ).select_related('usuario')
        serializer = ProfesionalSerializer(profesionales, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(description="Listar historial de estados de citas"),
    create=extend_schema(description="Crear un nuevo estado de cita"),
    retrieve=extend_schema(description="Obtener un estado específico"),
    update=extend_schema(description="Actualizar un estado"),
    partial_update=extend_schema(description="Actualizar parcialmente un estado"),
    destroy=extend_schema(description="Eliminar un estado")
)
class HistorialEstadoCitaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar el historial de estados de citas.
    
    Permite rastrear los diferentes estados por los que
    pasa una cita durante su ciclo de vida.
    """
    queryset = HistorialEstadoCita.objects.all()
    serializer_class = HistorialEstadoCitaSerializer
    permission_classes = [IsApiKeyOrAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['estado_cita']
    ordering_fields = ['fecha_registro']
    ordering = ['-fecha_registro']


@extend_schema_view(
    list=extend_schema(description="Listar todas las citas"),
    create=extend_schema(description="Crear una nueva cita"),
    retrieve=extend_schema(description="Obtener una cita específica"),
    update=extend_schema(description="Actualizar una cita"),
    partial_update=extend_schema(description="Actualizar parcialmente una cita"),
    destroy=extend_schema(description="Eliminar una cita")
)
class CitaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar citas.
    
    Permite operaciones CRUD completas sobre citas,
    incluyendo filtros por estado, fecha y profesional.
    """
    queryset = Cita.objects.select_related(
        'cliente', 'producto', 'profesional_asignado', 'estado_actual'
    ).all()
    permission_classes = [IsApiKeyOrAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['producto', 'profesional_asignado', 'estado_actual__estado_cita']
    search_fields = ['cliente__nombres', 'cliente__apellidos', 'observaciones']
    ordering_fields = ['fecha_hora_inicio', 'fecha_hora_fin']
    ordering = ['fecha_hora_inicio']

    def get_serializer_class(self):
        """Usar serializador simplificado para listados"""
        if self.action == 'list':
            return CitaListSerializer
        return CitaSerializer

    @extend_schema(
        description="Obtener citas por rango de fechas",
        responses={200: CitaListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def por_fecha(self, request):
        """
        Filtrar citas por rango de fechas
        
        Parámetros:
        - fecha_inicio: Fecha de inicio del rango (YYYY-MM-DD o YYYY-MM-DDTHH:MM:SS)
        - fecha_fin: Fecha de fin del rango (YYYY-MM-DD o YYYY-MM-DDTHH:MM:SS)
        
        Ambos parámetros filtran por la fecha de inicio de la cita.
        """
        logger.info("=== INICIO - Endpoint por_fecha llamado ===")
        
        fecha_inicio = request.query_params.get('fecha_inicio', None)
        fecha_fin = request.query_params.get('fecha_fin', None)
        
        logger.info(f"Parámetros recibidos - fecha_inicio: {fecha_inicio}, fecha_fin: {fecha_fin}")
        
        queryset = self.get_queryset()
        
        if fecha_inicio:
            logger.info(f"APLICANDO FILTRO fecha_inicio >= {fecha_inicio}")
            # Usar __date para comparar solo la fecha, sin hora
            queryset = queryset.filter(fecha_hora_inicio__date__gte=fecha_inicio)
            
        if fecha_fin:
            logger.info(f"APLICANDO FILTRO fecha_fin <= {fecha_fin}")
            # Usar __date para comparar solo la fecha, sin hora
            queryset = queryset.filter(fecha_hora_inicio__date__lte=fecha_fin)
        
        # Logging del SQL generado
        logger.debug(f"SQL Query generado: {queryset.query}")
        

        # Usar paginación como en el list normal
        page = self.paginate_queryset(queryset)
        if page is not None:
            logger.info(f"Aplicando paginación - Items en página actual: {len(page)}")
            serializer = CitaListSerializer(page, many=True)
            logger.info("=== FIN - Retornando resultados paginados ===")
            return self.get_paginated_response(serializer.data)
            
        serializer = CitaListSerializer(queryset, many=True)
        logger.info(f"=== FIN - Retornando todos los resultados ({len(serializer.data)} items) ===")
        return Response(serializer.data)

    @extend_schema(
        description="Obtener citas de hoy",
        responses={200: CitaListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def hoy(self, request):
        """Obtener citas de hoy"""
        from django.utils import timezone
        hoy = timezone.now().date()
        
        citas = self.get_queryset().filter(
            fecha_hora_inicio__date=hoy
        )
        serializer = CitaListSerializer(citas, many=True)
        return Response(serializer.data)

    @extend_schema(
        description="Cambiar estado de una cita",
        request=HistorialEstadoCitaSerializer,
        responses={200: CitaSerializer}
    )
    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        """
        Cambiar el estado de una cita y registrar automáticamente en historial
        
        Estructura del JSON esperado:
        {
            "estado_cita": "PRIMER_CONFIRMADO",
            "observaciones": "Cliente confirmó por WhatsApp"  // opcional
        }
        """
        logger.info("=== INICIO - Cambio de estado de cita ===")
        
        cita = self.get_object()
        nuevo_estado = request.data.get('estado_cita')
        observaciones = request.data.get('observaciones')
        
        logger.info(f"Cita ID: {cita.id}")
        logger.info(f"Estado actual: {cita.get_estado_actual_nombre()}")
        logger.info(f"Nuevo estado solicitado: {nuevo_estado}")
        logger.info(f"Observaciones: {observaciones}")
        
        if not nuevo_estado:
            return Response({
                'error': 'El campo estado_cita es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Usar el método del modelo para cambiar estado
            historial_creado = cita.cambiar_estado(
                nuevo_estado=nuevo_estado,
                observaciones_adicionales=observaciones
            )
            
            logger.info(f"Estado cambiado exitosamente a: {nuevo_estado}")
            logger.info(f"Historial creado - ID: {historial_creado.id}")
            
            # Retornar la cita actualizada
            serializer = self.get_serializer(cita)
            
            response_data = {
                'message': 'Estado de cita actualizado exitosamente',
                'estado_anterior': historial_creado.cita.historial_estados.exclude(
                    id=historial_creado.id
                ).last().estado_cita if historial_creado.cita.historial_estados.count() > 1 else None,
                'estado_actual': nuevo_estado,
                'fecha_cambio': historial_creado.fecha_registro,
                'cita': serializer.data
            }
            
            logger.info("=== FIN - Estado de cita actualizado exitosamente ===")
            return Response(response_data)
            
        except ValueError as e:
            logger.error(f"Error de validación: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error cambiando estado de cita: {str(e)}")
            return Response({
                'error': 'Error interno del servidor',
                'detalles': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        description="Obtener historial de estados de una cita",
        responses={200: HistorialEstadoCitaSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def historial_estados(self, request, pk=None):
        """Obtener todo el historial de estados de una cita específica"""
        logger.info("=== INICIO - Consulta historial de estados de cita ===")
        
        cita = self.get_object()
        logger.info(f"Cita ID: {cita.id}")
        
        # Obtener historial completo ordenado por fecha
        historial = cita.get_historial_completo()
        serializer = HistorialEstadoCitaSerializer(historial, many=True)
        
        logger.info(f"Historial encontrado: {len(serializer.data)} registros")
        logger.info("=== FIN - Historial de estados consultado ===")
        
        return Response({
            'cita_id': cita.id,
            'estado_actual': cita.get_estado_actual_nombre(),
            'total_cambios': len(serializer.data),
            'historial': serializer.data
        })

    @extend_schema(
        description="Actualizar cita por ID (enviado en JSON)",
        request=CitaSerializer,
        responses={200: CitaSerializer}
    )
    @action(detail=False, methods=['put', 'patch'], url_path='actualizar-por-id')
    def actualizar_por_id(self, request):
        """
        Actualizar cita utilizando el ID de la cita enviado en el JSON
        
        Este endpoint permite al bot actualizar una cita usando el ID de la cita
        enviado en el cuerpo de la petición, no en la URL.
        
        URL FIJA: /api/citas/actualizar-por-id/
        
        Estructura esperada del JSON (todos los campos opcionales excepto cita_id):
        {
            "cita_id": 123,
            "cliente_id": 456,
            "profesional_asignado_id": 789,
            "producto_id": 10,
            "fecha_hora_inicio": "25/12/2024 14:30",
            "fecha_hora_fin": "25/12/2024 15:30",
            "observaciones": "Cita reprogramada",
            "google_calendar_event_id": "evento_123",
            "google_calendar_url_event": "https://calendar.google.com/calendar/event?eid=abcd1234567890"
        }
        
        Validaciones automáticas:
        - cliente_id debe ser de tipo CLIENTE y tener perfil Cliente
        - profesional_asignado_id debe ser de tipo PROFESIONAL y tener perfil Profesional  
        - producto_id debe existir
        - Debe existir relación ProductoProfesional entre profesional y producto
        - Fechas en formato dd/mm/aaaa hh:mm
        """
        logger.info("=== INICIO - Actualizando cita por ID (desde JSON) ===")
        
        data = request.data
        cita_id = data.get('cita_id')
        
        logger.info(f"Datos recibidos: {data}")
        logger.info(f"Cita ID extraído del JSON: {cita_id}")
        
        if not cita_id:
            return Response({
                'error': 'cita_id es requerido en el JSON'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Buscar la cita
            cita = Cita.objects.select_related(
                'cliente', 'producto', 'profesional_asignado', 'estado_actual'
            ).get(id=cita_id)
            
            logger.info(f"Cita encontrada - ID: {cita.id}")
            logger.info(f"Cliente actual: {cita.cliente.nombres} {cita.cliente.apellidos}")
            logger.info(f"Producto actual: {cita.producto.nombre}")
            if cita.profesional_asignado:
                logger.info(f"Profesional actual: {cita.profesional_asignado.nombres} {cita.profesional_asignado.apellidos}")
            
            from django.db import transaction
            
            with transaction.atomic():
                # Excluir cita_id de los datos a procesar (no es un campo del modelo)
                update_data = {key: value for key, value in data.items() if key != 'cita_id'}
                
                logger.info(f"Datos para actualización: {update_data}")
                
                # Usar el serializador con validaciones completas
                partial = request.method == 'PATCH'
                serializer = CitaSerializer(
                    cita, 
                    data=update_data, 
                    partial=partial
                )
                
                if not serializer.is_valid():
                    logger.error(f"Errores de validación: {serializer.errors}")
                    return Response({
                        'error': 'Datos de cita inválidos',
                        'detalles': serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Guardar la cita actualizada
                cita_actualizada = serializer.save()
                
                logger.info(f"Cita actualizada exitosamente - ID: {cita_actualizada.id}")
                logger.info(f"Campos actualizados: {list(update_data.keys())}")
                
                # Retornar la cita actualizada con el formato mejorado
                response_serializer = CitaSerializer(cita_actualizada)
                
                logger.info("=== FIN - Cita actualizada exitosamente por ID (desde JSON) ===")
                return Response({
                    'message': 'Cita actualizada exitosamente',
                    'cita': response_serializer.data
                })
                
        except Cita.DoesNotExist:
            logger.error(f"Cita no encontrada con ID: {cita_id}")
            return Response({
                'error': 'Cita no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error actualizando cita por ID: {str(e)}")
            return Response({
                'error': 'Error interno del servidor',
                'detalles': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema_view(
    list=extend_schema(description="Listar relaciones producto-profesional"),
    create=extend_schema(description="Crear nueva relación producto-profesional"),
    retrieve=extend_schema(description="Obtener una relación específica"),
    update=extend_schema(description="Actualizar una relación"),
    partial_update=extend_schema(description="Actualizar parcialmente una relación"),
    destroy=extend_schema(description="Eliminar una relación")
)
class ProductoProfesionalViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar relaciones entre productos y profesionales.
    
    Permite definir qué profesionales pueden atender
    qué productos o servicios.
    """
    queryset = ProductoProfesional.objects.select_related(
        'producto', 'profesional__usuario'
    ).all()
    serializer_class = ProductoProfesionalSerializer
    permission_classes = [IsApiKeyOrAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['producto', 'profesional']

    @extend_schema(
        description="Obtener relaciones por producto",
        responses={200: ProductoProfesionalSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def por_producto(self, request):
        """Obtener todas las relaciones de un producto específico"""
        producto_id = request.query_params.get('producto_id', None)
        if not producto_id:
            return Response({'error': 'Parámetro producto_id es requerido'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        relaciones = self.get_queryset().filter(producto_id=producto_id)
        serializer = self.get_serializer(relaciones, many=True)
        return Response(serializer.data)

    @extend_schema(
        description="Obtener relaciones por profesional",
        responses={200: ProductoProfesionalSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def por_profesional(self, request):
        """Obtener todas las relaciones de un profesional específico"""
        profesional_id = request.query_params.get('profesional_id', None)
        if not profesional_id:
            return Response({'error': 'Parámetro profesional_id es requerido'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        relaciones = self.get_queryset().filter(profesional_id=profesional_id)
        serializer = self.get_serializer(relaciones, many=True)
        return Response(serializer.data)
