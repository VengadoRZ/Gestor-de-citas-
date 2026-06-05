from datetime import date

from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .forms import CustomUserCreationForm, ServicioForm
from .models import Usuario, Empresa, Cliente, Servicio, Cita


# ---------------------------------------------------------------------------
# Páginas públicas
# ---------------------------------------------------------------------------

def home(request):
    return render(request, 'citas/home.html')


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.email = form.cleaned_data.get('email')
            user.save()

            current_site = get_current_site(request)
            mail_subject = 'Activa tu cuenta en Gestor de Citas'
            context = {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
                'protocol': 'https' if request.is_secure() else 'http',
            }
            html_message = render_to_string('registration/account_verification_email.html', context)
            send_mail(
                mail_subject,
                '',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
            )

            messages.success(request, 'Te hemos enviado un enlace para activar tu cuenta. Revisa tu correo.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            if not hasattr(user, 'cliente') and not hasattr(user, 'empresa'):
                return redirect('elegir_perfil')
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Usuario.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.is_email_verified = True
        user.save()
        messages.success(request, 'Tu cuenta ha sido activada. Ya puedes iniciar sesión.')
        return redirect('login')
    else:
        return render(request, 'registration/activation_invalid.html')


# ---------------------------------------------------------------------------
# Perfil y registro de datos
# ---------------------------------------------------------------------------

@login_required
def elegir_perfil(request):
    if hasattr(request.user, 'cliente') or hasattr(request.user, 'empresa'):
        return redirect('home')

    if request.method == 'POST':
        tipo = request.POST.get('tipo_perfil')
        request.user.tipo_perfil = tipo
        request.user.save()

        if tipo == 'empresa':
            return redirect('completar_empresa')
        else:
            return redirect('completar_cliente')

    return render(request, 'perfil/elegir_perfil.html')


@login_required
def completar_cliente(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '')
        apellido = request.POST.get('apellido', '')
        cedula = request.POST.get('cedula')
        telefono = request.POST.get('telefono')
        Cliente.objects.create(usuario=request.user, nombre=nombre, apellido=apellido, cedula=cedula, telefono=telefono)
        return redirect('home')

    return render(request, 'citas/completar_cliente.html')


@login_required
def completar_empresa(request):
    if hasattr(request.user, 'empresa'):
        return redirect('home')

    if request.method == 'POST':
        Empresa.objects.create(
            usuario=request.user,
            nombre_negocio=request.POST.get('nombre_negocio', ''),
            nit_rif=request.POST.get('nit_rif', ''),
            direccion=request.POST.get('direccion', ''),
        )
        return redirect('home')

    return render(request, 'citas/completar_empresa.html')


@login_required
def completar_perfil(request):
    usuario = request.user

    if hasattr(usuario, 'cliente') or hasattr(usuario, 'empresa'):
        return redirect('home')

    if request.method == 'POST':
        tipo = request.POST.get('tipo_perfil', 'cliente')
        usuario.tipo_perfil = tipo
        usuario.save()

        if tipo == 'empresa':
            Empresa.objects.create(
                usuario=usuario,
                nombre_negocio=request.POST.get('nombre_negocio', ''),
                nit_rif=request.POST.get('nit_rif', ''),
                direccion=request.POST.get('direccion', ''),
            )
        else:
            Cliente.objects.create(
                usuario=usuario,
                nombre=request.POST.get('nombre', ''),
                apellido=request.POST.get('apellido', ''),
                cedula=request.POST.get('cedula', ''),
                telefono=request.POST.get('telefono', ''),
            )
        return redirect('home')

    return render(request, 'citas/completar_cliente.html')


@login_required
def perfil(request):
    user = request.user
    if request.method == 'POST':
        # Foto de perfil
        if 'foto' in request.FILES:
            user.foto = request.FILES['foto']
            user.save()
        if user.tipo_perfil == 'cliente':
            cliente = user.cliente
            cliente.nombre = request.POST.get('nombre')
            cliente.apellido = request.POST.get('apellido')
            cliente.cedula = request.POST.get('cedula')
            cliente.telefono = request.POST.get('telefono')
            cliente.save()
        elif user.tipo_perfil == 'empresa':
            empresa = user.empresa
            empresa.nombre_negocio = request.POST.get('nombre_negocio')
            empresa.nit_rif = request.POST.get('nit_rif')
            empresa.direccion = request.POST.get('direccion')
            empresa.save()
        return redirect('perfil')

    return render(request, 'perfil/perfil.html', {'user': user})


# ---------------------------------------------------------------------------
# Catálogo y citas (cliente)
# ---------------------------------------------------------------------------

@login_required
def catalogo_servicios(request):
    busqueda = request.GET.get('q', '')
    categoria = request.GET.get('categoria', '')

    servicios = Servicio.objects.filter(activo=True)
    if busqueda:
        servicios = servicios.filter(
            models.Q(nombre__icontains=busqueda) |
            models.Q(empresa__nombre_negocio__icontains=busqueda)
        )
    if categoria:
        servicios = servicios.filter(categoria=categoria)

    return render(request, 'citas/catalogo.html', {
        'servicios': servicios,
        'query': busqueda,
        'categoria_activa': categoria,
    })


@login_required
def agendar_cita(request, servicio_id):
    servicio = get_object_or_404(Servicio, id=servicio_id)

    try:
        cliente_perfil = Cliente.objects.get(usuario=request.user)
    except Cliente.DoesNotExist:
        if request.user.tipo_perfil == 'empresa':
            messages.error(request, 'Solo los clientes pueden agendar citas.')
            return redirect('home')
        messages.warning(request, 'Debes completar tu perfil de cliente antes de agendar una cita.')
        return redirect('completar_cliente')

    if request.method == 'POST':
        fecha_seleccionada = request.POST.get('fecha_hora')

        choque = Cita.objects.filter(
            servicio__empresa=servicio.empresa,
            fecha_hora=fecha_seleccionada,
        ).exists()

        if choque:
            return render(request, 'citas/reserva.html', {
                'servicio': servicio,
                'error': 'Este horario ya está ocupado.',
            })

        Cita.objects.create(
            cliente=cliente_perfil,
            servicio=servicio,
            fecha_hora=fecha_seleccionada,
        )
        messages.success(request, '¡Cita agendada con éxito!')
        return redirect('home')

    return render(request, 'citas/reserva.html', {'servicio': servicio})


@login_required
def mis_citas(request):
    try:
        cliente_perfil = Cliente.objects.get(usuario=request.user)
    except Cliente.DoesNotExist:
        if request.user.tipo_perfil == 'empresa':
            messages.error(request, 'Las empresas no tienen citas como cliente.')
            return redirect('home')
        messages.warning(request, 'Debes completar tu perfil de cliente para ver tus citas.')
        return redirect('completar_perfil')

    citas_list = Cita.objects.filter(cliente=cliente_perfil).order_by('fecha_hora')
    return render(request, 'citas/calendario_cliente.html', {'citas': citas_list})


@login_required
def cancelar_cita(request, cita_id):
    try:
        cliente_perfil = Cliente.objects.get(usuario=request.user)
    except Cliente.DoesNotExist:
        return redirect('home')

    cita = get_object_or_404(Cita, id=cita_id, cliente=cliente_perfil)
    
    if cita.estado == 'pendiente':
        cita.estado = 'cancelada'
        cita.save()
        messages.success(request, 'Cita cancelada correctamente.')
    else:
        messages.error(request, 'La cita no se puede cancelar porque ya está en progreso o fue completada.')
        
    return redirect('calendario_cliente')


# ---------------------------------------------------------------------------
# Agenda y servicios (empresa)
# ---------------------------------------------------------------------------

@login_required
def agenda_empresa(request):
    if request.user.tipo_perfil!= 'empresa':
        return redirect('home')

    empresa_perfil = get_object_or_404(Empresa, usuario=request.user)
    ahora = timezone.now()

    try:
        mes_param = int(request.GET.get('mes', ahora.month))
        anio_param = int(request.GET.get('anio', ahora.year))
    except (ValueError, TypeError):
        mes_param = ahora.month
        anio_param = ahora.year

    if mes_param < 1:
        mes_param = 1
    if mes_param > 12:
        mes_param = 12

    fecha_actual = date(anio_param, mes_param, 1)

    if mes_param == 1:
        mes_anterior = date(anio_param - 1, 12, 1)
    else:
        mes_anterior = date(anio_param, mes_param - 1, 1)

    if mes_param == 12:
        mes_siguiente = date(anio_param + 1, 1, 1)
    else:
        mes_siguiente = date(anio_param, mes_param + 1, 1)

    citas = Cita.objects.filter(
        servicio__empresa=empresa_perfil,
        fecha_hora__month=mes_param,
        fecha_hora__year=anio_param,
    ).order_by('fecha_hora')

    return render(request, 'citas/agenda.html', {
        'citas': citas,
        'mes': fecha_actual,
        'mes_anterior': mes_anterior,
        'mes_siguiente': mes_siguiente,
    })


@login_required
def cambiar_estado_cita(request, cita_id):
    if request.user.tipo_perfil != 'empresa':
        return redirect('home')
    if request.method == 'POST':
        cita = get_object_or_404(Cita, id=cita_id, servicio__empresa__usuario=request.user)
        # No se puede revertir una cancelación hecha por el cliente
        if cita.estado == 'cancelada':
            messages.warning(request, 'Esta cita fue cancelada por el cliente y no se puede revertir.')
            return redirect('agenda_empresa')
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in ['pendiente', 'activa', 'finalizada']:
            cita.estado = nuevo_estado
            cita.save()
    return redirect('agenda_empresa')


@login_required
def crear_servicio(request):
    if request.user.tipo_perfil != 'empresa':
        return redirect('home')

    if request.method == 'POST':
        form = ServicioForm(request.POST, request.FILES)
        if form.is_valid():
            servicio = form.save(commit=False)
            servicio.empresa = request.user.empresa
            servicio.save()
            messages.success(request, '¡Servicio publicado con éxito!')
            return redirect('home')
    else:
        form = ServicioForm()

    return render(request, 'citas/crear_servicio.html', {'form': form})


@login_required
def toggle_servicio(request, servicio_id):
    if request.method == 'POST':
        try:
            servicio = get_object_or_404(Servicio, id=servicio_id, empresa=request.user.empresa)
            servicio.activo = not servicio.activo
            servicio.save()
        except:
            pass
    return redirect('crear_servicio')


@login_required
def eliminar_servicio(request, servicio_id):
    if request.method == 'POST':
        try:
            servicio = get_object_or_404(Servicio, id=servicio_id, empresa=request.user.empresa)
            servicio.delete()
            messages.success(request, 'Servicio eliminado correctamente.')
        except Exception as e:
            messages.error(request, 'Hubo un error al eliminar el servicio.')
    return redirect('crear_servicio')