from django.contrib import admin
from .models import Usuario, DiarioEmocional, Cuestionario, Pregunta, RespuestaUsuario

# Registramos los modelos para que aparezcan en el panel
admin.site.register(Usuario)
admin.site.register(DiarioEmocional)
admin.site.register(Cuestionario)
admin.site.register(Pregunta)
admin.site.register(RespuestaUsuario)