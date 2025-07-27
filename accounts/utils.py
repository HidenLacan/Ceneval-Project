import os
import json
from io import BytesIO
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import folium
from PIL import Image as PILImage
import base64
import tempfile


def generate_route_pdf(configuracion_ruta, empleados_info):
    """
    Generate a PDF with route information for employees
    """
    # Create a temporary file for the PDF
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=20,
        textColor=colors.darkgreen
    )
    
    normal_style = styles['Normal']
    
    # Build the PDF content
    story = []
    
    # Title
    story.append(Paragraph("📋 REPORTE DE RUTAS ASIGNADAS", title_style))
    story.append(Spacer(1, 20))
    
    # Route information
    story.append(Paragraph(f"<b>Colonia:</b> {configuracion_ruta.colonia.nombre}", subtitle_style))
    story.append(Paragraph(f"<b>Fecha de configuración:</b> {configuracion_ruta.fecha_creacion.strftime('%d/%m/%Y %H:%M')}", normal_style))
    story.append(Paragraph(f"<b>Configurado por:</b> {configuracion_ruta.configurado_por.username}", normal_style))
    story.append(Spacer(1, 20))
    
    # Employee information
    story.append(Paragraph("👥 EMPLEADOS ASIGNADOS", subtitle_style))
    
    for empleado in empleados_info:
        story.append(Paragraph(f"<b>• {empleado['nombre']}</b> ({empleado['email']})", normal_style))
    
    story.append(Spacer(1, 20))
    
    # Route details
    if configuracion_ruta.mapa_calculado and 'rutas' in configuracion_ruta.mapa_calculado:
        story.append(Paragraph("🗺️ DETALLES DE RUTAS", subtitle_style))
        
        for ruta in configuracion_ruta.mapa_calculado['rutas']:
            empleado_nombre = ruta.get('empleado_nombre', 'N/A')
            distancia = ruta.get('distancia', 0)
            tiempo_estimado = ruta.get('tiempo_estimado', 0)
            
            story.append(Paragraph(f"<b>Ruta para {empleado_nombre}:</b>", normal_style))
            story.append(Paragraph(f"  - Distancia: {distancia:.2f} km", normal_style))
            story.append(Paragraph(f"  - Tiempo estimado: {tiempo_estimado} minutos", normal_style))
            story.append(Spacer(1, 10))
    
    # Route statistics
    if hasattr(configuracion_ruta, 'tiempo_calculado') and configuracion_ruta.tiempo_calculado:
        story.append(Paragraph("📊 ESTADÍSTICAS GENERALES", subtitle_style))
        story.append(Paragraph(f"<b>Tiempo total estimado:</b> {configuracion_ruta.tiempo_calculado}", normal_style))
    
    # Build the PDF
    doc.build(story)
    pdf_buffer.seek(0)
    return pdf_buffer


def generate_map_image(configuracion_ruta):
    """
    Generate a map image from the route data
    """
    if not configuracion_ruta.mapa_calculado:
        return None
    
    # Create a folium map
    mapa_calculado = configuracion_ruta.mapa_calculado
    
    # Get center coordinates
    if 'centro_colonia' in mapa_calculado:
        center_lat = mapa_calculado['centro_colonia']['center_lat']
        center_lon = mapa_calculado['centro_colonia']['center_lon']
    else:
        center_lat, center_lon = 19.4326, -99.1332  # Default to Mexico City
    
    # Create map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=15,
        tiles='OpenStreetMap'
    )
    
    # Add polygon if available
    if 'poligono_colonia' in mapa_calculado:
        folium.GeoJson(
            mapa_calculado['poligono_colonia'],
            name='Colonia',
            style_function=lambda x: {
                'fillColor': '#ff7800',
                'color': '#000000',
                'weight': 2,
                'fillOpacity': 0.1
            }
        ).add_to(m)
    
    # Add routes
    if 'rutas' in mapa_calculado:
        for ruta in mapa_calculado['rutas']:
            if 'puntos' in ruta and ruta['puntos']:
                # Convert points to folium format
                points = []
                for punto in ruta['puntos']:
                    if len(punto) >= 2:
                        points.append([punto[1], punto[0]])  # lat, lon
                
                if points:
                    folium.PolyLine(
                        points,
                        color=ruta.get('color_ruta', '#ff0000'),
                        weight=4,
                        opacity=0.8,
                        popup=f"Ruta: {ruta.get('empleado_nombre', 'N/A')}"
                    ).add_to(m)
    
    # Save map to temporary file
    with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as tmp_file:
        m.save(tmp_file.name)
        tmp_file_path = tmp_file.name
    
    # Convert HTML to image (this would require additional setup)
    # For now, we'll return the HTML file path
    return tmp_file_path


