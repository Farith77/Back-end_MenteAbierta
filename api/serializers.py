from rest_framework import serializers
from .models import Usuario, DiarioEmocional

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