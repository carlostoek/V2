import secrets
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from src.core.interfaces.IEventBus import IEventBus
from src.core.interfaces.ICoreService import ICoreService
from src.bot.database.models import Tariff, SubscriptionToken

class AdminService(ICoreService):
    """Servicio para manejar la lógica de administración."""

    def __init__(self, event_bus: IEventBus, session: AsyncSession):
        self._event_bus = event_bus
        self._session = session
        self.free_channel_id: int | None = None
        self.wait_time_minutes: int = 15

    async def setup(self) -> None:
        """Suscribe el servicio a los eventos relevantes."""
        pass

    def set_free_channel_id(self, channel_id: int) -> None:
        """Guarda el ID del canal gratuito."""
        print(f"[Admin] Canal gratuito configurado con ID: {channel_id}")
        self.free_channel_id = channel_id

    def get_free_channel_id(self) -> int | None:
        """Recupera el ID del canal gratuito."""
        return self.free_channel_id

    def set_wait_time(self, minutes: int) -> None:
        """Guarda el tiempo de espera para el canal gratuito."""
        print(f"[Admin] Tiempo de espera configurado a: {minutes} minutos")
        self.wait_time_minutes = minutes

    def get_wait_time(self) -> int:
        """Recupera el tiempo de espera para el canal gratuito."""
        return self.wait_time_minutes

    def send_message_to_channel(self, text: str, media: list | None = None) -> bool:
        """Simula el envío de un mensaje al canal gratuito."""
        print(f"[Admin] Enviando mensaje al canal {self.free_channel_id}:")
        print(f"[Admin] Texto: {text}")
        if media:
            print(f"[Admin] Media: {media}")
        return True

    async def create_tariff(self, name: str, price: float, duration_days: int) -> Tariff:
        """Crea una nueva tarifa."""
        new_tariff = Tariff(name=name, price=price, duration_days=duration_days)
        self._session.add(new_tariff)
        await self._session.commit()
        print(f"[Admin] Tarifa creada: {new_tariff}")
        return new_tariff

    async def get_tariff(self, tariff_id: int) -> Tariff | None:
        """Recupera una tarifa por su ID."""
        return await self._session.get(Tariff, tariff_id)

    async def get_all_tariffs(self) -> list[Tariff]:
        """Recupera todas las tarifas."""
        result = await self._session.execute(select(Tariff))
        return result.scalars().all()

    async def delete_tariff(self, tariff_id: int) -> bool:
        """Elimina una tarifa por su ID."""
        tariff = await self.get_tariff(tariff_id)
        if tariff:
            await self._session.delete(tariff)
            await self._session.commit()
            print(f"[Admin] Tarifa eliminada: {tariff_id}")
            return True
        return False

    async def generate_subscription_token(self, tariff_id: int) -> SubscriptionToken | None:
        """Genera un token de suscripción para una tarifa."""
        tariff = await self.get_tariff(tariff_id)
        if not tariff:
            return None
        
        token = secrets.token_urlsafe(16)
        new_token = SubscriptionToken(token=token, tariff_id=tariff_id)
        self._session.add(new_token)
        await self._session.commit()
        print(f"[Admin] Token generado: {new_token}")
        return new_token

    async def validate_token(self, token: str, user_id: int) -> SubscriptionToken | None:
        """Valida un token de suscripción."""
        result = await self._session.execute(select(SubscriptionToken).where(SubscriptionToken.token == token))
        token_data = result.scalars().first()

        if not token_data or token_data.is_used:
            return None
        
        token_data.is_used = True
        token_data.user_id = user_id
        token_data.used_at = datetime.now()

        # Crear suscripción
        tariff = await self.get_tariff(token_data.tariff_id)
        if tariff:
            expires_at = datetime.now() + timedelta(days=tariff.duration_days)
            # Aquí se crearía un registro de suscripción en la base de datos
            print(f"[Admin] Suscripción creada para el usuario {user_id} hasta {expires_at}")

        await self._session.commit()
        return token_data

    async def get_expiring_subscriptions(self, days_to_expire: int) -> list[SubscriptionToken]:
        """Recupera las suscripciones que expiran en un número de días."""
        # Esta lógica se implementará cuando se creen los registros de suscripción
        return []
