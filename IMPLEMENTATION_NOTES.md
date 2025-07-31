# Notas de Implementación - Sistema de Misiones

## Estructura del Sistema

El sistema de misiones ha sido implementado siguiendo la arquitectura limpia del proyecto, con una clara separación entre:

1. **Modelos de datos** (`src/bot/database/models/gamification.py`)
   - `Mission`: Define misiones disponibles en el sistema
   - `UserMission`: Relaciona usuarios con misiones y su progreso
   - `MissionTypeEnum`: Tipos de misiones (DAILY, WEEKLY, ONE_TIME, EVENT, STORY)
   - `MissionStatusEnum`: Estados de misiones (AVAILABLE, IN_PROGRESS, COMPLETED, FAILED, EXPIRED)

2. **Servicio de Gamificación** (`src/modules/gamification/service.py`)
   - Lógica de negocio para asignar, actualizar y completar misiones
   - Gestión de puntos y recompensas
   - Verificación de logros relacionados con misiones
   - Asignación inicial y refresco de misiones diarias

3. **Handlers de Interfaz** 
   - `src/bot/handlers/gamification/misiones.py`: Comando `/misiones` para ver misiones
   - `src/bot/handlers/gamification/progress.py`: Visualización de progreso y detalles

4. **Sistema de Eventos**
   - `src/modules/events.py`: Definición de eventos (MissionCompletedEvent, etc.)
   - `src/bot/listeners/mission_listener.py`: Escucha eventos y envía notificaciones

## Funcionalidades Implementadas

1. **Comando /misiones**
   - Visión general de misiones disponibles, en progreso y completadas
   - Navegación detallada por categorías
   - Visualización del progreso de cada misión

2. **Visualización de Progreso**
   - Barras de progreso visuales para misiones
   - Desglose de objetivos individuales
   - Información detallada sobre fechas y recompensas

3. **Sistema de Notificaciones**
   - Notificaciones cuando una misión avanza significativamente
   - Alertas cuando se completa una misión
   - Recordatorios para reclamar recompensas

4. **Integración con Eventos**
   - Las misiones progresan automáticamente en respuesta a eventos del sistema
   - Conectado con el sistema narrativo y de gamificación
   - Misiones que avanzan por reacciones, progreso narrativo y desbloqueo de pistas

## Flujo de Trabajo

1. El usuario recibe misiones iniciales al empezar a usar el bot
2. Las misiones avanzan automáticamente según las acciones del usuario
3. El usuario puede ver su progreso con `/misiones`
4. Al completar una misión, recibe una notificación y puede reclamar recompensas
5. Las misiones diarias se refrescan automáticamente

## Próximos Pasos

1. **Refinamiento de la Interfaz**
   - Mejorar la visualización de recompensas
   - Añadir filtros para misiones por categoría

2. **Sistema de Misiones Especiales**
   - Implementar misiones exclusivas para eventos temporales
   - Añadir misiones basadas en la narrativa principal

3. **Pruebas y Validación**
   - Crear tests unitarios y de integración
   - Validar la progresión correcta de misiones

4. **Optimización de Rendimiento**
   - Mejorar el sistema de caché para misiones
   - Optimizar consultas a la base de datos