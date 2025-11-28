from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import DiarioEmocional
from .serializers import UsuarioRegistroSerializer, DiarioEmocionalSerializer
from .serializers import UsuarioRegistroSerializer, DiarioEmocionalSerializer, UsuarioPerfilSerializer # Importa el nuevo serializador

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