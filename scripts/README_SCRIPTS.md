# 🎭 Scripts de Diana Bot - Testing Dinámico

Esta carpeta contiene scripts especializados para probar y demostrar las capacidades dinámicas de Diana Bot, incluyendo generación de usuarios aleatorios y testing de interfaces adaptativas.

## 📋 Scripts Disponibles

### 🎲 `populate_random_users.py`
**Generador de usuarios completamente aleatorios**

Genera perfiles de usuario únicos cada vez que se ejecuta, con:
- Nombres realistas aleatorios
- Niveles y puntos variables (distribución realista)
- Estados VIP aleatorios (20% probabilidad)
- Personalidades diversas (10 tipos diferentes)
- Progreso narrativo variable
- Rachas de actividad realistas
- Patrones de comportamiento únicos

```bash
# Generar usuarios aleatorios
python scripts/populate_random_users.py

# El script preguntará cuántos usuarios generar (1-100)
# Los datos se guardan en scripts/generated_data/
```

**Características:**
- ✅ 100% aleatorio cada ejecución
- ✅ Perfiles realistas y diversos
- ✅ Guarda datos en JSON para reutilización
- ✅ Estadísticas de distribución
- ✅ Ejemplos de usuarios generados

### 🔍 `test_interface_with_user.py`
**Tester de interfaces dinámicas**

Permite inyectar cualquier ID de usuario y ver exactamente la interfaz que Diana le mostraría.

```bash
# Iniciar modo interactivo
python scripts/test_interface_with_user.py
```

**Funcionalidades:**
- 🎯 Probar ID específico
- 🎲 Usuario aleatorio de los generados
- 📊 Listar usuarios disponibles
- 🆚 Comparar interfaces entre 2 usuarios
- 🔍 Ver contexto completo detectado por Diana

**Análisis que muestra:**
- 📊 Stats básicos (nivel, puntos, racha)
- 🎭 Contexto Diana (mood, engagement, personalización)
- 👤 Contexto usuario (tier, intimidad, señales de conversión)
- 👑 Permisos admin
- 🎪 Preview de interfaces generadas

### 🎪 `diana_interface_showcase.py`
**Demostración completa de capacidades**

Showcase diseñado para mostrar todas las capacidades dinámicas de Diana con escenarios predefinidos.

```bash
# Ejecutar showcase completo
python scripts/diana_interface_showcase.py
```

**Escenarios incluidos:**
1. 🆕 **Usuario Nuevo** - Primer contacto con Diana
2. 🎯 **Usuario Activo FREE** - Buscando más contenido
3. 💎 **Usuario VIP Reciente** - Recién convertido
4. 👑 **Usuario VIP Elite** - Círculo íntimo
5. 🎪 **Usuario Explorador** - Le gusta descubrir
6. 📖 **Usuario Narrativo** - Conectado con la historia

**Para cada escenario muestra:**
- 👤 Perfil completo del usuario
- 🧠 Cómo Diana analiza al usuario
- 💬 Interfaz personalizada generada
- 🎨 Elementos únicos de esa interfaz

## 🚀 Guía de Uso Rápida

### 1. Generar datos de prueba
```bash
# Generar 20 usuarios aleatorios
echo "20" | python scripts/populate_random_users.py
```

### 2. Probar interfaz con ID específico
```bash
# Probar usuario con ID 12345
echo -e "2\n12345\n5" | python scripts/test_interface_with_user.py
```

### 3. Ver demostración completa
```bash
# Showcase completo (modo automático)
echo "1" | python scripts/diana_interface_showcase.py
```

## 📊 Estructura de Datos

### Usuario Generado (Ejemplo)
```json
{
  "user_id": 1691435327123,
  "username": "sofia456",
  "first_name": "Sofía",
  "last_name": "García",
  "level": 4,
  "points": 1250,
  "is_vip": false,
  "consecutive_days": 7,
  "narrative_progress": 45.2,
  "personality": "achiever",
  "intimacy_level": 0.65,
  "conversion_signals": 6
}
```

### Análisis de Contexto
```json
{
  "diana_context": {
    "mood": "yearning",
    "engagement_pattern": "regular_user",
    "personalization_score": 0.82
  },
  "user_context": {
    "tier": "free",
    "mood": "devoted",
    "intimacy_level": 0.65
  }
}
```

## 🎯 Casos de Uso

### Para Desarrollo
- ✅ Probar nuevas funcionalidades con perfiles diversos
- ✅ Verificar lógica de mood detection
- ✅ Validar elementos de conversión
- ✅ Debug de interfaces dinámicas

### Para Demostraciones
- ✅ Mostrar capacidades a stakeholders
- ✅ Exhibir personalización avanzada
- ✅ Comparar experiencias FREE vs VIP
- ✅ Demostrar ROI de features premium

### Para Testing
- ✅ Casos edge con perfiles extremos
- ✅ Regresión testing con datos consistentes
- ✅ Performance testing con múltiples usuarios
- ✅ A/B testing de interfaces

## 🔧 Configuración Avanzada

### Personalizar Generación
En `populate_random_users.py`, puedes modificar:

```python
# Cambiar distribución de niveles
level_weights = [0.3, 0.25, 0.2, 0.15, 0.05, 0.03, 0.02]

# Ajustar probabilidad VIP
is_vip = random.random() < 0.2  # 20%

# Agregar nuevas personalidades
personality_patterns = ["explorer", "achiever", "new_personality"]
```

### Crear Escenarios Personalizados
En `diana_interface_showcase.py`:

```python
custom_scenario = {
    "name": "🎨 Mi Escenario",
    "description": "Descripción personalizada",
    "profile_override": {
        "level": 5,
        "is_vip": True,
        "personality": "custom"
    }
}
```

## 📁 Archivos Generados

```
scripts/generated_data/
├── random_users_20250807_211027.json  # Usuarios generados
├── random_users_20250807_214532.json  # Otra ejecución
└── ...
```

Cada archivo incluye:
- ✅ Timestamp de generación
- ✅ Perfiles completos con metadatos
- ✅ Estadísticas de distribución
- ✅ Formato JSON compatible

## 🎭 Resultados Esperados

### Interfaces Dinámicas
- **Usuarios Newcomer**: Guías, tutoriales, lenguaje acogedor
- **Usuarios FREE activos**: Elementos de conversión sutiles
- **Usuarios VIP**: Contenido exclusivo, trato preferencial
- **Usuarios Elite**: Experiencias ultra-personalizadas

### Mood Detection
- **Explorer**: Múltiples opciones de navegación
- **Achiever**: Enfoque en logros y progreso
- **Storyteller**: Contenido narrativo rico
- **Sophisticated**: Lenguaje elegante y refinado

### Elementos de Conversión
- **FREE → VIP**: Invitaciones al Diván, previews exclusivos
- **VIP → Premium**: Experiencias más personales, contenido custom

## 🐛 Troubleshooting

### Errores Comunes

**Error: No users loaded**
```bash
# Solución: Generar usuarios primero
python scripts/populate_random_users.py
```

**Error: Service not available**
```bash
# Solución: Verificar que main.py funcione
python main.py
```

**Error: Database issues**
```bash
# Solución: Reinicializar DB
rm src/bot/database/bot.db
python scripts/populate_random_users.py
```

## 🎉 ¡Experimenta!

Estos scripts te permiten:
- 🎲 Generar miles de perfiles únicos
- 🔍 Ver interfaces desde cualquier perspectiva
- 🎪 Demostrar la sofisticación del sistema
- 🧪 Experimentar con diferentes configuraciones

**¡Diana Bot nunca será igual para dos usuarios!** 🎭✨