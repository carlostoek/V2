###SERVICIOS
**1. Gestión de Usuarios (User)**                           *   **Descripción**: Maneja el ciclo de vida de los usuarios, incluyendo registro, autenticación, gestión de perfiles y almacenamiento de datos básicos. Es el núcleo para identificar y gestionar a los usuarios en todos los demás sistemas.  *   **Estado**: Activo.       *   **Ubicación**: `src/modules/user/`
                              ---                                                         **2. Sistema de Gamificación (Gamification)**               *   **Descripción**: Implementa mecánicas de juego como puntos, niveles, logros y recompensas para incentivar la interacción del usuario. Se integra con otras funcionalidades para registrar el compromiso.
*   **Estado**: Activo.       *   **Ubicación**: `src/modules/gamification/`              
---                           
**3. Sistema Narrativo (Narrative)**
*   **Descripción**: Gestiona la progresión de la historia y las interacciones contextuales con el bot. Adapta las respuestas y eventos según el avance del usuario en la narrativa diseñada.                     *   **Estado**: Activo.
*   **Ubicación**: `src/modules/narrative/`
                              ---
                              **4. Menú de Administración (Admin)**                       *   **Descripción**: Proporciona una interfaz para que los administradores gestionen el bot. Incluye herramientas para supervisar usuarios, configurar el sistema, enviar notificaciones y gestionar otros módulos.                             *   **Estado**: Activo.
*   **Ubicación**: `src/modules/admin/`
                              ---
                              **5. Gestión de Tokens (Token)**                            *   **Descripción**: Administra la creación, distribución y uso de tokens (la moneda virtual del bot). Se integra con la tienda, recompensas y otras funcionalidades.               *   **Estado**: Activo.
*   **Ubicación**: `src/modules/token/`
                              ---
                              **6. Tienda (Shop)**
*   **Descripción**: Permite a los usuarios gastar sus tokens para comprar artículos virtuales, ventajas o acceso a contenido exclusivo.              *   **Estado**: Activo.
*   **Ubicación**: `src/modules/shop/`
                              ---
                              **7. Sistema de Tarifas/Suscripciones (Tariff)**            *   **Descripción**: Gestiona los planes de suscripción de los usuarios, los pagos y el acceso a funcionalidades premium basadas en su nivel de tarifa.                             *   **Estado**: Activo.
*   **Ubicación**: `src/modules/tariff/`
                              ---
                              **8. Sistema Emocional (Emotional)**                        *   **Descripción**: Analiza el texto del usuario para detectar emociones y adapta las respuestas del bot para que sean más empáticas y coherentes con el estado de ánimo del usuario.
*   **Estado**: Activo.       *   **Ubicación**: `src/modules/emotional/`                 
---                           
**9. Recompensas Diarias (Daily Rewards)**

*   **Descripción**: Gestiona la entrega de recompensas diarias (como tokens o puntos) a los usuarios que inician sesión o interactúan con el bot cada día.                         *   **Estado**: Activo.       *   **Ubicación**: `src/modules/daily_rewards/`             
---                                                         **10. Gestión de Canales (Channel)**
*   **Descripción**: Administra la interacción del bot con los canales de Telegram, incluyendo la publicación de contenido, la gestión de miembros y la moderación.
*   **Estado**: En pruebas.
*   **Ubicación**: `src/modules/channel/`

---

**11. Sistema de Trivia (Trivia)**
*   **Descripción**: Implementa un juego de preguntas y respuestas donde los usuarios pueden participar para ganar recompensas y competir en clasificaciones.
*   **Estado**: En pruebas.   *   **Ubicación**: `src/modules/trivia/`


,

