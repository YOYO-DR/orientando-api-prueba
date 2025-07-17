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
    list=extend_schema(description="Listar todos los usuarios"),
    create=extend_schema(description="Crear un nuevo usuario"),
    retrieve=extend_schema(description="Obtener un usuario específico"),
    update=extend_schema(description="Actualizar un usuario"),
    partial_update=extend_schema(description="Actualizar parcialmente un usuario"),
    destroy=extend_schema(description="Eliminar un usuario")
)
class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar usuarios del sistema.
    
    Permite operaciones CRUD completas sobre usuarios.
    Incluye filtros por tipo de usuario y búsqueda por nombre.
    """
    queryset = Usuario.objects.all()
    permission_classes = [IsApiKeyOrAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tipo', 'tipo_documento']
    search_fields = ['nombres', 'apellidos', 'numero_documento', 'email']
    ordering_fields = ['nombres', 'apellidos', 'tipo']
    ordering = ['nombres']

    def get_serializer_class(self):
        """Usar serializador simplificado para listados"""
        if self.action == 'list':
            return UsuarioListSerializer
        return UsuarioSerializer

    @extend_schema(
        description="Obtener solo clientes",
        responses={200: UsuarioListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def clientes(self, request):
        """Obtener solo usuarios de tipo Cliente"""
        clientes = self.queryset.filter(tipo=TipoUsuarioEnum.CLIENTE)
        serializer = UsuarioListSerializer(clientes, many=True)
        return Response(serializer.data)

    @extend_schema(
        description="Obtener solo profesionales",
        responses={200: UsuarioListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def profesionales(self, request):
        """Obtener solo usuarios de tipo Profesional"""
        profesionales = self.queryset.filter(tipo=TipoUsuarioEnum.PROFESIONAL)
        serializer = UsuarioListSerializer(profesionales, many=True)
        return Response(serializer.data)


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
            "usuario": {
                "nombres": "Juan",
                "apellidos": "Pérez",
                "tipo_documento": "CC",
                "numero_documento": "12345678",
                "email": "juan@email.com",
                "telefono": "3001234567"
            },
            "edad": 25,
            "barrio": "Centro",
            "colegio": "Colegio Nacional",
            "remitido_colegio": true,
            "estado_chat": {
                "numero_whatsapp": "573001234567",
                "estado_conversacion": {
                    "fase": "recoleccion_datos",
                    "step": "datos_personales",
                    "datos_recolectados": {
                        "nombre": "Juan",
                        "documento": "12345678"
                    },
                    "contexto": "cliente_nuevo"
                }
            }
        }
        
        Respuesta exitosa:
        {
            "id": 123,  // ID del Usuario - usar este para actualizaciones
            "usuario": { ... },
            "edad": 25,
            "barrio": "Centro",
            // ... otros campos
            "message": "Cliente creado exitosamente"
        }
        """
        logger.info("=== INICIO - Creando cliente completo ===")
        
        data = request.data
        logger.info(f"Datos recibidos: {data}")
        
        try:
            from django.db import transaction
            
            with transaction.atomic():
                # 1. Crear Usuario
                usuario_data = data.get('usuario', {})
                if not usuario_data:
                    return Response({'error': 'Datos de usuario son requeridos'}, 
                                  status=status.HTTP_400_BAD_REQUEST)
                
                # Asegurar que el tipo de usuario sea CLIENTE
                usuario_data['tipo'] = TipoUsuarioEnum.CLIENTE
                
                usuario_serializer = UsuarioSerializer(data=usuario_data)
                if not usuario_serializer.is_valid():
                    logger.error(f"Error validando usuario: {usuario_serializer.errors}")
                    return Response({'error': 'Datos de usuario inválidos', 'detalles': usuario_serializer.errors}, 
                                  status=status.HTTP_400_BAD_REQUEST)
                
                usuario = usuario_serializer.save()
                logger.info(f"Usuario creado - ID: {usuario.id}, Nombre: {usuario.nombres} {usuario.apellidos}")
                
                # 2. Crear o actualizar EstadoChat si se proporciona
                estado_chat = None
                estado_chat_data = data.get('estado_chat')
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
                
                # 3. Crear Cliente
                cliente_data = {
                    'usuario_id': usuario.id,
                    'edad': data.get('edad'),
                    'barrio': data.get('barrio'),
                    'colegio': data.get('colegio'),
                    'remitido_colegio': data.get('remitido_colegio', False),
                    'estado_chat_id': estado_chat.id if estado_chat else None
                }
                
                cliente_serializer = ClienteSerializer(data=cliente_data)
                if not cliente_serializer.is_valid():
                    logger.error(f"Error validando cliente: {cliente_serializer.errors}")
                    return Response({'error': 'Datos de cliente inválidos', 'detalles': cliente_serializer.errors}, 
                                  status=status.HTTP_400_BAD_REQUEST)
                
                cliente = cliente_serializer.save()
                logger.info(f"Cliente creado - ID: {cliente.id}")
                
                # 4. Retornar cliente completo
                cliente_completo = Cliente.objects.select_related('usuario', 'estado_chat').get(id=cliente.id)
                response_serializer = ClienteSerializer(cliente_completo)
                
                logger.info("=== FIN - Cliente completo creado exitosamente ===")
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            logger.error(f"Error creando cliente completo: {str(e)}")
            return Response({'error': 'Error interno del servidor', 'detalles': str(e)}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        """
        Actualizar cliente completo con usuario y estado de chat
        
        Estructura esperada del JSON (todos los campos opcionales):
        {
            "usuario": {
                "nombres": "Juan Carlos",
                "apellidos": "Pérez García",
                "email": "juan.nuevo@email.com",
                "telefono": "3009876543"
            },
            "edad": 26,
            "barrio": "Zona Norte",
            "colegio": "Nuevo Colegio",
            "estado_chat": {
                "estado_conversacion": {
                    "fase": "confirmacion_cita",
                    "step": "seleccion_horario",
                    "datos_recolectados": {
                        "servicio": "orientacion_vocacional",
                        "fecha_preferida": "2025-07-20"
                    },
                    "contexto": "agendamiento_en_proceso"
                }
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
                # 1. Actualizar Usuario si se proporciona
                usuario_data = data.get('usuario')
                if usuario_data:
                    usuario_serializer = UsuarioSerializer(
                        instance.usuario, 
                        data=usuario_data, 
                        partial=True
                    )
                    if not usuario_serializer.is_valid():
                        logger.error(f"Error validando usuario: {usuario_serializer.errors}")
                        return Response({'error': 'Datos de usuario inválidos', 'detalles': usuario_serializer.errors}, 
                                      status=status.HTTP_400_BAD_REQUEST)
                    
                    usuario_serializer.save()
                    logger.info(f"Usuario actualizado - ID: {instance.usuario.id}")
                
                # 2. Actualizar EstadoChat si se proporciona
                estado_chat_data = data.get('estado_chat')
                if estado_chat_data:
                    if instance.estado_chat:
                        # Actualizar estado chat existente
                        estado_chat_serializer = EstadoChatSerializer(
                            instance.estado_chat, 
                            data=estado_chat_data, 
                            partial=True
                        )
                        if not estado_chat_serializer.is_valid():
                            logger.error(f"Error validando estado chat: {estado_chat_serializer.errors}")
                            return Response({'error': 'Datos de estado chat inválidos', 'detalles': estado_chat_serializer.errors}, 
                                          status=status.HTTP_400_BAD_REQUEST)
                        
                        estado_chat_serializer.save()
                        logger.info(f"EstadoChat actualizado - ID: {instance.estado_chat.id}")
                    else:
                        # Crear nuevo estado chat si no existe
                        estado_chat_serializer = EstadoChatSerializer(data=estado_chat_data)
                        if not estado_chat_serializer.is_valid():
                            logger.error(f"Error validando nuevo estado chat: {estado_chat_serializer.errors}")
                            return Response({'error': 'Datos de estado chat inválidos', 'detalles': estado_chat_serializer.errors}, 
                                          status=status.HTTP_400_BAD_REQUEST)
                        
                        nuevo_estado_chat = estado_chat_serializer.save()
                        instance.estado_chat = nuevo_estado_chat
                        instance.save()  # Guardar la instancia cliente con el nuevo estado_chat
                        logger.info(f"Nuevo EstadoChat creado - ID: {nuevo_estado_chat.id}")
                
                # 3. Actualizar Cliente
                cliente_data = {
                    key: value for key, value in data.items() 
                    if key not in ['usuario', 'estado_chat']
                }
                
                if cliente_data:
                    cliente_serializer = ClienteSerializer(
                        instance, 
                        data=cliente_data, 
                        partial=True
                    )
                    if not cliente_serializer.is_valid():
                        logger.error(f"Error validando cliente: {cliente_serializer.errors}")
                        return Response({'error': 'Datos de cliente inválidos', 'detalles': cliente_serializer.errors}, 
                                      status=status.HTTP_400_BAD_REQUEST)
                    
                    cliente_serializer.save()
                    logger.info(f"Cliente actualizado - ID: {instance.id}")
                
                # 4. Retornar cliente actualizado completo
                cliente_actualizado = Cliente.objects.select_related('usuario', 'estado_chat').get(id=instance.id)
                response_serializer = ClienteSerializer(cliente_actualizado)
                
                logger.info("=== FIN - Cliente completo actualizado exitosamente ===")
                return Response(response_serializer.data)
                
        except Exception as e:
            logger.error(f"Error actualizando cliente completo: {str(e)}")
            return Response({'error': 'Error interno del servidor', 'detalles': str(e)}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
            
            serializer = self.get_serializer(cliente)
            logger.info("=== FIN - Cliente encontrado y retornado ===")
            return Response(serializer.data)
            
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

    @extend_schema(
        description="Obtener productos agendables por bot",
        responses={200: ProductoListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def agendables_bot(self, request):
        """Obtener solo productos agendables por bot"""
        productos = self.queryset.filter(es_agendable_por_bot=True)
        serializer = ProductoListSerializer(productos, many=True)
        return Response(serializer.data)

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
        """Cambiar el estado de una cita"""
        cita = self.get_object()
        
        # Crear nuevo estado
        estado_serializer = HistorialEstadoCitaSerializer(data=request.data)
        if estado_serializer.is_valid():
            nuevo_estado = estado_serializer.save()
            cita.estado_actual = nuevo_estado
            cita.save()
            
            serializer = self.get_serializer(cita)
            return Response(serializer.data)
        
        return Response(estado_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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


@extend_schema_view(
    list=extend_schema(description="Listar todas las API Keys"),
    create=extend_schema(description="Crear una nueva API Key"),
    retrieve=extend_schema(description="Obtener una API Key específica"),
    update=extend_schema(description="Actualizar una API Key"),
    partial_update=extend_schema(description="Actualizar parcialmente una API Key"),
    destroy=extend_schema(description="Eliminar una API Key")
)
class ApiKeyViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar API Keys.
    
    Permite crear, listar y gestionar API Keys para chatbots
    y servicios externos.
    """
    queryset = ApiKey.objects.all()
    permission_classes = [IsAuthenticated]  # Solo usuarios autenticados pueden gestionar API Keys
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'last_used', 'usage_count']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Usar diferentes serializadores según la acción"""
        if self.action == 'create':
            return ApiKeyCreateSerializer
        elif self.action == 'list':
            return ApiKeyListSerializer
        return ApiKeySerializer

    @extend_schema(
        description="Regenerar una API Key existente",
        responses={200: ApiKeyCreateSerializer}
    )
    @action(detail=True, methods=['post'])
    def regenerate(self, request, pk=None):
        """Regenerar la key de una API Key existente"""
        api_key = self.get_object()
        
        # Generar nueva key
        api_key.key = ApiKey.generate_api_key()
        api_key.usage_count = 0
        api_key.last_used = None
        api_key.save()
        
        serializer = ApiKeyCreateSerializer(api_key)
        return Response(serializer.data)

    @extend_schema(
        description="Activar/desactivar una API Key",
        responses={200: ApiKeySerializer}
    )
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Activar o desactivar una API Key"""
        api_key = self.get_object()
        api_key.is_active = not api_key.is_active
        api_key.save()
        
        serializer = self.get_serializer(api_key)
        return Response(serializer.data)

    @extend_schema(description="Obtener estadísticas de uso de API Keys")
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Obtener estadísticas de uso de las API Keys"""
        from django.db.models import Sum
        
        total_keys = ApiKey.objects.count()
        active_keys = ApiKey.objects.filter(is_active=True).count()
        total_usage = ApiKey.objects.aggregate(Sum('usage_count'))['usage_count__sum'] or 0
        
        most_used = ApiKey.objects.filter(usage_count__gt=0).order_by('-usage_count').first()
        most_used_data = None
        if most_used:
            most_used_data = {
                'name': most_used.name,
                'usage_count': most_used.usage_count,
                'last_used': most_used.last_used
            }
        
        return Response({
            'total_keys': total_keys,
            'active_keys': active_keys,
            'total_usage': total_usage,
            'most_used': most_used_data
        })
