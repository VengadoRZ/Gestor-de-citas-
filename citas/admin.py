from django.contrib import admin
from .models import Usuario, Empresa, Cliente, Servicio, Cita

admin.site.register(Usuario)
admin.site.register(Empresa)
admin.site.register(Cliente)
admin.site.register(Servicio)
admin.site.register(Cita)

class CitaAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'servicio', 'fecha_hora', 'pagado')