# Módulo de Narrativa

Este módulo gestiona el flujo de la historia, los diálogos y las decisiones.

## Eventos Consumidos (Inputs)

- `UserMessageSent`: Para procesar respuestas a preguntas abiertas.
- `CallbackQueryReceived`: Para procesar clics en botones de decisión.
- `MissionCompleted`: Para desbloquear nuevos arcos narrativos.
- `AchievementUnlocked`: Para reaccionar a logros importantes con diálogos especiales.

## Eventos Producidos (Outputs)

- `NarrativeNodeChanged`: Notifica que el usuario ha avanzado a un nuevo punto de la historia.
- `NarrativeDecisionMade`: Informa qué opción ha elegido el usuario.
- `QuestStarted`: Anuncia el inicio de una nueva misión narrativa.
