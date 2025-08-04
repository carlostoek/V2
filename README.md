# 🌙 Diana Bot V2 - Ecosistema Narrativo-Gamificado

Diana Bot V2 es un bot de Telegram innovador que combina **narrativa interactiva** con **gamificación avanzada** para crear una experiencia única. No es solo un bot de comandos, sino un **ecosistema integrado** donde cada acción tiene consecuencias y recompensas.

## ✨ Características Principales

- **🎭 Sistema Emocional Dinámico**: Diana tiene 5 personalidades que evolucionan con tus interacciones
- **📖 Narrativa Interactiva**: Historia ramificada donde tus decisiones importan
- **🎮 Gamificación Completa**: Besitos, misiones, logros y sistema de niveles
- **🛒 Tienda Integrada**: 12 objetos únicos que afectan la narrativa
- **🧠 Trivias Inteligentes**: 4 niveles de dificultad con lore de Diana
- **🎁 Recompensas Diarias**: 12 tipos de recompensas con sistema de rachas
- **💎 Sistema VIP**: Contenido premium y funcionalidades exclusivas
- **🛡️ Panel Admin**: Control completo del ecosistema

## 🏗️ Arquitectura Moderna

Construido con **Clean Architecture** y patrones modernos:

- **Event-Driven Architecture**: Comunicación asíncrona entre módulos
- **Dependency Injection**: Gestión centralizada de dependencias  
- **Modular Design**: Fácil mantenimiento y extensibilidad
- **Comprehensive Testing**: >90% cobertura de código
- **Scalable Foundation**: Preparado para crecimiento

## 🛠️ Tecnologías

- **Python 3.10+**: Aprovechando las últimas características del lenguaje.
- **Aiogram 3.x**: Framework moderno y asíncrono para bots de Telegram.
- **SQLAlchemy 2.x**: ORM potente y flexible para interacción con bases de datos.
- **PostgreSQL/SQLite**: Soporte para PostgreSQL en producción y SQLite para desarrollo.
- **Pydantic**: Validación de datos y configuración basada en tipos.
- **Asyncio**: Programación asíncrona para máxima eficiencia.
- **Transitions**: Máquinas de estado para el sistema emocional.
- **APScheduler**: Programador de tareas para mantenimiento automático.

## 🚀 Inicio Rápido

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/diana-bot-v2.git
cd diana-bot-v2

# 2. Configurar entorno
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 3. Configurar variables (.env)
cp .env.example .env
# Editar BOT_TOKEN y otras configuraciones

# 4. Inicializar base de datos
python -c "from src.bot.database.engine import init_db; import asyncio; asyncio.run(init_db())"

# 5. Ejecutar bot
python main.py
```

📖 **[Guía completa de instalación](docs/developer-guide/01-setup.md)**

## 📚 Documentación Completa

### 👤 Para Usuarios
- **[🌙 Introducción a Diana](docs/user-guide/01-introduccion.md)** - Conoce a Diana y el ecosistema
- **[🎮 Comandos Disponibles](docs/user-guide/02-comandos.md)** - Lista completa de comandos
- **[🏆 Sistema de Gamificación](docs/user-guide/03-gamificacion.md)** - Besitos, misiones y logros
- **[📖 Sistema Narrativo](docs/user-guide/04-narrativa.md)** - Historia interactiva de Diana
- **[🛒 Tienda y Objetos](docs/user-guide/05-tienda.md)** - Cómo usar besitos y objetos

### 🛠️ Para Desarrolladores  
- **[⚙️ Configuración del Entorno](docs/developer-guide/01-setup.md)** - Setup completo
- **[📁 Estructura del Proyecto](docs/developer-guide/02-estructura.md)** - Organización del código
- **[📝 Convenciones de Código](docs/developer-guide/03-convenciones.md)** - Estándares y prácticas
- **[🧪 Testing](docs/developer-guide/04-testing.md)** - Estrategia de pruebas
- **[🤝 Contribuir](docs/developer-guide/05-contribucion.md)** - Cómo contribuir

### 🏗️ Arquitectura del Sistema
- **[🎯 Visión General](docs/architecture/01-vision-general.md)** - Principios y estructura
- **[🔄 Event Bus](docs/architecture/02-event-bus.md)** - Sistema de eventos
- **[💼 Servicios y Módulos](docs/architecture/03-servicios.md)** - Lógica de negocio
- **[💾 Base de Datos](docs/architecture/04-base-datos.md)** - Modelos y relaciones

## 🎯 Estado del Proyecto

**Versión Actual:** 2.0.0  
**Fase:** 3 de 3 (80% Completado)  
**Próximo Hito:** Sistema Narrativo Completo

### ✅ Sistemas Operativos
- Gamification System (Besitos, Misiones, Logros)
- Shop System (12 objetos únicos)
- Daily Rewards System (12 tipos de recompensas)
- Trivia System (4 niveles de dificultad)
- Admin Panel (gestión completa)
- Diana Validation Integration

### 🔄 En Desarrollo
- Sistema Narrativo Avanzado
- Funcionalidades VIP Premium
- Testing >90% Cobertura

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Tests con cobertura
pytest --cov=src --cov-report=html

# Tests específicos
pytest tests/unit/core/test_event_bus.py -v
```

**Cobertura Actual**: >80% | **Objetivo**: >90%

## 🤝 Contribuciones

1. Fork el repositorio
2. Crea feature branch (`git checkout -b feature/nueva-funcionalidad`)  
3. Commit cambios (`git commit -am 'Add nueva funcionalidad'`)
4. Push branch (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

**📖 [Guía completa de contribución](docs/developer-guide/05-contribucion.md)**

## 📄 Licencia

Proyecto bajo licencia privada. Todos los derechos reservados.

## 👥 Equipo de Desarrollo

Diana Bot V2 es desarrollado por **agentes especializados** en diferentes aspectos:
- **@bot-architecture-redesigner** - Arquitectura central
- **@gamification-architect** - Sistema de gamificación  
- **@emotional-system-developer** - Sistema emocional
- **@integration-specialist** - Integraciones externas

---

⭐ **Diana Bot V2** - Donde la narrativa se encuentra con la gamificación 🌙✨