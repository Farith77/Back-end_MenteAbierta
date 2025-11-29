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

# --- MODELO DIARIO EMOCIONAL (Actualizado) ---
class DiarioEmocional(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='entradas_diario')
    # NUEVO CAMPO: Título para la tarjeta en el listado
    titulo = models.CharField(max_length=200, default="Sin título") 
    fecha_entrada = models.DateTimeField(auto_now_add=True)
    contenido = models.TextField()
    
    ESCALA_HUMOR = [
        (1, 'Muy Mal'), (2, 'Mal'), (3, 'Neutral'), (4, 'Bien'), (5, 'Muy Bien'),
    ]
    humor = models.IntegerField(choices=ESCALA_HUMOR, default=3)

    class Meta:
        ordering = ['-fecha_entrada']
        
        
# --- MODELO CUESTIONARIO (Actualizado) ---
class Cuestionario(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    # NUEVO CAMPO: Para mostrar "1 min" o "5-7 min" en la tarjeta
    tiempo_estimado = models.CharField(max_length=50, default="5 min")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre
        

# --- MODELO PREGUNTA (Actualizado) ---
class Pregunta(models.Model):
    # Tipos de pregunta para que el Frontend sepa qué componente renderizar
    TIPOS_PREGUNTA = [
        ('ESCALA', 'Escala 1-10 (Slider)'),
        ('SELECCION', 'Selección Única (Botones)'),
        ('BOOLEAN', 'Sí/No'),
        ('TEXTO', 'Texto Libre'),
    ]

    cuestionario = models.ForeignKey(Cuestionario, on_delete=models.CASCADE, related_name='preguntas')
    texto = models.TextField()
    # NUEVO CAMPO: Tipo de visualización
    tipo_pregunta = models.CharField(max_length=20, choices=TIPOS_PREGUNTA, default='SELECCION')
    orden = models.IntegerField(default=1)

    class Meta:
        ordering = ['orden']
        unique_together = ('cuestionario', 'orden')

    def __str__(self):
        return f"{self.orden}. {self.texto} ({self.tipo_pregunta})"

# --- MODELO RESPUESTA DE USUARIO (RF4) ---
class RespuestaUsuario(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='respuestas')
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE, related_name='respuestas')
    valor_respuesta = models.IntegerField()
    fecha_respuesta = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'pregunta', 'fecha_respuesta')
        
        
# --- MÓDULO 3: REGISTRO DE EMOCIONES ---
class RegistroEmocion(models.Model):
    """
    Registra el estado emocional del usuario basado en categorías predefinidas.
    """
    # Opciones exactas basadas en tu diseño UI
    OPCIONES_EMOCION = [
        ('FELIZ', 'Feliz'),
        ('TRANQUILO', 'Tranquilo'),
        ('NEUTRAL', 'Neutral'),
        ('ANSIOSO', 'Ansioso'),
        ('TRISTE', 'Triste'),
        ('ENOJADO', 'Enojado'),
    ]

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='registros_emocionales')
    emocion = models.CharField(max_length=20, choices=OPCIONES_EMOCION)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    # El documento menciona intensidad y nota opcional[cite: 243, 256].
    # Agregamos 'nota' por si en el futuro el diseño lo incluye, 
    # aunque en la imagen actual no se ve input de texto.
    nota = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-fecha_registro']
        verbose_name = "Registro de Emoción"
        verbose_name_plural = "Registros de Emociones"

    def __str__(self):
        return f"{self.usuario.email} - {self.emocion} ({self.fecha_registro.strftime('%Y-%m-%d')})"
        
        
# --- MÓDULO 7: EJERCICIOS DE AUTOCUIDADO ---
class Ejercicio(models.Model):
    # Categorías basadas en la imagen del Frontend
    CATEGORIAS = [
        ('RESPIRACION', 'Respiración'),
        ('RELAJACION', 'Relajación'),
        ('MINDFULNESS', 'Mindfulness'),
        ('MOVIMIENTO', 'Movimiento'),
    ]

    # Tipos de icono para que el frontend sepa qué SVG mostrar (Viento, Corazón, Luna, etc.)
    TIPOS_ICONO = [
        ('VIENTO', 'Viento (Respiración)'),
        ('CORAZON', 'Corazón (Relajación)'),
        ('LUNA', 'Luna (Noche/Mindfulness)'),
        ('SOL', 'Sol (Día/Gratitud)'),
    ]

    titulo = models.CharField(max_length=200)
    descripcion = models.CharField(max_length=300, help_text="Descripción corta para la tarjeta")
    categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    icono = models.CharField(max_length=20, choices=TIPOS_ICONO, default='VIENTO')
    
    # Duración en minutos (ej: 5, 10, 15)
    duracion = models.IntegerField(help_text="Duración en minutos")
    
    # Contenido detallado (instrucciones paso a paso)
    instrucciones = models.TextField()
    
    # Opcional: URL de un archivo de audio o video (ej: link de YouTube o archivo estático)
    media_url = models.URLField(blank=True, null=True)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titulo} ({self.categoria})"

