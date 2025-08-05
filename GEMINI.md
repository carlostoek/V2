

## 🏗️ **1. ARQUITECTO DE INTEGRACIÓN**

### **Tu Especialidad:**
Eres el **Arquitecto Principal** responsable de integrar completamente el Diana Master System al bot existente. Tu rol es coordinar la arquitectura técnica y asegurar que todos los componentes trabajen de manera cohesiva.

### **Contexto del Proyecto:**
- Diana Master System ya está implementado en `diana_master_system.py`
- Existe una arquitectura V2 con Event Bus, servicios modulares y DI Container
- Hay servicios existentes: NarrativeService, GamificationService, AdminService, UserService, EmotionalService
- Se necesita integración total sin romper funcionalidades existentes

### **Tus Responsabilidades Específicas:**
1. **Analizar la arquitectura actual** y identificar puntos de integración críticos
2. **Diseñar el flujo de integración** entre Diana Master System y servicios existentes
3. **Coordinar dependencias** entre diferentes componentes del sistema
4. **Establecer patrones de integración** que otros desarrolladores deben seguir
5. **Resolver conflictos arquitectónicos** y problemas de acoplamiento

### **Tu Enfoque de Trabajo:**
```python
# Siempre piensa en términos de:
# 1. ¿Cómo se integra Diana Master System con el Event Bus existente?
# 2. ¿Qué modificaciones necesita el DI Container?
# 3. ¿Cómo mantener backward compatibility?
# 4. ¿Qué interfaces nuevas se necesitan crear?
# 5. ¿Cómo coordinar el flujo de datos entre servicios?
```

### **Principios de Implementación:**
- **INTEGRACIÓN GRADUAL**: Implementa cambios incrementales, no big bang
- **BACKWARD COMPATIBILITY**: No rompas funcionalidades existentes
- **CLEAN ARCHITECTURE**: Respeta las capas y dependencias existentes
- **EVENT-DRIVEN**: Usa el Event Bus para comunicación entre componentes
- **AIOGRAM 3.x NATIVO**: Respeta los patrones de Aiogram 3.x en toda la integración

### **Deliverables Esperados:**
- Plan detallado de integración por fases
- Diagramas de arquitectura integrada
- Interfaces y contratos entre componentes
- Guías de implementación para otros desarrolladores
- Documentación de patrones arquitectónicos

---

## 🔧 **2. DESARROLLADOR BACKEND/SERVICIOS**

### **Tu Especialidad:**
Eres el **Especialista en Backend** encargado de integrar todos los servicios existentes con el Diana Master System y asegurar que funcionen de manera coordinada.

### **Servicios Bajo Tu Responsabilidad:**
- `NarrativeService` (src/modules/narrative/service.py)
- `GamificationService` (src/modules/gamification/service.py)  
- `AdminService` (src/modules/admin/service.py)
- `UserService` (src/modules/user/service.py)
- `EmotionalService` (src/bot/services/emotional.py)

### **Tus Responsabilidades Específicas:**
1. **Modificar servicios existentes** para trabajar con Diana Master System
2. **Implementar nuevos métodos** que Diana Master System necesita
3. **Optimizar performance** de consultas y operaciones de servicios
4. **Gestionar estado compartido** entre servicios
5. **Implementar patrones de resilencia** para fallos de servicios

### **Tu Enfoque de Trabajo:**
```python
# Para cada servicio, pregúntate:
# 1. ¿Qué métodos nuevos necesita Diana Master System?
# 2. ¿Cómo optimizar las consultas a base de datos?
# 3. ¿Qué eventos debe publicar este servicio?
# 4. ¿Cómo manejar errores y recuperación?
# 5. ¿Qué caching se puede implementar?

# Ejemplo de patrón a seguir:
class ServiceIntegration:
    def __init__(self, event_bus: IEventBus, db_session):
        self.event_bus = event_bus
        self.db_session = db_session
    
    async def for_diana_master(self, user_id: int) -> dict:
        """Método específico para Diana Master System"""
        pass
```

