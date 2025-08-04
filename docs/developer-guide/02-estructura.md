# 📁 Estructura del Proyecto

## 🎯 Visión General

Diana Bot V2 sigue una arquitectura **Clean Architecture** con separación clara de responsabilidades. La estructura está diseñada para ser **modular**, **testeable** y **escalable**.

## 🗂️ Estructura Completa del Directorio

```
V2/
├── 📄 main.py                          # 🚀 Punto de entrada principal
├── 📄 pyproject.toml                   # 📋 Configuración del proyecto
├── 📄 requirements.txt                 # 📦 Dependencias
├── 📄 README.md                        # 📖 Documentación principal
│
├── 🗂️ src/                             # 📚 Código fuente principal
│   ├── 🗂️ core/                        # 🔄 Núcleo del sistema
│   │   ├── event_bus.py                # Bus de eventos central
│   │   ├── interfaces/                 # Contratos e interfaces
│   │   │   ├── IEventBus.py           # Interface del event bus
│   │   │   └── ICoreService.py        # Interface de servicios core
│   │   └── services/                   # Servicios base
│   │       └── config.py              # Servicio de configuración
│   │
│   ├── 🗂️ modules/                     # 💼 Módulos de negocio
│   │   ├── admin/                     # 🛡️ Administración
│   │   │   ├── service.py             # Lógica administrativa
│   │   │   └── README.md              # Documentación del módulo
│   │   ├── gamification/              # 🎮 Gamificación
│   │   │   ├── service.py             # Sistema de puntos/misiones
│   │   │   ├── diana_missions.py      # Misiones específicas de Diana
│   │   │   └── README.md              # Documentación del módulo
│   │   ├── narrative/                 # 📖 Sistema narrativo
│   │   │   ├── service.py             # Lógica narrativa
│   │   │   ├── diana_integration.py   # Integración con Diana
│   │   │   └── README.md              # Documentación del módulo
│   │   ├── shop/                      # 🛒 Tienda
│   │   │   └── service.py             # Sistema de compras
│   │   ├── daily_rewards/             # 🎁 Regalos diarios
│   │   │   └── service.py             # Sistema de recompensas
│   │   ├── trivia/                    # 🧠 Trivias
│   │   │   └── service.py             # Sistema de preguntas
│   │   ├── emotional/                 # 🎭 Sistema emocional
│   │   │   ├── service.py             # Lógica emocional
│   │   │   ├── diana_state.py         # Estados de Diana
│   │   │   ├── middleware.py          # Middleware emocional
│   │   │   └── events.py              # Eventos emocionales
│   │   ├── user/                      # 👤 Gestión de usuarios
│   │   │   └── service.py             # Servicio de usuarios
│   │   ├── channel/                   # 📺 Gestión de canales
│   │   │   ├── service.py             # Lógica de canales
│   │   │   └── events.py              # Eventos de canal
│   │   ├── token/                     # 🎫 Sistema de tokens
│   │   │   ├── tokeneitor.py          # Generador de tokens
│   │   │   └── events.py              # Eventos de tokens
│   │   └── events.py                  # Eventos globales de módulos
│   │
│   ├── 🗂️ infrastructure/             # 💾 Implementaciones externas
│   │   ├── database/                  # Acceso a datos
│   │   └── telegram/                  # Integración con Telegram API
│   │       ├── adapter.py             # Adaptador principal
│   │       ├── handlers.py            # Handlers legacy (estables)
│   │       ├── keyboards.py           # Teclados base
│   │       └── listener.py            # Listener de eventos
│   │
│   ├── 🗂️ bot/                        # 🌐 Capa de presentación Telegram
│   │   ├── __main__.py                # Entrada alternativa del bot
│   │   ├── core/                      # 🎯 Componentes centrales del bot
│   │   │   ├── bootstrap.py           # Inicialización del sistema
│   │   │   ├── bot.py                 # Configuración principal del bot
│   │   │   ├── containers.py          # Contenedor de dependencias (DI)
│   │   │   ├── di.py                  # Sistema DI simple
│   │   │   ├── errors.py              # Manejo de errores
│   │   │   ├── handlers.py            # Configuración de handlers modernos
│   │   │   ├── middleware.py          # Middlewares del bot
│   │   │   ├── orchestrator.py        # 🎭 Facade principal (CRÍTICO)
│   │   │   └── scheduler.py           # Programador de tareas
│   │   ├── config/                    # ⚙️ Configuración del bot
│   │   │   ├── constants.py           # Constantes del sistema
│   │   │   └── settings.py            # Configuraciones
│   │   ├── database/                  # 🗄️ Capa de datos
│   │   │   ├── base.py                # Base de modelos
│   │   │   ├── engine.py              # Motor de BD
│   │   │   ├── bot.db                 # BD SQLite (desarrollo)
│   │   │   ├── migrations/            # Migraciones de Alembic
│   │   │   │   └── versions/          # Versiones de migración
│   │   │   └── models/                # 📊 Modelos de datos
│   │   │       ├── admin.py           # Modelo administrativo
│   │   │       ├── channel.py         # Modelo de canales
│   │   │       ├── emotional.py       # Modelo emocional
│   │   │       ├── gamification.py    # Modelo de gamificación
│   │   │       ├── narrative.py       # Modelo narrativo
│   │   │       ├── token.py           # Modelo de tokens
│   │   │       └── user.py            # Modelo de usuarios
│   │   ├── filters/                   # 🔍 Filtros de Telegram
│   │   │   ├── is_admin.py            # Filtro de administrador
│   │   │   └── role.py                # Filtros de roles
│   │   ├── handlers/                  # 🎮 Manejadores de comandos (MODERNOS)
│   │   │   ├── admin/                 # 🛡️ Handlers administrativos
│   │   │   │   ├── main.py            # Comando /admin principal
│   │   │   │   ├── callbacks.py       # Callbacks de admin
│   │   │   │   ├── role_management.py # Gestión de roles
│   │   │   │   ├── tariff.py          # Gestión de tarifas
│   │   │   │   └── token_callbacks.py # Callbacks de tokens
│   │   │   ├── user/                  # 👤 Handlers de usuario
│   │   │   │   ├── start.py           # Comando /start
│   │   │   │   ├── help.py            # Comando /help
│   │   │   │   ├── profile.py         # Comando /profile
│   │   │   │   ├── info.py            # Información del usuario
│   │   │   │   ├── shop.py            # Comando /shop
│   │   │   │   ├── daily_rewards.py   # Comando /daily
│   │   │   │   ├── trivia.py          # Comando /trivia
│   │   │   │   └── token_redemption.py # Canje de tokens
│   │   │   ├── gamification/          # 🎮 Handlers de gamificación
│   │   │   │   ├── misiones.py        # Comando /misiones
│   │   │   │   └── progress.py        # Progreso del usuario
│   │   │   └── narrative/             # 📖 Handlers narrativos
│   │   │       ├── mochila.py         # Comando /mochila
│   │   │       └── navigation.py      # Navegación narrativa
│   │   ├── keyboards/                 # ⌨️ Teclados y UI
│   │   │   ├── keyboard_factory.py    # Factory de teclados
│   │   │   ├── admin_keyboards.py     # Teclados administrativos
│   │   │   └── admin/                 # Teclados específicos de admin
│   │   │       └── main_kb.py         # Teclado principal admin
│   │   ├── listeners/                 # 👂 Listeners de eventos
│   │   │   └── mission_listener.py    # Listener de misiones
│   │   ├── middlewares/               # 🔀 Middlewares específicos
│   │   │   ├── admin.py               # Middleware de admin
│   │   │   ├── database.py            # Middleware de BD
│   │   │   ├── emotional.py           # Middleware emocional
│   │   │   ├── points.py              # Middleware de puntos
│   │   │   ├── role.py                # Middleware de roles
│   │   │   ├── throttling.py          # Middleware de rate limiting
│   │   │   └── user.py                # Middleware de usuario
│   │   ├── services/                  # 🔧 Servicios del bot (Bridge Layer)
│   │   │   ├── base.py                # Servicio base
│   │   │   ├── admin.py               # Servicio admin (bridge)
│   │   │   ├── emotional.py           # Servicio emocional (bridge)
│   │   │   ├── gamification.py        # Servicio gamificación (bridge)
│   │   │   ├── narrative.py           # Servicio narrativo (bridge)
│   │   │   ├── role.py                # Servicio de roles
│   │   │   └── user.py                # Servicio de usuarios (bridge)
│   │   └── tasks/                     # 📅 Tareas programadas
│   │       ├── role_maintenance.py    # Mantenimiento de roles
│   │       └── subscription.py        # Mantenimiento de suscripciones
│   │
│   └── 🗂️ utils/                      # 🛠️ Utilidades
│       └── sexy_logger.py             # Sistema de logging visual
│
├── 🗂️ tests/                          # 🧪 Pruebas
│   ├── conftest.py                    # Configuración global de pytest
│   ├── integration/                   # Pruebas de integración
│   │   ├── conftest.py                # Config de integración
│   │   ├── run_manual_test.py         # Tests manuales
│   │   ├── test_admin_flow.py         # Flujo administrativo
│   │   ├── test_diana_validation_integration.py # Integración Diana
│   │   ├── test_full_flow.py          # Flujo completo
│   │   ├── test_gamification_integration.py # Integración gamificación
│   │   ├── test_narrative_flow.py     # Flujo narrativo
│   │   ├── test_telegram_flow.py      # Flujo de Telegram
│   │   └── test_user_flow.py          # Flujo de usuario
│   └── unit/                          # Pruebas unitarias
│       ├── basic/                     # Tests básicos
│       │   └── test_basic.py          # Tests fundamentales
│       ├── core/                      # Tests del núcleo
│       │   ├── services/              # Tests de servicios core
│       │   │   └── test_config.py     # Test de configuración
│       │   └── test_containers.py     # Test de contenedores
│       ├── emotional/                 # Tests del sistema emocional
│       │   ├── conftest.py            # Config emocional
│       │   ├── test_basic_functionality.py # Funcionalidad básica
│       │   ├── test_diana_state.py    # Estados de Diana
│       │   └── test_emotional_service.py # Servicio emocional
│       ├── handlers/                  # Tests de handlers
│       │   ├── conftest.py            # Config handlers
│       │   ├── test_start_handler.py  # Handler de start
│       │   ├── test_start_handler_fixed.py # Handler start corregido
│       │   └── test_user_handlers.py  # Handlers de usuario
│       ├── keyboards/                 # Tests de teclados
│       │   └── test_keyboard_factory.py # Factory de teclados
│       ├── services/                  # Tests de servicios
│       ├── tokeneitor_tests/          # Tests del sistema de tokens
│       │   └── test_tokeneitor.py     # Tokeneitor tests
│       ├── test_admin_service.py      # Test servicio admin
│       ├── test_core.py               # Tests del core
│       └── test_event_bus.py          # Tests del event bus
│
├── 🗂️ docs/                           # 📚 Documentación
│   ├── README.md                      # Índice de documentación
│   ├── ARCHIVE.md                     # Documentación histórica
│   ├── HANDLERS_ARCHITECTURE_GUIDE.md # ⚠️ GUÍA CRÍTICA DE HANDLERS
│   ├── inventario_funciones.md       # 📋 Inventario completo de funciones
│   ├── ANALISIS_ECOSISTEMA_UNIFICADO.md # 🔱 Análisis del ecosistema
│   ├── user-guide/                   # Guías para usuarios
│   ├── developer-guide/              # Guías para desarrolladores
│   ├── architecture/                 # Documentación arquitectónica
│   ├── api/                          # Documentación de API
│   └── deployment/                   # Guías de despliegue
│
├── 🗂️ examples/                       # 📝 Ejemplos de código
│   └── diana_integration_example.py   # Ejemplo de integración Diana
│
├── 🗂️ scripts/                        # 📜 Scripts de utilidad
│
├── 🗂️ archive-docs/                   # 📁 Documentación archivada
│   └── [documentos históricos]        # Documentos consolidados
│
├── 🗂️ remp_narrativa/                 # 📖 Recursos narrativos temporales
│   ├── diana_validation_client.py     # Cliente de validación Diana
│   ├── ejemplo_integracion_diana.py   # Ejemplo de integración
│   ├── funcionalidades.md            # Funcionalidades narrativas
│   ├── guia_logger.md                # Guía del logger
│   ├── guía.md                       # Guía general
│   ├── sexy_logger.py                # Logger específico
│   └── unificado.md                  # Análisis unificado
│
├── 📄 test_env_setup.py               # Test de configuración del entorno
├── 📄 test_integration_basic.py       # Test de integración básica
├── 📄 run_tests.py                    # Runner de tests
├── 📄 fix.sql                         # Script de corrección SQL
└── 📄 nano                            # Archivo temporal
```

