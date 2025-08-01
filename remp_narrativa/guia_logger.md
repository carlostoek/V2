# 🎬 Guía de Integración - Sistema de Logging Sexy

## 🚀 Instalación Súper Rápida (2 minutos)

### Paso 1: Instalar el Sistema
```bash
# Copiar sexy_logger.py a tu proyecto
cp sexy_logger.py src/utils/
```

### Paso 2: Reemplazar Logging Actual
```python
# En lugar de:
import logging
logger = logging.getLogger(__name__)

# Usar:
from src.utils.sexy_logger import sexy_logger as logger
# o más simple:
from src.utils.sexy_logger import log
```

### Paso 3: ¡Disfruta de Logs Increíbles!
```python
# En lugar de:
logger.info("Usuario 12345 completó validación")

# Ahora:
log.diana_validation_success(
    user_id=12345,
    level="level_1_to_2",
    score=0.85,
    archetype="explorer",
    points_awarded=25
)
```

## 🎯 Integración en Diferentes Partes del Bot

### 1. En el Inicio del Bot (main.py)
```python
from src.utils.sexy_logger import sexy_logger as log

async def main():
    # Banner de inicio increíble
    log.banner(
        "🎭 BOT DIANA - PRODUCCIÓN",
        f"Versión {VERSION} | Ambiente: {ENVIRONMENT}"
    )
    
    # Inicialización con secciones
    with log.section("INICIALIZACIÓN DE SERVICIOS", "🔧"):
        log.startup("Cargando configuración...")
        config = load_config()
        
        log.database("Conectando a PostgreSQL...", operation="connect")
        await setup_database()
        
        log.startup("Inicializando servicios de gamificación...")
        gamification_service = GamificationService()
        
        log.startup("Inicializando Diana Validation Service...")
        diana_service = DianaValidationService()
        
        log.success("✅ Todos los servicios inicializados correctamente")
    
    # Al final, resumen automático
    log.summary("🏆 INICIALIZACIÓN COMPLETADA")
```

### 2. En el Servicio de Gamificación
```python
from src.utils.sexy_logger import log

class GamificationService:
    @log_execution_time(log, "Otorgar puntos por evento")
    async def award_points_for_event(self, user_id: int, event_type: str, points: int):
        try:
            log.gamification(
                f"Otorgando puntos por {event_type}",
                user_id=user_id,
                points=points
            )
            
            # Tu lógica existente aquí...
            await self.add_points(user_id, points)
            
            log.success(f"✅ Puntos otorgados exitosamente")
            
        except Exception as e:
            log.error(f"Error otorgando puntos", error=e)
            raise
```

### 3. En el Servicio de Validaciones Diana
```python
from src.utils.sexy_logger import log

class DianaValidationService:
    async def validate_level_transition(self, user_id: int, from_level: str, to_level: str, data: dict):
        validation_key = f"{from_level}_to_{to_level}"
        
        log.validation(
            f"🎯 Iniciando validación: {validation_key}",
            user_id=user_id,
            level=validation_key
        )
        
        try:
            # Tu lógica de validación...
            result = await self.validator.validate(user_id, validation_key, data)
            
            if result.passed:
                log.diana_validation_success(
                    user_id=user_id,
                    level=validation_key,
                    score=result.score,
                    archetype=result.archetype,
                    points_awarded=result.points_awarded
                )
            else:
                log.diana_validation_failed(
                    user_id=user_id,
                    level=validation_key,
                    score=result.score,
                    reason=result.failure_reason
                )
            
            return result
            
        except Exception as e:
            log.error(f"Error en validación {validation_key}", error=e)
            raise
```

### 4. En los Handlers del Bot de Telegram
```python
from src.utils.sexy_logger import log

class DianaBot:
    async def handle_user_message(self, update, context):
        user_id = update.effective_user.id
        message_text = update.message.text
        
        # Log de acción del usuario
        log.user_action(
            f"Mensaje recibido: '{message_text[:50]}...'",
            user_id=user_id,
            action="send_message"
        )
        
        # Procesar mensaje...
        try:
            response = await self.process_message(user_id, message_text)
            
            log.success(f"Mensaje procesado exitosamente")
            
        except Exception as e:
            log.error(f"Error procesando mensaje", error=e)
    
    async def handle_reaction_added(self, update, context):
        user_id = update.effective_user.id
        
        log.user_action(
            "Reacción añadida al canal",
            user_id=user_id,
            action="add_reaction"
        )
        
        # Trigger validación si es necesario
        if self.should_validate_level_1(user_id):
            await self.trigger_diana_validation(user_id, "level_1_to_2")
```

### 5. En el Servicio de Narrativa
```python
from src.utils.sexy_logger import log

class NarrativeService:
    async def deliver_narrative_fragment(self, user_id: int, fragment_key: str):
        log.narrative(
            f"Entregando fragmento narrativo: {fragment_key}",
            user_id=user_id,
            fragment=fragment_key
        )
        
        try:
            # Obtener contenido personalizado
            content = await self.get_adaptive_content(user_id, fragment_key)
            
            # Entregar al usuario
            await self.send_to_user(user_id, content)
            
            log.success(f"✅ Fragmento narrativo entregado")
            
        except Exception as e:
            log.error(f"Error entregando narrativa", error=e)
            raise
```