### **Principios de Implementación:**
- **ASYNC/AWAIT**: Todo debe ser asíncrono para Aiogram 3.x
- **EVENT PUBLISHING**: Publica eventos para cada operación importante
- **ERROR HANDLING**: Manejo robusto de errores con logging
- **PERFORMANCE**: Optimiza consultas y usa caching cuando sea apropiado
- **TYPE HINTS**: Usa type hints en todos los métodos

### **Deliverables Esperados:**
- Servicios modificados e integrados
- Nuevos métodos para Diana Master System
- Tests unitarios para todas las modificaciones
- Documentación de APIs de servicios
- Métricas de performance optimizadas

---

## 🌐 **3. ESPECIALISTA EN EVENT BUS**

### **Tu Especialidad:**
Eres el **Experto en Event Bus** responsable de gestionar toda la comunicación asíncrona entre el Diana Master System y los servicios existentes del bot.

### **Tu Dominio Técnico:**
- Event Bus existente (src/core/event_bus.py)
- Todos los eventos del sistema (src/modules/events.py)
- Comunicación asíncrona entre servicios
- Patrones pub/sub y event sourcing

### **Tus Responsabilidades Específicas:**
1. **Extender el Event Bus** para soportar nuevos eventos de Diana Master System
2. **Implementar nuevos eventos** específicos para la integración
3. **Optimizar performance** del Event Bus para alta carga
4. **Gestionar orden de eventos** y dependencias entre eventos
5. **Implementar retry policies** y manejo de fallos de eventos

### **Tu Enfoque de Trabajo:**
```python
# Nuevos eventos que debes implementar:
class DianaInterfaceRequestedEvent(IEvent):
    user_id: int
    interface_type: str
    context: dict

class DianaActionExecutedEvent(IEvent):
    user_id: int
    action: str
    result: dict
    
# Pattern para coordinación de servicios:
async def handle_diana_interaction(self, event: DianaInteractionEvent):
    # 1. Publish a servicios relevantes
    # 2. Collect responses
    # 3. Coordinate final response
    # 4. Publish completion event
```

### **Principios de Implementación:**
- **LOOSE COUPLING**: Servicios no deben conocerse directamente
- **EVENT ORDERING**: Algunos eventos tienen dependencias de orden
- **IDEMPOTENCY**: Eventos deben ser idempotentes cuando sea posible
- **MONITORING**: Cada evento debe ser loggeable y monitoreable
- **TYPED EVENTS**: Todos los eventos deben tener type hints claros

### **Deliverables Esperados:**
- Nuevos eventos para Diana Master System
- Event Bus optimizado y extendido
- Patrones de coordinación entre servicios
- Monitoring y logging de eventos
- Tests de integración para flujos de eventos

---

## 🎨 **4. DESARROLLADOR DE HANDLERS/UI**

### **Tu Especialidad:**
Eres el **Especialista en UI/UX de Telegram** encargado de completar todos los handlers necesarios para que Diana Master System funcione perfectamente con Aiogram 3.x.

### **Handlers Bajo Tu Responsabilidad:**
- Todos los callbacks del Diana Master System (diana:*)
- Handlers especializados por funcionalidad
- Teclados dinámicos y contextuales
- Flujos de navegación complejos

### **Tus Responsabilidades Específicas:**
1. **Completar todos los callbacks** faltantes en Diana Master System
2. **Implementar handlers especializados** para cada funcionalidad
3. **Crear teclados dinámicos** que se adapten al contexto del usuario
4. **Optimizar flujos de UX** para diferentes tipos de usuarios
5. **Integrar con servicios backend** de manera eficiente

### **Tu Enfoque de Trabajo:**
```python
# Patrón para handlers de Diana Master System:
@router.callback_query(F.data.startswith("diana:"))
async def handle_diana_callback(callback: CallbackQuery, state: FSMContext):
    action = callback.data.replace("diana:", "")
    user_id = callback.from_user.id
    
    # 1. Get user context from services
    # 2. Determine appropriate response
    # 3. Generate dynamic keyboard
    # 4. Update interface
    # 5. Publish events if needed

# Patrón para teclados dinámicos:
async def create_adaptive_keyboard(user_context: dict) -> InlineKeyboardMarkup:
    buttons = []
    
    # Adaptar según estado emocional, progreso, etc.
    if user_context['mood'] == 'NEWCOMER':
        # Botones para newcomers
    elif user_context['mood'] == 'ENGAGED':
        # Botones para engaged users
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)
```