### 1. Estructura del Menú Actual                                                         El menú administrativo principal se define en la variable `ADMIN_MENU_STRUCTURE`. Está compuesto por 7 secciones principales, cada una con sus respectivos submenús:                                              *   **💎 VIP**                    *   `🛠 Configuración VIP (Mensajes/Recordatorios/Suscripciones/Despedidas)`               *   `🏷 Generar Invitación`    *   `📊 Estadísticas VIP`     *   `📊 Suscriptores (CRUD)`                                *   `📢 Enviar Post`      *   **🔓 Canal Gratuito**         *   `⚙ Configuración (Bienvenida/Flow/Tiempo)`              *   `📊 Estadísticas`         *   `📋 Solicitudes Pendientes`                             *   `🧪 Probar Flujo`     *   **⚙ Configuración Global**    *   `🕒 Programadores`        *   `📅 Firmar mensajes`      *   `🎚 Administrar canales`                                 *   `➕ Añadir Canales`   *   **🎮 Gamificación**           *   `📊 Estadísticas`         *   `👥 Usuarios`             *   `📜 Misiones`             *   `🏅 Insignias`            *   `📈 Niveles`              *   `🎁 Recompensas`      *   **🛒 Subastas**               *   `📊 Estadísticas`         *   `📋 Pendientes`           *   `🔄 Activas`              *   `➕ Crear`            *   **🎉 Eventos y Sorteos**      *   `🎫 Eventos (Listar/Crear)`                             *   `🎁 Sorteos (Listar/Crear)`                         *   **❓ Trivias**                *   `📋 Listar`               *   `➕ Crear`                                          ### 2. Callbacks y Handlers por Botón Principal                                           El menú principal se genera en la función `_create_main_admin_keyboard`. Cada botón principal está asociado a un `callback_data` que sigue el patrón `admin:section:<nombre_seccion>`.                                                          | Botón Principal | `callback_data` |                       | :--- | :--- |               | 💎 VIP | `admin:section:vip` |                            | 🔓 Canal Gratuito | `admin:section:free_channel` |        | ⚙ Config Global | `admin:section:global_config` |         | 🎮 Gamificación | `admin:section:gamification` |          | 🛒 Subastas | `admin:section:auctions` |                  | 🎉 Eventos | `admin:section:events` |                     | ❓ Trivias | `admin:section:trivia` |                     | 📊 Analytics Pro | `admin:analytics` |                                                  Todos estos callbacks son manejados por un único handler principal:                                   ###EVENTBUS                  *   **`handle_admin_callbacks(callback: CallbackQuery)`**: Este manejador, decorado con `@admin_router.callback_query(F.data.startswith("admin:"))`, captura todos los callbacks que comienzan con `admin:`.      *   Dentro de esta función, si el `callback_data` empieza con `admin:section:`, extrae la clave de la sección y llama a `diana_admin_master.create_section_interface(user_id, section_key)` para renderizar el submenú correspondiente.                                       ### 3. Rutas de Archivos                                    Toda la lógica para la definición de la estructura, la creación de los teclados (keyboards) y los manejadores de callbacks se encuentra centralizada en un único archivo:                                         *   **Ruta del archivo**: `/data/data/com.termux/files/home/repos/refactor/V2/src/bot/core/diana_admin_master.py`                                     En resumen:                   *   **Estructura de datos**: `ADMIN_MENU_STRUCTURE` (en el archivo mencionado).           *   **Creación de teclados**: Métodos `_create_main_admin_keyboard` y `_create_section_keyboard` dentro de la clase `DianaAdminMaster`.               *   **Manejador de interacciones**: Función `handle_admin_callbacks` en el mismo arc

