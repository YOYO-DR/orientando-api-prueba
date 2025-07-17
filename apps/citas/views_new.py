from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view

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
        """Filtrar citas por rango de fechas"""
        fecha_inicio = request.query_params.get('fecha_inicio', None)
        fecha_fin = request.query_params.get('fecha_fin', None)
        
        queryset = self.get_queryset()
        
        if fecha_inicio:
            queryset = queryset.filter(fecha_hora_inicio__gte=fecha_inicio)
        if fecha_fin:
            queryset = queryset.filter(fecha_hora_fin__lte=fecha_fin)
            
        serializer = CitaListSerializer(queryset, many=True)
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