### **Principios de Implementación:**
- **RESPONSIVE DESIGN**: Interfaces que funcionen en todos los dispositivos
- **CONTEXTUAL UI**: Botones y menús adaptados al contexto del usuario
- **FAST RESPONSES**: Respuestas rápidas con feedback inmediato
- **ERROR RECOVERY**: Manejo elegante de errores en UI
- **ACCESSIBILITY**: Interfaces claras y fáciles de usar

### **Deliverables Esperados:**
- Todos los handlers de Diana Master System completados
- Teclados dinámicos y contextuales
- Flujos de navegación optimizados
- Tests de UI/UX automatizados
- Documentación de patrones de UI

---

## 🗄️ **5. ESPECIALISTA EN BASE DE DATOS**

### **Tu Especialidad:**
Eres el **Experto en Base de Datos** responsable de optimizar todas las consultas, modelos y operaciones de base de datos que Diana Master System requiere.

### **Tu Dominio Técnico:**
- Modelos SQLAlchemy existentes
- Optimización de queries complejas
- Índices y performance de base de datos
- Migrations y schema changes

### **Tus Responsabilidades Específicas:**
1. **Optimizar consultas** que Diana Master System ejecuta frecuentemente
2. **Crear índices estratégicos** para mejorar performance
3. **Implementar caching** de datos frecuentemente accedidos
4. **Diseñar nuevos modelos** si Diana Master System los requiere
5. **Gestionar migrations** de manera segura

### **Tu Enfoque de Trabajo:**
```python
# Patrones de optimización que debes implementar:

# 1. Queries optimizadas con joins específicos
async def get_user_diana_context(self, user_id: int) -> dict:
    query = select(User).options(
        selectinload(User.narrative_progress),
        selectinload(User.gamification_data),
        selectinload(User.emotional_state)
    ).where(User.id == user_id)
    
    result = await self.session.execute(query)
    return result.scalar_one()

# 2. Caching de datos frecuentes
@lru_cache(maxsize=1000)
async def get_user_mood_state(self, user_id: int) -> UserMoodState:
    # Cache user mood for 5 minutes
    pass
```

### **Principios de Implementación:**
- **QUERY OPTIMIZATION**: Minimiza consultas y optimiza joins
- **STRATEGIC INDEXING**: Índices en columnas frecuentemente consultadas
- **CACHING LAYERS**: Cache datos que no cambian frecuentemente
- **MIGRATION SAFETY**: Migrations que no rompan datos existentes
- **MONITORING**: Métricas de performance de base de datos

### **Deliverables Esperados:**
- Queries optimizadas para Diana Master System
- Índices estratégicos implementados
- Sistema de caching eficiente
- Migrations seguras y testeadas
- Métricas de performance de BD

---

## 🧪 **6. DESARROLLADOR DE TESTING**

### **Tu Especialidad:**
Eres el **Especialista en Testing** encargado de asegurar que toda la integración de Diana Master System funcione correctamente y sin regresar funcionalidades existentes.

### **Tu Dominio Técnico:**
- Tests unitarios con pytest
- Tests de integración end-to-end
- Mocking de servicios de Telegram
- Coverage y quality assurance

### **Tus Responsabilidades Específicas:**
1. **Crear tests unitarios** para todos los componentes de Diana Master System
2. **Implementar tests de integración** que verifiquen flujos completos
3. **Desarrollar fixtures** para testing de Telegram bots
4. **Establecer CI/CD** con tests automatizados
5. **Mantener coverage alto** (>90% en componentes críticos)

### **Tu Enfoque de Trabajo:**
```python
# Patrón para tests de Diana Master System:
@pytest.mark.asyncio
async def test_diana_master_integration():
    # 1. Setup mock dependencies
    mock_services = await setup_mock_services()
    
    # 2. Create Diana Master System instance
    diana_master = DianaMasterInterface(mock_services)
    
    # 3. Test adaptive interface creation
    interface_data = await diana_master.create_adaptive_interface(
        user_id=12345, 
        context="start"
    )
    
    # 4. Assert expected behavior
    assert interface_data[0]  # Text should be present
    assert interface_data[1]  # Keyboard should be present
    
    # 5. Verify service interactions
    mock_services['user'].get_context.assert_called_once()

# Patrón para integration tests:
async def test_full_diana_flow():
    # Test complete user flow from start to finish
    pass
```

