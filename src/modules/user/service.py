from src.core.interfaces.IEventBus import IEventBus
from src.core.interfaces.ICoreService import ICoreService
from src.modules.events import UserStartedBotEvent
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.bot.database.engine import get_session
from src.bot.database.models.user import User

class UserService(ICoreService):
    """Servicio para manejar la lógica de usuarios."""

    def __init__(self, event_bus: IEventBus):
        self._event_bus = event_bus
        self.users = set()

    async def setup(self) -> None:
        self._event_bus.subscribe(UserStartedBotEvent, self.handle_user_started)

    async def handle_user_started(self, event: UserStartedBotEvent) -> None:
        if event.user_id not in self.users:
            print(f"[User Service] Nuevo usuario registrado: {event.user_id} (@{event.username})")
            self.users.add(event.user_id)
            
            # Crear usuario en base de datos si no existe
            await self._ensure_user_exists(event.user_id, event.username)
        else:
            print(f"[User Service] Usuario recurrente: {event.user_id}")
            
    async def _ensure_user_exists(self, user_id: int, username: str = None) -> None:
        """Asegura que el usuario existe en la base de datos."""
        try:
            async for session in get_session():
                # Verificar si el usuario ya existe
                query = select(User).where(User.id == user_id)
                result = await session.execute(query)
                user = result.scalars().first()
                
                if not user:
                    # Crear nuevo usuario con datos mínimos
                    new_user = User(
                        id=user_id,
                        username=username,
                        first_name="Unknown",  # Podría mejorarse obteniendo desde Telegram
                        last_name=None,
                        language_code="es"
                    )
                    session.add(new_user)
                    await session.commit()
                    print(f"[User Service] Usuario {user_id} creado en base de datos")
        except Exception as e:
            print(f"[User Service] Error al crear usuario en base de datos: {e}")

