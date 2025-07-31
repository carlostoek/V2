"""
Listener para eventos relacionados con misiones.

Este módulo se encarga de escuchar eventos del sistema y enviar notificaciones
a los usuarios cuando hay cambios en sus misiones.
"""

import structlog
from typing import Dict, Any

from aiogram import Bot
from src.core.interfaces.IEventBus import IEventBus
from src.modules.events import (
    MissionCompletedEvent,
    PointsAwardedEvent,
    ReactionAddedEvent,
    NarrativeProgressionEvent,
    PieceUnlockedEvent
)
from src.modules.gamification.service import GamificationService
from src.bot.handlers.gamification.progress import (
    send_mission_update_notification,
    send_mission_completed_notification
)

logger = structlog.get_logger()

class MissionEventListener:
    """
    Listener para eventos relacionados con misiones.
    
    Este listener se suscribe a eventos del sistema y envía
    notificaciones a los usuarios cuando hay cambios en sus misiones.
    """
    
    def __init__(self, bot: Bot, event_bus: IEventBus, gamification_service: GamificationService):
        """
        Inicializa el listener.
        
        Args:
            bot: Instancia del bot para enviar mensajes.
            event_bus: Bus de eventos.
            gamification_service: Servicio de gamificación.
        """
        self.bot = bot
        self.event_bus = event_bus
        self.gamification_service = gamification_service
        self.mission_progress_cache: Dict[int, Dict[int, float]] = {}  # {user_id: {mission_id: progress}}
        
        # Registrar manejadores de eventos
        self._register_event_handlers()
        
        logger.info("MissionEventListener inicializado")
    
    def _register_event_handlers(self) -> None:
        """Registra los manejadores de eventos."""
        self.event_bus.subscribe(MissionCompletedEvent, self.handle_mission_completed)
        self.event_bus.subscribe(PointsAwardedEvent, self.handle_points_awarded)
        self.event_bus.subscribe(ReactionAddedEvent, self.handle_reaction_added)
        self.event_bus.subscribe(NarrativeProgressionEvent, self.handle_narrative_progression)
        self.event_bus.subscribe(PieceUnlockedEvent, self.handle_piece_unlocked)
        
        logger.info("MissionEventListener: Eventos registrados")
    
    async def handle_mission_completed(self, event: MissionCompletedEvent) -> None:
        """
        Maneja el evento de misión completada.
        
        Args:
            event: Evento de misión completada.
        """
        logger.info(f"Misión completada por usuario {event.user_id}: {event.mission_id}")
        
        # Enviar notificación al usuario
        await send_mission_completed_notification(
            self.bot,
            event,
            self.gamification_service
        )
    
    async def handle_points_awarded(self, event: PointsAwardedEvent) -> None:
        """
        Maneja el evento de puntos otorgados.
        
        Args:
            event: Evento de puntos otorgados.
        """
        # Verificar si hay misiones que se actualizaron
        user_id = event.user_id
        
        # Obtener misiones actuales
        missions = await self.gamification_service.get_user_missions(user_id)
        
        # Verificar cambios en progreso
        await self._check_mission_progress_changes(user_id, missions)
    
    async def handle_reaction_added(self, event: ReactionAddedEvent) -> None:
        """
        Maneja el evento de reacción añadida.
        
        Args:
            event: Evento de reacción añadida.
        """
        # La reacción puede actualizar progreso en misiones
        user_id = event.user_id
        
        # Obtener misiones actuales
        missions = await self.gamification_service.get_user_missions(user_id)
        
        # Verificar cambios en progreso
        await self._check_mission_progress_changes(user_id, missions)
    
    async def handle_narrative_progression(self, event: NarrativeProgressionEvent) -> None:
        """
        Maneja el evento de progresión narrativa.
        
        Args:
            event: Evento de progresión narrativa.
        """
        # El avance narrativo puede actualizar progreso en misiones
        user_id = event.user_id
        
        # Obtener misiones actuales
        missions = await self.gamification_service.get_user_missions(user_id)
        
        # Verificar cambios en progreso
        await self._check_mission_progress_changes(user_id, missions)
    
    async def handle_piece_unlocked(self, event: PieceUnlockedEvent) -> None:
        """
        Maneja el evento de pieza desbloqueada.
        
        Args:
            event: Evento de pieza desbloqueada.
        """
        # El desbloqueo de piezas puede actualizar progreso en misiones
        user_id = event.user_id
        
        # Obtener misiones actuales
        missions = await self.gamification_service.get_user_missions(user_id)
        
        # Verificar cambios en progreso
        await self._check_mission_progress_changes(user_id, missions)
    
    async def _check_mission_progress_changes(self, user_id: int, missions: Dict[str, Any]) -> None:
        """
        Verifica cambios en el progreso de misiones y envía notificaciones.
        
        Args:
            user_id: ID del usuario.
            missions: Misiones del usuario.
        """
        # Inicializar caché para este usuario si no existe
        if user_id not in self.mission_progress_cache:
            self.mission_progress_cache[user_id] = {}
        
        # Verificar misiones en progreso
        for mission in missions["in_progress"]:
            mission_id = mission["id"]
            current_progress = mission["progress_percentage"]
            
            # Si no tenemos registro previo, guardarlo y continuar
            if mission_id not in self.mission_progress_cache[user_id]:
                self.mission_progress_cache[user_id][mission_id] = current_progress
                continue
            
            # Verificar si ha cambiado significativamente (más de 10%)
            previous_progress = self.mission_progress_cache[user_id][mission_id]
            if current_progress - previous_progress >= 10:
                # Actualizar caché
                self.mission_progress_cache[user_id][mission_id] = current_progress
                
                # Enviar notificación solo si hay cambio significativo
                await send_mission_update_notification(
                    self.bot,
                    user_id,
                    mission_id,
                    current_progress,
                    self.gamification_service
                )
                
                logger.info(f"Notificación de progreso enviada a {user_id} para misión {mission_id}: {current_progress}%")

def setup_mission_listener(bot: Bot, event_bus: IEventBus, gamification_service: GamificationService) -> None:
    """
    Configura el listener de misiones.
    
    Args:
        bot: Instancia del bot.
        event_bus: Bus de eventos.
        gamification_service: Servicio de gamificación.
    """
    # Crear y guardar instancia (no es necesario retornarla, se queda suscrita al bus)
    MissionEventListener(bot, event_bus, gamification_service)
    logger.info("MissionEventListener configurado")