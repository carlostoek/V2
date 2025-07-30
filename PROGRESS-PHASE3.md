# Fase 3: Integración con Telegram y Flujo de Usuario Básico

## Objetivo
Conectar la aplicación al API de Telegram, manejar el primer comando de usuario (`/start`), y establecer un flujo de comunicación bidireccional entre la capa de Telegram y los servicios de negocio.

## Criterio de Éxito
Un usuario envía `/start`, el bot responde con un menú con un botón. Al pulsar el botón "Consultar mis puntos", el bot edita el mensaje para mostrar los puntos del usuario (obtenidos del `GamificationService`).

---

## Plan de Acción y Registro de Progreso

### 1. Configuración y Adaptador de Telegram
- **Estado:** ✅ COMPLETADO
- **Descripción:** Se creó la configuración para el token y un `TelegramAdapter` para la lógica de `aiogram`.
- **Puntos Clave:**
  - Se creó `src/core/services/config.py` usando `pydantic-settings` para cargar el token desde un archivo `.env`.
  - Se creó `src/infrastructure/telegram/adapter.py`. Esta clase encapsula el `Bot` y `Dispatcher` de `aiogram` y recibirá los servicios necesarios por inyección de dependencias.

### 2. Creación del Servicio de Usuario
- **Estado:** ✅ COMPLETADO
- **Descripción:** Se creó un `UserService` para manejar el registro de usuarios.
- **Puntos Clave:**
  - Se añadió el `UserStartedBotEvent` a `src/modules/events.py`.
  - Se creó el directorio `src/modules/user/`.
  - Se implementó `UserService` en `src/modules/user/service.py`, que escucha el evento y añade al usuario a un set (simulando un registro).

### 3. Implementación del Handler `/start`
- **Estado:** ✅ COMPLETADO
- **Descripción:** Se implementó el handler para `/start` que publica un evento y muestra un menú.
- **Puntos Clave:**
  - Se creó `src/infrastructure/telegram/handlers.py`.
  - El handler `handle_start` publica `UserStartedBotEvent` al bus de eventos, desacoplando la acción de Telegram del registro de usuario.
  - Se inyecta el `event_bus` en la configuración de handlers para permitir esta comunicación.

### 4. Consulta de Puntos en Gamificación
- **Estado:** ✅ COMPLETADO
- **Descripción:** Se añadió un método de consulta directa al `GamificationService`.
- **Puntos Clave:**
  - Se añadió el método `get_points(user_id)` a `src/modules/gamification/service.py`.
  - Este método permite a la capa de infraestructura (handlers) consultar el estado de un servicio de forma síncrona, un patrón necesario para responder a las interacciones del usuario.

### 5. Implementación del Handler de Callback
- **Estado:** ✅ COMPLETADO
- **Descripción:** Se implementó el handler para el callback del botón, que consulta y muestra los puntos.
- **Puntos Clave:**
  - Se añadió el handler `handle_get_points_callback` a `src/infrastructure/telegram/handlers.py`.
  - El handler recibe el `gamification_service` por inyección de dependencias.
  - Llama directamente al método `get_points` del servicio para obtener los datos y responder al usuario.

### 6. Integración Final en `main.py`
- **Estado:** ✅ COMPLETADO
- **Descripción:** Se actualizó `main.py` para instanciar y ejecutar el `TelegramAdapter`.
- **Puntos Clave:**
  - `main.py` ahora actúa como el Composition Root de la aplicación.
  - Instancia todos los servicios y el bus de eventos.
  - Inyecta las dependencias necesarias en el `TelegramAdapter` y lo inicia, arrancando el bot.

### 7. Test de Integración con Mock Bot
- **Estado:** ⏳ PENDIENTE
- **Descripción:** El Especialista en Calidad creará un test de integración que valide todo el flujo usando un `Bot` de `aiogram` mockeado para verificar las llamadas a la API.
