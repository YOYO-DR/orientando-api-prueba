from rest_framework import viewsets, status, filters, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view
from zoneinfo import ZoneInfo
import logging

# Logger específico para este módulo
logger = logging.getLogger(__name__)

from .models import (
    Usuario, EstadoChat, Profesional, Cliente, Producto,
    HistorialEstadoCita, Cita, ProductoProfesional,
    TipoUsuarioEnum
)
from .serializers import (
    UsuarioSerializer,
    EstadoChatSerializer,
    ProfesionalSerializer,
    ClienteSerializer,
    ProductoSerializer, ProductoListSerializer,
    HistorialEstadoCitaSerializer,
    CitaSerializer, CitaListSerializer
)
from .permissions import IsApiKeyOrAuthenticated

@extend_schema_view()
class EstadoChatViewSet(viewsets.GenericViewSet,mixins.CreateModelMixin):
    """
    ViewSet para gestionar estados de conversaciones WhatsApp.
    
    Permite gestionar el estado de las conversaciones de WhatsApp
    para cada número registrado.
    """
    queryset = EstadoChat.objects.all()
    serializer_class = EstadoChatSerializer
    permission_classes = [IsApiKeyOrAuthenticated]

    @extend_schema(
        description="Buscar estado por número de WhatsApp",
        responses={200: EstadoChatSerializer}
    )
    @action(detail=False, methods=['get'], url_path='por-numero')
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
    @action(detail=False, methods=['patch'], url_path='actualizar-por-numero')
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


@extend_schema_view()
class ProfesionalViewSet(viewsets.GenericViewSet):
    """
    ViewSet para gestionar profesionales.
    
    Maneja la información específica de los profesionales
    del sistema, incluyendo su cargo y número de WhatsApp.
    """
    queryset = Profesional.objects.select_related('usuario').all()
    serializer_class = ProfesionalSerializer
    permission_classes = [IsApiKeyOrAuthenticated]

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


