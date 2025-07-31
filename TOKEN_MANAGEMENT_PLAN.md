# Plan de Implementación: Sistema de Gestión de Tokens

## 📋 Descripción General

El Sistema de Gestión de Tokens permitirá a los administradores de canales crear y administrar suscripciones de pago mediante tokens de un solo uso. Los usuarios podrán canjear estos tokens para obtener acceso a canales VIP durante un período específico.

## 🔄 Flujo de Operación

1. **Configuración de Tarifas**:
   - El administrador accede a la sección de tarifas en la configuración del bot
   - Registra nuevas tarifas especificando:
     - Nombre de la tarifa
     - Duración de la suscripción (en días)
     - Precio
     - Tiempo de validez del token (opcional, por defecto 7 días)

2. **Generación de Enlaces**:
   - El administrador selecciona "Generar Enlace" en el panel de administración
   - El bot muestra un teclado inline con las tarifas disponibles
   - Al seleccionar una tarifa, el bot genera un token único y devuelve un enlace con vista previa

3. **Canje de Tokens**:
   - El usuario hace clic en el enlace recibido
   - El bot verifica la validez del token y su fecha de expiración
   - Si el token es válido:
     - El bot genera una invitación nativa al canal
     - Registra al usuario como miembro VIP
     - Establece la fecha de expiración según la tarifa
     - Marca el token como utilizado

4. **Monitoreo y Gestión**:
   - El administrador puede ver estadísticas de tokens generados y canjeados
   - El sistema verifica automáticamente membresías expiradas
   - Notificaciones automáticas para expiración próxima

## 🛠️ Componentes Principales

### 1. Modelos de Base de Datos

```python
class Tariff(Base, TimestampMixin):
    """Modelo para almacenar tarifas de suscripción."""
    
    __tablename__ = "tariffs"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    duration_days = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    token_validity_days = Column(Integer, default=7)
    description = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False)
    
    # Relaciones
    channel = relationship("Channel", back_populates="tariffs")
    tokens = relationship("SubscriptionToken", back_populates="tariff", cascade="all, delete-orphan")


class SubscriptionToken(Base, TimestampMixin):
    """Modelo para almacenar tokens de suscripción."""
    
    __tablename__ = "subscription_tokens"
    
    id = Column(Integer, primary_key=True)
    token = Column(String(64), unique=True, nullable=False)
    tariff_id = Column(Integer, ForeignKey("tariffs.id"), nullable=False)
    generated_by = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    is_used = Column(Boolean, default=False)
    used_by = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    used_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=False)
    
    # Relaciones
    tariff = relationship("Tariff", back_populates="tokens")
    generator = relationship("User", foreign_keys=[generated_by])
    user = relationship("User", foreign_keys=[used_by])
```

### 2. Eventos del Sistema

```python
class TokenGeneratedEvent(IEvent):
    """Evento que se dispara cuando se genera un token de suscripción."""
    def __init__(self, token_id: int, tariff_id: int, admin_id: int):
        self.token_id = token_id
        self.tariff_id = tariff_id
        self.admin_id = admin_id


class TokenRedeemedEvent(IEvent):
    """Evento que se dispara cuando se canjea un token de suscripción."""
    def __init__(self, token_id: int, user_id: int, channel_id: int, expiry_date: datetime):
        self.token_id = token_id
        self.user_id = user_id
        self.channel_id = channel_id
        self.expiry_date = expiry_date


class TokenExpiredEvent(IEvent):
    """Evento que se dispara cuando expira un token sin usar."""
    def __init__(self, token_id: int, tariff_id: int):
        self.token_id = token_id
        self.tariff_id = tariff_id
```

### 3. Servicio Tokeneitor

