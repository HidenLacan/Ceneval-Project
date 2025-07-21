from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from core.models import ColoniaProcesada
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
        action = request.POST.get('action')
        colonia = request.POST.get('colonia')
        
        if action == 'guardar' and colonia:
            try:
                # Obtener o crear la colonia
                colonia_obj, created = ColoniaProcesada.objects.get_or_create(
                    nombre=colonia,
                    defaults={'creado_por': request.user}
                )
                
                # Guardar imagen si se subió
                if 'png_file' in request.FILES:
                    colonia_obj.imagen = request.FILES['png_file']
                
                # Obtener configuración de la colonia
                from core.utils.main import download_bbox
                from core.utils.polygon_logic import get_colonia_config
                cache_path = download_bbox(colonia)
                config = get_colonia_config(cache_path)
                colonia_obj.configuracion = config
                
                # Guardar polígono y datos JSON si se proporcionan
                poligono_geojson = request.POST.get('poligono_geojson')
                datos_json = request.POST.get('datos_json')
                
                if poligono_geojson:
                    try:
                        colonia_obj.poligono_geojson = json.loads(poligono_geojson)
                        print(f"Polígono guardado para {colonia}")
                    except json.JSONDecodeError:
                        print(f"Error al parsear polígono JSON para {colonia}")
                
                if datos_json:
                    try:
                        colonia_obj.datos_json = json.loads(datos_json)
                        print(f"Datos JSON guardados para {colonia}")
                    except json.JSONDecodeError:
                        print(f"Error al parsear datos JSON para {colonia}")
                
                colonia_obj.save()
                
                context['success'] = f"Colonia '{colonia}' guardada exitosamente con todos los datos"
                context['colonia'] = colonia
                context['config'] = config
                
            except Exception as e:
                context['error'] = f"Error al guardar la colonia: {str(e)}"
        
        elif action == 'modificar' and colonia:
            try:
                colonia_obj = ColoniaProcesada.objects.get(nombre=colonia)
                
                # Actualizar imagen si se subió
                if 'png_file' in request.FILES:
                    colonia_obj.imagen = request.FILES['png_file']
                
                # Actualizar polígono y datos JSON si se proporcionan
                poligono_geojson = request.POST.get('poligono_geojson')
                datos_json = request.POST.get('datos_json')
                
                if poligono_geojson:
                    try:
                        colonia_obj.poligono_geojson = json.loads(poligono_geojson)
                    except json.JSONDecodeError:
                        pass
                
                if datos_json:
                    try:
                        colonia_obj.datos_json = json.loads(datos_json)
                    except json.JSONDecodeError:
                        pass
                
                colonia_obj.save()
                context['success'] = f"Colonia '{colonia}' modificada exitosamente"
                context['colonia'] = colonia
                context['config'] = colonia_obj.configuracion
                
            except ColoniaProcesada.DoesNotExist:
                context['error'] = f"La colonia '{colonia}' no existe"
            except Exception as e:
                context['error'] = f"Error al modificar la colonia: {str(e)}"
        
        elif action == 'borrar' and colonia:
            try:
                colonia_obj = ColoniaProcesada.objects.get(nombre=colonia)
                colonia_obj.delete()
                context['success'] = f"Colonia '{colonia}' eliminada exitosamente"
            except ColoniaProcesada.DoesNotExist:
                context['error'] = f"La colonia '{colonia}' no existe"
            except Exception as e:
                context['error'] = f"Error al eliminar la colonia: {str(e)}"
        
        elif action == 'usuarios':
            return redirect('admin_user_control')
        elif colonia:
            # Solo buscar la colonia
            try:
                from core.utils.main import download_bbox
                from core.utils.polygon_logic import get_colonia_config
                cache_path = download_bbox(colonia)
                config = get_colonia_config(cache_path)
                context['colonia'] = colonia
                context['config'] = config
                
                # Verificar si ya existe en la base de datos
                try:
                    colonia_existente = ColoniaProcesada.objects.get(nombre=colonia)
                    context['colonia_existente'] = colonia_existente
                except ColoniaProcesada.DoesNotExist:
                    pass
                    
            except Exception as e:
                context['error'] = f"Error al buscar la colonia: {str(e)}"
        else:
            context['error'] = 'Debes ingresar el nombre de la colonia.'
    
    # Obtener lista de colonias existentes
    context['colonias_existentes'] = ColoniaProcesada.objects.all()[:10]
    
    return render(request, 'admin_dashboard.html', context)

