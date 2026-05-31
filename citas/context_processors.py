from .models import Cita
from django.utils import timezone
from datetime import timedelta

def notificaciones(request):
    citas_notificacion = []
    pendientes = 0
    if request.user.is_authenticated:
        now = timezone.now()
        tomorrow_end = now + timedelta(days=2)
        try:
            if request.user.tipo_perfil == 'cliente' and hasattr(request.user, 'cliente'):
                citas_qs = Cita.objects.filter(cliente=request.user.cliente, fecha_hora__gte=now, fecha_hora__lte=tomorrow_end, estado__in=['pendiente', 'activa']).order_by('fecha_hora')
                citas_notificacion = list(citas_qs[:5])
                pendientes = citas_qs.count()
            elif request.user.tipo_perfil == 'empresa' and hasattr(request.user, 'empresa'):
                citas_qs = Cita.objects.filter(servicio__empresa=request.user.empresa, fecha_hora__gte=now, fecha_hora__lte=tomorrow_end, estado__in=['pendiente', 'activa']).order_by('fecha_hora')
                citas_notificacion = list(citas_qs[:5])
                pendientes = citas_qs.count()
        except:
            pass
    return {'notificaciones_pendientes': pendientes, 'citas_notificacion': citas_notificacion}