## 🎯 Patrones Arquitectónicos Implementados

### 1. **Clean Architecture**
```
🌐 Presentation Layer    ← src/bot/ (Telegram-specific)
🎯 Application Layer     ← src/bot/core/ (orchestrator, handlers)
💼 Business Layer        ← src/modules/ (domain logic)
🔄 Core Layer           ← src/core/ (event bus, interfaces)
💾 Infrastructure Layer  ← src/infrastructure/ (external services)
```

### 2. **Dependency Injection**
```python
# Contenedor principal en src/bot/core/containers.py
class ApplicationContainer(DeclarativeContainer):
    # Core services
    event_bus = providers.Singleton(EventBus)
    central_config = providers.Singleton(CentralConfig)
    
    # Module services
    gamification_service = providers.Factory(
        GamificationService,
        event_bus=event_bus
    )
```

### 3. **Event-Driven Architecture**
```python
# Event Bus central en src/core/event_bus.py
await event_bus.publish(UserActionEvent(
    user_id=123,
    action="trivia_completed"
))

# Servicios reaccionan automáticamente
gamification_service.on_user_action()  # Otorga puntos
narrative_service.on_user_action()     # Desbloquea contenido
```

### 4. **Facade Pattern**
```python
# Bot Orchestrator en src/bot/core/orchestrator.py
class BotOrchestrator:
    """Facade principal que coordina todos los servicios."""
    
    async def handle_user_message(self, user_id, message):
        # Coordina: user → emotional → gamification → narrative
        pass
```