@login_required
@csrf_exempt
def guardar_poligono_colonia(request):
    """Endpoint para guardar el polígono dibujado en el mapa"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    if request.user.role != 'admin':
        return JsonResponse({'error': 'Acceso denegado'}, status=403)
    
    try:
        print("=== DEBUG: Guardando polígono ===")
        data = json.loads(request.body)
        print(f"Datos recibidos: {data}")
        
        nombre_colonia = data.get('nombre_colonia')
        poligono_geojson = data.get('poligono_geojson')
        datos_json = data.get('datos_json')
        
        print(f"Nombre colonia: {nombre_colonia}")
        print(f"Tiene polígono: {poligono_geojson is not None}")
        print(f"Tiene datos JSON: {datos_json is not None}")
        
        if not nombre_colonia:
            return JsonResponse({'error': 'Nombre de colonia requerido'}, status=400)
        
        # Obtener o crear la colonia
        colonia_obj, created = ColoniaProcesada.objects.get_or_create(
            nombre=nombre_colonia,
            defaults={'creado_por': request.user}
        )
        
        print(f"Colonia creada: {created}, ID: {colonia_obj.id}")
        
        # Actualizar datos
        if poligono_geojson:
            colonia_obj.poligono_geojson = poligono_geojson
            print("Polígono guardado")
        if datos_json:
            colonia_obj.datos_json = datos_json
            print("Datos JSON guardados")
        
        colonia_obj.save()
        print("Colonia guardada exitosamente")
        
        return JsonResponse({
            'success': True,
            'message': f"Polígono guardado para '{nombre_colonia}'",
            'colonia_id': colonia_obj.id
        })
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def cargar_colonia_existente(request):
    """Endpoint para cargar una colonia existente desde la base de datos"""
    if request.user.role != 'admin':
        return JsonResponse({'error': 'Acceso denegado'}, status=403)
    
    colonia_nombre = request.GET.get('nombre')
    if not colonia_nombre:
        return JsonResponse({'error': 'Nombre de colonia requerido'}, status=400)
    
    try:
        colonia = ColoniaProcesada.objects.get(nombre=colonia_nombre)
        
        # Preparar datos para el frontend
        datos_colonia = {
            'nombre': colonia.nombre,
            'configuracion': colonia.configuracion,
            'tiene_imagen': bool(colonia.imagen),
            'tiene_poligono': bool(colonia.poligono_geojson),
            'tiene_json': bool(colonia.datos_json),
            'imagen_url': colonia.imagen.url if colonia.imagen else None,
            'poligono_geojson': colonia.poligono_geojson,
            'datos_json': colonia.datos_json
        }
        
        return JsonResponse(datos_colonia)
        
    except ColoniaProcesada.DoesNotExist:
        return JsonResponse({'error': f'Colonia "{colonia_nombre}" no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def staff_dashboard(request):
    if request.user.role != 'staff':
        return HttpResponseForbidden('Acceso denegado: No eres staff.')
    
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # Obtener colonias procesadas (solo lectura)
    colonias = ColoniaProcesada.objects.all().order_by('-fecha_creacion')
    
    # Obtener empleados (usuarios con rol 'employee')
    empleados = User.objects.filter(role='employee', is_active=True).order_by('username')
    
    context = {
        'colonias': colonias,
        'empleados': empleados,
    }
    
    return render(request, 'staff_dashboard.html', context)

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

@login_required
def admin_user_control(request):
    """Vista para el control de usuarios por parte del administrador"""
    if request.user.role != 'admin':
        return HttpResponseForbidden('Acceso denegado: No eres administrador.')
    
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    context = {}
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'crear_usuario':
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            role = request.POST.get('role')
            
            if not all([username, email, password, role]):
                context['error'] = 'Todos los campos son requeridos'
            else:
                try:
                    # Verificar si el usuario ya existe
                    if User.objects.filter(username=username).exists():
                        context['error'] = f'El usuario "{username}" ya existe'
                    elif User.objects.filter(email=email).exists():
                        context['error'] = f'El email "{email}" ya está registrado'
                    else:
                        # Crear nuevo usuario
                        user = User.objects.create_user(
                            username=username,
                            email=email,
                            password=password,
                            role=role
                        )
                        context['success'] = f'Usuario "{username}" creado exitosamente con rol "{role}"'
                except Exception as e:
                    context['error'] = f'Error al crear usuario: {str(e)}'
        
        elif action == 'editar_usuario':
            user_id = request.POST.get('user_id')
            username = request.POST.get('username')
            email = request.POST.get('email')
            role = request.POST.get('role')
            is_active = request.POST.get('is_active') == 'on'
            
            try:
                user = User.objects.get(id=user_id)
                user.username = username
                user.email = email
                user.role = role
                user.is_active = is_active
                user.save()
                context['success'] = f'Usuario "{username}" actualizado exitosamente'
            except User.DoesNotExist:
                context['error'] = 'Usuario no encontrado'
            except Exception as e:
                context['error'] = f'Error al actualizar usuario: {str(e)}'
        
        elif action == 'eliminar_usuario':
            user_id = request.POST.get('user_id')
            
            try:
                user = User.objects.get(id=user_id)
                if user == request.user:
                    context['error'] = 'No puedes eliminar tu propia cuenta'
                else:
                    username = user.username
                    user.delete()
                    context['success'] = f'Usuario "{username}" eliminado exitosamente'
            except User.DoesNotExist:
                context['error'] = 'Usuario no encontrado'
            except Exception as e:
                context['error'] = f'Error al eliminar usuario: {str(e)}'
    
    # Obtener lista de usuarios
    context['usuarios'] = User.objects.all().order_by('-date_joined')
    
    return render(request, 'admin_user_control.html', context)

@login_required
@csrf_exempt
def procesar_usuarios_masivos(request):
    """Endpoint para procesar la creación masiva de usuarios desde archivos"""
    if request.user.role != 'admin':
        return JsonResponse({'error': 'Acceso denegado'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        data = json.loads(request.body)
        usuarios_data = data.get('usuarios', [])
        
        if not usuarios_data:
            return JsonResponse({'error': 'No se proporcionaron datos de usuarios'}, status=400)
        
        creados = 0
        errores = 0
        errores_detalle = []
        
        for usuario_data in usuarios_data:
            try:
                username = usuario_data.get('username', '').strip()
                email = usuario_data.get('email', '').strip()
                password = usuario_data.get('password', '').strip()
                role = usuario_data.get('role', 'employee').strip()
                
                # Validaciones
                if not username or not email or not password:
                    errores += 1
                    errores_detalle.append(f"Usuario {username}: Campos requeridos vacíos")
                    continue
                
                if User.objects.filter(username=username).exists():
                    errores += 1
                    errores_detalle.append(f"Usuario {username}: Ya existe")
                    continue
                
                if User.objects.filter(email=email).exists():
                    errores += 1
                    errores_detalle.append(f"Usuario {username}: Email {email} ya registrado")
                    continue
                
                # Validar rol
                roles_validos = ['admin', 'staff', 'employee', 'researcher']
                if role not in roles_validos:
                    role = 'employee'  # Rol por defecto
                
                # Crear usuario
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    role=role
                )
                
                creados += 1
                print(f"Usuario creado: {username} ({email}) con rol {role}")
                
            except Exception as e:
                errores += 1
                errores_detalle.append(f"Usuario {usuario_data.get('username', 'N/A')}: {str(e)}")
                print(f"Error creando usuario: {str(e)}")
        
        return JsonResponse({
            'success': True,
            'creados': creados,
            'errores': errores,
            'errores_detalle': errores_detalle,
            'total': len(usuarios_data)
        })
        
    except Exception as e:
        print(f"ERROR en procesamiento masivo: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def cargar_colonia_staff(request):
    """Endpoint para que el staff cargue una colonia específica"""
    if request.user.role != 'staff':
        return JsonResponse({'error': 'Acceso denegado'}, status=403)
    
    colonia_id = request.GET.get('id')
    if not colonia_id:
        return JsonResponse({'error': 'ID de colonia requerido'}, status=400)
    try:
        colonia = ColoniaProcesada.objects.get(id=colonia_id)
        
        # Preparar datos para el frontend (solo lectura)
        datos_colonia = {
            'id': colonia.id,  # Agregar el ID de la colonia
            'nombre': colonia.nombre,
            'configuracion': colonia.configuracion,
            'tiene_imagen': bool(colonia.imagen),
            'tiene_poligono': bool(colonia.poligono_geojson),
            'tiene_json': bool(colonia.datos_json),
            'imagen_url': colonia.imagen.url if colonia.imagen else None,
            'poligono_geojson': colonia.poligono_geojson,
            'datos_json': colonia.datos_json
        }
        
        return JsonResponse({
            'success': True,
            'colonia': datos_colonia
        })
        
    except ColoniaProcesada.DoesNotExist:
        return JsonResponse({'error': 'Colonia no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@csrf_exempt
def guardar_configuracion_rutas(request):
    """Endpoint para guardar la configuración de rutas del staff"""
    if request.user.role != 'staff':
        return JsonResponse({'error': 'Acceso denegado'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        print(f"=== DEBUG: Iniciando guardar_configuracion_rutas ===")
        print(f"Request body: {request.body}")
        
        data = json.loads(request.body)
        print(f"Data parsed: {data}")
        
        colonia_id = data.get('colonia_id')
        empleados = data.get('empleados', [])
        
        print(f"Colonia ID: {colonia_id}")
        print(f"Empleados: {empleados}")
        
        if not colonia_id:
            print("ERROR: No colonia_id provided")
            return JsonResponse({'error': 'ID de colonia requerido'}, status=400)
        
        if not empleados:
            print("ERROR: No empleados provided")
            return JsonResponse({'error': 'Debe seleccionar al menos un empleado'}, status=400)
        
        # Verificar que la colonia existe
        try:
            colonia = ColoniaProcesada.objects.get(id=colonia_id)
        except ColoniaProcesada.DoesNotExist:
            return JsonResponse({'error': 'Colonia no encontrada'}, status=404)
        
        # Verificar que los empleados existen y son empleados
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        empleados_validos = []
        for empleado_id in empleados:
            try:
                empleado = User.objects.get(id=empleado_id, role='employee', is_active=True)
                empleados_validos.append(empleado)
            except User.DoesNotExist:
                return JsonResponse({'error': f'Empleado con ID {empleado_id} no encontrado'}, status=404)
        
        # Guardar la configuración en la base de datos
        from core.models import ConfiguracionRuta
        from datetime import timedelta
        import random
        
        # Calcular tiempo estimado (simulación)
        tiempo_estimado = timedelta(minutes=random.randint(30, 120))
        
        # Preparar información detallada de empleados
        informacion_empleados = []
        for empleado in empleados_validos:
            informacion_empleados.append({
                'id': empleado.id,
                'username': empleado.username,
                'email': empleado.email,
                'role': empleado.role,
                'fecha_asignacion': data.get('fecha_creacion'),
                'estado_asignacion': 'activo'
            })
        
        # Simular datos de ruta calculada
        datos_ruta = {
            'fecha_creacion_frontend': data.get('fecha_creacion'),
            'empleados_ids': [e.id for e in empleados_validos],
            'empleados_usernames': [e.username for e in empleados_validos],
            'distancia_total': round(random.uniform(5.0, 25.0), 2),
            'puntos_parada': random.randint(8, 20),
            'tipo_ruta': 'optimizada'
        }
        
        # Simular mapa calculado
        mapa_calculado = {
            'rutas': [],
            'centro_colonia': colonia.get_configuracion_centro(),
            'poligono_colonia': colonia.poligono_geojson
        }
        
        # Crear rutas simuladas para cada empleado
        for i, empleado in enumerate(empleados_validos):
            ruta_empleado = {
                'empleado_id': empleado.id,
                'empleado_nombre': empleado.username,
                'color_ruta': ['#e74c3c', '#3498db', '#2ecc71'][i % 3],
                'puntos': [],
                'distancia': round(random.uniform(2.0, 8.0), 2),
                'tiempo_estimado': random.randint(15, 45)
            }
            mapa_calculado['rutas'].append(ruta_empleado)
        
        configuracion_ruta = ConfiguracionRuta.objects.create(
            colonia=colonia,
            creado_por=request.user,
            estado='pendiente',
            informacion_empleados=informacion_empleados,
            notas=f"Ruta asignada por {request.user.username}",
            datos_ruta=datos_ruta,
            mapa_calculado=mapa_calculado,
            chat_asignado=f"chat_ruta_{colonia.id}_{random.randint(1000, 9999)}",
            tiempo_calculado=tiempo_estimado
        )
        
        # Agregar empleados a la configuración
        configuracion_ruta.empleados_asignados.set(empleados_validos)
        
        print(f"Configuración guardada en BD por {request.user.username}:")
        print(f"  ID Configuración: {configuracion_ruta.id}")
        print(f"  Colonia: {colonia.nombre}")
        print(f"  Empleados: {[e.username for e in empleados_validos]}")
        print(f"  Fecha: {data.get('fecha_creacion')}")
        print(f"  Tiempo estimado: {configuracion_ruta.get_tiempo_formateado()}")
        print(f"  Chat asignado: {configuracion_ruta.chat_asignado}")
        
        return JsonResponse({
            'success': True,
            'message': f'Configuración guardada para {len(empleados_validos)} empleados en "{colonia.nombre}"',
            'colonia': colonia.nombre,
            'empleados_count': len(empleados_validos),
            'configuracion_id': configuracion_ruta.id,
            'tiempo_estimado': configuracion_ruta.get_tiempo_formateado(),
            'chat_asignado': configuracion_ruta.chat_asignado,
            'estado': configuracion_ruta.estado
        })
        
    except Exception as e:
        print(f"ERROR en guardar_configuracion_rutas: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def listar_rutas_staff(request):
    """Endpoint para listar las rutas creadas por el staff"""
    if request.user.role != 'staff':
        return JsonResponse({'error': 'Acceso denegado'}, status=403)
    
    try:
        from core.models import ConfiguracionRuta
        
        # Obtener rutas creadas por el usuario actual
        rutas = ConfiguracionRuta.objects.filter(creado_por=request.user).order_by('-fecha_creacion')
        
        rutas_data = []
        for ruta in rutas:
            empleados_info = ruta.get_empleados_info()
            rutas_data.append({
                'id': ruta.id,
                'colonia_nombre': ruta.colonia.nombre,
                'empleados': empleados_info,
                'empleados_count': ruta.get_empleados_count(),
                'estado': ruta.estado,
                'fecha_creacion': ruta.fecha_creacion.isoformat(),
                'tiempo_estimado': ruta.get_tiempo_formateado(),
                'chat_asignado': ruta.chat_asignado,
                'notas': ruta.notas,
                'datos_ruta': ruta.datos_ruta
            })
        
        return JsonResponse({
            'success': True,
            'rutas': rutas_data,
            'total_rutas': len(rutas_data)
        })
        
    except Exception as e:
        print(f"ERROR en listar_rutas_staff: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
