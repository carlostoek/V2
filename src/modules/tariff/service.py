"""Servicio independiente para gestión de tarifas VIP."""

import secrets
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from src.core.interfaces.IEventBus import IEventBus
from src.core.interfaces.ICoreService import ICoreService
from src.bot.database.models import Tariff, SubscriptionToken


class TariffService(ICoreService):
    """
    Servicio independiente para gestión completa de tarifas VIP.
    
    NO depende de ningún sistema de menú. Es pura lógica de negocio.
    """

    def __init__(self, event_bus: IEventBus):
        self._event_bus = event_bus
        self._session = None

    async def setup(self) -> None:
        """Inicializa el servicio."""
        from src.bot.database.engine import async_session
        self._session = async_session

    # ==========================================
    # GESTIÓN DE TARIFAS
    # ==========================================

    async def create_tariff(self, name: str, price: float, duration_days: int, channel_id: int, description: str = "") -> Dict:
        """
        Crea una nueva tarifa VIP.
        
        Args:
            name: Nombre de la tarifa
            price: Precio de la tarifa
            duration_days: Duración en días
            channel_id: ID del canal al que pertenece la tarifa
            description: Descripción opcional
        
        Returns:
            dict: {"success": bool, "tariff": Tariff, "message": str}
        """
        try:
            new_tariff = Tariff(
                name=name, 
                price=price, 
                duration_days=duration_days,
                channel_id=channel_id,
                description=description,
                created_at=datetime.now()
            )
            
            async with self._session() as session:
                session.add(new_tariff)
                await session.commit()
                await session.refresh(new_tariff)
                
                return {
                    "success": True,
                    "tariff": new_tariff,
                    "message": f"Tarifa '{name}' creada exitosamente"
                }
        except Exception as e:
            return {
                "success": False,
                "tariff": None,
                "message": f"Error al crear tarifa: {str(e)}"
            }

    async def get_all_tariffs(self) -> List[Tariff]:
        """Obtiene todas las tarifas activas."""
        async with self._session() as session:
            result = await session.execute(select(Tariff).where(Tariff.is_active == True))
            return result.scalars().all()

    async def get_tariff_by_id(self, tariff_id: int) -> Optional[Tariff]:
        """Obtiene una tarifa por ID."""
        async with self._session() as session:
            return await session.get(Tariff, tariff_id)

    async def update_tariff(self, tariff_id: int, **kwargs) -> Dict:
        """
        Actualiza una tarifa existente.
        
        Args:
            tariff_id: ID de la tarifa
            **kwargs: Campos a actualizar (name, price, duration_days, description)
        """
        try:
            async with self._session() as session:
                tariff = await session.get(Tariff, tariff_id)
                if not tariff:
                    return {"success": False, "message": "Tarifa no encontrada"}
                
                for key, value in kwargs.items():
                    if hasattr(tariff, key):
                        setattr(tariff, key, value)
                
                tariff.updated_at = datetime.now()
                await session.commit()
                
                return {
                    "success": True,
                    "tariff": tariff,
                    "message": "Tarifa actualizada exitosamente"
                }
        except Exception as e:
            return {"success": False, "message": f"Error al actualizar: {str(e)}"}

    async def delete_tariff(self, tariff_id: int) -> Dict:
        """Elimina (desactiva) una tarifa."""
        try:
            async with self._session() as session:
                tariff = await session.get(Tariff, tariff_id)
                if not tariff:
                    return {"success": False, "message": "Tarifa no encontrada"}
                
                tariff.is_active = False
                tariff.updated_at = datetime.now()
                await session.commit()
                
                return {
                    "success": True,
                    "message": f"Tarifa '{tariff.name}' desactivada exitosamente"
                }
        except Exception as e:
            return {"success": False, "message": f"Error al eliminar: {str(e)}"}

    # ==========================================
    # GESTIÓN DE TOKENS
    # ==========================================

    async def generate_token(self, tariff_id: int, quantity: int = 1) -> Dict:
        """
        Genera token(s) para una tarifa específica.
        
        Args:
            tariff_id: ID de la tarifa
            quantity: Cantidad de tokens a generar
            
        Returns:
            dict: {"success": bool, "tokens": List[str], "message": str}
        """
        try:
            tariff = await self.get_tariff_by_id(tariff_id)
            if not tariff:
                return {"success": False, "tokens": [], "message": "Tarifa no encontrada"}
            
            tokens = []
            async with self._session() as session:
                for _ in range(quantity):
                    token_value = secrets.token_urlsafe(16)
                    new_token = SubscriptionToken(
                        token=token_value,
                        tariff_id=tariff_id,
                        created_at=datetime.now()
                    )
                    session.add(new_token)
                    tokens.append(token_value)
                
                await session.commit()
                
                return {
                    "success": True,
                    "tokens": tokens,
                    "message": f"{quantity} token(s) generado(s) para tarifa '{tariff.name}'"
                }
        except Exception as e:
            return {"success": False, "tokens": [], "message": f"Error al generar tokens: {str(e)}"}

    async def validate_and_use_token(self, token: str, user_id: int) -> Dict:
        """
        Valida y usa un token de suscripción.
        
        Returns:
            dict: {"success": bool, "subscription_end": datetime, "tariff": Tariff, "message": str}
        """
        try:
            async with self._session() as session:
                result = await session.execute(
                    select(SubscriptionToken).where(SubscriptionToken.token == token)
                )
                token_data = result.scalars().first()

                if not token_data:
                    return {"success": False, "message": "Token no válido"}
                
                if token_data.is_used:
                    return {"success": False, "message": "Token ya utilizado"}
                
                # Marcar token como usado
                token_data.is_used = True
                token_data.user_id = user_id
                token_data.used_at = datetime.now()

                # Obtener tarifa
                tariff = await session.get(Tariff, token_data.tariff_id)
                if not tariff:
                    return {"success": False, "message": "Tarifa asociada no encontrada"}

                # Calcular fecha de expiración
                subscription_end = datetime.now() + timedelta(days=tariff.duration_days)
                
                await session.commit()

                return {
                    "success": True,
                    "subscription_end": subscription_end,
                    "tariff": tariff,
                    "message": f"Suscripción VIP activada hasta {subscription_end.strftime('%Y-%m-%d')}"
                }
        except Exception as e:
            return {"success": False, "message": f"Error al validar token: {str(e)}"}

    # ==========================================
    # ESTADÍSTICAS Y REPORTES
    # ==========================================

    async def get_tariff_stats(self) -> Dict:
        """Obtiene estadísticas de uso de tarifas."""
        try:
            async with self._session() as session:
                # Total tarifas activas
                tariffs_result = await session.execute(
                    select(Tariff).where(Tariff.is_active == True)
                )
                active_tariffs = len(tariffs_result.scalars().all())
                
                # Total tokens generados
                tokens_result = await session.execute(select(SubscriptionToken))
                total_tokens = len(tokens_result.scalars().all())
                
                # Tokens usados
                used_tokens_result = await session.execute(
                    select(SubscriptionToken).where(SubscriptionToken.is_used == True)
                )
                used_tokens = len(used_tokens_result.scalars().all())
                
                return {
                    "active_tariffs": active_tariffs,
                    "total_tokens": total_tokens,
                    "used_tokens": used_tokens,
                    "unused_tokens": total_tokens - used_tokens,
                    "usage_rate": (used_tokens / total_tokens * 100) if total_tokens > 0 else 0
                }
        except Exception as e:
            return {"error": f"Error al obtener estadísticas: {str(e)}"}

    async def get_tokens_by_tariff(self, tariff_id: int) -> List[SubscriptionToken]:
        """Obtiene todos los tokens de una tarifa específica."""
        async with self._session() as session:
            result = await session.execute(
                select(SubscriptionToken).where(SubscriptionToken.tariff_id == tariff_id)
            )
            return result.scalars().all()