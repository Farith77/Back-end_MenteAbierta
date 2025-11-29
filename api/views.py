from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import DiarioEmocional
from .serializers import UsuarioRegistroSerializer, DiarioEmocionalSerializer
from .serializers import UsuarioRegistroSerializer, DiarioEmocionalSerializer, UsuarioPerfilSerializer
from .models import Cuestionario, RespuestaUsuario
from .serializers import CuestionarioDetailSerializer, RespuestaUsuarioSerializer
from .models import RegistroEmocion
from .serializers import RegistroEmocionSerializer
from .models import Ejercicio, EjercicioCompletado
from .serializers import EjercicioSerializer, EjercicioCompletadoSerializer
from .models import Publicacion, Comentario
from .serializers import PublicacionSerializer, ComentarioSerializer
from .models import Articulo
from .serializers import ArticuloSerializer
from rest_framework import filters
from .models import Tip
from .serializers import TipSerializer
from django.utils import timezone

# --- 1. VISTAS DE AUTENTICACIÓN (RF1, RF2) ---

class RegistroUsuarioView(generics.CreateAPIView):
    """
    Endpoint: POST /api/v1/auth/registro/
    Permite registrar un nuevo usuario (sin necesidad de autenticación previa).
    """
    serializer_class = UsuarioRegistroSerializer
    # Permite acceso a cualquiera, ya que es la vista de registro
    permission_classes = [permissions.AllowAny]
    
    # Sobrescribimos el método post para añadir la generación de tokens tras el registro.
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Llama al método create del serializador para crear y cifrar la contraseña
        user = serializer.save()
        
        # Generar tokens JWT para iniciar sesión inmediatamente
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "user": UsuarioRegistroSerializer(user).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


# --- 2. VISTAS DEL DIARIO EMOCIONAL (RF3) ---

class DiarioEmocionalListCreateView(generics.ListCreateAPIView):
    """
    Endpoint: GET /api/v1/diario/ (Lista las entradas)
    Endpoint: POST /api/v1/diario/ (Crea una nueva entrada)
    """
    serializer_class = DiarioEmocionalSerializer
    # Solo permite el acceso a usuarios que han iniciado sesión (autenticados)
    permission_classes = [permissions.IsAuthenticated]

    # Sobreescribe este método para asegurar que solo se muestren las entradas del usuario actual
    def get_queryset(self):
        # Filtra las entradas del diario para el usuario autenticado
        return DiarioEmocional.objects.filter(usuario=self.request.user)

    # Sobreescribe este método para asignar automáticamente el usuario que crea la entrada
    def perform_create(self, serializer):
        # Asigna el usuario autenticado (request.user) al campo 'usuario' del modelo
        serializer.save(usuario=self.request.user)


class DiarioEmocionalRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Endpoint: GET/PUT/DELETE /api/v1/diario/{id}/
    Permite ver, actualizar o eliminar una entrada específica.
    """
    serializer_class = DiarioEmocionalSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    # Usamos get_queryset para asegurar que un usuario solo pueda ver, actualizar 
    # o borrar sus propias entradas.
    def get_queryset(self):
        return DiarioEmocional.objects.filter(usuario=self.request.user)
        
        
class PerfilUsuarioView(generics.RetrieveAPIView):
    """
    Endpoint: GET /api/v1/perfil/me/
    Devuelve los datos del usuario autenticado.
    """
    serializer_class = UsuarioPerfilSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Devuelve el objeto Usuario asociado a la solicitud (gracias al token)
        return self.request.user
  
  
# --- VISTAS DE CUESTIONARIOS (RF4) ---
class CuestionarioListView(generics.ListAPIView):
    """
    GET /api/v1/cuestionarios/
    Lista los cuestionarios activos con sus preguntas.
    """
    queryset = Cuestionario.objects.filter(activo=True)
    serializer_class = CuestionarioDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

class RespuestaCreateView(generics.CreateAPIView):
    """
    POST /api/v1/cuestionarios/responder/
    Permite enviar una respuesta a una pregunta específica.
    """
    serializer_class = RespuestaUsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    
# --- VISTA PARA REGISTRO DE EMOCIONES (Módulo 3) ---
class RegistroEmocionCreateView(generics.CreateAPIView):
    """
    POST /api/v1/emociones/
    Permite registrar una emoción (Feliz, Triste, etc.)
    """
    queryset = RegistroEmocion.objects.all()
    serializer_class = RegistroEmocionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    
# --- VISTAS DE EJERCICIOS (RF7) ---
class EjercicioListView(generics.ListAPIView):
    """
    GET /api/v1/ejercicios/
    Lista todos los ejercicios disponibles (para llenar las tarjetas).
    """
    queryset = Ejercicio.objects.all()
    serializer_class = EjercicioSerializer
    permission_classes = [permissions.IsAuthenticated]

class MarcarEjercicioCompletadoView(generics.CreateAPIView):
    """
    POST /api/v1/ejercicios/completar/
    Registra que el usuario terminó un ejercicio.
    """
    serializer_class = EjercicioCompletadoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)
        
        
# --- VISTAS DEL FORO (RF6) --- 
class PublicacionListCreateView(generics.ListCreateAPIView):
    """
    GET /api/v1/foro/publicaciones/ (Listar con filtros)
    POST /api/v1/foro/publicaciones/ (Crear)
    """
    serializer_class = PublicacionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Publicacion.objects.all()
        # Filtro opcional por categoría: ?categoria=ANSIEDAD
        categoria = self.request.query_params.get('categoria')
        if categoria and categoria != 'TODOS':
            queryset = queryset.filter(categoria=categoria)
        return queryset

class PublicacionDetailView(generics.RetrieveDestroyAPIView):
    """
    GET /api/v1/foro/publicaciones/{id}/ (Ver detalle para comentar)
    DELETE /api/v1/foro/publicaciones/{id}/ (Borrar si es mía)
    """
    queryset = Publicacion.objects.all()
    serializer_class = PublicacionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    # Opcional: Asegurar que solo el dueño pueda borrar (requiere permisos custom, 
    # por ahora IsAuthenticated permite borrar a cualquiera si no restringimos más, 
    # pero para MVP lo dejamos simple o añadimos validación simple).
    def perform_destroy(self, instance):
        if instance.usuario == self.request.user:
            instance.delete()
        else:
            # En producción se debería lanzar un 403 Forbidden
            pass 

class ComentarPublicacionView(generics.CreateAPIView):
    """
    POST /api/v1/foro/publicaciones/{id}/comentar/
    """
    serializer_class = ComentarioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        publicacion_id = self.kwargs.get('pk')
        publicacion = Publicacion.objects.get(id=publicacion_id)
        serializer.save(usuario=self.request.user, publicacion=publicacion)

class ToggleLikeView(APIView):
    """
    POST /api/v1/foro/publicaciones/{id}/like/
    Alterna el like (si no tiene like, lo pone; si ya tiene, lo quita).
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            publicacion = Publicacion.objects.get(pk=pk)
            user = request.user
            if publicacion.likes.filter(id=user.id).exists():
                publicacion.likes.remove(user)
                liked = False
            else:
                publicacion.likes.add(user)
                liked = True
            return Response({'liked': liked, 'total_likes': publicacion.total_likes()})
        except Publicacion.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
            
            
# --- VISTA DE CONTENIDO PSICOEDUCATIVO (RF8) ---
class ArticuloListView(generics.ListAPIView):
    """
    GET /api/v1/contenido/articulos/
    Lista artículos con opción de búsqueda y filtro.
    Ejemplos:
    - ?search=ansiedad (Busca en título y resumen)
    - ?categoria=SUENO (Filtra por categoría)
    """
    queryset = Articulo.objects.all()
    serializer_class = ArticuloSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # Permitir lectura a todos (opcional) o solo auth
    
    # Configuración de búsqueda y filtrado
    filter_backends = [filters.SearchFilter]
    search_fields = ['titulo', 'resumen', 'categoria']

    def get_queryset(self):
        queryset = super().get_queryset()
        categoria = self.request.query_params.get('categoria')
        if categoria and categoria != 'TODOS':
            queryset = queryset.filter(categoria=categoria)
        return queryset

class ArticuloDetailView(generics.RetrieveAPIView):
    """
    GET /api/v1/contenido/articulos/{id}/
    Ver el contenido completo de un artículo.
    """
    queryset = Articulo.objects.all()
    serializer_class = ArticuloSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
# --- VISTAS DE TIPS (RF9) ---
class TipListView(generics.ListAPIView):
    """
    GET /api/v1/tips/
    Lista todos los tips con filtro por categoría.
    Ej: ?categoria=SUENO
    """
    queryset = Tip.objects.all()
    serializer_class = TipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        categoria = self.request.query_params.get('categoria')
        if categoria and categoria != 'TODOS':
            queryset = queryset.filter(categoria=categoria)
        return queryset

class TipDelDiaView(generics.RetrieveAPIView):
    """
    GET /api/v1/tips/dia/
    Devuelve UN solo tip basado en la fecha actual (rotación automática).
    """
    serializer_class = TipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # 1. Obtenemos todos los tips
        tips = Tip.objects.all()
        count = tips.count()
        
        if count == 0:
            return None # O manejar un 404
        
        # 2. Lógica matemática para rotar 
        # Usamos el día del año (1 a 365) para elegir el índice
        dia_actual = timezone.now().timetuple().tm_yday
        indice = dia_actual % count # Operación Módulo para ciclar si se acaban
        
        return tips[indice]