import sys
import os

# Añade el directorio src al PYTHONPATH para que los tests puedan encontrar los módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
