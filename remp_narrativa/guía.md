# 🚀 Guía de Instalación Rápida - Sistema Diana

## ✅ Instalación Plug & Play (5 minutos)

### Paso 1: Instalar Dependencias
```bash
pip install aiohttp transitions asyncio
```

### Paso 2: Copiar Archivos
1. **Copiar** `diana_validation_client.py` a tu proyecto
2. **Copiar** `ejemplo_integracion_diana.py` como referencia

### Paso 3: Integrar en tu Bot (3 líneas de código)
```python
# En tu bot principal
from diana_validation_client import DianaValidator, DianaValidatorForTransitions

class TuBot:
    def __init__(self):
        # ¡Solo estas 3 líneas!
        self.validator = DianaValidator("http://validation-service:8000")
        self.transitions_validator = DianaValidatorForTransitions(self.validator)
        self.setup_transitions()  # Tu configuración actual de transitions
```

### Paso 4: Usar en Transitions
```python
# En tus transitions conditions
transitions = [
    {
        'trigger': 'user_reacted',
        'source': 'level_1_challenge',
        'dest': 'level_2_observation',
        'conditions': self.validate_level_1,  # ← Una línea
        'after': 'deliver_rewards'
    }
]

async def validate_level_1(self):
    # ¡Una sola línea para validar!
    return await self.transitions_validator.validate_level_1_completion(
        self.user_id, 
        self.reaction_data
    )
```

## 🎯 Métodos Disponibles Inmediatamente

### Validaciones para Transitions
```python
# Todas estas funcionan como conditions de transitions:
await validator.can_advance_to_level_2(user_id, reaction_data)
await validator.can_advance_to_level_3(user_id, observation_events) 
await validator.can_advance_to_vip(user_id, desire_profile)
await validator.can_advance_to_level_6(user_id, empathy_responses)
```

### Tracking Automático (No bloquea)
```python
# Trackea eventos sin bloquear el bot:
await validator.track_user_event(user_id, 'reaction', data)
await validator.track_user_event(user_id, 'message', data)
await validator.track_user_event(user_id, 'clue_found', data)
```

### Contenido Personalizado
```python
# Obtiene contenido adaptado al arquetipo:
content = await validator.get_adaptive_content(user_id, 'diana_welcome')
await send_message(content['text'])
```

## 📋 Formatos de Datos Esperados

### Para Validación Nivel 1 → 2
```python
reaction_data = {
    'timestamp': 1234567890.0,
    'speed_seconds': 30,  # Segundos desde mensaje hasta reacción
    'message_id': 'msg_123'
}
```

### Para Validación Nivel 2 → 3
```python
observation_events = [
    {
        'type': 'clue_found',
        'clue_id': 'pista_1', 
        'timestamp': 1234567890.0,
        'time_to_find': 120  # segundos
    },
    {
        'type': 'exploration',
        'duration': 300,  # segundos explorando
        'interactions': 5
    }
]
```

### Para Validación Nivel 3 → VIP
```python
desire_profile = {
    'question_1': 'Respuesta del usuario...',
    'question_2': 'Respuesta del usuario...',
    'question_3': 'Respuesta del usuario...'
    # Tantas como necesites
}
```

### Para Validación Nivel 5 → 6
```python
empathy_responses = [
    {
        'diana_vulnerability': 'Texto de vulnerabilidad de Diana',
        'user_response': 'Respuesta empática del usuario',
        'response_time': 180,  # segundos para responder
        'timestamp': 1234567890.0
    }
]
```

## 🔧 Configuración del Servicio de Validaciones

### Opción A: Servidor Local (Para Testing)
```bash
# Clonar repo del servicio (cuando esté disponible)
git clone [repo-validaciones-diana]
cd diana-validation-service

# Instalar dependencias
pip install fastapi uvicorn postgresql redis

# Configurar variables de entorno
export DATABASE_URL="postgresql://user:pass@localhost:5432/diana"
export REDIS_URL="redis://localhost:6379"

# Ejecutar servidor
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Opción B: Mock Server (Para Desarrollo)
```python
# mock_validation_server.py - Para empezar inmediatamente
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.post("/api/v1/validate/level-1-to-2")
async def validate_level_1(data: dict):
    # Mock que siempre pasa para testing
    return {
        "passed": True,
        "engagement_score": 0.8,
        "reaction_type": "thoughtful" if data.get("speed_seconds", 0) > 60 else "immediate",
        "diana_response": "adaptive_response_1",
        "reward_type": "mochila_standard"
    }