## 🔍 Responsabilidades por Capa

### 🌐 **Presentation Layer** (`src/bot/`)
**Responsabilidad**: Interfaz con Telegram API
- **Handlers**: Procesamiento de comandos y callbacks
- **Keyboards**: Generación de interfaces de usuario
- **Middlewares**: Preprocessing de mensajes
- **Filters**: Validación de permisos y contexto

### 🎯 **Application Layer** (`src/bot/core/`)
**Responsabilidad**: Orquestación y coordinación
- **Orchestrator**: Facade principal del sistema
- **Containers**: Inyección de dependencias
- **Bootstrap**: Inicialización del sistema
- **Handlers Setup**: Configuración de manejadores

### 💼 **Business Layer** (`src/modules/`)
**Responsabilidad**: Lógica de negocio pura
- **Services**: Reglas de dominio específicas
- **Events**: Eventos de negocio
- **Domain Logic**: Algoritmos y cálculos

### 🔄 **Core Layer** (`src/core/`)
**Responsabilidad**: Infraestructura central
- **Event Bus**: Comunicación entre módulos
- **Interfaces**: Contratos del sistema
- **Base Services**: Servicios fundamentales

### 💾 **Infrastructure Layer** (`src/infrastructure/`)
**Responsabilidad**: Servicios externos
- **Telegram Adapter**: Integración con Telegram
- **Database**: Acceso a datos
- **External APIs**: Servicios de terceros

