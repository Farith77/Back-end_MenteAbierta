from rest_framework import serializers
from .models import Usuario, DiarioEmocional
from .models import Cuestionario, Pregunta, RespuestaUsuario
from .models import RegistroEmocion
from .models import Ejercicio, EjercicioCompletado
from .models import Publicacion, Comentario
from .models import Articulo
from .models import Tip

# --- SERIALIZADOR PARA REGISTRO Y LOGIN (Usuario) ---
class UsuarioRegistroSerializer(serializers.ModelSerializer):
    """
    Serializador para el registro de nuevos usuarios.
    """
    class Meta:
        model = Usuario
        # Solo necesitamos el email, la contraseña y el seudónimo
        fields = ('email', 'password', 'seudonimo')
        extra_kwargs = {
            # La contraseña solo debe poder ser escrita, no leída de vuelta
            'password': {'write_only': True},
            # El seudónimo es opcional
            'seudonimo': {'required': False},
        }

    def create(self, validated_data):
        # DRF usa este método para crear el objeto. Es crucial usar create_user 
        # para que la contraseña se encripte correctamente.
        user = Usuario.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            seudonimo=validated_data.get('seudonimo')
        )
        return user


# --- SERIALIZADOR PARA ENTRADAS DE DIARIO (RF3) ---
class DiarioEmocionalSerializer(serializers.ModelSerializer):
    """
    Serializador para crear, ver y actualizar entradas de diario.
    """
    # Campo de solo lectura para mostrar el seudónimo del creador
    usuario_seudonimo = serializers.CharField(source='usuario.seudonimo', read_only=True)
    
    class Meta:
        model = DiarioEmocional
        fields = ('id', 'usuario', 'usuario_seudonimo', 'fecha_entrada', 'contenido', 'humor')
        read_only_fields = ('usuario', 'fecha_entrada') # El usuario se asigna automáticamente
  
  
class UsuarioPerfilSerializer(serializers.ModelSerializer):
    """
    Serializador para mostrar datos de perfil (email y alias/seudónimo).
    """
    class Meta:
        model = Usuario
        # Solo expone los campos necesarios para el perfil
        fields = ('id', 'email', 'seudonimo', 'is_active', 'date_joined')
        read_only_fields = ('id', 'email', 'is_active', 'date_joined')
      
      
class PreguntaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pregunta
        fields = ['id', 'texto', 'orden']

class CuestionarioDetailSerializer(serializers.ModelSerializer):
    """Muestra el cuestionario con sus preguntas anidadas"""
    preguntas = PreguntaSerializer(many=True, read_only=True)

    class Meta:
        model = Cuestionario
        fields = ['id', 'nombre', 'descripcion', 'preguntas']

class RespuestaUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = RespuestaUsuario
        fields = ['id', 'pregunta', 'valor_respuesta', 'fecha_respuesta']
        read_only_fields = ['usuario', 'fecha_respuesta']

    def create(self, validated_data):
        # Asigna el usuario autenticado automáticamente
        validated_data['usuario'] = self.context['request'].user
        return super().create(validated_data)
        
        
class RegistroEmocionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistroEmocion
        # ACTUALIZADO: Agregamos 'intensidad' y 'nota'
        fields = ['id', 'usuario', 'emocion', 'intensidad', 'nota', 'fecha_registro'] 
        read_only_fields = ['id', 'usuario', 'fecha_registro'] 

    def create(self, validated_data):
        # Asigna el usuario autenticado automáticamente al guardar
        validated_data['usuario'] = self.context['request'].user
        return super().create(validated_data)
        
class EjercicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ejercicio
        fields = ['id', 'titulo', 'descripcion', 'categoria', 'icono', 'duracion', 'instrucciones', 'media_url']

class EjercicioCompletadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EjercicioCompletado
        fields = ['id', 'ejercicio', 'fecha_completado']
        read_only_fields = ['fecha_completado']
        
        
class ComentarioSerializer(serializers.ModelSerializer):
    autor_seudonimo = serializers.CharField(source='usuario.seudonimo', read_only=True)
    
    class Meta:
        model = Comentario
        fields = ['id', 'autor_seudonimo', 'contenido', 'fecha_creacion']
        read_only_fields = ['fecha_creacion']

class PublicacionSerializer(serializers.ModelSerializer):
    autor_seudonimo = serializers.CharField(source='usuario.seudonimo', read_only=True)
    num_likes = serializers.SerializerMethodField()
    num_comentarios = serializers.SerializerMethodField()
    ya_di_like = serializers.SerializerMethodField() # Para saber si pintar el corazón de color

    class Meta:
        model = Publicacion
        fields = [
            'id', 'autor_seudonimo', 'titulo', 'contenido', 
            'categoria', 'fecha_creacion', 
            'num_likes', 'num_comentarios', 'ya_di_like'
        ]
        read_only_fields = ['fecha_creacion']

    def get_num_likes(self, obj):
        return obj.total_likes()

    def get_num_comentarios(self, obj):
        return obj.total_comentarios()

    def get_ya_di_like(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False

    def create(self, validated_data):
        validated_data['usuario'] = self.context['request'].user
        return super().create(validated_data)
        
        
class ArticuloSerializer(serializers.ModelSerializer):
    class Meta:
        model = Articulo
        fields = [
            'id', 'titulo', 'resumen', 'contenido', 
            'categoria', 'imagen_url', 'tiempo_lectura', 'fecha_publicacion'
        ]
        
        
class TipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tip
        fields = ['id', 'titulo', 'contenido', 'categoria']