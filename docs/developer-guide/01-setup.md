# 🛠️ Configuración del Entorno de Desarrollo

## 📋 Requisitos Previos

### Sistema
- **Python 3.10+** (recomendado 3.11)
- **Git** para control de versiones
- **PostgreSQL 13+** (para producción) o **SQLite** (para desarrollo)

### Herramientas Recomendadas
- **VS Code** con extensiones de Python
- **Docker** (opcional, para base de datos)
- **Postman** o **Insomnia** (para testing de APIs)

## 🚀 Instalación Paso a Paso

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/diana-bot-v2.git
cd diana-bot-v2
```

### 2. Configurar Entorno Virtual
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Linux/Mac:
source venv/bin/activate
# En Windows:
venv\\Scripts\\activate
```

### 3. Instalar Dependencias
```bash
# Instalar dependencias principales
pip install -r requirements.txt

# Para desarrollo (incluye herramientas de testing)
pip install -e .
```

### 4. Configurar Variables de Entorno
```bash
# Copiar archivo de ejemplo
cp .env.example .env
```

Editar `.env` con tus configuraciones:
```bash
# Bot Configuration
BOT_TOKEN=tu_token_de_botfather
ENVIRONMENT=development

# Database
DATABASE_URL=sqlite:///bot.db
# Para PostgreSQL: postgresql://user:password@localhost/diana_bot

# External Services
DIANA_VALIDATION_URL=https://api.diana-validation.com
DIANA_API_KEY=tu_api_key

# Logging
LOG_LEVEL=DEBUG
ENABLE_SEXY_LOGGER=true

# Telegram
ADMIN_USER_IDS=123456789,987654321
```

### 5. Configurar Base de Datos

#### Opción A: SQLite (Desarrollo)
```bash
# La base de datos se crea automáticamente
python -c "from src.bot.database.engine import init_db; import asyncio; asyncio.run(init_db())"
```

#### Opción B: PostgreSQL (Producción)
```bash
# Crear base de datos
createdb diana_bot

# Ejecutar migraciones
alembic upgrade head
```

#### Opción C: Docker (Recomendado)
```bash
# Levantar PostgreSQL con Docker
docker run -d \
  --name diana-postgres \
  -e POSTGRES_DB=diana_bot \
  -e POSTGRES_USER=diana \
  -e POSTGRES_PASSWORD=your_password \
  -p 5432:5432 \
  postgres:13

# Actualizar DATABASE_URL en .env
DATABASE_URL=postgresql://diana:your_password@localhost:5432/diana_bot
```

### 6. Verificar Instalación
```bash
# Ejecutar tests básicos
python -m pytest tests/unit/basic/ -v

# Verificar que el bot puede iniciarse
python -c "from src.bot.core.containers import ApplicationContainer; print('✅ Container OK')"

# Test de conexión a base de datos
python test_env_setup.py
```

## 🔧 Configuración del IDE

### VS Code (Recomendado)
1. **Instalar extensiones**:
   ```json
   {
     "recommendations": [
       "ms-python.python",
       "ms-python.pylint", 
       "ms-python.black-formatter",
       "ms-python.isort",
       "littlefoxteam.vscode-python-test-adapter"
     ]
   }
   ```

2. **Configurar settings.json**:
   ```json
   {
     "python.defaultInterpreterPath": "./venv/bin/python",
     "python.linting.enabled": true,
     "python.linting.pylintEnabled": true,
     "python.formatting.provider": "black",
     "python.formatting.blackArgs": ["--line-length=88"],
     "python.sortImports.args": ["--profile", "black"],
     "python.testing.pytestEnabled": true,
     "python.testing.pytestArgs": ["tests/"]
   }
   ```

### PyCharm
1. **Configurar intérprete**: File > Settings > Project > Python Interpreter
2. **Configurar Black**: File > Settings > Tools > External Tools
3. **Configurar pytest**: Run > Edit Configurations > + > Python tests > pytest

## 🧪 Configuración de Testing

### Estructura de Tests
```
tests/
├── conftest.py              # Configuración global de pytest
├── unit/                    # Tests unitarios
│   ├── basic/              # Tests básicos de sistema
│   ├── core/               # Tests del núcleo
│   ├── services/           # Tests de servicios
│   └── handlers/           # Tests de handlers
└── integration/            # Tests de integración
    ├── test_full_flow.py   # Flujo completo
    └── test_telegram_flow.py # Integración con Telegram
```