@extend_schema_view()
class ClienteViewSet(viewsets.GenericViewSet):
    """
    ViewSet para gestionar clientes.
    
    Maneja la información específica de los clientes,
    incluyendo datos personales y de contacto.
    """
    queryset = Cliente.objects.select_related('usuario', 'estado_chat').all()
    serializer_class = ClienteSerializer
    permission_classes = [IsApiKeyOrAuthenticated]

    @extend_schema(
        description="Crear cliente completo con usuario y estado de chat en estructura flat",
        request={
            "application/json": {
                "example": {
                    "nombres": "Juan Carlos",
                    "apellidos": "Pérez García",
                    "tipo_documento": "CC",
                    "numero_documento": "12345678",
                    "email": "juan.nuevo@email.com",
                    "celular": "3009876543",
                    "edad": 26,
                    "barrio": "Zona Norte",
                    "colegio": "Nuevo Colegio",
                    "remitido_colegio": True,
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
            }
        },
        responses={
            201: {
                "description": "Cliente creado exitosamente",
                "content": {
                    "application/json": {
                        "example": {
                            "usuario_id": 123,
                            "nombres": "Juan Carlos",
                            "apellidos": "Pérez García",
                            "tipo_documento": "CC",
                            "numero_documento": "12345678",
                            "email": "juan.nuevo@email.com",
                            "celular": "3009876543",
                            "edad": 26,
                            "barrio": "Zona Norte",
                            "colegio": "Nuevo Colegio",
                            "remitido_colegio": True,
                            "nombre_acudiente": "María García",
                            "direccion": "Calle 123 #45-67",
                            "estado_chat": {
                                "numero_whatsapp": "57123465798",
                                "estado_conversacion": {
                                    "fase": "confirmacion_cita",
                                    "step": "seleccion_horario"
                                }
                            }
                        }
                    }
                }
            },
            400: {
                "description": "Datos inválidos",
                "content": {
                    "application/json": {
                        "example": {
                            "error": "Datos de usuario inválidos",
                            "detalles": {
                                "nombres": ["Este campo es requerido."]
                            }
                        }
                    }
                }
            }
        }
    )
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

    @extend_schema(
        description="Actualizar cliente por ID de usuario (enviado en JSON)",
        request=ClienteSerializer,
        responses={200: ClienteSerializer}
    )
    @action(detail=False, methods=['patch'], url_path='actualizar-por-usuario')
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
        description="Buscar cliente por número de documento (cédula)",
        responses={200: ClienteSerializer}
    )
    @action(detail=False, methods=['get'],url_path='por-documento')
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
)
class ProductoViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """
    ViewSet para gestionar productos/servicios.
    
    Permite gestionar los diferentes productos o servicios
    que se pueden agendar en el sistema.
    """
    queryset = Producto.objects.all()
    permission_classes = [IsApiKeyOrAuthenticated]

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
            "producto_id": 45,
            "nombre": "Consulta General",
            "descripcion": "Consulta psicológica general",
            "es_agendable_por_bot": true,
            "duracion_minutos": 50,
            "profesionales": [
                {
                    "profesional_id": 2,
                    "nombres": "Dr. Juan",
                    "apellidos": "Pérez",
                    "email": "juan.perez@orientando.com",
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

@extend_schema_view(
    create=extend_schema(description="Crear una nueva cita"),
)
class CitaViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    """
    ViewSet para gestionar citas.
    
    Permite operaciones CRUD completas sobre citas,
    incluyendo filtros por estado, fecha y profesional.
    """
    queryset = Cita.objects.select_related(
        'cliente', 'producto', 'profesional_asignado', 'estado_actual'
    ).all()
    permission_classes = [IsApiKeyOrAuthenticated]

    def get_serializer_class(self):
        """Usar serializador simplificado para listados"""
        if self.action == 'list':
            return CitaListSerializer
        return CitaSerializer

    @extend_schema(
        description="Obtener citas por rango de fechas",
        responses={200: CitaListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'],url_path='por-fecha')
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
        
        # Usar queryset optimizado que incluye el usuario del cliente para el número de documento
        queryset = Cita.objects.select_related(
            'cliente', 'producto', 'profesional_asignado', 'estado_actual'
        ).all()
        
        if fecha_inicio:
            logger.info(f"APLICANDO FILTRO fecha_inicio >= {fecha_inicio}")
            # Usar __date para comparar solo la fecha, sin hora
            queryset = queryset.filter(fecha_hora_inicio__date__gte=fecha_inicio)
            
        if fecha_fin:
            logger.info(f"APLICANDO FILTRO fecha_fin <= {fecha_fin}")
            # Usar __date para comparar solo la fecha, sin hora
            queryset = queryset.filter(fecha_hora_inicio__date__lte=fecha_fin)
        
        # Contar resultados antes de la paginación
        total_resultados = queryset.count()
        logger.info(f"Total de resultados encontrados: {total_resultados}")
        

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
        description="Obtener citas por rango de fechas con información completa",
        responses={200: {
            "description": "Lista de citas con información completa",
            "content": {
                "application/json": {
                    "example": {
                        "results": [
                            {
                                "cita": {
                                    "id": 123,
                                    "fecha_hora_inicio": "25/12/2024 14:30",
                                    "fecha_hora_fin": "25/12/2024 15:30",
                                    "observaciones": "Consulta psicológica",
                                    "google_calendar_event_id": "evento_123",
                                    "google_calendar_url_event": "https://calendar.google.com/event",
                                    "estado_actual": "Agendado"
                                },
                                "cliente": {
                                    "usuario_id": 456,
                                    "nombres": "Juan Carlos",
                                    "apellidos": "Pérez García",
                                    "numero_documento": "12345678",
                                    "email": "juan@email.com",
                                    "celular": "3001234567",
                                    "edad": 25,
                                    "barrio": "Centro",
                                    "direccion": "Calle 123 #45-67",
                                    "colegio": "Colegio ABC"
                                },
                                "profesional": {
                                    "profesional_id": 789,
                                    "nombres": "Dr. María Elena",
                                    "apellidos": "González",
                                    "email": "maria@orientando.com",
                                    "cargo": "Psicóloga Clínica",
                                    "numero_whatsapp": "3007654321"
                                },
                                "producto": {
                                    "producto_id": 10,
                                    "nombre": "Orientación Vocacional",
                                    "descripcion": "Proceso de orientación vocacional",
                                    "duracion_minutos": 60
                                }
                            }
                        ],
                        "count": 1
                    }
                }
            }
        }}
    )
    @action(detail=False, methods=['get'], url_path='por-fecha-completo')
    def por_fecha_completo(self, request):
        """
        Filtrar citas por rango de fechas con información completa de cita, cliente, profesional y producto
        
        Parámetros:
        - fecha_inicio: Fecha de inicio del rango (YYYY-MM-DD o YYYY-MM-DDTHH:MM:SS)
        - fecha_fin: Fecha de fin del rango (YYYY-MM-DD o YYYY-MM-DDTHH:MM:SS)
        
        Retorna información completa estructurada por separado para cada entidad.
        """
        logger.info("=== INICIO - Endpoint por_fecha_completo llamado ===")
        
        fecha_inicio = request.query_params.get('fecha_inicio', None)
        fecha_fin = request.query_params.get('fecha_fin', None)
        
        logger.info(f"Parámetros recibidos - fecha_inicio: {fecha_inicio}, fecha_fin: {fecha_fin}")
        
        # Usar queryset optimizado con todas las relaciones necesarias
        queryset = Cita.objects.select_related(
            'cliente', 'producto', 'profesional_asignado', 'estado_actual'
        ).all()
        
        if fecha_inicio:
            logger.info(f"APLICANDO FILTRO fecha_inicio >= {fecha_inicio}")
            queryset = queryset.filter(fecha_hora_inicio__date__gte=fecha_inicio)
            
        if fecha_fin:
            logger.info(f"APLICANDO FILTRO fecha_fin <= {fecha_fin}")
            queryset = queryset.filter(fecha_hora_inicio__date__lte=fecha_fin)
        
        total_resultados = queryset.count()
        logger.info(f"Total de resultados encontrados: {total_resultados}")
        
        # Aplicar paginación si está configurada
        page = self.paginate_queryset(queryset)
        citas_a_procesar = page if page is not None else queryset
        
        # Construir respuesta con información completa
        resultados = []
        
        for cita in citas_a_procesar:
            logger.info(f"Procesando cita ID: {cita.id}")
            
            # Información básica de la cita
            # Convertir fechas de UTC a zona horaria de Colombia (UTC-5)
            zona_colombia = ZoneInfo('America/Bogota')
            
            fecha_inicio_colombia = None
            if cita.fecha_hora_inicio:
                fecha_inicio_colombia = cita.fecha_hora_inicio.astimezone(zona_colombia).strftime('%d/%m/%Y %H:%M')
            
            fecha_fin_colombia = None
            if cita.fecha_hora_fin:
                fecha_fin_colombia = cita.fecha_hora_fin.astimezone(zona_colombia).strftime('%d/%m/%Y %H:%M')
            
            cita_data = {
                'id': cita.id,
                'fecha_hora_inicio': fecha_inicio_colombia,
                'fecha_hora_fin': fecha_fin_colombia,
                'observaciones': cita.observaciones,
                'google_calendar_event_id': cita.google_calendar_event_id,
                'google_calendar_url_event': cita.google_calendar_url_event,
                'estado_actual': cita.get_estado_actual_nombre() if hasattr(cita, 'get_estado_actual_nombre') else 'Sin estado'
            }
            
            # Información del cliente (Usuario que es cliente)
            cliente_data = None
            if cita.cliente:
                # Buscar el perfil Cliente asociado al Usuario
                try:
                    from .models import Cliente
                    cliente_perfil = Cliente.objects.select_related('usuario', 'estado_chat').get(usuario=cita.cliente)
                    cliente_data = {
                        'usuario_id': cita.cliente.id,
                        'nombres': cita.cliente.nombres,
                        'apellidos': cita.cliente.apellidos,
                        'tipo_documento': cita.cliente.tipo_documento,
                        'numero_documento': cita.cliente.numero_documento,
                        'email': cita.cliente.email,
                        'celular': cita.cliente.celular,
                        'edad': cliente_perfil.edad,
                        'barrio': cliente_perfil.barrio,
                        'direccion': cliente_perfil.direccion,
                        'nombre_acudiente': cliente_perfil.nombre_acudiente,
                        'remitido_colegio': cliente_perfil.remitido_colegio,
                        'colegio': cliente_perfil.colegio
                    }
                except Cliente.DoesNotExist:
                    logger.warning(f"No se encontró perfil Cliente para usuario ID: {cita.cliente.id}")
                    cliente_data = {
                        'usuario_id': cita.cliente.id,
                        'nombres': cita.cliente.nombres,
                        'apellidos': cita.cliente.apellidos,
                        'tipo_documento': cita.cliente.tipo_documento,
                        'numero_documento': cita.cliente.numero_documento,
                        'email': cita.cliente.email,
                        'celular': cita.cliente.celular,
                        'edad': None,
                        'barrio': None,
                        'direccion': None,
                        'nombre_acudiente': None,
                        'remitido_colegio': None,
                        'colegio': None
                    }
            
            # Información del profesional (Usuario que es profesional)
            profesional_data = None
            if cita.profesional_asignado:
                # Buscar el perfil Profesional asociado al Usuario
                try:
                    from .models import Profesional
                    profesional_perfil = Profesional.objects.select_related('usuario').get(usuario=cita.profesional_asignado)
                    profesional_data = {
                        'profesional_id': cita.profesional_asignado.id,
                        'nombres': cita.profesional_asignado.nombres,
                        'apellidos': cita.profesional_asignado.apellidos,
                        'tipo_documento': cita.profesional_asignado.tipo_documento,
                        'numero_documento': cita.profesional_asignado.numero_documento,
                        'email': cita.profesional_asignado.email,
                        'celular': cita.profesional_asignado.celular,
                        'cargo': profesional_perfil.cargo,
                        'numero_whatsapp': profesional_perfil.numero_whatsapp
                    }
                except Profesional.DoesNotExist:
                    logger.warning(f"No se encontró perfil Profesional para usuario ID: {cita.profesional_asignado.id}")
                    profesional_data = {
                        'profesional_id': cita.profesional_asignado.id,
                        'nombres': cita.profesional_asignado.nombres,
                        'apellidos': cita.profesional_asignado.apellidos,
                        'tipo_documento': cita.profesional_asignado.tipo_documento,
                        'numero_documento': cita.profesional_asignado.numero_documento,
                        'email': cita.profesional_asignado.email,
                        'celular': cita.profesional_asignado.celular,
                        'cargo': None,
                        'numero_whatsapp': None
                    }
            
            # Información del producto
            producto_data = None
            if cita.producto:
                producto_data = {
                    'producto_id': cita.producto.id,
                    'nombre': cita.producto.nombre,
                    'descripcion': cita.producto.descripcion,
                    'es_agendable_por_bot': cita.producto.es_agendable_por_bot,
                    'duracion_minutos': cita.producto.duracion_minutos
                }
            
            # Agregar al resultado
            resultado_cita = {
                'cita': cita_data,
                'cliente': cliente_data,
                'profesional': profesional_data,
                'producto': producto_data
            }
            
            resultados.append(resultado_cita)
        
        # Preparar respuesta
        if page is not None:
            logger.info(f"Aplicando paginación - Items en página actual: {len(resultados)}")
            response_data = {
                'results': resultados,
                'count': len(resultados)
            }
            logger.info("=== FIN - Retornando resultados paginados con información completa ===")
            return self.get_paginated_response(response_data)
        else:
            logger.info(f"=== FIN - Retornando todos los resultados con información completa ({len(resultados)} items) ===")
            return Response({
                'results': resultados,
                'count': len(resultados)
            })

    @extend_schema(
        description="Cambiar estado de una cita por ID (enviado en JSON)",
        request={
            "application/json": {
                "example": {
                    "cita_id": 123,
                    "cliente_id": 456,
                    "estado_cita": "PRIMER_CONFIRMADO",
                    "observaciones": "Cliente confirmó por WhatsApp"
                }
            }
        },
        responses={
            200: {
                "description": "Estado de cita cambiado exitosamente",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Estado de cita actualizado exitosamente",
                            "estado_anterior": "AGENDADO",
                            "estado_actual_variable": "PRIMER_CONFIRMADO",
                            "estado_actual_db": "Primer Confirmado",
                            "fecha_cambio": "2024-12-25T10:30:00Z",
                            "cita": {
                                "id": 123,
                                "cliente": {
                                    "id": 456,
                                    "nombres": "Juan Carlos",
                                    "apellidos": "Pérez García"
                                },
                                "estado_actual": "Primer Confirmado"
                            }
                        }
                    }
                }
            },
            400: {
                "description": "Datos inválidos",
                "content": {
                    "application/json": {
                        "example": {
                            "error": "estado_cita inválido. Estados válidos: ['AGENDADO', 'NOTIFICADO_PROFESIONAL', 'PENDIENTE_24H', 'PRIMER_CONFIRMADO', 'PENDIENTE_2H', 'SEGUNDO_CONFIRMADO', 'FINALIZADO']"
                        }
                    }
                }
            },
            404: {
                "description": "Cita no encontrada",
                "content": {
                    "application/json": {
                        "example": {
                            "error": "Cita no encontrada"
                        }
                    }
                }
            }
        }
    )
    @action(detail=False, methods=['post'], url_path='cambiar-estado-por-id')
    def cambiar_estado(self, request):
        """
        Cambiar el estado de una cita y registrar automáticamente en historial
        
        Este endpoint permite al bot cambiar el estado de una cita usando el ID de la cita
        enviado en el cuerpo de la petición, no en la URL.
        
        URL FIJA: /api/citas/cambiar-estado-por-id/
        
        Estructura esperada del JSON:
        {
            "cita_id": 123,
            "cliente_id": 456,
            "estado_cita": "PRIMER_CONFIRMADO",
            "observaciones": "Cliente confirmó por WhatsApp"  // opcional
        }
        
        Estados válidos (nombres de variables del enum):
        - AGENDADO
        - NOTIFICADO_PROFESIONAL  
        - PENDIENTE_24H
        - PRIMER_CONFIRMADO
        - PENDIENTE_2H
        - SEGUNDO_CONFIRMADO
        - FINALIZADO
        - CANCELADO
        
        Estos se convierten automáticamente a los valores de base de datos:
        - "Agendado", "Notificado Profesional", "Pendiente Primer Confirmación 24 Horas", "Cancelado", etc.
        """
        logger.info("=== INICIO - Cambio de estado de cita por ID (desde JSON) ===")
        
        # Mapeo de nombres de variables del enum a valores de base de datos
        from .models import EstadoCitaEnum
        estado_variable_to_db = {
            'AGENDADO': EstadoCitaEnum.AGENDADO.value,
            'NOTIFICADO_PROFESIONAL': EstadoCitaEnum.NOTIFICADO_PROFESIONAL.value,
            'PENDIENTE_24H': EstadoCitaEnum.PENDIENTE_24H.value,
            'PRIMER_CONFIRMADO': EstadoCitaEnum.PRIMER_CONFIRMADO.value,
            'PENDIENTE_2H': EstadoCitaEnum.PENDIENTE_2H.value,
            'SEGUNDO_CONFIRMADO': EstadoCitaEnum.SEGUNDO_CONFIRMADO.value,
            'FINALIZADO': EstadoCitaEnum.FINALIZADO.value,
            'CANCELADO': EstadoCitaEnum.CANCELADO.value,
        }
        
        data = request.data
        cita_id = data.get('cita_id')
        cliente_id = data.get('cliente_id')
        nuevo_estado_variable = data.get('estado_cita')
        observaciones = data.get('observaciones')
        
        logger.info(f"Datos recibidos: {data}")
        logger.info(f"Cita ID extraído del JSON: {cita_id}")
        logger.info(f"Cliente ID extraído del JSON: {cliente_id}")
        logger.info(f"Nuevo estado variable solicitado: {nuevo_estado_variable}")
        logger.info(f"Observaciones: {observaciones}")
        
        if not cita_id:
            return Response({
                'error': 'cita_id es requerido en el JSON'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not cliente_id:
            return Response({
                'error': 'cliente_id es requerido en el JSON'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not nuevo_estado_variable:
            return Response({
                'error': 'estado_cita es requerido en el JSON'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar que el estado variable sea válido y convertir a valor de DB
        if nuevo_estado_variable not in estado_variable_to_db:
            estados_validos = list(estado_variable_to_db.keys())
            logger.error(f"Estado variable inválido: {nuevo_estado_variable}")
            return Response({
                'error': f'estado_cita inválido. Estados válidos: {estados_validos}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Convertir el nombre de variable al valor de base de datos
        nuevo_estado_db = estado_variable_to_db[nuevo_estado_variable]
        logger.info(f"Estado convertido - Variable: {nuevo_estado_variable} -> DB: {nuevo_estado_db}")
        
        try:
            # Buscar la cita con validación de que pertenezca al cliente
            cita = Cita.objects.select_related(
                'cliente', 'producto', 'profesional_asignado', 'estado_actual'
            ).get(id=cita_id, cliente_id=cliente_id)
            
            logger.info(f"Cita encontrada - ID: {cita.id}")
            logger.info(f"Cliente: {cita.cliente.nombres} {cita.cliente.apellidos}")
            logger.info(f"Cliente ID verificado: {cita.cliente.id} == {cliente_id}")
            logger.info(f"Estado actual: {cita.get_estado_actual_nombre()}")
            
            # Usar el método del modelo para cambiar estado (usando valor de DB)
            historial_creado = cita.cambiar_estado(
                nuevo_estado=nuevo_estado_db,
                observaciones_adicionales=observaciones
            )
            
            logger.info(f"Estado cambiado exitosamente a: {nuevo_estado_db} (desde variable: {nuevo_estado_variable})")
            logger.info(f"Historial creado - ID: {historial_creado.id}")
            
            # Retornar la cita actualizada
            serializer = CitaSerializer(cita)
            
            response_data = {
                'message': 'Estado de cita actualizado exitosamente',
                'estado_anterior': historial_creado.cita.historial_estados.exclude(
                    id=historial_creado.id
                ).last().estado_cita if historial_creado.cita.historial_estados.count() > 1 else None,
                'estado_actual_variable': nuevo_estado_variable,  # Nombre de variable para el bot
                'estado_actual_db': nuevo_estado_db,  # Valor guardado en DB
                'fecha_cambio': historial_creado.fecha_registro,
                'cita': serializer.data
            }
            
            logger.info("=== FIN - Estado de cita actualizado exitosamente por ID (desde JSON) ===")
            return Response(response_data)
            
        except Cita.DoesNotExist:
            logger.error(f"Cita no encontrada con ID: {cita_id} para cliente ID: {cliente_id}")
            return Response({
                'error': 'Cita no encontrada o no pertenece al cliente especificado'
            }, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            logger.error(f"Error de validación: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error cambiando estado de cita por ID: {str(e)}")
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
    @action(detail=False, methods=['patch'], url_path='actualizar-por-id')
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

    @extend_schema(
        description="Consultar cita por ID (enviado en JSON)",
        request={
            "application/json": {
                "example": {
                    "cita_id": 123
                }
            }
        },
        responses={
            200: {
                "description": "Cita encontrada exitosamente",
                "content": {
                    "application/json": {
                        "example": {
                            "cita": {
                                "id": 123,
                                "cliente": {
                                    "id": 456,
                                    "nombres": "Juan Carlos",
                                    "apellidos": "Pérez García",
                                    "email": "juan@email.com",
                                    "celular": "3001234567"
                                },
                                "producto": {
                                    "producto_id": 10,
                                    "nombre": "Orientación Vocacional",
                                    "precio": 150000
                                },
                                "profesional_asignado": {
                                    "profesional_id": 789,
                                    "nombres": "María Elena",
                                    "apellidos": "González",
                                    "email": "maria@orientando.com"
                                },
                                "fecha_hora_inicio": "25/12/2024 14:30",
                                "fecha_hora_fin": "25/12/2024 15:30",
                                "observaciones": "Cita de orientación vocacional",
                                "google_calendar_event_id": "evento_123",
                                "google_calendar_url_event": "https://calendar.google.com/calendar/event?eid=abcd1234567890",
                                "estado_actual": "AGENDADO"
                            }
                        }
                    }
                }
            },
            400: {
                "description": "ID de cita no proporcionado",
                "content": {
                    "application/json": {
                        "example": {
                            "error": "cita_id es requerido en el JSON"
                        }
                    }
                }
            },
            404: {
                "description": "Cita no encontrada",
                "content": {
                    "application/json": {
                        "example": {
                            "error": "Cita no encontrada"
                        }
                    }
                }
            }
        }
    )
    @action(detail=False, methods=['post'], url_path='consultar-por-id')
    def consultar_por_id(self, request):
        """
        Consultar cita utilizando el ID de la cita enviado en el JSON
        
        Este endpoint permite al bot consultar una cita usando el ID de la cita
        enviado en el cuerpo de la petición, no en la URL.
        
        URL FIJA: /api/citas/consultar-por-id/
        
        Estructura esperada del JSON:
        {
            "cita_id": 123
        }
        
        Respuesta exitosa:
        {
            "cita": {
                "id": 123,
                "cliente": {...},
                "producto": {...},
                "profesional_asignado": {...},
                "fecha_hora_inicio": "25/12/2024 14:30",
                "fecha_hora_fin": "25/12/2024 15:30",
                "observaciones": "...",
                "google_calendar_event_id": "...",
                "google_calendar_url_event": "...",
                "estado_actual": "AGENDADO"
            }
        }
        """
        logger.info("=== INICIO - Consultando cita por ID (desde JSON) ===")
        
        data = request.data
        cita_id = data.get('cita_id')
        
        logger.info(f"Datos recibidos: {data}")
        logger.info(f"Cita ID extraído del JSON: {cita_id}")
        
        if not cita_id:
            return Response({
                'error': 'cita_id es requerido en el JSON'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Buscar la cita con todas las relaciones cargadas
            cita = Cita.objects.select_related(
                'cliente', 'producto', 'profesional_asignado', 'estado_actual'
            ).get(id=cita_id)
            
            logger.info(f"Cita encontrada - ID: {cita.id}")
            logger.info(f"Cliente: {cita.cliente.nombres} {cita.cliente.apellidos}")
            logger.info(f"Producto: {cita.producto.nombre}")
            if cita.profesional_asignado:
                logger.info(f"Profesional: {cita.profesional_asignado.nombres} {cita.profesional_asignado.apellidos}")
            logger.info(f"Estado actual: {cita.get_estado_actual_nombre()}")
            
            # Serializar la cita
            serializer = CitaSerializer(cita)
            
            logger.info("=== FIN - Cita consultada exitosamente por ID (desde JSON) ===")
            return Response({
                'cita': serializer.data
            })
                
        except Cita.DoesNotExist:
            logger.error(f"Cita no encontrada con ID: {cita_id}")
            return Response({
                'error': 'Cita no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error consultando cita por ID: {str(e)}")
            return Response({
                'error': 'Error interno del servidor',
                'detalles': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        description="Cancelar cita por ID (enviado en JSON)",
        request={
            "application/json": {
                "example": {
                    "cita_id": 123
                }
            }
        },
        responses={
            200: {
                "description": "Cita cancelada exitosamente",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Cita cancelada exitosamente",
                            "cita_cancelada": {
                                "id": 123,
                                "cliente": "Juan Carlos Pérez García",
                                "producto": "Orientación Vocacional",
                                "fecha_hora_inicio": "25/12/2024 14:30",
                                "fecha_hora_fin": "25/12/2024 15:30",
                                "estado_anterior": "AGENDADO",
                                "estado_actual": "CANCELADO"
                            }
                        }
                    }
                }
            },
            400: {
                "description": "ID de cita no proporcionado",
                "content": {
                    "application/json": {
                        "example": {
                            "error": "cita_id es requerido en el JSON"
                        }
                    }
                }
            },
            404: {
                "description": "Cita no encontrada",
                "content": {
                    "application/json": {
                        "example": {
                            "error": "Cita no encontrada"
                        }
                    }
                }
            }
        }
    )
    @action(detail=False, methods=['delete'], url_path='eliminar-por-id')
    def eliminar_por_id(self, request):
        """
        Cancelar cita utilizando el ID de la cita enviado en el JSON
        
        Este endpoint permite al bot cancelar una cita (cambiar estado a CANCELADO) 
        usando el ID de la cita enviado en el cuerpo de la petición, no en la URL.
        
        NOTA: La cita NO se elimina físicamente de la base de datos, 
        solo se cambia su estado a "CANCELADO" para mantener el historial.
        
        URL FIJA: /api/citas/eliminar-por-id/
        
        Estructura esperada del JSON:
        {
            "cita_id": 123
        }
        
        Respuesta exitosa:
        {
            "message": "Cita cancelada exitosamente",
            "cita_cancelada": {
                "id": 123,
                "cliente": "Juan Carlos Pérez García",
                "producto": "Orientación Vocacional",
                "fecha_hora_inicio": "25/12/2024 14:30",
                "fecha_hora_fin": "25/12/2024 15:30",
                "estado_anterior": "AGENDADO",
                "estado_actual": "CANCELADO"
            }
        }
        """
        logger.info("=== INICIO - Cancelando cita por ID (desde JSON) ===")
        
        data = request.data
        cita_id = data.get('cita_id')
        
        logger.info(f"Datos recibidos: {data}")
        logger.info(f"Cita ID extraído del JSON: {cita_id}")
        
        if not cita_id:
            return Response({
                'error': 'cita_id es requerido en el JSON'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Buscar la cita con todas las relaciones cargadas
            cita = Cita.objects.select_related(
                'cliente', 'producto', 'profesional_asignado', 'estado_actual'
            ).get(id=cita_id)
            
            logger.info(f"Cita encontrada para cancelar - ID: {cita.id}")
            logger.info(f"Cliente: {cita.cliente.nombres} {cita.cliente.apellidos}")
            logger.info(f"Producto: {cita.producto.nombre}")
            if cita.profesional_asignado:
                logger.info(f"Profesional: {cita.profesional_asignado.nombres} {cita.profesional_asignado.apellidos}")
            
            # Guardar estado anterior
            estado_anterior = cita.get_estado_actual_nombre()
            logger.info(f"Estado anterior: {estado_anterior}")
            
            # Verificar si la cita ya está cancelada
            from .models import EstadoCitaEnum
            if cita.get_estado_actual_nombre() == EstadoCitaEnum.CANCELADO.value:
                logger.warning(f"La cita ID {cita.id} ya está cancelada")
                return Response({
                    'error': 'La cita ya está cancelada',
                    'estado_actual': EstadoCitaEnum.CANCELADO.value
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Cambiar estado a CANCELADO usando transacción para asegurar consistencia
            from django.db import transaction
            
            with transaction.atomic():
                logger.info(f"Cambiando estado de cita ID {cita.id} a CANCELADO")
                
                # Usar el método del modelo para cambiar estado
                historial_creado = cita.cambiar_estado(
                    nuevo_estado=EstadoCitaEnum.CANCELADO.value,
                    observaciones_adicionales="Cita cancelada por solicitud"
                )
                
                logger.info(f"Estado cambiado exitosamente a CANCELADO")
                logger.info(f"Historial creado - ID: {historial_creado.id}")
            
            # Guardar información de la cita cancelada
            cita_info = {
                'id': cita.id,
                'cliente': f"{cita.cliente.nombres} {cita.cliente.apellidos}",
                'producto': cita.producto.nombre,
                'fecha_hora_inicio': cita.fecha_hora_inicio.strftime('%d/%m/%Y %H:%M') if cita.fecha_hora_inicio else None,
                'fecha_hora_fin': cita.fecha_hora_fin.strftime('%d/%m/%Y %H:%M') if cita.fecha_hora_fin else None,
                'estado_anterior': estado_anterior,
                'estado_actual': EstadoCitaEnum.CANCELADO.value,
                'google_calendar_event_id': cita.google_calendar_event_id,
                'google_calendar_url_event': cita.google_calendar_url_event
            }
            
            logger.info("=== FIN - Cita cancelada exitosamente por ID (desde JSON) ===")
            return Response({
                'message': 'Cita cancelada exitosamente',
                'cita_cancelada': cita_info
            })
                
        except Cita.DoesNotExist:
            logger.error(f"Cita no encontrada con ID: {cita_id}")
            return Response({
                'error': 'Cita no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            logger.error(f"Error de validación: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error cancelando cita por ID: {str(e)}")
            return Response({
                'error': 'Error interno del servidor',
                'detalles': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
