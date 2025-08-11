# Reporte de Módulos Implementados

A continuación se presenta un listado de los módulos y sistemas más importantes implementados en el proyecto, junto con su estado de conexión y los archivos relevantes.

## 1. Core del Bot y Orquestación

-   **Descripción**: Componentes centrales que arrancan y orquestan el bot.
-   **Estado**: Conectado.

### Archivos Importantes:

-   `src/bot/__main__.py`: Punto de entrada principal de la aplicación.
-   `src/bot/core/bootstrap.py`: Orquesta la inicialización de todos los servicios y componentes del bot.
-   `src/bot/core/orchestrator.py`: Probablemente maneja la lógica de alto nivel de la interacción del bot.

## 2. Event Bus

-   **Descripción**: Sistema de comunicación asíncrona entre los diferentes módulos del proyecto. Permite el desacoplamiento de los servicios.
-   **Estado**: Conectado.

### Archivos Importantes:

-   `src/core/event_bus.py`: Implementación del bus de eventos.
-   `src/modules/events.py`: Definición de los eventos que se pueden publicar en el bus.

## 3. Diana Master System

-   **Descripción**: Es el sistema principal de la interfaz de usuario. Utiliza un motor de contexto adaptativo para personalizar la experiencia del usuario en tiempo real.
-   **Estado**: Conectado.

### Archivos Importantes:

-   `src/bot/core/diana_master_system.py`: Implementación del sistema principal de la interfaz de usuario.
-   `src/bot/core/diana_user_master_system.py`: Una versión especializada para usuarios.
-   `src/bot/core/diana_admin_master.py`: Una versión especializada para administradores.

## 4. Módulo de Gamificación

-   **Descripción**: Gestiona toda la lógica de ludificación, incluyendo puntos (besitos), misiones, logros y niveles de usuario.
-   **Estado**: Conectado.

### Archivos Importantes:

-   `src/modules/gamification/service.py`: Servicio principal que maneja la lógica de gamificación.
-   `src/bot/database/models/gamification.py`: Modelos de base de datos para la gamificación.

## 5. Módulo Narrativo

-   **Descripción**: Gestiona la historia interactiva del bot, el progreso narrativo de los usuarios y el sistema de pistas (LorePieces).
-   **Estado**: Conectado.

### Archivos Importantes:

-   `src/modules/narrative/service.py`: Servicio que maneja la lógica de la narrativa.
-   `src/bot/database/models/narrative.py`: Modelos de base de datos para la narrativa.

## 6. Módulo Emocional (Máquina de Estados)

-   **Descripción**: Simula los estados emocionales de Diana a través de una máquina de estados finitos, permitiendo que el bot reaccione de manera más humana y dinámica.
-   **Estado**: Conectado.

### Archivos Importantes:

-   `src/modules/emotional/diana_state.py`: Define la máquina de estados emocionales.
-   `src/modules/emotional/service.py`: Servicio que gestiona las máquinas de estado para cada usuario.
-   `src/modules/emotional/middleware.py`: Middleware que integra el sistema emocional en el flujo de mensajes.

## 7. Módulo de Administración

-   **Descripción**: Proporciona funcionalidades para la administración del bot, como la gestión de tarifas y tokens de suscripción.
-   **Estado**: Conectado.

### Archivos Importantes:

-   `src/modules/admin/service.py`: Servicio con la lógica de administración.
-   `src/bot/database/models/admin.py`: Modelos de base de datos para la administración.

## 8. Módulo de Usuarios

-   **Descripción**: Gestiona la información y el registro de los usuarios en el sistema.
-   **Estado**: Conectado.

### Archivos Importantes:

-   `src/modules/user/service.py`: Servicio para la gestión de usuarios.
-   `src/bot/database/models/user.py`: Modelo de base de datos para los usuarios.

## 9. Módulo de Tokens (Tokeneitor)

-   **Descripción**: Sistema robusto para la creación, gestión y canje de tokens de suscripción, integrado con las tarifas de los canales.
-   **Estado**: Conectado.

### Archivos Importantes:

-   `src/modules/token/tokeneitor.py`: Servicio principal para la gestión de tokens.
-   `src/bot/database/models/token.py`: Modelos de base de datos para tokens y tarifas.

## Módulos Adicionales

-   **`src/modules/shop/`**: Probablemente relacionado con una tienda en el bot.
-   **`src/modules/daily_rewards/`**: Sistema de recompensas diarias.
-   **`src/modules/trivia/`**: Módulo para juegos de trivia.
-   **`src/modules/channel/`**: Gestión de canales de Telegram.

Estos módulos también parecen estar **conectados** a través de los servicios que son inyectados en el `DianaMasterSystem` y otros componentes.
