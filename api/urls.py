from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegistroUsuarioView, 
    DiarioEmocionalListCreateView, 
    DiarioEmocionalRetrieveUpdateDestroyView,
    PerfilUsuarioView,
    CuestionarioListView,
    RespuestaCreateView,
    RegistroEmocionCreateView,
    EjercicioListView,
    MarcarEjercicioCompletadoView,
    PublicacionListCreateView,
    PublicacionDetailView,
    ComentarPublicacionView,
    ToggleLikeView,
    ArticuloListView,
    ArticuloDetailView,
    TipListView,
    TipDelDiaView
)

urlpatterns = [
    # --- ENDPOINTS DE AUTENTICACIÓN (RF1, RF2) ---
    # 1. Registro de Usuario (POST /api/v1/auth/registro/)
    path('auth/registro/', RegistroUsuarioView.as_view(), name='registro'),
    
    # 2. Login (Generación de Tokens) (POST /api/v1/auth/login/)
    # Usamos la vista de simplejwt para el login estándar.
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # 3. Refrescar Token (POST /api/v1/auth/refresh/)
    # Permite obtener un nuevo token de acceso cuando el actual caduca.
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # --- ENDPOINTS DEL PERFIL ---
    path('user/me/', PerfilUsuarioView.as_view(), name='user-me'),

    # --- ENDPOINTS DEL DIARIO EMOCIONAL (RF3) ---
    # 4. Listar y Crear Entradas (GET, POST /api/v1/diario/)
    path('diario/', DiarioEmocionalListCreateView.as_view(), name='diario-list-create'),
    # 5. Detalle, Actualizar y Eliminar (GET, PUT, DELETE /api/v1/diario/{id}/)
    path('diario/<uuid:pk>/', DiarioEmocionalRetrieveUpdateDestroyView.as_view(), name='diario-detail'),
    # Nota sobre <uuid:pk>: indica que el parámetro de la URL es un UUID y se pasa como 'pk' a la vista.
    
    # --- ENDPOINTS DE CUESTIONARIOS ---
    path('cuestionarios/', CuestionarioListView.as_view(), name='cuestionario-list'),
    path('cuestionarios/responder/', RespuestaCreateView.as_view(), name='responder-pregunta'),
    
    # --- ENDPOINT DE EMOCIONES ---
    path('emociones/', RegistroEmocionCreateView.as_view(), name='registrar-emocion'),
    
    # --- ENDPOINTS DE EJERCICIOS ---
    path('ejercicios/', EjercicioListView.as_view(), name='lista-ejercicios'),
    path('ejercicios/completar/', MarcarEjercicioCompletadoView.as_view(), name='completar-ejercicio'),
    
    # --- ENDPOINTS DEL FORO ---
    path('foro/publicaciones/', PublicacionListCreateView.as_view(), name='foro-lista'),
    path('foro/publicaciones/<int:pk>/', PublicacionDetailView.as_view(), name='foro-detalle'),
    path('foro/publicaciones/<int:pk>/comentar/', ComentarPublicacionView.as_view(), name='foro-comentar'),
    path('foro/publicaciones/<int:pk>/like/', ToggleLikeView.as_view(), name='foro-like'),
    
    # --- ENDPOINTS DE CONTENIDO ---
    path('contenido/articulos/', ArticuloListView.as_view(), name='lista-articulos'),
    path('contenido/articulos/<int:pk>/', ArticuloDetailView.as_view(), name='detalle-articulo'),
    
    # --- ENDPOINTS DE TIPS ---
    path('tips/', TipListView.as_view(), name='lista-tips'),
    path('tips/dia/', TipDelDiaView.as_view(), name='tip-del-dia'),
]