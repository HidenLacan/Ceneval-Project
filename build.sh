#!/bin/bash

# Script para instalar dependencias sin compilación
echo "Instalando dependencias para deploy..."

# Actualizar pip
pip install --upgrade pip setuptools wheel

# Instalar numpy y scipy primero (wheels precompilados)
echo "Instalando numpy y scipy..."
pip install --only-binary=all numpy==2.2.6 scipy==1.11.4

# Instalar scikit-learn (wheel precompilado)
echo "Instalando scikit-learn..."
pip install --only-binary=all scikit-learn==1.3.2

# Instalar el resto de dependencias
echo "Instalando resto de dependencias..."
pip install --only-binary=all -r requirements-deploy.txt

# Verificar instalación
echo "Verificando instalación..."
python -c "import numpy; import scipy; import sklearn; print('Todas las dependencias instaladas correctamente')"

echo "Build completado exitosamente!"