@app.post("/api/v1/validate/level-2-to-3")
async def validate_level_2(data: dict):
    clues_found = data.get("clues_found", 0)
    return {
        "passed": clues_found >= 2,
        "observation_score": min(clues_found / 3.0, 1.0),
        "observation_type": "explorer" if clues_found > 3 else "focused",
        "user_archetype": "explorer",
        "rewards": ["pista_2", "vision_partial"]
    }

# Ejecutar: uvicorn mock_validation_server:app --port 8000
```

## 📱 Ejemplos de Integración por Librería

### Con python-telegram-bot
```python
from telegram.ext import Application, MessageHandler, filters
from diana_validation_client import DianaValidator

class DianaBot:
    def __init__(self):
        self.validator = DianaValidator()
        
    async def handle_message(self, update, context):
        user_id = update.effective_user.id
        
        # Track automático
        await self.validator.track_user_event(
            user_id, 
            'message', 
            {'text': update.message.text}
        )
        
        # Procesar según estado actual...
```

### Con aiogram
```python
from aiogram import Bot, Dispatcher, types
from diana_validation_client import DianaValidator

class DianaBot:
    def __init__(self):
        self.validator = DianaValidator()
        
    async def handle_message(self, message: types.Message):
        user_id = message.from_user.id
        
        # Track automático
        await self.validator.track_user_event(
            user_id,
            'message',
            {'text': message.text}
        )
```

## 🎭 Respuestas del Sistema

### Validation Response Format
```python
class ValidationResponse:
    result: ValidationResult  # PASSED, FAILED, PENDING
    score: float             # 0.0 - 1.0
    data: Dict[str, Any]     # Datos específicos para personalización
    message: str             # Mensaje explicativo
    next_action: str         # Siguiente acción recomendada
```

### Contenido Adaptativo Format
```python
adaptive_content = {
    'text': 'Mensaje personalizado para el usuario',
    'buttons': [
        {'text': 'Botón 1', 'callback': 'action_1'},
        {'text': 'Botón 2', 'callback': 'action_2'}
    ],
    'media': 'https://url-imagen-opcional.jpg',
    'archetype': 'explorer'  # Arquetipo detectado
}
```

## 🚦 Estados de Transiciones Compatibles

```python
# Estados recomendados para tu FSM
states = [
    'level_1_intro',         # Bienvenida inicial
    'level_1_challenge',     # Desafío de reacción
    'level_2_observation',   # Misión de observación
    'level_2_searching_clues', # Búsqueda activa de pistas
    'level_3_desire_profile', # Evaluación de perfil
    'level_4_vip_intro',     # Bienvenida VIP
    'level_5_empathy_test',  # Evaluación empática
    'level_6_synthesis',     # Síntesis final
    'inner_circle'          # Círculo íntimo
]

# Triggers recomendados
triggers = [
    'user_reacted_to_post',  # Para level_1 → level_2
    'observation_completed', # Para level_2 → level_3
    'profile_completed',     # Para level_3 → VIP
    'empathy_completed',     # Para level_5 → level_6
    'validation_failed'      # Para manejo de fallos
]
```

## ⚡ Quick Start Checklist

- [ ] Instalar dependencias: `pip install aiohttp transitions`
- [ ] Copiar `diana_validation_client.py` al proyecto
- [ ] Inicializar validator en bot: `self.validator = DianaValidator()`
- [ ] Configurar transitions con conditions que usen el validator
- [ ] Agregar tracking de eventos: `await validator.track_user_event()`
- [ ] Usar contenido adaptativo: `await validator.get_adaptive_content()`
- [ ] Configurar servidor de validaciones (local o mock)
- [ ] Testear transiciones con datos de ejemplo

## 🆘 Troubleshooting

### Error: "Connection refused"
- Verificar que el servicio de validaciones esté ejecutándose
- Usar mock server para desarrollo local

### Error: "Validation always fails"
- Verificar formato de datos enviados
- Revisar logs del servidor de validaciones
- Usar mock server que siempre pasa para testing

### Error: "AsyncMachine not working"
- Verificar que estés usando `AsyncMachine` de transitions
- Usar `await` en todos los métodos de validación

## 📞 Soporte Rápido

**Para integración inmediata:**
1. Usar el mock server incluido
2. Copiar el ejemplo completo de integración
3. Adaptar los handlers de tu bot actual
4. Testear con un usuario de prueba

**El sistema está diseñado para funcionar inmediatamente** con configuración mínima. ¡El equipo puede empezar a usarlo hoy mismo!