```python
class Tokeneitor(ICoreService):
    """Servicio para manejar la lógica de tokens de suscripción."""
    
    def __init__(self, event_bus: IEventBus):
        self._event_bus = event_bus
        self.logger = logging.getLogger(__name__)
    
    async def setup(self) -> None:
        """Suscribe el servicio a los eventos relevantes."""
        # Suscribir a eventos relevantes
        # Iniciar tareas periódicas para verificación de tokens
    
    async def create_tariff(self, channel_id: int, name: str, duration_days: int, 
                           price: float, token_validity_days: int = 7,
                           description: str = None) -> Optional[int]:
        """Crea una nueva tarifa para un canal."""
        # Implementación
    
    async def generate_token(self, tariff_id: int, admin_id: int) -> Optional[str]:
        """Genera un nuevo token para una tarifa específica."""
        # Implementación
    
    async def verify_token(self, token: str, user_id: int) -> Optional[Dict[str, Any]]:
        """Verifica la validez de un token y lo marca como utilizado si es válido."""
        # Implementación
    
    async def get_user_subscriptions(self, user_id: int) -> List[Dict[str, Any]]:
        """Obtiene las suscripciones activas de un usuario."""
        # Implementación
    
    async def get_channel_tariffs(self, channel_id: int) -> List[Dict[str, Any]]:
        """Obtiene las tarifas disponibles para un canal."""
        # Implementación
```

### 4. Handlers de UI

```python
# Handler para configuración de tarifas
async def handle_tariff_setup(message: types.Message, state: FSMContext):
    """Maneja la configuración de nuevas tarifas."""
    # Implementación

# Handler para generación de tokens
async def handle_generate_token(callback_query: types.CallbackQuery, tokeneitor: Tokeneitor):
    """Maneja la generación de tokens para una tarifa seleccionada."""
    # Implementación

# Handler para comando /start con token
async def handle_token_redemption(message: types.Message, token: str, tokeneitor: Tokeneitor):
    """Maneja el canje de un token desde un enlace de invitación."""
    # Implementación
```

## 🚀 Plan de Implementación

### Etapa 1: Infraestructura Básica (2 días)

1. Implementar modelos de base de datos para tarifas y tokens
2. Desarrollar eventos relacionados con tokens
3. Crear estructura básica del `Tokeneitor`
4. Implementar funciones de generación y verificación de tokens

### Etapa 2: UI y Flujo de Usuario (2 días)

1. Desarrollar handlers para configuración de tarifas
2. Implementar teclados inline para selección de tarifas
3. Crear comandos para generación de enlaces
4. Desarrollar sistema de enlaces con vista previa

### Etapa 3: Integración con Sistema de Canales (1 día)

1. Integrar `Tokeneitor` con `ChannelService`
2. Implementar proceso de invitación nativa a canales
3. Desarrollar sistema de gestión de membresías VIP

### Etapa 4: Estadísticas y Administración (1 día)

1. Implementar panel de estadísticas para administradores
2. Desarrollar sistema de notificaciones para expiración
3. Crear comandos para gestión de tarifas y tokens

## 📊 Métricas y Evaluación

- **Tasa de Conversión**: Porcentaje de tokens generados que son efectivamente canjeados
- **Tiempo de Validez Óptimo**: Análisis del tiempo promedio entre generación y canje
- **Retención VIP**: Tiempo que los usuarios permanecen como miembros VIP
- **Distribución de Tarifas**: Popularidad relativa de las diferentes tarifas

## 🔐 Consideraciones de Seguridad

1. **Tokens Únicos**: Algoritmo de generación segura para evitar colisiones o predicciones
2. **Validación Estricta**: Verificación completa antes de otorgar acceso
3. **Limitación de Intentos**: Prevención de ataques de fuerza bruta
4. **Auditoría**: Registro detallado de todas las operaciones para seguimiento

---

## 💻 Implementación Detallada

### Generación de Tokens

