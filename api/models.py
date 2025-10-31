from django.db import models

# Usaremos AbstractBaseUser para controlar la autenticación.
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
import uuid

# --- GESTOR DE USUARIOS PERSONALIZADO ---
# Se requiere un Manager para manejar la creación de usuarios con nuestro modelo personalizado
class UsuarioManager(BaseUserManager):
    """
    Manager personalizado para manejar la creación de usuarios (se requiere email y contraseña)
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio para el registro.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


# --- MODELO USUARIO (RF1: Anónimos/Seudónimos) ---
class Usuario(AbstractBaseUser, PermissionsMixin):
    """
    Modelo de Usuario adaptado para MenteAbierta.
    Usa el email como identificador de inicio de sesión, pero permite un seudónimo público.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(
        verbose_name='Email de registro', 
        max_length=255, 
        unique=True
    )
    # RF1: Permite registrarse con un seudónimo
    seudonimo = models.CharField(
        max_length=150, 
        unique=True, 
        null=True, 
        blank=True,
        help_text="Nombre público en el foro, opcional."
    )
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()

    # Define el campo usado para el inicio de sesión
    USERNAME_FIELD = 'email'
    # Campos que se piden al crear un usuario (aparte del password)
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Usuario de MenteAbierta'
        verbose_name_plural = 'Usuarios de MenteAbierta'
        
    def __str__(self):
        return self.seudonimo if self.seudonimo else str(self.id)


# --- MODELO DIARIO EMOCIONAL (RF3) ---
class DiarioEmocional(models.Model):
    """
    Modelo para almacenar las entradas diarias de emociones y pensamientos de un usuario.
    """
    # Se relaciona con el usuario que creó la entrada
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='entradas_diario')
    
    # Campo para registrar la fecha de la entrada
    fecha_entrada = models.DateField(auto_now_add=True)
    
    # Texto principal del diario (entrada de texto libre)
    contenido = models.TextField()
    
    # Opcional: una escala simple de estado de ánimo (1=Muy mal, 5=Muy bien)
    ESCALA_HUMOR = [
        (1, 'Muy Mal'),
        (2, 'Mal'),
        (3, 'Neutral'),
        (4, 'Bien'),
        (5, 'Muy Bien'),
    ]
    humor = models.IntegerField(
        choices=ESCALA_HUMOR,
        default=3,
        help_text="Nivel de autopercepción emocional (1 a 5)."
    )

    class Meta:
        verbose_name = 'Entrada de Diario Emocional'
        verbose_name_plural = 'Entradas de Diario Emocional'
        # Asegura que las entradas se ordenen por fecha, de más reciente a más antigua
        ordering = ['-fecha_entrada'] 

    def __str__(self):
        return f"Diario de {self.usuario} - {self.fecha_entrada}"