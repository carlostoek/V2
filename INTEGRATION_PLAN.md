# Plan de Integración y Desarrollo - DianaBot V2

## Visión General

Este documento detalla el plan de integración para los tres sistemas principales del bot: Narrativa, Gamificación y Administración de Canales. El objetivo es crear un ecosistema cohesivo donde cada acción del usuario afecte y active los diferentes módulos del bot.

## Estructura del Sistema

El bot se organiza en tres sistemas principales interconectados:

### 1. Sistema de Narrativa Inmersiva 📖
- Historia ramificada con decisiones del usuario
- Ambientación erótica, elegante y psicológica
- Niveles 1-3 accesibles desde canal gratuito
- Niveles 4-6 exclusivos para canal VIP
- Sistema de pistas (LorePieces) desbloqueables

### 2. Sistema de Gamificación Total 🎯
- "Besitos" como moneda del sistema
- Misiones diarias y especiales
- Logros y badges desbloqueables
- Tienda, trivias y subastas
- Sistema de niveles basado en puntos acumulados

### 3. Sistema de Administración de Canales 🛡️
- Gestión de canales gratuitos y VIP
- Control de acceso mediante tokens
- Programación de publicaciones
- Gestión de usuarios y suscripciones

## Puntos de Interconexión

| Acción del Usuario | Efecto en Narrativa | Efecto en Gamificación | Efecto en Administración |
|-------------------|---------------------|------------------------|--------------------------|
| Reacciona a publicación | Puede desbloquear pista | Otorga besitos | Registra participación |
| Toma decisión narrativa | Cambia rumbo de historia | Puede activar misiones | Puede registrarse para eventos |
| Compra objeto en tienda | Puede ser necesario para avanzar | Gasta besitos | No impacta |
| Participa en trivia | Puede otorgar fragmento oculto | Da puntos o badges | No impacta |
| Accede a canal VIP | Desbloquea niveles avanzados | Accede a misiones especiales | Requiere suscripción activa |
| Completa misión | Puede desbloquear fragmento | Gana besitos/logros | No impacta |

## Plan de Implementación

### Fase 1: Infraestructura Base

1. **Ampliar Event Bus**
   - [x] Crear `ReactionAddedEvent` (completado)
   - [x] Crear `PointsAwardedEvent` (completado)
   - [x] Crear `NarrativeProgressionEvent` (completado)
   - [x] Crear `PieceUnlockedEvent` (completado)
   - [x] Crear `MissionCompletedEvent` (completado)
   - [x] Crear `LevelUpEvent` (completado)

2. **Expandir Modelos de Base de Datos**
   - [x] Ampliar modelo `User`: nivel, puntos, rol (free/VIP) (completado)
   - [x] Crear modelo `NarrativePiece`: fragmentos y pistas (completado)
   - [ ] Crear modelo `Mission`: misiones y requisitos
   - [x] Crear modelo `UserProgress`: progreso narrativo (completado como `UserNarrativeState`)

3. **Servicios Core**
   - [x] Implementar `GamificationService` básico (completado)
   - [x] Implementar `NarrativeService` básico (completado)
   - [ ] Ampliar `GamificationService`: misiones y niveles
   - [x] Ampliar `NarrativeService`: gestión de pistas (completado)
   - [ ] Implementar `ChannelService`: gestión de canales

### Fase 2: Implementación de Handlers

1. **Handlers de Usuario**
   - [x] `/start`: Comando básico (completado)
   - [x] `/help`: Ayuda básica (completado)
   - [x] `/profile`: Perfil básico (completado)
   - [ ] Ampliar `/start`: Presentación de Lucien
   - [ ] Ampliar `/profile`: Mostrar puntos y nivel
   - [x] Implementar `/mochila`: Pistas desbloqueadas (completado)
   - [x] Implementar `/misiones`: Misiones disponibles

2. **Handlers de Narrativa**
   - [x] Sistema de navegación narrativa (completado)
   - [x] Manejo de decisiones en la historia (completado)
   - [x] Visualización de pistas desbloqueadas (completado)
   - [x] Combinación de pistas para desbloquear contenido (completado con integración básica)

3. **Handlers de Gamificación**
   - [ ] Sistema de tienda con besitos
   - [ ] Sistema de trivias y respuestas
   - [ ] Sistema de misiones y seguimiento
   - [ ] Sistema de regalos diarios

4. **Handlers de Administración**
   - [ ] Panel admin para gestión de canales
   - [ ] Sistema de tokens VIP
   - [ ] Herramientas de programación de contenido
   - [ ] Gestión de subastas VIP

### Fase 3: Integración y Sistemas Avanzados

1. **Sistema de Reacciones**
   - [ ] Conectar reacciones con recompensas
   - [ ] Desbloqueo de pistas basado en reacciones

2. **Sistema de Progresión**
   - [ ] Verificación de nivel para acceso a contenido
   - [ ] Desbloqueo progresivo de funcionalidades

3. **Sistema de Subastas VIP**
   - [ ] Mecánica de subasta con besitos
   - [ ] Notificaciones para ofertas y resultados

## Próximos Pasos (Sprint Actual)

1. **Ampliar NarrativeService**
   - [x] Sistema básico de fragmentos narrativos (completado)
   - [x] Funcionalidad para trackear progreso (completado)
   - [x] Sistema de pistas y almacenamiento (completado)

2. **Desarrollar Handlers de Narrativa**
   - [x] Command handler para `/mochila` (completado)
   - [x] Callbacks para navegación narrativa (completado)
   - [x] Visualización de fragmentos y pistas (completado)

3. **Integrar con GamificationService**
   - [x] Conectar desbloqueo de fragmentos con puntos (completado)
   - [x] Verificación de nivel para acceso a contenido (completado)

4. **Próximos Pasos**
   - [x] Implementar sistema de misiones y recompensas
   - [x] Ampliar GamificationService con niveles y economía
   - [ ] Desarrollar sistema de tienda y trivias
   - [ ] Implementar panel de administración de canales

## Arquitectura de Eventos

Para facilitar la comunicación entre módulos, utilizaremos estos eventos clave:

1. **ReactionAddedEvent**
   - Disparado cuando: Usuario reacciona a publicación
   - Datos: user_id, message_id, reaction_type
   - Consumidores: GamificationService, NarrativeService

2. **PointsAwardedEvent**
   - Disparado cuando: Se otorgan puntos a un usuario
   - Datos: user_id, points, source_event
   - Consumidores: NarrativeService, UserService

3. **NarrativeProgressionEvent**
   - Disparado cuando: Usuario avanza en la narrativa
   - Datos: user_id, fragment_id, choices_made
   - Consumidores: GamificationService, AdminService

4. **PieceUnlockedEvent**
   - Disparado cuando: Usuario desbloquea una pista narrativa
   - Datos: user_id, piece_id, unlock_method
   - Consumidores: NarrativeService, UserService

5. **MissionCompletedEvent**
   - Disparado cuando: Usuario completa una misión
   - Datos: user_id, mission_id, completion_time
   - Consumidores: GamificationService, NarrativeService

## Notas Importantes

- Todo el sistema debe funcionar con o sin base de datos, usando fallbacks en memoria cuando sea necesario.
- Las transiciones entre niveles narrativos deben ser fluidas y con feedback al usuario.
- La experiencia de usuario debe ser coherente, sin importar por qué módulo navegue.
- Cada implementación debe incluir tests unitarios y de integración apropiados.

Este plan está sujeto a revisiones y ajustes a medida que avance el desarrollo.

**Fecha de última actualización:** 31/07/2025  
**Última tarea completada:** Implementación del sistema narrativo y su integración