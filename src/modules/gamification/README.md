# Módulo de Gamificación

Este módulo gestiona puntos, logros y misiones.

## Eventos Consumidos (Inputs)

- `UserMessageSent`: Para recompensar la participación.
- `MinigameCompleted`: Para dar puntos por ganar un minijuego.
- `NarrativeDecisionMade`: Para recompensar el avance en la historia.
- `DailyGiftClaimed`: Para registrar el bonus diario.

## Eventos Producidos (Outputs)

- `PointsAwarded`: Notifica que un usuario ha ganado puntos.
- `LevelUp`: Notifica que un usuario ha subido de nivel.
- `AchievementUnlocked`: Notifica que se ha desbloqueado un logro.
- `MissionCompleted`: Notifica que una misión ha sido completada.
