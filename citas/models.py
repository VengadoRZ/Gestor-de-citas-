from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator


class Usuario(AbstractUser):
    TIPO_USUARIO = (
        ('cliente', 'Cliente'),
        ('empresa', 'Empresa'),
    )
    tipo_perfil = models.CharField(max_length=10, choices=TIPO_USUARIO, default='cliente')
    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)
    foto = models.ImageField(upload_to='fotos_perfil/', null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.get_tipo_perfil_display()})"

class Empresa(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    nombre_negocio = models.CharField(max_length=200)
    nit_rif = models.CharField(max_length=50)
    direccion = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre_negocio

class Cliente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    nombre = models.CharField(max_length=100, default='')
    apellido = models.CharField(max_length=100, default='')
    cedula = models.CharField(max_length=20)
    telefono = models.CharField(max_length=20)

    def __str__(self):
        full_name = f"{self.nombre} {self.apellido}".strip()
        return full_name if full_name else self.usuario.username

class Servicio(models.Model):
    CATEGORIAS = (
        ('salud', 'Salud y Medicina'),
        ('bienestar', 'Barbería y Estética'),
        ('deporte', 'Deporte y Fitness'),
        ('educacion', 'Educación y Tutorías'),
        ('asesoria', 'Asesoría y Consultoría'),
        ('hogar', 'Hogar y Reparaciones'),
        ('tecnologia', 'Tecnología y Soporte'),
        ('creatividad', 'Diseño y Creatividad'),
        ('automotriz', 'Automotriz'),
        ('general', 'General / Otros'),
    )
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='servicios')
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.0)])
    categoria = models.CharField(max_length=50, choices=CATEGORIAS, default='general')
    imagen = models.ImageField(upload_to='servicios/', null=True, blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class Cita(models.Model):
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('activa', 'Activa'),
        ('cancelada', 'Cancelada'),
        ('finalizada', 'Finalizada'),
    )
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField()
    pagado = models.BooleanField(default=False)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')

    def __str__(self):
        return f"Cita para {self.cliente} - {self.servicio} ({self.fecha_hora})"