def send_route_email(configuracion_ruta, empleados_info):
    """
    Send route information via email to assigned employees
    """
    try:
        # Generate PDF
        pdf_buffer = generate_route_pdf(configuracion_ruta, empleados_info)
        
        # Generate map image (optional)
        map_path = generate_map_image(configuracion_ruta)
        
        # Email content
        subject = f"🗺️ Rutas Asignadas - {configuracion_ruta.colonia.nombre}"
        
        # Create email body
        context = {
            'configuracion_ruta': configuracion_ruta,
            'empleados_info': empleados_info,
            'colonia_nombre': configuracion_ruta.colonia.nombre
        }
        
        html_message = render_to_string('email_route_assignment.html', context)
        plain_message = f"""
        Rutas Asignadas - {configuracion_ruta.colonia.nombre}
        
        Hola,
        
        Se han asignado rutas para la colonia {configuracion_ruta.colonia.nombre}.
        
        Empleados asignados:
        """
        
        for empleado in empleados_info:
            plain_message += f"- {empleado['nombre']} ({empleado['email']})\n"
        
        plain_message += f"""
        
        Fecha de configuración: {configuracion_ruta.fecha_creacion.strftime('%d/%m/%Y %H:%M')}
        Configurado por: {configuracion_ruta.configurado_por.username}
        
        Revisa el PDF adjunto para más detalles.
        """
        
        # Send email to each employee
        for empleado in empleados_info:
            email = EmailMessage(
                subject=subject,
                body=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[empleado['email']],
                reply_to=[settings.DEFAULT_FROM_EMAIL]
            )
            
            # Attach PDF
            email.attach(
                f"rutas_{configuracion_ruta.colonia.nombre}_{configuracion_ruta.fecha_creacion.strftime('%Y%m%d')}.pdf",
                pdf_buffer.getvalue(),
                'application/pdf'
            )
            
            # Send email
            email.send()
        
        # Clean up temporary files
        if map_path and os.path.exists(map_path):
            os.unlink(map_path)
        
        return True, "Emails enviados exitosamente"
        
    except Exception as e:
        return False, f"Error al enviar emails: {str(e)}"


def send_route_email_from_staff_dashboard(colonia_id, employee_ids):
    """
    Send route information from staff dashboard
    """
    try:
        from core.models import ColoniaProcesada
        from .models import ConfiguracionRuta, User
        
        # Get colonia
        colonia = ColoniaProcesada.objects.get(id=colonia_id)
        
        # Get employees
        empleados = User.objects.filter(id__in=employee_ids, role='employee')
        
        # Get or create configuration
        configuracion_ruta, created = ConfiguracionRuta.objects.get_or_create(
            colonia=colonia,
            configurado_por=User.objects.filter(role='staff').first(),
            defaults={
                'mapa_calculado': {},
                'tiempo_calculado': '00:00:00'
            }
        )
        
        # Prepare employee info
        empleados_info = []
        for empleado in empleados:
            empleados_info.append({
                'id': empleado.id,
                'nombre': empleado.username,
                'email': empleado.email
            })
        
        # Send emails
        success, message = send_route_email(configuracion_ruta, empleados_info)
        
        return success, message
        
    except Exception as e:
        return False, f"Error: {str(e)}" 