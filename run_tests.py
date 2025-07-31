
import sys
import os
import pytest

if __name__ == "__main__":
    # Añadir el directorio src al PYTHONPATH
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
    
    # Ejecutar pytest
    sys.exit(pytest.main())
