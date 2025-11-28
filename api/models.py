from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
import uuid

# --- GESTOR DE USUARIOS ---
class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

# --- MODELO USUARIO (RF1) ---
class Usuario(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, max_length=255)
    seudonimo = models.CharField(max_length=150, unique=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True) # Agregado para el perfil

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

# --- MODELO DIARIO EMOCIONAL (RF3) ---
class DiarioEmocional(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='entradas_diario')
    fecha_entrada = models.DateTimeField(auto_now_add=True) # Cambiado a DateTimeField para mejor precisión
    # El contenido se guardará aquí. [cite_start]Según RF3, debe permitir notas[cite: 7].
    contenido = models.TextField()
    
    ESCALA_HUMOR = [
        (1, 'Muy Mal'), (2, 'Mal'), (3, 'Neutral'), (4, 'Bien'), (5, 'Muy Bien'),
    ]
    humor = models.IntegerField(choices=ESCALA_HUMOR, default=3)

    class Meta:
        ordering = ['-fecha_entrada']

# --- MODELO CUESTIONARIO (RF4) ---
class Cuestionario(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

# --- MODELO PREGUNTA (RF4) ---
class Pregunta(models.Model):
    cuestionario = models.ForeignKey(Cuestionario, on_delete=models.CASCADE, related_name='preguntas')
    texto = models.TextField()
    orden = models.IntegerField(default=1)

    class Meta:
        ordering = ['orden']
        unique_together = ('cuestionario', 'orden')

    def __str__(self):
        return f"{self.orden}. {self.texto}"

# --- MODELO RESPUESTA DE USUARIO (RF4) ---
class RespuestaUsuario(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='respuestas')
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE, related_name='respuestas')
    valor_respuesta = models.IntegerField()
    fecha_respuesta = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'pregunta', 'fecha_respuesta')