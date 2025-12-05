from django.contrib import admin
from .models import (
    Usuario, 
    Cuestionario, 
    Pregunta, 
    RespuestaUsuario, 
    DiarioEmocional, 
    RegistroEmocion,  
    Articulo,         
    Tip, 
    Ejercicio, 
    Publicacion,
    Comentario
)

# Registramos los modelos para que aparezcan en el panel
admin.site.register(Usuario)
admin.site.register(DiarioEmocional)
admin.site.register(Cuestionario)
admin.site.register(Pregunta)
admin.site.register(RespuestaUsuario)

@admin.register(RegistroEmocion)
class RegistroEmocionAdmin(admin.ModelAdmin):
    # Esto hace que se vea bonito en la lista, mostrando columnas clave
    list_display = ('usuario', 'emocion', 'intensidad', 'fecha_registro')
    list_filter = ('emocion', 'fecha_registro')
    search_fields = ('usuario__email', 'nota')
    
admin.site.register(Articulo)
admin.site.register(Tip)
admin.site.register(Ejercicio)
admin.site.register(Publicacion)
admin.site.register(Comentario)