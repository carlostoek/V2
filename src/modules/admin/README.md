# Módulo de Administración

Este módulo gestiona los comandos de administrador, las suscripciones y las analíticas.

## Eventos Consumidos (Inputs)

- `UserRegistered`: Para las estadísticas de nuevos usuarios.
- `SubscriptionPurchased`: Para activar el acceso VIP.
- `PointsAwarded`: Para agregar a las analíticas de gamificación.
- `NarrativeNodeChanged`: Para seguir el progreso de los usuarios en la historia.

## Eventos Producidos (Outputs)

- `UserBanned`: Notifica que un usuario ha sido baneado.
- `ScheduledPostCreated`: Anuncia que un nuevo post ha sido programado para un canal.
- `SystemHealthChecked`: Emite un reporte periódico del estado del sistema.
