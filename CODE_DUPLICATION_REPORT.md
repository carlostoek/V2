# Reporte de Duplicación de Código

## Introducción

Este reporte detalla el código duplicado encontrado en el directorio `src/` del proyecto. El análisis se enfoca en funciones, lógica, importaciones, patrones, validaciones y handlers duplicados. Para cada instancia, se proporciona la ubicación, una descripción, el nivel de gravedad, una recomendación de refactorización y el impacto en la mantenibilidad.

---

## Análisis Detallado

### 1. Obtención de Sesión de Base de Datos

-   **Ubicación:**
    -   `src/modules/gamification/service.py` (en casi todos los métodos)
    -   `src/modules/admin/service.py` (en casi todos los métodos)
-   **Descripción:** El bloque `async for session in get_session():` se repite en casi todos los métodos asíncronos que interactúan con la base de datos.
-   **Gravedad:** Media
-   **Recomendación:** Crear un decorador o un context manager que maneje la obtención y cierre de la sesión de base de datos. Esto centralizaría la lógica de la sesión y reduciría el código repetitivo.
-   **Impacto en Mantenibilidad:** Alto. Simplificaría enormemente los métodos de servicio, reduciría la probabilidad de errores de manejo de sesión y haría el código más legible y fácil de mantener.

### 2. Verificación de Existencia de Usuario

-   **Ubicación:**
    -   `src/modules/gamification/service.py` (múltiples métodos como `_award_points`, `_update_missions_progress`, `get_user_missions`, etc.)
-   **Descripción:** Varios métodos en `GamificationService` comienzan con una consulta para verificar si un usuario existe antes de continuar.
-   **Gravedad:** Media
-   **Recomendación:** Crear un método de servicio compartido o un decorador (por ejemplo, `@user_exists`) que realice esta verificación. Si el usuario no existe, podría lanzar una excepción personalizada (por ejemplo, `UserNotFoundError`) que se maneje en un nivel superior.
-   **Impacto en Mantenibilidad:** Alto. Eliminaría la lógica de validación repetida de cada método, haciendo que el propósito principal del método sea más claro y reduciendo la cantidad de código.

### 3. Manejo de Errores y Logging

-   **Ubicación:**
    -   `src/modules/gamification/service.py`
    -   `src/modules/admin/service.py`
-   **Descripción:** Bloques `try...except` con `self.logger.error(...)` se repiten en muchos métodos. La estructura es casi idéntica.
-   **Gravedad:** Baja
-   **Recomendación:** Implementar un decorador de manejo de errores que envuelva los métodos del servicio. Este decorador podría registrar la excepción y, opcionalmente, relanzarla o devolver un valor predeterminado.
-   **Impacto en Mantenibilidad:** Medio. Reduciría el código repetitivo de manejo de errores, haciendo que los métodos sean más limpios y enfocados en su lógica de negocio.

### 4. Lógica de Paginación y Respuesta en Handlers

-   **Ubicación:**
    -   `src/infrastructure/telegram/handlers.py`
-   **Descripción:** Varios handlers de callback (`handle_free_channel_menu_callback`, `handle_set_wait_time_value_callback`, `handle_delete_tariff_callback`, etc.) siguen el mismo patrón:
    1.  Realizar una acción de servicio.
    2.  Volver a obtener datos (por ejemplo, `get_all_tariffs`).
    3.  Editar un mensaje con un nuevo teclado.
-   **Gravedad:** Media
-   **Recomendación:** Crear funciones auxiliares genéricas para las respuestas. Por ejemplo, una función `update_admin_menu(query, message_text, keyboard)` podría ser reutilizada. Esto también podría combinarse con un refactor de los teclados para que sean más dinámicos.
-   **Impacto en Mantenibilidad:** Alto. Reduciría la duplicación en los handlers, facilitando la adición de nuevos comandos y la modificación de los menús existentes.

### 5. Otorgamiento de Puntos y Recompensas

-   **Ubicación:**
    -   `src/modules/gamification/service.py` (en `_check_level_achievements`, `_complete_mission`, `_check_mission_achievements`, `_check_diana_validation_achievements`)
-   **Descripción:** La lógica para otorgar puntos como recompensa por logros o misiones es muy similar: se busca `UserPoints`, se actualizan los puntos y se agrega una entrada al historial.
-   **Gravedad:** Media
-   **Recomendación:** Centralizar la lógica de recompensa en un único método. Por ejemplo, `_grant_reward(session, user_id, points, source, items)` que se encargue de actualizar los puntos y el inventario del usuario.
-   **Impacto en Mantenibilidad:** Alto. Simplificaría la lógica de finalización de misiones y logros, y facilitaría la adición de nuevos tipos de recompensas en el futuro.

### 6. Duplicación de Lógica de Negocio entre Servicios

-   **Ubicación:**
    -   `src/infrastructure/telegram/handlers.py` (en `handle_start`)
    -   `src/modules/admin/service.py` (en `validate_token`)
-   **Descripción:** En `handle_start`, hay una lógica de fallback para validar un token que llama a `self._admin_service.validate_token`. Sin embargo, la lógica principal de validación de tokens también existe en `admin_service`. Esto sugiere una falta de cohesión y una posible duplicación de la responsabilidad.
-   **Gravedad:** Alta
-   **Recomendación:** La validación de tokens debería ser responsabilidad de un único servicio (probablemente `TokenService` o `AdminService`, pero no ambos). El handler `handle_start` debería llamar a este servicio único. La lógica de fallback debería eliminarse en favor de una única fuente de verdad.
-   **Impacto en Mantenibilidad:** Alto. Tener una única fuente de verdad para la validación de tokens es crucial. Reduce la confusión, previene bugs y hace que el sistema sea más fácil de razonar.

