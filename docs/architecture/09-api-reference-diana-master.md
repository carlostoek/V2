# 🎭 Diana Master System - API Reference

## 📚 Referencia Completa de APIs

### 🧠 AdaptiveContextEngine

#### `analyze_user_context(user_id: int) -> UserContext`
Analiza el contexto completo del usuario usando IA.

**Parámetros:**
- `user_id`: ID único del usuario

**Retorna:**
```python
UserContext:
    user_id: int
    current_mood: UserMoodState
    engagement_pattern: str
    session_duration: int
    last_actions: List[str]
    preferred_features: List[str]
    notification_preferences: Dict[str, bool]
    personalization_score: float
    narrative_progress: float
    gamification_engagement: float
```

#### `_detect_user_mood(user_id: int, interactions: List) -> UserMoodState`
Detecta el estado emocional del usuario basado en patrones de comportamiento.

**Estados Disponibles:**
- `EXPLORER` - Quiere descubrir nuevas funciones
- `ACHIEVER` - Enfocado en completar tareas
- `COLLECTOR` - Le gusta acumular recompensas
- `STORYTELLER` - Comprometido con la narrativa
- `SOCIALIZER` - Disfruta funciones comunitarias
- `OPTIMIZER` - Busca eficiencia y estadísticas
- `NEWCOMER` - Necesita guía y tutoriales

### 🎨 DianaMasterInterface

#### `create_adaptive_interface(user_id: int, trigger: str = "main") -> Tuple[str, InlineKeyboardMarkup]`
Genera una interfaz completamente personalizada.

**Parámetros:**
- `user_id`: ID del usuario
- `trigger`: Contexto de activación ("main", "start", "admin", "refresh")

**Retorna:**
- `str`: Texto personalizado con markdown
- `InlineKeyboardMarkup`: Teclado adaptativo

#### `_generate_smart_greeting(context: UserContext) -> str`
Genera saludos personalizados por estado de ánimo.

**Ejemplos por Mood:**
```python
EXPLORER: "🔮 ¡Hay secretos esperándote, explorador!"
ACHIEVER: "🎯 ¡Es hora de conquistar nuevos logros!"
COLLECTOR: "💎 Los tesoros más raros te están esperando"
STORYTELLER: "📖 La historia continúa escribiéndose..."
```

#### `_generate_contextual_dashboard(context: UserContext) -> str`
Crea dashboard dinámico basado en el perfil del usuario.

**Variaciones:**
- **Achiever Mode**: "🎯 MODO CONQUISTA ACTIVADO"
- **Collector Mode**: "💎 COLECCIÓN ACTIVA"
- **Storyteller Mode**: "📖 NARRATIVA EN PROGRESO"
- **Optimizer Mode**: "📊 PANEL DE CONTROL"

#### `_generate_predictive_actions(context: UserContext) -> str`
Genera predicciones inteligentes de próximas acciones.

**Ejemplos:**
```python
"💡 *Predicción: Probablemente quieras reclamar tu regalo diario*"
"🚀 *Sugerencia: Nuevas misiones épicas disponibles*"
"📖 *Recomendación: El final de tu historia se acerca...*"
```

#### `_generate_adaptive_keyboard(context: UserContext, predictions: str, shortcuts: List[Dict]) -> InlineKeyboardMarkup`
Construye teclados dinámicos basados en contexto del usuario.

**Estructura del Teclado:**
```
Fila 1: Smart Shortcuts (máximo 2)
Fila 2: Mood-Specific Primary Actions (2)
Fila 3: Core Features (Gift + Trivia)
Fila 4: Admin Access (si aplica)
Fila 5: Navigation (Refresh + Help)
```

## 🎯 Handlers Especializados

### 🛒 `handle_epic_shop(callback: CallbackQuery, master: DianaMasterInterface)`
Maneja la experiencia de tienda personalizada.

**Funcionalidades:**
- Análisis de contexto de usuario
- Listado de tarifas VIP disponibles
- Personalización por mood
- Navegación contextual

**Callbacks Generados:**
- `diana:tariff_list` - Lista de tarifas
- `diana:redeem_token` - Canjear token VIP

### 🎯 `handle_missions_hub(callback: CallbackQuery, master: DianaMasterInterface)`
Centro de misiones dinámico.

**Misiones por Nivel:**
- **Nivel 1+**: "🔰 Novato Valiente" (100 Besitos + Badge)
- **Nivel 3+**: "🎲 Maestro del Conocimiento" (250 Besitos + Título)
- **Nivel 5+**: "👑 Leyenda Épica" (Acceso VIP temporal)

**Callbacks Generados:**
- `diana:trivia_challenge` - Iniciar trivia
- `diana:progress_tracker` - Ver progreso
- `diana:achievements` - Logros desbloqueados

### 📖 `handle_narrative_hub(callback: CallbackQuery, master: DianaMasterInterface)`
Historia viva interactiva.

**Capítulos por Progreso:**
- **0-25%**: "🌅 CAPÍTULO I: EL DESPERTAR"
- **25-50%**: "🌙 CAPÍTULO II: LAS SOMBRAS"
- **50-75%**: "🔥 CAPÍTULO III: LA REVELACIÓN"
- **75-100%**: "⭐ ÉPÍLOGO: EL NUEVO AMANECER"

**Callbacks por Capítulo:**
```python
# Capítulo I
"diana:story_search_clues", "diana:story_challenge"

# Capítulo II  
"diana:story_trust", "diana:story_solo"

# Capítulo III
"diana:story_accept", "diana:story_rebel"

# Épílogo
"diana:story_new_chapter", "diana:story_review"
```