```python
async def generate_token(self, tariff_id: int, admin_id: int) -> Optional[str]:
    """Genera un nuevo token para una tarifa específica."""
    try:
        async for session in get_session():
            # Verificar que la tarifa existe
            tariff_query = select(Tariff).where(Tariff.id == tariff_id)
            tariff_result = await session.execute(tariff_query)
            tariff = tariff_result.scalars().first()
            
            if not tariff:
                self.logger.error(f"Tarifa {tariff_id} no existe.")
                return None
            
            # Generar token único
            token_value = secrets.token_urlsafe(32)
            
            # Calcular fecha de expiración
            expires_at = datetime.now() + timedelta(days=tariff.token_validity_days)
            
            # Crear token
            new_token = SubscriptionToken(
                token=token_value,
                tariff_id=tariff_id,
                generated_by=admin_id,
                expires_at=expires_at,
                is_used=False
            )
            
            session.add(new_token)
            await session.commit()
            
            # Refrescar para obtener el ID
            await session.refresh(new_token)
            
            # Publicar evento
            token_event = TokenGeneratedEvent(
                token_id=new_token.id,
                tariff_id=tariff_id,
                admin_id=admin_id
            )
            await self._event_bus.publish(token_event)
            
            # Generar enlace
            bot_username = "TestingRefactor_bot"  # Debería obtenerse de la configuración
            start_param = f"token_{token_value}"
            token_url = f"https://t.me/{bot_username}?start={start_param}"
            
            return token_url
    
    except Exception as e:
        self.logger.error(f"Error al generar token: {e}")
        return None
```

### Verificación y Canje de Tokens

```python
async def verify_token(self, token: str, user_id: int) -> Optional[Dict[str, Any]]:
    """Verifica la validez de un token y lo marca como utilizado si es válido."""
    try:
        async for session in get_session():
            # Buscar token
            token_query = select(SubscriptionToken).options(
                selectinload(SubscriptionToken.tariff).selectinload(Tariff.channel)
            ).where(
                and_(
                    SubscriptionToken.token == token,
                    SubscriptionToken.is_used == False,
                    SubscriptionToken.expires_at > datetime.now()
                )
            )
            token_result = await session.execute(token_query)
            token_obj = token_result.scalars().first()
            
            if not token_obj:
                return None
            
            # Marcar token como utilizado
            token_obj.is_used = True
            token_obj.used_by = user_id
            token_obj.used_at = datetime.now()
            
            # Obtener datos relevantes
            tariff = token_obj.tariff
            channel = tariff.channel
            
            # Calcular fecha de expiración de la membresía
            membership_expires_at = datetime.now() + timedelta(days=tariff.duration_days)
            
            # Crear o actualizar membresía
            membership_query = select(ChannelMembership).where(
                and_(
                    ChannelMembership.user_id == user_id,
                    ChannelMembership.channel_id == channel.id
                )
            )
            membership_result = await session.execute(membership_query)
            membership = membership_result.scalars().first()
            
            if membership:
                # Actualizar membresía existente
                membership.is_active = True
                membership.role = "vip"
                membership.expires_at = membership_expires_at
            else:
                # Crear nueva membresía
                membership = ChannelMembership(
                    user_id=user_id,
                    channel_id=channel.id,
                    is_active=True,
                    join_date=datetime.now(),
                    expires_at=membership_expires_at,
                    role="vip"
                )
                session.add(membership)
            
            await session.commit()
            
            # Publicar evento
            redemption_event = TokenRedeemedEvent(
                token_id=token_obj.id,
                user_id=user_id,
                channel_id=channel.id,
                expiry_date=membership_expires_at
            )
            await self._event_bus.publish(redemption_event)
            
            # Devolver información para la invitación
            return {
                "channel_id": channel.id,
                "telegram_id": channel.telegram_id,
                "name": channel.name,
                "expiry_date": membership_expires_at,
                "tariff_name": tariff.name,
                "duration_days": tariff.duration_days
            }
    
    except Exception as e:
        self.logger.error(f"Error al verificar token: {e}")
        return None
```

## 🧪 Pruebas Unitarias

Se implementarán pruebas para:

1. Creación y validación de tarifas
2. Generación y verificación de tokens
3. Proceso completo de canje de tokens
4. Manejo de casos especiales (tokens expirados, ya utilizados, etc.)
5. Integración con el sistema de canales

---

**Documento creado el:** 31/07/2025