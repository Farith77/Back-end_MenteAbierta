from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegistroUsuarioView, 
    DiarioEmocionalListCreateView, 
    DiarioEmocionalRetrieveUpdateDestroyView,
    PerfilUsuarioView
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
]