### Ejecutar Tests
```bash
# Todos los tests
pytest

# Tests unitarios solamente
pytest tests/unit/

# Tests específicos
pytest tests/unit/core/test_event_bus.py -v

# Con cobertura
pytest --cov=src --cov-report=html

# Tests en modo watch (desarrollo)
ptw tests/unit/
```

### Configurar Pre-commit Hooks (Opcional)
```bash
# Instalar pre-commit
pip install pre-commit

# Configurar hooks
pre-commit install

# Ejecutar manualmente
pre-commit run --all-files
```

## 🐳 Configuración con Docker

### Dockerfile para Desarrollo
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copiar código
COPY . .

# Instalar en modo desarrollo
RUN pip install -e .

CMD ["python", "main.py"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  bot:
    build: .
    depends_on:
      - postgres
    environment:
      - DATABASE_URL=postgresql://diana:password@postgres:5432/diana_bot
    volumes:
      - .:/app
    command: python main.py

  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: diana_bot
      POSTGRES_USER: diana
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Ejecutar con Docker:
```bash
# Construir e iniciar
docker-compose up --build

# Solo la base de datos
docker-compose up postgres

# En background
docker-compose up -d
```

## 📊 Configuración de Monitoreo

### Logs de Desarrollo
El sistema incluye **Sexy Logger** para logs visuales:
```python
from src.utils.sexy_logger import log

# Diferentes tipos de logs
log.info("Información general")
log.success("Operación exitosa") 
log.warning("Advertencia importante")
log.error("Error crítico")
log.debug("Información de debug")

# Logs contextuales
log.database("Operación de BD", operation="select")
log.telegram("Mensaje enviado", user_id=123)
log.gamification("Puntos otorgados", points=50)
```

### Variables de Debug
```bash
# En .env para desarrollo
LOG_LEVEL=DEBUG
ENABLE_SEXY_LOGGER=true
TELEGRAM_TEST_MODE=true
SKIP_EXTERNAL_APIS=true
```

## 🔧 Troubleshooting

### Problemas Comunes

#### 1. Error de Token de Telegram
```
TelegramUnauthorizedError: Unauthorized
```
**Solución**: Verificar BOT_TOKEN en .env

#### 2. Error de Base de Datos
```
sqlalchemy.exc.OperationalError: no such table
```
**Solución**: 
```bash
alembic upgrade head
# o para SQLite:
python -c "from src.bot.database.engine import init_db; import asyncio; asyncio.run(init_db())"
```

#### 3. Importation Errors
```
ModuleNotFoundError: No module named 'src'
```
**Solución**: 
```bash
pip install -e .
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### 4. Puerto en Uso
```
OSError: [Errno 48] Address already in use
```
**Solución**:
```bash
# Encontrar y matar proceso
lsof -i :8080
kill -9 PID
```

### Verificación del Entorno
```bash
# Script de verificación completa
python scripts/verify_setup.py
```

### Logs Útiles para Debug
```bash
# Logs del bot en tiempo real
tail -f logs/diana_bot.log

# Logs de base de datos
tail -f logs/database.log

# Logs específicos de un módulo
grep "gamification" logs/diana_bot.log
```

## ✅ Checklist de Configuración

- [ ] Python 3.10+ instalado
- [ ] Entorno virtual creado y activado  
- [ ] Dependencias instaladas
- [ ] Variables de entorno configuradas
- [ ] Base de datos configurada
- [ ] Tests básicos pasan
- [ ] IDE configurado con extensiones
- [ ] Pre-commit hooks instalados (opcional)
- [ ] Docker configurado (opcional)

## 🚀 Próximos Pasos

Una vez completada la configuración:

1. **Lee la [Estructura del Proyecto](02-estructura.md)**
2. **Revisa las [Convenciones de Código](03-convenciones.md)**  
3. **Ejecuta los [Tests](04-testing.md)** para verificar todo funciona
4. **Consulta la [Guía de Contribución](05-contribucion.md)** antes de hacer cambios

---

¡Tu entorno está listo para desarrollar con Diana Bot V2! 🎉