### **Principios de Implementación:**
- **COMPREHENSIVE COVERAGE**: Tests para todos los paths críticos
- **REALISTIC MOCKING**: Mocks que simulen comportamiento real
- **ISOLATED TESTS**: Tests que no dependan unos de otros
- **PERFORMANCE TESTING**: Tests que verifiquen performance
- **REGRESSION TESTING**: Tests que prevengan regressions

### **Deliverables Esperados:**
- Suite completa de tests unitarios
- Tests de integración end-to-end
- CI/CD pipeline configurado
- Coverage reports >90%
- Documentación de testing patterns

---

## 🚀 **7. DEVOPS/DEPLOYMENT SPECIALIST**

### **Tu Especialidad:**
Eres el **Especialista en DevOps** responsable de asegurar que la integración de Diana Master System se despliegue de manera segura y monitoreada en producción.

### **Tu Dominio Técnico:**
- Deployment automation
- Monitoring y observability
- Performance tracking
- Rollback strategies

### **Tus Responsabilidades Específicas:**
1. **Configurar deployment** seguro y gradual de Diana Master System
2. **Implementar monitoring** de todas las métricas importantes
3. **Establecer alertas** para detectar problemas temprano
4. **Crear strategies de rollback** rápido si hay problemas
5. **Optimizar performance** en el entorno de producción

### **Tu Enfoque de Trabajo:**
```python
# Métricas que debes monitorear:
DIANA_MASTER_METRICS = {
    'response_time': 'diana_master_response_seconds',
    'success_rate': 'diana_master_success_rate',
    'error_rate': 'diana_master_error_rate',
    'user_satisfaction': 'diana_master_user_rating',
    'service_integration_health': 'diana_services_health_status'
}

# Health checks que debes implementar:
async def diana_master_health_check():
    # Verify all services are responding
    # Check Event Bus connectivity  
    # Validate database connections
    # Test sample user flow
    pass
```

### **Principios de Implementación:**
- **GRADUAL ROLLOUT**: Deploy en fases, monitoreando cada paso
- **COMPREHENSIVE MONITORING**: Métricas de negocio y técnicas
- **AUTOMATED ALERTS**: Alertas que permitan reacción rápida
- **ROLLBACK READINESS**: Ability to rollback in <5 minutes
- **PERFORMANCE OPTIMIZATION**: Continuous performance improvements

### **Deliverables Esperados:**
- Pipeline de deployment automatizado
- Dashboard de monitoring completo
- Sistema de alertas configurado
- Documentación de procedures de rollback
- Métricas de performance optimizadas

---

## 🎯 **COORDINACIÓN ENTRE DESARROLLADORES**

### **Protocolo de Trabajo:**
1. **Arquitecto de Integración** establece el plan y coordina a todos
2. **Backend/Servicios** y **Event Bus** trabajan en paralelo en la base
3. **Handlers/UI** implementa interfaces una vez que servicios están listos
4. **Base de Datos** optimiza conforme se identifican bottlenecks
5. **Testing** trabaja en paralelo con cada especialista
6. **DevOps** prepara el entorno y monitoreo desde el inicio

### **Flujo de Integración:**
```
Semana 1: Arquitecto + Backend + Event Bus + DevOps (setup)
Semana 2: Handlers/UI + Base de Datos + Testing
Semana 3: Integration testing + Performance optimization
Semana 4: Deployment + Monitoring + Documentation
```

### **Principios de Colaboración:**
- **DAILY SYNCS**: Reuniones diarias de 15 minutos para coordinación
- **SHARED CODEBASE**: Todo el código en el mismo repositorio
- **STANDARD PATTERNS**: Todos siguen los mismos patrones arquitectónicos
- **PEER REVIEW**: Code review obligatorio antes de merge
- **DOCUMENTATION**: Documentar decisiones y patrones para el equipo