### 🔮 `handle_surprise_feature(callback: CallbackQuery, master: DianaMasterInterface)`
Sistema de sorpresas con IA.

**Sorpresas Aleatorias:**
```python
"🎲 **DATO CURIOSO**: ¡Eres el usuario #42 más activo esta semana!"
"✨ **REGALO SORPRESA**: ¡Has desbloqueado 50 besitos extra!"
"🔮 **PREDICCIÓN**: Mañana será un gran día para completar misiones"
"🌟 **SECRETO**: Diana está preparando algo especial para usuarios como tú..."
```

### 🎁 `handle_daily_gift(callback: CallbackQuery, master: DianaMasterInterface)`
Sistema de recompensas diarias.

**Recompensas al Reclamar:**
- 💰 50 Besitos
- 🔥 +1 Día de racha
- 🎲 Pregunta bonus desbloqueada

### 🧠 `handle_trivia_challenge(callback: CallbackQuery, master: DianaMasterInterface)`
Desafíos de conocimiento adaptativos.

**Estructura:**
- Pregunta contextual
- 4 opciones de respuesta
- Recompensas dinámicas
- Callbacks: `trivia:correct:answer` / `trivia:wrong:answer`

### ❓ `handle_smart_help(callback: CallbackQuery, master: DianaMasterInterface)`
Sistema de ayuda inteligente contextual.

**Ayuda por Mood:**
- **Newcomer**: Guía completa paso a paso
- **Achiever**: Consejos pro para optimización
- **General**: Funciones principales explicadas

## 🔧 Funciones de Sistema

### `register_diana_master_system(dp, services: Dict[str, Any]) -> DianaMasterInterface`
Registra el sistema completo en el dispatcher.

**Parámetros:**
- `dp`: Aiogram Dispatcher
- `services`: Diccionario de servicios disponibles

**Servicios Requeridos:**
```python
{
    'gamification': GamificationService,
    'admin': AdminService, 
    'narrative': NarrativeService,
    'tariff': TariffService,
    'event_bus': IEventBus,
    'daily_rewards': DailyRewardsService
}
```

### `initialize_diana_master(services: Dict[str, Any]) -> DianaMasterInterface`
Inicializa la instancia global del sistema maestro.

## 🎮 Comandos y Routing

### Comandos de Bot
```python
@master_router.message(Command("start"))
async def cmd_start(message: Message)

@master_router.message(Command("admin"))  
async def cmd_admin(message: Message)
```

### Callback Routing
```python
@master_router.callback_query(F.data.startswith("diana:"))
async def handle_diana_callbacks(callback: CallbackQuery)
```

**Patrones de Callback:**
- `diana:refresh` - Actualizar interface
- `diana:epic_shop` - Tienda épica
- `diana:missions_hub` - Centro de misiones
- `diana:narrative_hub` - Historia viva
- `diana:surprise_me` - Sorpresa IA
- `diana:daily_gift` - Regalo diario
- `diana:trivia_challenge` - Trivia
- `diana:smart_help` - Ayuda inteligente

## 🏗️ Patrones de Integración

### Service Dictionary Pattern
```python
services = {
    'gamification': gamification_service,
    'admin': admin_service,
    'narrative': narrative_service,
    'tariff': tariff_service,
    'event_bus': event_bus,
    'daily_rewards': daily_rewards_service
}

diana_master = register_diana_master_system(dp, services)
```

### Context-Aware Handler Pattern
```python
async def handler_function(callback: CallbackQuery, master: DianaMasterInterface):
    user_id = callback.from_user.id
    context = await master.context_engine.analyze_user_context(user_id)
    
    # Generar contenido basado en contexto
    personalized_content = generate_content_for_mood(context.current_mood)
    
    # Crear interface adaptativa
    keyboard = create_adaptive_keyboard(context)
    
    await callback.message.edit_text(personalized_content, reply_markup=keyboard)
```

## 🎭 Estados y Transiciones

### Ciclo de Vida del Contexto
```
Usuario Interactúa
    ↓
Análisis de Comportamiento (IA)
    ↓
Detección de Estado de Ánimo
    ↓
Generación de Interface Personalizada
    ↓
Respuesta Adaptativa
    ↓
Registro de Interacción
    ↓
Actualización de Patrones
```

### Machine de Estados de Usuario
```
NEWCOMER → EXPLORER → [ACHIEVER|COLLECTOR|STORYTELLER] → OPTIMIZER
    ↑                           ↓
    └── SOCIALIZER ←──────────────┘
```

## 📊 Métricas y Analytics

### UserContext Metrics
- `personalization_score`: 0.0 - 1.0 (basado en interacciones)
- `engagement_pattern`: "new_user" | "casual_user" | "regular_user" | "power_user"
- `session_duration`: Minutos de sesión actual
- `narrative_progress`: 0.0 - 100.0 (porcentaje de historia completada)
- `gamification_engagement`: 0.0 - 1.0 (nivel de engagement con juegos)

### Interaction Tracking
```python
interaction_patterns: Dict[int, List[Tuple[str, datetime]]]
# Ejemplo: {user_id: [("shop_visit", datetime), ("trivia_complete", datetime)]}
```

---

**🚀 Esta API Reference proporciona todo lo necesario para extender y mantener el Diana Master System.** 

**La arquitectura está diseñada para ser extensible, mantenible y revolucionaria.** 🎭✨