## ⚠️ **Arquitectura Híbrida Actual**

### 🚨 **IMPORTANTE: Sistema de Handlers Dual**

El proyecto actualmente maneja **DOS sistemas de handlers**:

#### ✅ **Sistema Legacy (ACTIVO)**
- **Ubicación**: `src/infrastructure/telegram/handlers.py`
- **Estado**: Estable, en producción
- **Funcionalidades**: Comando `/admin`, gestión VIP, tokens

#### 🏗️ **Sistema Moderno (EN INTEGRACIÓN)**
- **Ubicación**: `src/bot/handlers/`
- **Estado**: UI moderna, integrándose gradualmente
- **Funcionalidades**: Nuevos comandos, interfaces avanzadas

**📖 Ver**: `docs/HANDLERS_ARCHITECTURE_GUIDE.md` para detalles completos

## 📊 **Estado de Implementación por Módulo**

| Módulo | Core Logic | API | Event Integration | Tests | Handlers |
|--------|------------|-----|-------------------|-------|----------|
| 🛒 Shop | ✅ 100% | ✅ 100% | ✅ 100% | ✅ 95% | ✅ Ready |
| 🎁 Daily Rewards | ✅ 100% | ✅ 100% | ✅ 100% | ✅ 90% | ✅ Ready |
| 🧠 Trivia | ✅ 100% | ✅ 100% | ✅ 100% | ✅ 85% | ✅ Ready |
| 🎮 Gamification | ✅ 100% | ✅ 100% | ✅ 100% | ✅ 90% | ✅ Ready |
| 🛡️ Admin | ✅ 100% | ✅ 100% | ✅ 100% | ✅ 80% | ✅ Active |
| 📖 Narrative | ✅ 80% | ✅ Event-Driven | ✅ 100% | ✅ 70% | 🔄 Integrating |
| 🎭 Emotional | ✅ 90% | ✅ State-Based | ✅ 100% | ✅ 75% | 🔄 Integrating |

