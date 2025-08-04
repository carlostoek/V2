# 🎮 Comandos Disponibles

## 📋 Lista Completa de Comandos

### 🚀 Comandos Básicos

#### `/start`
**Función**: Inicia el bot y la experiencia narrativa  
**Disponible para**: Todos los usuarios  
**Respuesta**: Mensaje de bienvenida + primer fragmento narrativo  

```
Usuario: /start
Diana: ¡Bienvenido a mi mundo! 🌙 
Soy Diana, y tengo muchos secretos que compartir contigo...
[Primer fragmento narrativo]
```

#### `/help`
**Función**: Muestra ayuda y comandos disponibles  
**Disponible para**: Todos los usuarios  
**Respuesta**: Lista de comandos según el rol del usuario

#### `/menu`
**Función**: Muestra el menú principal interactivo  
**Disponible para**: Todos los usuarios  
**Respuesta**: Teclado con opciones principales

### 👤 Comandos de Usuario

#### `/profile` o `/perfil`
**Función**: Muestra tu perfil completo  
**Disponible para**: Todos los usuarios  
**Información mostrada**:
- Nivel actual
- Besitos disponibles  
- Logros obtenidos
- Racha de días consecutivos
- Progreso narrativo

```
📊 TU PERFIL

👤 Nivel: 3 (Explorador)
💰 Besitos: 1,247
🏆 Logros: 12/45
🔥 Racha: 7 días
📖 Progreso: Capítulo 2, Fragmento 8
```

#### `/besitos`
**Función**: Ver balance y transacciones de besitos  
**Disponible para**: Todos los usuarios  
**Información mostrada**:
- Balance actual
- Últimas transacciones
- Próximas oportunidades de ganancia

#### `/misiones`
**Función**: Ver misiones activas y disponibles  
**Disponible para**: Todos los usuarios  
**Información mostrada**:
- Misiones en progreso
- Misiones completadas hoy
- Próximas misiones disponibles
- Recompensas pendientes

### 🎮 Comandos de Gamificación

#### `/trivia`
**Función**: Inicia una trivia interactiva  
**Disponible para**: Todos los usuarios  
**Opciones**:
- Selección de dificultad (Fácil, Medio, Difícil, Experto)
- Categorías diferentes
- Preguntas VIP (solo usuarios premium)

#### `/regalo` o `/daily`
**Función**: Reclama tu regalo diario  
**Disponible para**: Todos los usuarios  
**Recompensas posibles**:
- Besitos (5-50)
- Pistas narrativas
- Objetos especiales
- Multiplicadores de puntos

#### `/tienda` o `/shop`
**Función**: Accede a la tienda de objetos  
**Disponible para**: Todos los usuarios  
**Categorías**:
- 🔮 Místicos - Objetos mágicos y únicos
- 💎 Elegantes - Items de lujo y distinción  
- 🎯 Útiles - Herramientas prácticas
- 🌟 Especiales - Ediciones limitadas

#### `/logros`
**Función**: Ver todos tus logros y badges  
**Disponible para**: Todos los usuarios  
**Tipos de logros**:
- Progreso narrativo
- Actividad social
- Constancia
- Habilidades especiales

### 📖 Comandos Narrativos

#### `/mochila` o `/inventario`
**Función**: Ver objetos y pistas en tu mochila  
**Disponible para**: Todos los usuarios  
**Contenido**:
- Pistas narrativas recolectadas
- Objetos comprados en la tienda
- Items especiales obtenidos
- Combinaciones posibles

#### `/historia`
**Función**: Revisa fragmentos narrativos anteriores  
**Disponible para**: Todos los usuarios  
**Opciones**:
- Últimos 5 fragmentos
- Búsqueda por capítulo
- Momentos clave marcados

#### `/pistas`
**Función**: Ver todas las pistas recolectadas  
**Disponible para**: Todos los usuarios  
**Información**:
- Pistas por categoría
- Progreso de combinaciones
- Pistas faltantes para secretos

### 💎 Comandos VIP

