# Fase 1: Implementación de Flujo Transversal

## Objetivo
Implementar una estructura funcional básica que conecte los módulos de Administración (reacciones del canal), Gamificación (puntos) y Narrativa (entrega de historia) en un único flujo de trabajo.

## Criterio de Éxito
Una reacción de un usuario en una publicación del canal resulta en que el usuario recibe puntos, y el sistema de narrativa registra que se debe entregar un nuevo fragmento de historia a ese usuario. Todo el flujo debe estar validado por un test de integración.

---

## Plan de Acción y Registro de Progreso

### 1. Definir los Eventos de Comunicación
- **Estado:** ✅ COMPLETADO
- **Descripción:** El Arquitecto de Núcleo definió los eventos `ReactionAddedEvent` y `PointsAwardedEvent`.
- **Puntos Clave:**
  - Se creó un nuevo archivo centralizado para eventos de módulos: `src/modules/events.py`.
  - `PointsAwardedEvent` incluye un campo `source_event` para trazabilidad.

### 2. Implementar el Listener de Reacciones (Simulado)
- **Estado:** ✅ COMPLETADO
- **Descripción:** El Ingeniero de Administración creó un `TelegramListener` para simular la recepción de una reacción.
- **Puntos Clave:**
  - Se creó el archivo `src/infrastructure/telegram/listener.py`.
  - La clase `TelegramListener` tiene un método `simulate_reaction` para inyectar un `ReactionAddedEvent` en el bus, desacoplando el sistema de la API real de Telegram para facilitar las pruebas.

### 3. Actualizar el Servicio de Gamificación
- **Estado:** ✅ COMPLETADO
- **Descripción:** El Especialista en Gamificación modificó el `GamificationService` para que se suscriba al `ReactionAddedEvent` y publique un `PointsAwardedEvent`.
- **Puntos Clave:**
  - Se modificó `src/modules/gamification/service.py`.
  - El servicio ahora escucha `ReactionAddedEvent`.
  - Al recibir el evento, otorga puntos y publica un nuevo evento `PointsAwardedEvent`, completando su parte del ciclo.

### 4. Implementar el Servicio de Narrativa
- **Estado:** ✅ COMPLETADO
- **Descripción:** El Experto en Narrativa creó un `NarrativeService` que se suscribe al `PointsAwardedEvent`.
- **Puntos Clave:**
  - Se creó el archivo `src/modules/narrative/service.py`.
  - El servicio escucha `PointsAwardedEvent` y verifica si el `source_event` es una reacción.
  - Si la condición se cumple, asigna un fragmento de historia al usuario, cerrando el ciclo del flujo.

### 5. Integrar los Servicios en el Punto de Entrada
- **Estado:** ✅ COMPLETADO
- **Descripción:** El Arquitecto de Núcleo actualizó `main.py` para instanciar e interconectar todos los servicios.
- **Puntos Clave:**
  - Se modificó `src/main.py`.
  - El archivo ahora importa e instancia `GamificationService`, `NarrativeService` y `TelegramListener`.
  - Se añadió una simulación de flujo directamente en `main` para facilitar la depuración inicial.

### 6. Crear el Test de Integración del Flujo Completo
- **Estado:** ✅ COMPLETADO
- **Descripción:** El Especialista en Calidad escribió un único test de integración que valida todo el flujo.
- **Puntos Clave:**
  - Se creó el archivo `tests/integration/test_full_flow.py`.
  - El test instancia todos los servicios y el bus en memoria.
  - Simula una reacción y comprueba que tanto el `GamificationService` como el `NarrativeService` terminan en el estado esperado.
  - **Este test valida el Criterio de Éxito de la Fase 2.**
