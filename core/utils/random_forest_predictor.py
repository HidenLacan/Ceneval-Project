"""
Módulo para predicción de tiempos de empleados usando Random Forest
"""
import os
import pickle
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

class RandomForestTimePredictor:
    """Clase para entrenar y usar Random Forest para predecir tiempos de rutas"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.features = [
            'distancia_km', 'num_nodos', 'area_zona_m2', 'densidad_nodos_km2',
            'densidad_calles_m_km2', 'experiencia_empleado_dias', 'hora_inicio',
            'dia_semana', 'temperatura_celsius'
        ]
        self.feature_names = [
            'Distancia (km)', 'Número de Nodos', 'Área Zona (m²)', 'Densidad Nodos (km²)',
            'Densidad Calles (m/km²)', 'Experiencia Empleado (días)', 'Hora Inicio',
            'Día Semana', 'Temperatura (°C)'
        ]
    
    def prepare_training_data(self, rutas_completadas):
        """
        Prepara los datos de entrenamiento desde el modelo RutaCompletada
        
        Args:
            rutas_completadas: QuerySet de RutaCompletada
            
        Returns:
            X: Features para entrenamiento
            y: Target (tiempo_real_minutos)
        """
        print("🔄 Preparando datos de entrenamiento...")
        
        data = []
        for ruta in rutas_completadas:
            # Obtener datos básicos
            row = {
                'distancia_km': ruta.distancia_km,
                'num_nodos': ruta.num_nodos,
                'area_zona_m2': ruta.area_zona_m2,
                'densidad_nodos_km2': ruta.densidad_nodos_km2,
                'densidad_calles_m_km2': ruta.densidad_calles_m_km2,
                'experiencia_empleado_dias': ruta.experiencia_empleado_dias,
                'hora_inicio': ruta.hora_inicio,
                'dia_semana': ruta.dia_semana,
                'temperatura_celsius': ruta.temperatura_celsius or 25.0,  # Default si no hay datos
                'tiempo_real_minutos': ruta.tiempo_real_minutos
            }
            data.append(row)
        
        if not data:
            print(" No hay datos de rutas completadas para entrenar")
            return None, None
        
        df = pd.DataFrame(data)
        print(f"Datos preparados: {len(df)} muestras")
        
        # Separar features y target
        X = df[self.features].fillna(0)  # Rellenar valores nulos con 0
        y = df['tiempo_real_minutos']
        
        return X, y
    
    def train_model(self, X, y, n_estimators=100, max_depth=None, min_samples_split=2):
        """
        Entrena el modelo Random Forest
        
        Args:
            X: Features de entrenamiento
            y: Target (tiempo_real_minutos)
            n_estimators: Número de árboles
            max_depth: Profundidad máxima de árboles
            min_samples_split: Mínimo de muestras para dividir
            
        Returns:
            dict: Métricas del modelo entrenado
        """
        print("🌲 Entrenando modelo Random Forest...")
        
        # Dividir datos en train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Escalar features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Crear y entrenar modelo
        self.model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            random_state=42,
            n_jobs=-1  # Usar todos los cores disponibles
        )
        
        # Entrenar modelo
        self.model.fit(X_train_scaled, y_train)
        
        # Hacer predicciones
        y_pred_train = self.model.predict(X_train_scaled)
        y_pred_test = self.model.predict(X_test_scaled)
        
        # Calcular métricas
        metrics = {
            'mae_train': mean_absolute_error(y_train, y_pred_train),
            'mae_test': mean_absolute_error(y_test, y_pred_test),
            'r2_train': r2_score(y_train, y_pred_train),
            'r2_test': r2_score(y_test, y_pred_test),
            'rmse_train': np.sqrt(mean_squared_error(y_train, y_pred_train)),
            'rmse_test': np.sqrt(mean_squared_error(y_test, y_pred_test)),
            'num_samples': len(X),
            'num_features': len(self.features),
            'feature_importance': dict(zip(self.feature_names, self.model.feature_importances_))
        }
        
        print(f"✅ Modelo entrenado exitosamente")
        print(f"   - MAE Test: {metrics['mae_test']:.2f} minutos")
        print(f"   - R² Test: {metrics['r2_test']:.3f}")
        print(f"   - RMSE Test: {metrics['rmse_test']:.2f} minutos")
        
        return metrics
    
    def predict_time(self, features_dict):
        """
        Predice el tiempo de una ruta usando el modelo entrenado
        
        Args:
            features_dict: Diccionario con las features de la ruta
            
        Returns:
            float: Tiempo predicho en minutos
        """
        if self.model is None:
            print("❌ Modelo no entrenado. Usando estimación por defecto.")
            return self._default_prediction(features_dict)
        
        try:
            # Preparar features en el orden correcto
            features = []
            for feature in self.features:
                value = features_dict.get(feature, 0)
                if feature == 'temperatura_celsius' and value is None:
                    value = 25.0  # Temperatura por defecto
                features.append(value)
            
            # Convertir a array y escalar
            X = np.array(features).reshape(1, -1)
            X_scaled = self.scaler.transform(X)
            
            # Hacer predicción
            prediction = self.model.predict(X_scaled)[0]
            
            print(f"🤖 Predicción Random Forest: {prediction:.1f} minutos")
            return max(1.0, prediction)  # Mínimo 1 minuto
            
        except Exception as e:
            print(f"❌ Error en predicción: {str(e)}")
            return self._default_prediction(features_dict)
    
    def _default_prediction(self, features_dict):
        """Predicción por defecto usando la fórmula actual"""
        distancia_km = features_dict.get('distancia_km', 0)
        return distancia_km * 15  # 15 minutos por km
    
    def get_feature_importance(self):
        """Retorna la importancia de las features"""
        if self.model is None:
            return {}
        
        importance_dict = {}
        for feature, importance in zip(self.feature_names, self.model.feature_importances_):
            importance_dict[feature] = round(importance * 100, 2)
        
        # Ordenar por importancia
        return dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
    
    def save_model(self, filepath):
        """Guarda el modelo entrenado"""
        if self.model is None:
            print("❌ No hay modelo para guardar")
            return False
        
        try:
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Guardar modelo
            with open(filepath, 'wb') as f:
                pickle.dump({
                    'model': self.model,
                    'scaler': self.scaler,
                    'features': self.features,
                    'feature_names': self.feature_names
                }, f)
            
            print(f"✅ Modelo guardado en: {filepath}")
            return True
            
        except Exception as e:
            print(f"❌ Error guardando modelo: {str(e)}")
            return False
    
    def load_model(self, filepath):
        """Carga un modelo guardado"""
        try:
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
            
            self.model = data['model']
            self.scaler = data['scaler']
            self.features = data['features']
            self.feature_names = data['feature_names']
            
            print(f"✅ Modelo cargado desde: {filepath}")
            return True
            
        except Exception as e:
            print(f"❌ Error cargando modelo: {str(e)}")
            return False


def generate_sample_data(num_samples=50):
    """
    Genera datos de muestra para entrenar el modelo inicial
    
    Args:
        num_samples: Número de muestras a generar
        
    Returns:
        list: Lista de diccionarios con datos de muestra
    """
    print(f"🎲 Generando {num_samples} muestras de datos...")
    
    np.random.seed(42)
    sample_data = []
    
    for i in range(num_samples):
        # Generar features realistas
        distancia_km = np.random.uniform(0.5, 10.0)
        num_nodos = np.random.randint(5, 50)
        area_zona_m2 = np.random.uniform(50000, 500000)
        densidad_nodos_km2 = np.random.uniform(10, 100)
        densidad_calles_m_km2 = np.random.uniform(1000, 10000)
        experiencia_empleado_dias = np.random.randint(1, 365)
        hora_inicio = np.random.randint(6, 18)  # 6 AM a 6 PM
        dia_semana = np.random.randint(0, 7)
        temperatura_celsius = np.random.uniform(15, 35)
        
        # Calcular tiempo real basado en features (con ruido)
        base_time = distancia_km * 12  # 12 min/km base
        experience_factor = max(0.7, 1 - (experiencia_empleado_dias / 365) * 0.3)  # Experiencia reduce tiempo
        temperature_factor = 1 + abs(temperatura_celsius - 25) * 0.01  # Temperatura extrema aumenta tiempo
        density_factor = 1 + (densidad_nodos_km2 / 100) * 0.2  # Más densidad = más tiempo
        
        tiempo_real = base_time * experience_factor * temperature_factor * density_factor
        tiempo_real += np.random.normal(0, tiempo_real * 0.1)  # 10% de ruido
        tiempo_real = max(5, tiempo_real)  # Mínimo 5 minutos
        
        sample_data.append({
            'distancia_km': round(distancia_km, 2),
            'num_nodos': num_nodos,
            'area_zona_m2': round(area_zona_m2),
            'densidad_nodos_km2': round(densidad_nodos_km2, 1),
            'densidad_calles_m_km2': round(densidad_calles_m_km2),
            'experiencia_empleado_dias': experiencia_empleado_dias,
            'hora_inicio': hora_inicio,
            'dia_semana': dia_semana,
            'temperatura_celsius': round(temperatura_celsius, 1),
            'tiempo_real_minutos': round(tiempo_real, 1)
        })
    
    print(f"✅ Datos de muestra generados: {len(sample_data)} registros")
    return sample_data


def create_sample_rutas_completadas():
    """
    Crea registros de muestra en la base de datos para entrenar el modelo
    """
    try:
        from core.models import RutaCompletada, ColoniaProcesada, ConfiguracionRuta
        from accounts.models import User
        from datetime import datetime, timedelta
        
        # Verificar si ya hay datos
        if RutaCompletada.objects.count() > 0:
            print("ℹ️ Ya existen datos de rutas completadas")
            return
        
        # Obtener colonias y empleados existentes
        colonias = ColoniaProcesada.objects.all()
        empleados = User.objects.filter(role='employee')
        
        if not colonias.exists():
            print("❌ No hay colonias en la base de datos")
            return
        
        if not empleados.exists():
            print("❌ No hay empleados en la base de datos")
            return
        
        # Generar datos de muestra
        sample_data = generate_sample_data(50)
        
        # Crear registros en la base de datos
        for i, data in enumerate(sample_data):
            # Seleccionar colonia y empleado aleatoriamente
            colonia = np.random.choice(colonias)
            empleado = np.random.choice(empleados)
            
            # Crear configuración de ruta ficticia
            config_ruta = ConfiguracionRuta.objects.create(
                colonia=colonia,
                creado_por=empleado,
                estado='completada',
                tiempo_calculado=timedelta(minutes=data['tiempo_real_minutos'])
            )
            
            # Calcular fechas
            fecha_fin = datetime.now() - timedelta(days=np.random.randint(1, 30))
            fecha_inicio = fecha_fin - timedelta(minutes=data['tiempo_real_minutos'])
            
            # Crear ruta completada
            RutaCompletada.objects.create(
                colonia=colonia,
                empleado=empleado,
                configuracion_ruta=config_ruta,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                tiempo_real_minutos=data['tiempo_real_minutos'],
                tiempo_estimado_minutos=data['tiempo_real_minutos'] * 1.1,  # 10% más que el real
                distancia_km=data['distancia_km'],
                num_nodos=data['num_nodos'],
                area_zona_m2=data['area_zona_m2'],
                densidad_nodos_km2=data['densidad_nodos_km2'],
                densidad_calles_m_km2=data['densidad_calles_m_km2'],
                experiencia_empleado_dias=data['experiencia_empleado_dias'],
                hora_inicio=data['hora_inicio'],
                dia_semana=data['dia_semana'],
                temperatura_celsius=data['temperatura_celsius'],
                algoritmo_usado='kmeans'
            )
        
        print(f"✅ {len(sample_data)} registros de rutas completadas creados")
        
    except Exception as e:
        print(f"❌ Error creando datos de muestra: {str(e)}")
