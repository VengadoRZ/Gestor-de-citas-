"""
URL configuration for gestor_citas project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from citas import views
import citas
from citas.views import home, register, completar_cliente, completar_perfil, elegir_perfil, completar_empresa
from django.contrib.auth.views import LoginView 
from django.contrib.auth import views as auth_views
from django.urls import path


urlpatterns = [
    path('admin/', admin.site.urls), 
    path('', home, name='home'), 
    path('register/', register, name='register'), 
    path('elegir-perfil/', views.elegir_perfil, name='elegir_perfil'),
    path('accounts/', include('django.contrib.auth.urls')),  
    path('login/', views.login_view, name='login'),
    path('completar_cliente/', completar_cliente, name='completar_cliente'),
    path('completar-empresa/', views.completar_empresa, name='completar_empresa'),
    path('completar_perfil/', views.completar_perfil, name='completar_perfil'),
    path('perfil/', views.perfil, name='perfil'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html',
             
             success_url='/reset/done/' 
         ), 
         name='password_reset_confirm'),
    
    path('reset/done/', auth_views.LoginView.as_view(template_name='registration/login.html', extra_context={'password_reset_complete': True}), name='password_reset_complete'),
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate_account'),
         
# Para la Empresa: Ver sus citas del mes
    path('empresa/agenda/', views.agenda_empresa, name='agenda_empresa'),
    
    # Para el Cliente: Buscar y agendar
    # Le puse name='catalogo_servicios' para que coincida con el HTML
    path('buscar/', views.catalogo_servicios, name='catalogo_servicios'),
    
    # Esta ruta SIEMPRE debe recibir el ID del servicio
    path('agendar/<int:servicio_id>/', views.agendar_cita, name='agendar_cita'),
    path('empresa/nuevo-servicio/', views.crear_servicio, name='crear_servicio'),
]