the event bus implementation is located in `src/core/event_bus.py`. I will also look for an `events.py` file in the `src/modules/` directory.I've confirmed `src/core/event_bus.py` exists. I'll read it to understand its function and check `src/modules/events.py` for defined events.call:read_file{absolute_path:I have the `EventBus` implementation from `src/core/event_bus.py`: class `EventBus` with `publish` and `subscribe` methods. Now I need to find usage examples and `IEvent` subclasses, likely in `src/modules/events.py`, which I will now read.Okay, I have the `EventBus` and `IEvent` subclasses. Now, I'll search the `src` directory for `event_bus.publish` to find event dispatches and for event class usages (e.g., `UserMessageEvent`) to locate handlers, likely within `src/modules`. A broad search should give me a good overview.I've analyzed the event bus system. The core is the `EventBus` class in `src/core/event_bus.py`, using `publish` to dispatch and `subscribe` to listen. Events are defined in `src/modules/events.py`. The `bot/core/orchestrator.py` and various services publish events, while other services and dedicated listeners subscribe to them, triggering handlers. This creates a clear flow: action, event creation, publication, and handling. I'm ready to present a detailed explanation with code examples and an event-consumer list.     Claro, aquí tienes un resumen detallado del sistema de eventos.                                                         ### 1. Clases y Funciones para Despachar Eventos                                          El sistema se centra en la clase `EventBus`, que implementa la interfaz `IEventBus`.

*   **Clase principal**: `src.core.event_bus.EventBus`
*   **Función para despachar**: `publish(event: IEvent)`
*   **Función para suscribirse**: `subscribe(event_type: Type[IEvent], handler: Callable)`

### 2. Ejemplos de Cómo se Envía un Evento

Los eventos se crean como instancias de clases de eventos (definidas en `src/modules/events.py`) y se publican en el bus.

**Ejemplo 1: Publicar un evento cuando un usuario envía un mensaje.**
El orquestador principal del bot captura un nuevo mensaje y lo despacha como un `UserMessageEvent`.

```python
# Ubicación: src/bot/core/orchestrator.py

from src.modules.events import UserMessageEvent
from datetime import datetime

class BotOrchestrator:
    # ... (inicialización con event_bus)

    async def handle_message(self, message):
        # ...
        await self._event_bus.publish(UserMessageEvent(
            user_id=user.id,
            message=message.text,
            timestamp=datetime.now().isoformat()
        ))
```

**Ejemplo 2: Publicar un evento al completar una misión.**
El servicio de gamificación publica un `MissionCompletedEvent` cuando un usuario cumple los requisitos de una misión.   
```python                     # Ubicación: src/modules/gamification/service.py
                              from src.modules.events import MissionCompletedEvent
from datetime import datetime                               class GamificationService:
    # ... (inicialización con event_bus)

    async def complete_mission(self, user_id: int, mission_id: str):
        # ... (lógica para completar la misión)

        mission_event = MissionCompletedEvent(
            user_id=user_id,
            mission_id=mission_id,
            completion_time=datetime.now().isoformat(),
            reward_points=100  # Puntos de recompensa               )
        await self._event_bus.publish(mission_event)        ```
                              ### 3. Ejemplos de Cómo se Escucha un Evento
                              Los servicios o listeners se suscriben a tipos de eventos específicos y definen funciones (manejadores o *handlers*) para procesarlos.
                              **Ejemplo 1: Escuchar eventos de puntos otorgados en el servicio de narrativa.**          El `NarrativeService` se suscribe a `PointsAwardedEvent` para saber si debe desbloquear contenido narrativo como recompensa.                          
```python                     # Ubicación: src/modules/narrative/service.py
                              from src.modules.events import PointsAwardedEvent

class NarrativeService:           def __init__(self, event_bus: IEventBus, ...):                  self._event_bus = event_bus                                 # ...                 
    def setup_listeners(self):        """Suscribe los manejadores a los eventos del bus."""                                     self._event_bus.subscribe(PointsAwardedEvent, self.handle_points_awarded)                                           async def handle_points_awarded(self, event: PointsAwardedEvent) -> None:                     """Procesa la obtención de puntos para avanzar la narrativa."""                           logger.info(f"NarrativeService: Recibido PointsAwardedEvent para user {event.user_id}")                                 # ... Lógica para ver si los puntos desbloquean algo```                                                         **Ejemplo 2: Un listener dedicado para manejar la finalización de misiones.**             Existe un listener específico en la capa del bot cuya única función es escuchar eventos y enviar notificaciones al usuario.                           
```python                     # Ubicación: src/bot/listeners/mission_listener.py
                              from src.modules.events import MissionCompletedEvent
from aiogram import Bot                                     class MissionListener:
    def __init__(self, event_bus: IEventBus, bot: Bot):             self.event_bus = event_bus                                  self.bot = bot        
    def subscribe_to_events(self):                                  self.event_bus.subscribe(MissionCompletedEvent, self.handle_mission_completed)    
    async def handle_mission_completed(self, event: MissionCompletedEvent) -> None:
        """Notifica al usuario que ha completado una misión."""                                   await self.bot.send_message(                                    event.user_id,
            f"¡Felicidades! Has completado la misión '{event.mission_id}'."                       )                     ```

La mayoría de las acciones se canalizan a través de la clase `DianaAdminServicesIntegration`, que actúa como un intermediario (Facade) para invocar al servicio correspondiente (ej. `VipService`, `ChannelService`, `GamificationService`).                                  ---                                                         ### 💎 Gestión VIP (`VipService`)                                                         Estos callbacks se definen en el método `_get_subsection_content` cuando `section_key` es `"vip"`. Son procesados por el handler `@admin_router.callback_query(F.data.startswith("admin:action:"))`.                                            *   **Nombre del callback:** `admin:action:vip:manage_tariffs`                                *   **Servicio que activa:** `VipService` (a través de `services_integration`) para gestionar las tarifas de suscripción.                             *   **Definido en:** `src/bot/core/diana_admin_master.py`, dentro del método `_get_subsection_content`.                                           *   **Nombre del callback:** `admin:action:vip:generate_token`                                *   **Servicio que activa:** `VipService` o un `TokenService` para crear nuevos tokens de invitación VIP.               *   **Definido en:** `src/bot/core/diana_admin_master.py`, método `_get_subsection_content`.                                                      *   **Nombre del callback:** `admin:action:vip:list_tokens`     *   **Servicio que activa:** `VipService` o `TokenService` para listar los tokens de invitación activos.                *   **Definido en:** `src/bot/core/diana_admin_master.py`, método `_get_subsection_content`.                                                      *   **Nombre del callback:** `admin:action:vip:conversion_stats`, `admin:action:vip:revenue_analysis`, etc.                 *   **Servicio que activa:** `VipService` o un servicio de analíticas para obtener y mostrar estadísticas del sistema VIP.                            *   **Definido en:** `src/bot/core/diana_admin_master.py`, método `_get_subsection_content`.                                                      ### ⚙️ Configuración Global (`ChannelService`)               
Estos callbacks se definen en `_get_subsection_content` cuando `section_key` es `"global_config"`. Son procesados por handlers más específicos como `@admin_router.callback_query(F.data.startswith("admin:action:global_config:"))`.                                         *   **Nombre del callback:** `admin:action:global_config:add_channels`                        *   **Servicio que activa:** `ChannelService` para iniciar el flujo de registro de un nuevo canal.                      *   **Definido en:** `src/bot/core/diana_admin_master.py`, método `_get_subsection_content` y manejado en `handle_global_config_actions`.                                       *   **Nombre del callback:** `admin:action:global_config:list_registered_channels`            *   **Servicio que activa:** `ChannelService` para obtener y mostrar la lista de todos los canales registrados.         *   **Definido en:** `src/bot/core/diana_admin_master.py`, método `_get_subsection_content` y manejado en `handle_global_config_actions`.                                       *   **Nombre del callback:** `admin:action:global_config:delete_channel:{channel_id}`         *   **Servicio que activa:** `ChannelService` para eliminar (desactivar) un canal del sistema.                          *   **Definido en:** No está en `_get_subsection_content`, se construye dinámicamente en `handle_global_config_actions` al listar los canales.                                  *   **Nombre del callback:** `admin:channel_confirm:{channel_id}`                             *   **Servicio que activa:** `ChannelService` para confirmar y finalizar el registro de un nuevo canal.                 *   **Definido en:** Se construye dinámicamente en los handlers `handle_admin_forwarded_messages` y `handle_admin_text_messages`, y es procesado por `handle_channel_confirmation_callbacks`.                                               ### 🎮 Gamificación (`GamificationService`)                 
Estos callbacks se definen en `_get_subsection_content` cuando `section_key` es `"gamification"`.                                                     *   **Nombre del callback:** `admin:action:gamification:points_distribution`                  *   **Servicio que activa:** `GamificationService` para analizar la distribución de puntos ("besitos").                 *   **Definido en:** `src/bot/core/diana_admin_master.py`, método `_get_subsection_content`.                                                      *   **Nombre del callback:** `admin:action:gamification:mission_popularity`                   *   **Servicio que activa:** `GamificationService` para obtener métricas sobre las misiones más populares.              *   **Definido en:** `src/bot/core/diana_admin_master.py`, método `_get_subsection_content`.                                                      *   **Nombre del callback:** `admin:action:gamification:full_report`                          *   **Servicio que activa:** `GamificationService` para generar un informe completo del estado del sistema de gamificación.                           *   **Definido en:** `src/bot/core/diana_admin_master.py`, método `_get_subsection_content`.