### 7. Chequeos de Disponibilidad de Módulos

-   **Ubicación:**
    -   `src/infrastructure/telegram/handlers.py` (en `handle_main_menu_callback`, `handle_historia_command`, `handle_mochila_command`, etc.)
-   **Descripción:** Se repite el patrón `if self._story_system:` o `if self._mochila_system:` para verificar si un módulo está disponible antes de usarlo.
-   **Gravedad:** Baja
-   **Recomendación:** Se podría implementar un decorador como `@module_available('story_system')` que realice esta comprobación y envíe un mensaje de "no disponible" si el módulo no está cargado.
-   **Impacto en Mantenibilidad:** Medio. Limpiaría los handlers y centralizaría la lógica de comprobación de disponibilidad de módulos.

### 8. Lógica de Creación de Usuario Duplicada

-   **Ubicación:**
    -   `src/modules/user/service.py` (en `_ensure_user_exists`)
    -   `src/modules/gamification/service.py` (verificaciones de existencia de usuario)
    -   `src/modules/channel/service.py` (verificaciones de existencia de usuario)
-   **Descripción:** La lógica para verificar si un usuario existe y, en caso de no existir, crearlo, está dispersa. `UserService` tiene una implementación, mientras que otros servicios realizan comprobaciones similares pero sin la capacidad de crear el usuario.
-   **Gravedad:** Alta
-   **Recomendación:** Centralizar toda la lógica de creación y recuperación de usuarios en `UserService`. Otros servicios no deberían consultar directamente la tabla de usuarios, sino que deberían llamar a métodos en `UserService` (por ejemplo, `get_or_create_user`). Esto asegura una única fuente de verdad para la gestión de usuarios.
-   **Impacto en Mantenibilidad:** Muy Alto. Centralizar la gestión de usuarios es fundamental para la integridad de los datos y para evitar inconsistencias. Simplifica el resto de servicios y reduce la probabilidad de errores.

### 9. Patrón de Carga de Datos Iniciales

-   **Ubicación:**
    -   `src/modules/gamification/service.py` (en `_load_initial_data`)
    -   `src/modules/channel/service.py` (en `_load_initial_data`)
-   **Descripción:** Varios servicios tienen un método `_load_initial_data` que carga datos de la base de datos y los almacena en una caché en memoria al iniciar.
-   **Gravedad:** Baja
-   **Recomendación:** Se podría crear una clase base de servicio (`CacheableService`) con un método genérico para cargar datos en una caché. Cada servicio podría entonces heredar de esta clase y especificar la consulta y la estructura de la caché.
-   **Impacto en Mantenibilidad:** Medio. Reduce el código repetitivo en la inicialización de los servicios y estandariza la forma en que se maneja el almacenamiento en caché.

### 10. Duplicación Masiva en Handlers de Administración

-   **Ubicación:**
    -   `src/bot/handlers/admin/user_management.py`
    -   `src/bot/handlers/admin/token_management.py`
    -   `src/bot/handlers/admin/tariff_management.py`
-   **Descripción:** Los handlers de administración presentan una duplicación masiva de código. En casi todas las funciones de los handlers se repiten los siguientes patrones:
    1.  **Instanciación de Servicios:** Servicios como `AdminService`, `Tokeneitor` y `EventBus` se instancian repetidamente dentro de cada función.
    2.  **Bloques `try/except`:** Cada función está envuelta en un bloque `try/except` idéntico que captura `Exception` y envía un mensaje de error.
    3.  **Creación Manual de Texto y Teclados:** El texto de los mensajes y los teclados `InlineKeyboardMarkup` se construyen manualmente en cada función, lo que resulta en una gran cantidad de código repetitivo y difícil de mantener.
    4.  **Lógica de FSM:** La lógica para manejar estados (FSM) es muy similar entre los diferentes flujos de creación y edición.
-   **Gravedad:** Crítica
-   **Recomendación:**
    1.  **Inyección de Dependencias:** Utilizar un contenedor de inyección de dependencias para instanciar los servicios una sola vez y pasarlos a los handlers. El `Dispatcher` de `aiogram` permite pasar dependencias a los handlers.
    2.  **Middleware para Errores:** Crear un middleware de `aiogram` para capturar errores de manera centralizada, eliminando la necesidad de bloques `try/except` en cada handler.
    3.  **Factoría de Teclados y Plantillas de Mensajes:** Centralizar la creación de teclados en un módulo `keyboards` y utilizar un motor de plantillas (como Jinja2) o funciones de formato para generar los mensajes. Esto separaría la lógica de la presentación.
    4.  **Abstracción de Flujos FSM:** Crear clases o funciones auxiliares que encapsulen los flujos comunes de FSM (por ejemplo, un flujo para pedir un valor, validarlo y pasar al siguiente estado).
-   **Impacto en Mantenibilidad:** Crítico. La refactorización de los handlers es la tarea más importante para mejorar la mantenibilidad del bot. Reducirá drásticamente la cantidad de código, eliminará la duplicación, facilitará la adición de nuevas funciones y reducirá la probabilidad de errores.

## Conclusión

El código base presenta varias oportunidades de refactorización para reducir la duplicación. Las áreas más críticas son la gestión de sesiones de base de datos, la validación y creación de usuarios, y la centralización de la lógica de negocio. Abordar estos problemas mejorará significativamente la mantenibilidad, la legibilidad y la robustez del sistema.