## 🔧 **Puntos de Entrada Críticos**

### **1. Inicio Principal**
```python
# main.py → punto de entrada único
async def main():
    # Inicializa: EventBus → Services → TelegramAdapter
    event_bus = EventBus()
    services = setup_services(event_bus)
    adapter = TelegramAdapter(services)
    await adapter.start()
```

### **2. Orchestrador (Facade)**
```python
# src/bot/core/orchestrator.py → coordinación central
class BotOrchestrator:
    async def handle_user_message(self, user_id, message):
        # 1. Get user profile
        # 2. Process through emotional system  
        # 3. Update gamification
        # 4. Record narrative interaction
        # 5. Generate response
        pass
```

### **3. Event Bus (Comunicación)**
```python
# src/core/event_bus.py → comunicación central
class EventBus:
    async def publish(self, event):
        # Notifica a todos los suscriptores automáticamente
        pass
```

## 🧪 **Estructura de Testing**

### **Tests Unitarios** (`tests/unit/`)
- **Aislamiento**: Cada módulo por separado
- **Mocking**: Dependencias mockeadas
- **Coverage**: >80% para módulos críticos

### **Tests de Integración** (`tests/integration/`)
- **End-to-End**: Flujos completos de usuario
- **Event Bus**: Verificación de integración via eventos
- **Database**: Tests con BD real

### **Tests Manuales**
- **`run_manual_test.py`**: Tests interactivos
- **Environment Testing**: Verificación de configuración

## 📁 **Archivos de Configuración Clave**

### **Dependencias**
- `requirements.txt` - Dependencias de producción
- `pyproject.toml` - Configuración del proyecto y dev dependencies

### **Base de Datos**
- `src/bot/database/engine.py` - Configuración de BD
- `src/bot/database/models/` - Modelos SQLAlchemy
- Migraciones Alembic en `src/bot/database/migrations/`

### **Configuración**
- `.env` - Variables de entorno (no versionado)
- `src/bot/config/settings.py` - Configuración centralizada
- `src/bot/config/constants.py` - Constantes del sistema

## 🚀 **Próximos Pasos Arquitectónicos**

### **Inmediatos**
1. **Completar migración** del sistema de handlers dual
2. **Integrar narrative service** completamente en UI
3. **Optimizar** bot orchestrator para mayor performance

### **Medio Plazo**
1. **Implementar caching** para servicios frecuentes
2. **Añadir monitoring** y métricas avanzadas
3. **Migrar a microservicios** módulos independientes

### **Largo Plazo**
1. **API REST/GraphQL** para acceso externo
2. **Dashboard web** para administración
3. **AI Integration** en emotional y narrative services

---

*Esta estructura ha sido optimizada para **mantenibilidad**, **escalabilidad** y **testabilidad**, siguiendo las mejores prácticas de Clean Architecture.*