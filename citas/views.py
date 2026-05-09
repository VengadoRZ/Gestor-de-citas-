from datetime import timezone

from django.contrib import messages
from django.shortcuts import redirect, render
from .forms import CustomUserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .models import Usuario, Empresa, Cliente, Servicio, Cita
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone  # <--- Agrega esta línea
from django.db import models
from django.shortcuts import render, redirect, get_object_or_404 # <--- Agrega get_object_or_404 aquí


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
            mail_subject = 'Activa tu cuenta en [Nombre de tu sitio]'
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
        cedula = request.POST.get('cedula')
        telefono = request.POST.get('telefono')
        Cliente.objects.create(usuario=request.user, cedula=cedula, telefono=telefono)
        return redirect('home')

    return render(request, 'citas/completar_cliente.html')

@login_required
def completar_empresa(request):
    if hasattr(request.user, 'empresa'): return redirect('home')

    if request.method == 'POST':
        Empresa.objects.create(
            usuario=request.user,
            nombre_negocio=request.POST.get('nombre_negocio', ''),
            nit_rif=request.POST.get('nit_rif', ''),
            direccion=request.POST.get('direccion', '')
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
                direccion=request.POST.get('direccion', '')
            )
        else:
            Cliente.objects.create(
                usuario=usuario,
                cedula=request.POST.get('cedula', ''),
                telefono=request.POST.get('telefono', '')
            )
        return redirect('home')

    return render(request, 'citas/completar_cliente.html')

@login_required
def perfil(request):
    user = request.user
    if request.method == 'POST':
        if user.tipo_perfil == 'cliente':
            cliente = user.cliente
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
    

@login_required
def catalogo_servicios(request):
    busqueda = request.GET.get('q', '')
    
    # Filtramos por el nombre del servicio o el nombre del negocio de la empresa
    servicios = Servicio.objects.filter(
        models.Q(nombre__icontains=busqueda) | 
        models.Q(empresa__nombre_negocio__icontains=busqueda)
    )
    
    return render(request, 'citas/catalogo.html', {
        'servicios': servicios, 
        'query': busqueda
    })


@login_required
def agendar_cita(request, servicio_id):
    servicio = get_object_or_404(Servicio, id=servicio_id)
    
    # Intentamos obtener el perfil de cliente de forma controlada
    try:
        cliente_perfil = Cliente.objects.get(usuario=request.user)
    except Cliente.DoesNotExist:
        if request.user.tipo_perfil == 'empresa':
            messages.error(request, "Solo los clientes pueden agendar citas. Inicia sesión con una cuenta de cliente.")
            return redirect('home')

        messages.warning(request, "Debes completar tu perfil de cliente antes de agendar una cita.")
        return redirect('completar_cliente')

    if request.method == 'POST':
        fecha_seleccionada = request.POST.get('fecha_hora')
        
        # Validación de choque de horarios
        choque = Cita.objects.filter(
            servicio__empresa=servicio.empresa,
            fecha_hora=fecha_seleccionada
        ).exists()

        if choque:
            return render(request, 'citas/reserva.html', {
                'servicio': servicio,
                'error': 'Este horario ya está ocupado.'
            })

        # Si todo está bien, crear cita
        Cita.objects.create(
            cliente=cliente_perfil,
            servicio=servicio,
            fecha_hora=fecha_seleccionada
        )
        messages.success(request, '¡Cita agendada con éxito!')
        return redirect('home')

    # Si es GET, mostramos el formulario
    return render(request, 'citas/reserva.html', {'servicio': servicio})

@login_required
def agenda_empresa(request):
    # Verificamos que sea empresa
    if request.user.tipo_perfil != 'empresa':
        return redirect('home')
        
    # IMPORTANTE: Obtenemos el objeto Empresa asociado al Usuario
    empresa_perfil = get_object_or_404(Empresa, usuario=request.user)
    ahora = timezone.now()
    
    # Filtramos las citas que pertenecen a los servicios de ESTA empresa
    citas = Cita.objects.filter(
        servicio__empresa=empresa_perfil, # <--- Corregido
        fecha_hora__month=ahora.month,
        fecha_hora__year=ahora.year
    ).order_by('fecha_hora')

    return render(request, 'citas/agenda.html', {'citas': citas, 'mes': ahora})

def catalogo_servicios(request):
    busqueda = request.GET.get('q', '')
    
    # Buscamos por nombre del servicio O nombre del negocio de la empresa
    servicios = Servicio.objects.filter(
        models.Q(nombre__icontains=busqueda) | 
        models.Q(empresa__nombre_negocio__icontains=busqueda)
    )
    
    return render(request, 'citas/catalogo.html', {
        'servicios': servicios, 
        'query': busqueda
    })

from .forms import ServicioForm

@login_required
def crear_servicio(request):
    # Verificamos que sea una empresa
    if request.user.tipo_perfil != 'empresa':
        return redirect('home')

    if request.method == 'POST':
        form = ServicioForm(request.POST)
        if form.is_valid():
            servicio = form.save(commit=False)
            # Vinculamos el servicio a la Empresa del usuario actual
            servicio.empresa = request.user.empresa 
            servicio.save()
            messages.success(request, '¡Servicio publicado con éxito!')
            return redirect('home') # O a una lista de tus servicios
    else:
        form = ServicioForm()
    
    return render(request, 'citas/crear_servicio.html', {'form': form})