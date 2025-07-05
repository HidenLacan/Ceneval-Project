from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

# Create your views here.

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirige según el rol, si lo deseas
            if user.role == 'admin':
                return redirect('admin_dashboard')  # Cambia por tu ruta real
            elif user.role == 'staff':
                return redirect('staff_dashboard')
            elif user.role == 'employee':
                return redirect('employee_dashboard')
            elif user.role == 'researcher':
                return redirect('researcher_dashboard')
            else:
                return redirect('home')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    return render(request, 'login.html')

@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        return HttpResponseForbidden('Acceso denegado: No eres admin.')
    context = {}
    if request.method == 'POST':
        colonia = request.POST.get('colonia')
        if colonia:
            try:
                from core.utils.main import download_bbox
                from core.utils.polygon_logic import get_colonia_config
                # Descargar y obtener configuración de la colonia
                cache_path = download_bbox(colonia)
                config = get_colonia_config(cache_path)
                context['colonia'] = colonia
                context['config'] = config
            except Exception as e:
                context['error'] = f"Error al buscar la colonia: {str(e)}"
        else:
            context['error'] = 'Debes ingresar el nombre de la colonia.'
    return render(request, 'admin_dashboard.html', context)

@login_required
def staff_dashboard(request):
    if request.user.role != 'staff':
        return HttpResponseForbidden('Acceso denegado: No eres staff.')
    return render(request, 'staff_dashboard.html')

@login_required
def employee_dashboard(request):
    if request.user.role != 'employee':
        return HttpResponseForbidden('Acceso denegado: No eres empleado.')
    return render(request, 'employee_dashboard.html')

@login_required
def researcher_dashboard(request):
    if request.user.role != 'researcher':
        return HttpResponseForbidden('Acceso denegado: No eres investigador.')
    return render(request, 'researcher_dashboard.html')

@login_required
def admin_map_dashboard(request):
    if request.user.role != 'admin':
        return HttpResponseForbidden('Acceso denegado: No eres admin.')
    context = {}
    if request.method == 'POST':
        colonia = request.POST.get('colonia')
        if colonia:
            from core.utils.main import download_bbox, procesar_poligono_completo
            try:
                # Descargar y guardar el bbox de la colonia
                cache_path = download_bbox(colonia)
                # Nombre del archivo de polígono esperado
                nombre_archivo = f"{colonia.strip().lower().replace(' ', '_')}.json"
                # Procesar el polígono si existe
                try:
                    resultado = procesar_poligono_completo(nombre_archivo)
                    context['resultado'] = resultado
                except Exception as e:
                    context['error'] = f"No se pudo procesar el polígono: {str(e)}"
            except Exception as e:
                context['error'] = f"Error al descargar datos de la colonia: {str(e)}"
        else:
            context['error'] = 'Debes ingresar el nombre de la colonia.'
    return render(request, 'admin_dashboard.html', context)