#### `/vip`
**Función**: Panel de control VIP  
**Disponible para**: Usuarios VIP solamente  
**Características exclusivas**:
- Contenido narrativo premium
- Trivias de nivel experto
- Objetos únicos en tienda
- Misiones especiales

#### `/canal_vip`
**Función**: Acceso directo al canal VIP  
**Disponible para**: Usuarios VIP con suscripción activa  

### 🛡️ Comandos de Administración

#### `/admin`
**Función**: Panel de administración  
**Disponible para**: Administradores solamente  
**Subcomandos**:
- `/admin users` - Gestión de usuarios
- `/admin stats` - Estadísticas del sistema
- `/admin events` - Control de eventos especiales
- `/admin channels` - Gestión de canales

#### `/broadcast`
**Función**: Enviar mensaje a todos los usuarios  
**Disponible para**: Administradores solamente  
**Sintaxis**: `/broadcast [mensaje]`

#### `/ban` / `/unban`
**Función**: Banear/desbanear usuarios  
**Disponible para**: Administradores solamente  
**Sintaxis**: 
- `/ban @usuario razón`
- `/unban @usuario`

## 🔄 Comandos Contextuales

### Durante Narrativa
Cuando estás en un fragmento narrativo interactivo:

- **Números (1, 2, 3...)** - Seleccionar opciones de decisión
- **Botones inline** - Usar objetos de la mochila
- **Reacciones** - Expresar emociones que afectan la historia

### Durante Trivia
- **A, B, C, D** - Responder preguntas múltiple opción
- `/salir` - Abandonar trivia actual
- `/pista` - Usar pista (si tienes disponibles)

### En la Tienda
- **Números** - Seleccionar items para comprar
- `/comprar [número]` - Comprar item específico
- `/salir` - Salir de la tienda

## ⚡ Atajos Rápidos

### Comandos Abreviados
- `/p` → `/profile`
- `/m` → `/misiones` 
- `/t` → `/trivia`
- `/s` → `/shop`
- `/i` → `/inventario`

### Comandos de Emojis
- `🎁` → Reclamar regalo diario
- `🎮` → Iniciar trivia rápida
- `🛒` → Abrir tienda
- `📖` → Ver historia actual
- `👤` → Ver perfil

## 📱 Interacciones Especiales

### Reacciones a Mensajes
Reaccionar a mensajes de Diana otorga besitos automáticamente:

- ❤️ **Like** - 1 besito
- 😍 **Love** - 2 besitos  
- 😮 **Wow** - 3 besitos
- 😘 **Kiss** - 5 besitos

### Menciones
- Mencionar a Diana (`@DianaBot`) en grupos activa respuestas especiales
- Responder directamente a sus mensajes profundiza la conversación

### Mensajes Libres
Diana responde a mensajes normales basándose en:
- Tu progreso narrativo actual
- Estado emocional del personaje  
- Historial de interacciones
- Objetos en tu mochila

## 🚫 Comandos Deshabilitados/Limitados

### Por Rol
- Comandos VIP para usuarios gratuitos
- Comandos admin para no-administradores

### Por Estado
- Algunos comandos requieren progreso narrativo mínimo
- Ciertas funciones se bloquean temporalmente tras uso excesivo

### Por Tiempo
- Comando de regalo diario (24 horas entre usos)
- Trivia con cooldown para evitar spam
- Límites de interacción por hora para usuarios gratuitos

## 🆘 Soporte

Si un comando no funciona como esperado:

1. **Verifica tu rol** - Algunos comandos son exclusivos
2. **Revisa la sintaxis** - Usa `/help [comando]` para detalles
3. **Comprueba el cooldown** - Algunos comandos tienen límites de tiempo
4. **Contacta admin** - Usa `/admin` si eres administrador, o reporta en el grupo

## 📈 Comandos en Desarrollo

### Próximamente
- `/auction` - Sistema de subastas VIP
- `/guild` - Funciones de gremios/clanes
- `/craft` - Sistema de crafteo de objetos
- `/pvp` - Competencias entre usuarios

---

💡 **Tip**: Usa `/menu` para acceder visualmente a la mayoría de estas funciones sin recordar comandos específicos.