# --- MODELO PARA TRACKING (Historial de ejercicios realizados) ---
class EjercicioCompletado(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='ejercicios_completados')
    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE)
    fecha_completado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_completado']

    def __str__(self):
        return f"{self.usuario.email} completó {self.ejercicio.titulo}"
        
       
# --- MÓDULO 10: FORO COMUNITARIO ---       
class Publicacion(models.Model):
    CATEGORIAS_FORO = [
        ('ANSIEDAD', 'Ansiedad'),
        ('BIENESTAR', 'Bienestar'),
        ('RELACIONES', 'Relaciones'),
        ('ESTRES', 'Estrés'),
        ('GENERAL', 'General'),
    ]

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='publicaciones')
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    categoria = models.CharField(max_length=20, choices=CATEGORIAS_FORO, default='GENERAL')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    # Sistema de Likes (Muchos usuarios pueden dar like a muchas publicaciones)
    likes = models.ManyToManyField(Usuario, related_name='publicaciones_likeadas', blank=True)

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.titulo} - {self.usuario.email}"

    # Métodos auxiliares para contar interacciones
    def total_likes(self):
        return self.likes.count()

    def total_comentarios(self):
        return self.comentarios.count()


class Comentario(models.Model):
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE, related_name='comentarios')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='comentarios_foro')
    contenido = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['fecha_creacion'] # Los comentarios más viejos primero (cronológico)

    def __str__(self):
        return f"Comentario de {self.usuario.email} en {self.publicacion.titulo}"
        
        
# --- MÓDULO 8: CONTENIDO PSICOEDUCATIVO ---
class Articulo(models.Model):
    CATEGORIAS_ARTICULO = [
        ('ANSIEDAD', 'Ansiedad'),
        ('ESTRES', 'Estrés'),
        ('SUENO', 'Sueño'),
        ('RELACIONES', 'Relaciones'),
        ('AUTOCUIDADO', 'Autocuidado'),
        ('GENERAL', 'General'),
    ]

    titulo = models.CharField(max_length=200)
    # Resumen para mostrar en la tarjeta (antes de entrar a leer)
    resumen = models.TextField(max_length=300, help_text="Breve descripción para la tarjeta")
    # Contenido completo del artículo (puede ser texto largo o HTML simple)
    contenido = models.TextField()
    
    categoria = models.CharField(max_length=20, choices=CATEGORIAS_ARTICULO, default='GENERAL')
    
    # URL de la imagen de portada (puede ser externa o local)
    imagen_url = models.URLField(blank=True, null=True, help_text="URL de la imagen de portada")
    
    # Tiempo de lectura estimado (ej: "8 min")
    tiempo_lectura = models.CharField(max_length=20, default="5 min")
    
    fecha_publicacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_publicacion']
        verbose_name = "Artículo Psicoeducativo"
        verbose_name_plural = "Artículos Psicoeducativos"

    def __str__(self):
        return self.titulo
        
        
# --- MÓDULO 9: TIPS DIARIOS ---
class Tip(models.Model):
    CATEGORIAS_TIP = [
        ('DIARIO', 'Diario'),
        ('ESTRES', 'Estrés'),
        ('SUENO', 'Sueño'),
        ('BIENESTAR', 'Bienestar'),
    ]

    titulo = models.CharField(max_length=200)
    contenido = models.TextField(help_text="Consejo breve (máx 2-3 líneas)")
    categoria = models.CharField(max_length=20, choices=CATEGORIAS_TIP, default='BIENESTAR')
    
    # Campo opcional por si queremos destacar manualmente alguno, 
    # aunque la lógica automática usará la fecha.
    es_destacado = models.BooleanField(default=False)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Tip de Bienestar"
        verbose_name_plural = "Tips de Bienestar"

    def __str__(self):
        return f"{self.titulo} ({self.categoria})"