## 🎨 Ejemplos de Logs que Verás

### Logs de Validación Diana
```
🎯 VALIDATION Validación EXITOSA: level_1_to_2 | Score: 0.85 | Arquetipo: explorer | +25 puntos | user_id: 12345 | level: level_1_to_2 | score: 0.85
```

### Logs de Gamificación
```
🎮 GAMIFICATION Otorgando puntos por reacción rápida | user_id: 12345 | points: 15
```

### Logs de Acciones de Usuario
```
👤 USER Mensaje recibido: 'Me fascina la complejidad emocional de Diana...' | user_id: 12345 | action: send_message
```

### Logs de Performance
```
⚡ PERFORMANCE ✅ Completado: Validación Diana nivel 1→2 | duration: 0.234s
```

### Logs de Arquetipo
```
👤 USER 🎭 Arquetipo detectado: EXPLORER (Confianza: 0.92) | user_id: 12345 | action: archetype_detection
```

## 🔧 Configuración Avanzada

### Personalizar Colores para tu Ambiente
```python
# En development
sexy_logger = SexyLogger("DianaBot-DEV", enable_colors=True)

# En production
sexy_logger = SexyLogger("DianaBot-PROD", enable_colors=False)  # Sin colores para logs de servidor
```

### Integración con tu Sistema de Monitoreo
```python
class ProductionSexyLogger(SexyLogger):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Integrar con tu sistema de monitoreo
        self.metrics_client = your_metrics_client
        
    def _log(self, level, message, **kwargs):
        # Log normal
        super()._log(level, message, **kwargs)
        
        # Enviar métricas a tu sistema
        if level == LogLevel.ERROR:
            self.metrics_client.increment('diana.errors')
        elif 'validación EXITOSA' in message:
            self.metrics_client.increment('diana.validations.success')
```

### Logs Estructurados para Análisis
```python
# Para análisis posterior, también log en JSON
import json

class AnalyticsSexyLogger(SexyLogger):
    def diana_validation_success(self, user_id: int, level: str, score: float, **kwargs):
        # Log visual normal
        super().diana_validation_success(user_id, level, score, **kwargs)
        
        # Log estructurado para analytics
        analytics_data = {
            'event': 'diana_validation_success',
            'user_id': user_id,
            'level': level,
            'score': score,
            'timestamp': time.time(),
            **kwargs
        }
        
        # Guardar en archivo de analytics o enviar a servicio
        with open('diana_analytics.jsonl', 'a') as f:
            f.write(json.dumps(analytics_data) + '\n')
```

## 🚀 Migration de tu Sistema Actual

### Paso 1: Identificar Lugares de Logging Actual
```bash
# Buscar todos los lugares donde usas logging
grep -r "logger\." src/
grep -r "logging\." src/
grep -r "\.info\|\.error\|\.warning" src/
```

### Paso 2: Reemplazar Gradualmente
```python
# Antes:
logger.info(f"Usuario {user_id} completó validación con score {score}")

# Después:
log.diana_validation_success(user_id=user_id, level="level_1_to_2", score=score)
```

### Paso 3: Añadir Contextos y Secciones
```python
# Envolver operaciones largas en secciones
with log.section("PROCESAMIENTO DE USUARIO", "👤"):
    await process_user_data()
    await validate_user()
    await send_response()
```

## 📊 Métricas Automáticas que Obtienes

El sistema automáticamente trackea:
- ✅ Validaciones exitosas vs fallidas
- 💰 Puntos totales otorgados
- 👥 Usuarios únicos procesados
- ⚡ Tiempo de ejecución de operaciones
- ❌ Conteo de errores
- 🎭 Distribución de arquetipos

Todo esto aparece automáticamente en el resumen final:

```
📊 RESUMEN DE EJECUCIÓN 
============================================================
✅ SUCCESS ⏰ Tiempo de ejecución: 45.67s
✅ SUCCESS 👥 Usuarios únicos procesados: 23
✅ SUCCESS 🎯 Validaciones exitosas: 18/20 (90.0%)
✅ SUCCESS 💰 Puntos otorgados: 1,240
✅ SUCCESS ✅ Ejecución sin errores
============================================================
```

## 🎯 Quick Start para tu Bot

```python
# 1. Importar
from src.utils.sexy_logger import log

# 2. En tu main()
log.banner("🎭 TU BOT DIANA", "Logs sexy en producción")

# 3. En validaciones
log.diana_validation_success(user_id, "level_1_to_2", 0.85, "explorer", 25)

# 4. En gamificación  
log.gamification("Puntos por reacción", user_id=user_id, points=15)

# 5. En errores
log.error("Error procesando usuario", error=e)

# 6. Al final
log.summary()
```

¡Y ya tienes logs increíbles como en el ejemplo! 🎉
