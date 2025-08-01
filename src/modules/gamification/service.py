import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union

from sqlalchemy import select, update, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.orm import selectinload

from src.core.interfaces.IEventBus import IEvent, IEventBus
from src.core.interfaces.ICoreService import ICoreService
from src.utils.sexy_logger import log, log_execution_time
from src.modules.events import (
    ReactionAddedEvent, 
    PointsAwardedEvent, 
    UserStartedBotEvent,
    MissionCompletedEvent,
    NarrativeProgressionEvent,
    PieceUnlockedEvent,
    LevelUpEvent,
    DianaValidationCompletedEvent,
    DianaValidationFailedEvent,
    NarrativeValidationProgressEvent
)
from src.bot.database.engine import get_session
from src.bot.database.models.user import User
from src.bot.database.models.gamification import (
    UserPoints,
    Mission,
    UserMission,
    Achievement,
    UserAchievement,
    MissionTypeEnum,
    MissionStatusEnum
)

class GamificationService(ICoreService):
    """
    Servicio para manejar la lógica de gamificación.
    
    Responsabilidades:
    - Gestionar el sistema de puntos (besitos)
    - Administrar misiones y su progreso
    - Otorgar logros y recompensas
    - Gestionar niveles de usuarios
    """

    def __init__(self, event_bus: IEventBus):
        self._event_bus = event_bus
        self.points = {}  # Cache en memoria para puntos
        self.missions = {}  # Cache en memoria para misiones
        self.logger = logging.getLogger(__name__)

    async def setup(self) -> None:
        """Suscribe el servicio a los eventos relevantes y carga datos iniciales."""
        # Suscribirse a eventos
        self._event_bus.subscribe(ReactionAddedEvent, self.handle_reaction_added)
        self._event_bus.subscribe(UserStartedBotEvent, self.handle_user_started)
        self._event_bus.subscribe(NarrativeProgressionEvent, self.handle_narrative_progression)
        self._event_bus.subscribe(PieceUnlockedEvent, self.handle_piece_unlocked)
        
        # Nuevos eventos de validación Diana
        self._event_bus.subscribe(DianaValidationCompletedEvent, self.handle_diana_validation_completed)
        self._event_bus.subscribe(DianaValidationFailedEvent, self.handle_diana_validation_failed)
        self._event_bus.subscribe(NarrativeValidationProgressEvent, self.handle_narrative_validation_progress)
        
        # Cargar datos iniciales
        await self._load_initial_data()
    
    async def _load_initial_data(self) -> None:
        """Carga datos iniciales del sistema de gamificación."""
        try:
            # Cargar misiones activas en cache
            async for session in get_session():
                query = select(Mission).where(Mission.is_active == True)
                result = await session.execute(query)
                missions = result.scalars().all()
                
                for mission in missions:
                    self.missions[mission.key] = {
                        "id": mission.id,
                        "title": mission.title,
                        "type": mission.mission_type,
                        "level_required": mission.level_required,
                        "is_vip_only": mission.is_vip_only
                    }
                
                self.logger.info(f"Cargadas {len(self.missions)} misiones activas en cache")
        except Exception as e:
            self.logger.error(f"Error al cargar datos iniciales: {e}")

    async def _award_points(self, user_id: int, points_to_award: int, source_event: IEvent) -> None:
        """
        Otorga puntos a un usuario y publica un evento.
        
        Args:
            user_id: ID del usuario.
            points_to_award: Cantidad de puntos a otorgar.
            source_event: Evento que originó los puntos.
        """
        log.gamification(
            f"Evento {source_event.__class__.__name__} procesado",
            user_id=user_id,
            points=points_to_award
        )
        
        # Actualizar puntos en memoria
        self.points[user_id] = self.points.get(user_id, 0) + points_to_award
        
        # Actualizar puntos en base de datos
        try:
            async for session in get_session():
                # Verificar que el usuario existe antes de proceder
                user_query = select(User).where(User.id == user_id)
                user_result = await session.execute(user_query)
                user = user_result.scalars().first()
                
                if not user:
                    log.error(f"Usuario {user_id} no existe en la base de datos - no se pueden otorgar puntos")
                    return
                
                if not user:
                    log.error(f"Usuario {user_id} no existe en la base de datos - no se pueden otorgar puntos")
                    return
                
                # Verificar si existe registro de puntos
                query = select(UserPoints).where(UserPoints.user_id == user_id)
                result = await session.execute(query)
                user_points = result.scalars().first()
                
                source_type = source_event.__class__.__name__.lower().replace('event', '')
                
                if user_points:
                    # Actualizar registro existente
                    user_points.current_points += points_to_award
                    user_points.total_earned += points_to_award
                    
                    # Actualizar categoría específica
                    if hasattr(user_points, f"points_from_{source_type}"):
                        setattr(user_points, f"points_from_{source_type}", 
                                getattr(user_points, f"points_from_{source_type}") + points_to_award)
                    
                    # Agregar al historial
                    history_entry = {
                        "timestamp": datetime.now().isoformat(),
                        "amount": points_to_award,
                        "source": source_event.__class__.__name__,
                        "balance": user_points.current_points
                    }
                    user_points.points_history.append(history_entry)
                    user_points.last_points_update = func.now()
                    
                else:
                    # Crear nuevo registro
                    user_points = UserPoints(
                        user_id=user_id,
                        current_points=points_to_award,
                        total_earned=points_to_award,
                        points_history=[{
                            "timestamp": datetime.now().isoformat(),
                            "amount": points_to_award,
                            "source": source_event.__class__.__name__,
                            "balance": points_to_award
                        }]
                    )
                    
                    # Establecer categoría específica
                    if hasattr(user_points, f"points_from_{source_type}"):
                        setattr(user_points, f"points_from_{source_type}", points_to_award)
                    
                    session.add(user_points)
                
                # Guardar cambios
                await session.commit()
                
                # Verificar si el usuario sube de nivel
                await self._check_level_up(session, user_id)
        
        except Exception as e:
            self.logger.error(f"Error al otorgar puntos: {e}")
        
        # Publicar evento de puntos otorgados
        points_event = PointsAwardedEvent(
            user_id=user_id, 
            points=points_to_award, 
            source_event=source_event.__class__.__name__
        )
        await self._event_bus.publish(points_event)
        
        # Verificar progreso en misiones
        await self._update_missions_progress(user_id, "points_earned", points_to_award, source_event.__class__.__name__)

    async def _check_level_up(self, session: AsyncSession, user_id: int) -> None:
        """
        Verifica si el usuario sube de nivel basado en sus puntos.
        
        Args:
            session: Sesión de base de datos.
            user_id: ID del usuario.
        """
        try:
            # Obtener usuario
            query = select(User).where(User.id == user_id)
            result = await session.execute(query)
            user = result.scalars().first()
            
            if not user:
                return
            
            # Obtener puntos actuales
            points_query = select(UserPoints).where(UserPoints.user_id == user_id)
            points_result = await session.execute(points_query)
            user_points = points_result.scalars().first()
            
            if not user_points:
                return
            
            # Calcular nivel basado en puntos
            current_level = user.level
            new_level = self._calculate_level(user_points.total_earned)
            
            # Si el usuario sube de nivel
            if new_level > current_level:
                # Actualizar nivel
                user.level = new_level
                await session.commit()
                
                # Publicar evento de subida de nivel
                level_up_event = LevelUpEvent(
                    user_id=user_id,
                    new_level=new_level,
                    rewards=self._get_level_rewards(new_level)
                )
                await self._event_bus.publish(level_up_event)
                
                self.logger.info(f"Usuario {user_id} subió al nivel {new_level}")
                
                # Verificar logros desbloqueados por nivel
                await self._check_level_achievements(session, user_id, new_level)
        
        except Exception as e:
            self.logger.error(f"Error al verificar subida de nivel: {e}")

    def _calculate_level(self, total_points: float) -> int:
        """
        Calcula el nivel basado en puntos totales.
        
        Args:
            total_points: Puntos totales ganados.
            
        Returns:
            Nivel calculado.
        """
        # Fórmula: nivel = 1 + raíz cuadrada(puntos / 100)
        # Nivel 1: 0-99 puntos
        # Nivel 2: 100-399 puntos
        # Nivel 3: 400-899 puntos
        # etc.
        import math
        level = 1 + int(math.sqrt(total_points / 100))
        return level

    def _get_level_rewards(self, level: int) -> Dict[str, Any]:
        """
        Obtiene las recompensas por subir de nivel.
        
        Args:
            level: Nivel alcanzado.
            
        Returns:
            Diccionario con recompensas.
        """
        rewards = {
            "besitos": level * 20,  # Más besitos por niveles más altos
            "items": []
        }
        
        # Recompensas especiales por nivel
        if level == 2:
            rewards["items"].append("badge_level_2")
        elif level == 3:
            rewards["items"].append("badge_level_3")
        elif level == 5:
            rewards["items"].append("badge_level_5")
        
        return rewards

    async def _check_level_achievements(self, session: AsyncSession, user_id: int, level: int) -> None:
        """
        Verifica logros desbloqueados por nivel.
        
        Args:
            session: Sesión de base de datos.
            user_id: ID del usuario.
            level: Nivel actual.
        """
        try:
            # Buscar logros relacionados con nivel
            query = select(Achievement).where(
                and_(
                    Achievement.criteria.contains({"type": "level"}),
                    Achievement.criteria.contains({"value": level})
                )
            )
            result = await session.execute(query)
            achievements = result.scalars().all()
            
            for achievement in achievements:
                # Verificar si ya tiene el logro
                user_achievement_query = select(UserAchievement).where(
                    and_(
                        UserAchievement.user_id == user_id,
                        UserAchievement.achievement_id == achievement.id
                    )
                )
                user_achievement_result = await session.execute(user_achievement_query)
                user_achievement = user_achievement_result.scalars().first()
                
                if not user_achievement:
                    # Crear nuevo logro
                    user_achievement = UserAchievement(
                        user_id=user_id,
                        achievement_id=achievement.id,
                        is_completed=True,
                        progress=100.0,
                        completed_at=datetime.now(),
                        completion_data={"level": level}
                    )
                    session.add(user_achievement)
                    
                    # Otorgar recompensa
                    if achievement.points_reward > 0:
                        # Agregar puntos
                        points_query = select(UserPoints).where(UserPoints.user_id == user_id)
                        points_result = await session.execute(points_query)
                        user_points = points_result.scalars().first()
                        
                        if user_points:
                            user_points.current_points += achievement.points_reward
                            user_points.total_earned += achievement.points_reward
                            
                            # Agregar al historial
                            history_entry = {
                                "timestamp": datetime.now().isoformat(),
                                "amount": achievement.points_reward,
                                "source": f"Achievement_{achievement.key}",
                                "balance": user_points.current_points
                            }
                            user_points.points_history.append(history_entry)
                    
                    await session.commit()
                    self.logger.info(f"Usuario {user_id} desbloqueó logro {achievement.key}")
                
                elif not user_achievement.is_completed:
                    # Actualizar logro existente
                    user_achievement.is_completed = True
                    user_achievement.progress = 100.0
                    user_achievement.completed_at = datetime.now()
                    user_achievement.completion_data = {"level": level}
                    
                    await session.commit()
                    self.logger.info(f"Usuario {user_id} completó logro {achievement.key}")
        
        except Exception as e:
            self.logger.error(f"Error al verificar logros de nivel: {e}")

    async def handle_reaction_added(self, event: ReactionAddedEvent) -> None:
        """
        Maneja el evento de reacción para otorgar puntos.
        
        Args:
            event: Evento de reacción.
        """
        await self._award_points(event.user_id, event.points_to_award, event)
        
        # Actualizar progreso en misiones relacionadas con reacciones
        await self._update_missions_progress(event.user_id, "reactions", 1, "ReactionAddedEvent")

    async def handle_user_started(self, event: UserStartedBotEvent) -> None:
        """
        Maneja el evento de inicio de bot para otorgar puntos de bienvenida.
        
        Args:
            event: Evento de inicio.
        """
        # Solo otorga puntos la primera vez
        if self.points.get(event.user_id, 0) == 0:
            await self._award_points(event.user_id, 10, event)
            
            # Asignar misiones iniciales
            await self._assign_initial_missions(event.user_id)

    async def handle_narrative_progression(self, event: NarrativeProgressionEvent) -> None:
        """
        Maneja el evento de progresión narrativa.
        
        Args:
            event: Evento de progresión narrativa.
        """
        # Actualizar progreso en misiones relacionadas con narrativa
        await self._update_missions_progress(event.user_id, "narrative_progress", 1, event.fragment_id)

    async def handle_piece_unlocked(self, event: PieceUnlockedEvent) -> None:
        """
        Maneja el evento de desbloqueo de pista narrativa.
        
        Args:
            event: Evento de desbloqueo de pista.
        """
        # Actualizar progreso en misiones relacionadas con pistas
        await self._update_missions_progress(event.user_id, "pieces_unlocked", 1, event.piece_id)

    async def _assign_initial_missions(self, user_id: int) -> None:
        """
        Asigna misiones iniciales a un usuario nuevo.
        
        Args:
            user_id: ID del usuario.
        """
        try:
            async for session in get_session():
                # Verificar nivel del usuario
                user_query = select(User).where(User.id == user_id)
                user_result = await session.execute(user_query)
                user = user_result.scalars().first()
                
                if not user:
                    self.logger.error(f"Usuario {user_id} no existe en la base de datos. No se pueden asignar misiones iniciales.")
                    return
                
                # Buscar misiones disponibles para nivel 1
                query = select(Mission).where(
                    and_(
                        Mission.level_required <= user.level,
                        Mission.is_active == True,
                        Mission.mission_type.in_([MissionTypeEnum.DAILY, MissionTypeEnum.ONE_TIME])
                    )
                )
                result = await session.execute(query)
                available_missions = result.scalars().all()
                
                # Asignar misiones al usuario
                for mission in available_missions:
                    # Verificar si ya tiene la misión asignada
                    exists_query = select(UserMission).where(
                        and_(
                            UserMission.user_id == user_id,
                            UserMission.mission_id == mission.id
                        )
                    )
                    exists_result = await session.execute(exists_query)
                    exists = exists_result.scalars().first()
                    
                    if not exists:
                        # Calcular fecha de expiración
                        expires_at = None
                        if mission.time_limit_hours:
                            expires_at = datetime.now() + timedelta(hours=mission.time_limit_hours)
                        
                        # Crear misión para el usuario
                        user_mission = UserMission(
                            user_id=user_id,
                            mission_id=mission.id,
                            status=MissionStatusEnum.AVAILABLE,
                            progress={},
                            progress_percentage=0.0,
                            expires_at=expires_at
                        )
                        session.add(user_mission)
                
                await session.commit()
                self.logger.info(f"Asignadas {len(available_missions)} misiones iniciales al usuario {user_id}")
        
        except Exception as e:
            self.logger.error(f"Error al asignar misiones iniciales: {e}")

    async def _update_missions_progress(self, user_id: int, action_type: str, action_value: Union[int, float], action_context: str) -> None:
        """
        Actualiza el progreso en misiones basado en las acciones del usuario.
        
        Args:
            user_id: ID del usuario.
            action_type: Tipo de acción realizada.
            action_value: Valor de la acción.
            action_context: Contexto adicional de la acción.
        """
        try:
            async for session in get_session():
                # Verificar que el usuario existe
                user_query = select(User).where(User.id == user_id)
                user_result = await session.execute(user_query)
                user = user_result.scalars().first()
                
                if not user:
                    self.logger.error(f"Usuario {user_id} no existe en la base de datos. No se pueden actualizar misiones.")
                    return
                # Verificar que el usuario existe
                user_query = select(User).where(User.id == user_id)
                user_result = await session.execute(user_query)
                user = user_result.scalars().first()
                
                if not user:
                    self.logger.error(f"Usuario {user_id} no existe en la base de datos. No se puede actualizar progreso de misiones.")
                    return
                
                # Obtener misiones activas del usuario
                query = select(UserMission).options(
                    selectinload(UserMission.mission)
                ).where(
                    and_(
                        UserMission.user_id == user_id,
                        UserMission.status.in_([MissionStatusEnum.AVAILABLE, MissionStatusEnum.IN_PROGRESS])
                    )
                )
                result = await session.execute(query)
                user_missions = result.scalars().all()
                
                for user_mission in user_missions:
                    mission = user_mission.mission
                    objectives = mission.objectives
                    
                    # Verificar si la misión tiene objetivos del tipo de acción
                    for objective in objectives:
                        if objective["type"] == action_type:
                            # Verificar restricciones de contexto si existen
                            if "context" in objective and action_context not in objective["context"]:
                                continue
                            
                            # Iniciar progreso si es necesario
                            if user_mission.status == MissionStatusEnum.AVAILABLE:
                                user_mission.status = MissionStatusEnum.IN_PROGRESS
                                user_mission.started_at = datetime.now()
                            
                            # Inicializar progreso para este objetivo
                            if objective["id"] not in user_mission.progress:
                                user_mission.progress[objective["id"]] = 0
                            
                            # Actualizar progreso
                            user_mission.progress[objective["id"]] += action_value
                            
                            # Calcular porcentaje de progreso total
                            total_objectives = len(objectives)
                            completed_objectives = 0
                            
                            for obj in objectives:
                                obj_id = obj["id"]
                                required = obj["required"]
                                current = user_mission.progress.get(obj_id, 0)
                                
                                if current >= required:
                                    completed_objectives += 1
                            
                            user_mission.progress_percentage = (completed_objectives / total_objectives) * 100
                            
                            # Verificar si la misión está completa
                            if user_mission.progress_percentage >= 100:
                                await self._complete_mission(session, user_id, user_mission)
                
                await session.commit()
        
        except Exception as e:
            self.logger.error(f"Error al actualizar progreso de misiones: {e}")

    async def _complete_mission(self, session: AsyncSession, user_id: int, user_mission: UserMission) -> None:
        """
        Completa una misión y otorga recompensas.
        
        Args:
            session: Sesión de base de datos.
            user_id: ID del usuario.
            user_mission: Misión completada.
        """
        try:
            # Actualizar estado
            user_mission.status = MissionStatusEnum.COMPLETED
            user_mission.completed_at = datetime.now()
            user_mission.progress_percentage = 100.0
            
            # Otorgar recompensa
            mission = user_mission.mission
            
            if mission.points_reward > 0:
                # Agregar puntos
                points_query = select(UserPoints).where(UserPoints.user_id == user_id)
                points_result = await session.execute(points_query)
                user_points = points_result.scalars().first()
                
                if user_points:
                    user_points.current_points += mission.points_reward
                    user_points.total_earned += mission.points_reward
                    user_points.points_from_missions += mission.points_reward
                    
                    # Agregar al historial
                    history_entry = {
                        "timestamp": datetime.now().isoformat(),
                        "amount": mission.points_reward,
                        "source": f"Mission_{mission.key}",
                        "balance": user_points.current_points
                    }
                    user_points.points_history.append(history_entry)
            
            # Marcar recompensa como reclamada
            user_mission.reward_claimed = True
            user_mission.reward_claimed_at = datetime.now()
            
            await session.commit()
            
            # Emitir evento de misión completada
            mission_event = MissionCompletedEvent(
                user_id=user_id,
                mission_id=mission.key,
                completion_time=user_mission.completed_at.isoformat(),
                reward_points=mission.points_reward
            )
            await self._event_bus.publish(mission_event)
            
            self.logger.info(f"Usuario {user_id} completó misión {mission.key}")
            
            # Verificar logros relacionados con misiones
            await self._check_mission_achievements(session, user_id, mission.key)
            
            # Asignar nuevas misiones si es diaria
            if mission.mission_type == MissionTypeEnum.DAILY:
                await self._refresh_daily_missions(session, user_id)
        
        except Exception as e:
            self.logger.error(f"Error al completar misión: {e}")

    async def _check_mission_achievements(self, session: AsyncSession, user_id: int, mission_key: str) -> None:
        """
        Verifica logros desbloqueados por completar misiones.
        
        Args:
            session: Sesión de base de datos.
            user_id: ID del usuario.
            mission_key: Clave de la misión completada.
        """
        try:
            # Contar misiones completadas
            count_query = select(func.count(UserMission.id)).where(
                and_(
                    UserMission.user_id == user_id,
                    UserMission.status == MissionStatusEnum.COMPLETED
                )
            )
            count_result = await session.execute(count_query)
            completed_count = count_result.scalar()
            
            # Buscar logros por cantidad de misiones completadas
            query = select(Achievement).where(
                and_(
                    Achievement.criteria.contains({"type": "missions_completed"}),
                    Achievement.criteria.contains({"value": completed_count})
                )
            )
            result = await session.execute(query)
            achievements = result.scalars().all()
            
            for achievement in achievements:
                # Verificar si ya tiene el logro
                user_achievement_query = select(UserAchievement).where(
                    and_(
                        UserAchievement.user_id == user_id,
                        UserAchievement.achievement_id == achievement.id
                    )
                )
                user_achievement_result = await session.execute(user_achievement_query)
                user_achievement = user_achievement_result.scalars().first()
                
                if not user_achievement or not user_achievement.is_completed:
                    # Crear o actualizar logro
                    if not user_achievement:
                        user_achievement = UserAchievement(
                            user_id=user_id,
                            achievement_id=achievement.id,
                            is_completed=True,
                            progress=100.0,
                            completed_at=datetime.now(),
                            completion_data={"missions_completed": completed_count}
                        )
                        session.add(user_achievement)
                    else:
                        user_achievement.is_completed = True
                        user_achievement.progress = 100.0
                        user_achievement.completed_at = datetime.now()
                        user_achievement.completion_data = {"missions_completed": completed_count}
                    
                    # Otorgar recompensa
                    if achievement.points_reward > 0:
                        # Agregar puntos
                        points_query = select(UserPoints).where(UserPoints.user_id == user_id)
                        points_result = await session.execute(points_query)
                        user_points = points_result.scalars().first()
                        
                        if user_points:
                            user_points.current_points += achievement.points_reward
                            user_points.total_earned += achievement.points_reward
                            
                            # Agregar al historial
                            history_entry = {
                                "timestamp": datetime.now().isoformat(),
                                "amount": achievement.points_reward,
                                "source": f"Achievement_{achievement.key}",
                                "balance": user_points.current_points
                            }
                            user_points.points_history.append(history_entry)
            
            await session.commit()
        
        except Exception as e:
            self.logger.error(f"Error al verificar logros de misiones: {e}")

    async def _refresh_daily_missions(self, session: AsyncSession, user_id: int) -> None:
        """
        Refresca las misiones diarias disponibles.
        
        Args:
            session: Sesión de base de datos.
            user_id: ID del usuario.
        """
        try:
            # Verificar nivel del usuario
            user_query = select(User).where(User.id == user_id)
            user_result = await session.execute(user_query)
            user = user_result.scalars().first()
            
            if not user:
                self.logger.error(f"Usuario {user_id} no existe en la base de datos. No se pueden refrescar misiones diarias.")
                return
            
            # Obtener misiones diarias disponibles
            query = select(Mission).where(
                and_(
                    Mission.level_required <= user.level,
                    Mission.is_active == True,
                    Mission.mission_type == MissionTypeEnum.DAILY
                )
            )
            result = await session.execute(query)
            available_missions = result.scalars().all()
            
            # Obtener misiones diarias actuales del usuario
            current_query = select(UserMission).options(
                selectinload(UserMission.mission)
            ).where(
                and_(
                    UserMission.user_id == user_id,
                    UserMission.mission.has(Mission.mission_type == MissionTypeEnum.DAILY)
                )
            )
            current_result = await session.execute(current_query)
            current_missions = current_result.scalars().all()
            
            # Expirar misiones diarias completadas
            for user_mission in current_missions:
                if user_mission.status == MissionStatusEnum.COMPLETED:
                    user_mission.expires_at = datetime.now()
            
            # Asignar nuevas misiones diarias
            assigned_count = len([m for m in current_missions if m.status != MissionStatusEnum.COMPLETED])
            max_daily_missions = 3  # Máximo de misiones diarias simultáneas
            
            if assigned_count < max_daily_missions:
                # Filtrar misiones que el usuario no tiene o que ya completó
                current_mission_ids = [m.mission_id for m in current_missions]
                new_missions = [m for m in available_missions if m.id not in current_mission_ids]
                
                # Seleccionar aleatoriamente hasta completar el máximo
                new_missions_to_assign = random.sample(new_missions, min(max_daily_missions - assigned_count, len(new_missions)))
                
                for mission in new_missions_to_assign:
                    # Calcular fecha de expiración
                    expires_at = None
                    if mission.time_limit_hours:
                        expires_at = datetime.now() + timedelta(hours=mission.time_limit_hours)
                    
                    # Crear misión para el usuario
                    user_mission = UserMission(
                        user_id=user_id,
                        mission_id=mission.id,
                        status=MissionStatusEnum.AVAILABLE,
                        progress={},
                        progress_percentage=0.0,
                        expires_at=expires_at
                    )
                    session.add(user_mission)
            
            await session.commit()
            self.logger.info(f"Misiones diarias actualizadas para usuario {user_id}")
        
        except Exception as e:
            self.logger.error(f"Error al refrescar misiones diarias: {e}")

    async def get_user_missions(self, user_id: int) -> Dict[str, List[Dict[str, Any]]]:
        """
        Obtiene las misiones disponibles para un usuario.
        
        Args:
            user_id: ID del usuario.
            
        Returns:
            Diccionario con misiones agrupadas por estado.
        """
        result = {
            "available": [],
            "in_progress": [],
            "completed": []
        }
        
        try:
            async for session in get_session():
                # Verificar que el usuario existe
                user_query = select(User).where(User.id == user_id)
                user_result = await session.execute(user_query)
                user = user_result.scalars().first()
                
                if not user:
                    self.logger.error(f"Usuario {user_id} no existe en la base de datos. No se pueden obtener misiones.")
                    return result
                
                # Obtener misiones del usuario
                query = select(UserMission).options(
                    selectinload(UserMission.mission)
                ).where(UserMission.user_id == user_id)
                query_result = await session.execute(query)
                user_missions = query_result.scalars().all()
                
                # Organizar por estado
                for user_mission in user_missions:
                    mission = user_mission.mission
                    
                    # Verificar si ha expirado
                    if user_mission.expires_at and user_mission.expires_at < datetime.now():
                        if user_mission.status != MissionStatusEnum.COMPLETED:
                            user_mission.status = MissionStatusEnum.EXPIRED
                            await session.commit()
                        continue
                    
                    mission_data = {
                        "id": mission.id,
                        "key": mission.key,
                        "title": mission.title,
                        "description": mission.description,
                        "type": mission.mission_type,
                        "category": mission.category,
                        "objectives": mission.objectives,
                        "progress": user_mission.progress,
                        "progress_percentage": user_mission.progress_percentage,
                        "rewards": {
                            "points": mission.points_reward,
                            "items": mission.item_rewards
                        },
                        "started_at": user_mission.started_at.isoformat() if user_mission.started_at else None,
                        "completed_at": user_mission.completed_at.isoformat() if user_mission.completed_at else None,
                        "expires_at": user_mission.expires_at.isoformat() if user_mission.expires_at else None
                    }
                    
                    if user_mission.status == MissionStatusEnum.AVAILABLE:
                        result["available"].append(mission_data)
                    elif user_mission.status == MissionStatusEnum.IN_PROGRESS:
                        result["in_progress"].append(mission_data)
                    elif user_mission.status == MissionStatusEnum.COMPLETED:
                        result["completed"].append(mission_data)
        
        except Exception as e:
            self.logger.error(f"Error al obtener misiones del usuario: {e}")
        
        return result

    async def get_user_achievements(self, user_id: int) -> Dict[str, List[Dict[str, Any]]]:
        """
        Obtiene los logros de un usuario.
        
        Args:
            user_id: ID del usuario.
            
        Returns:
            Diccionario con logros agrupados por estado.
        """
        result = {
            "completed": [],
            "in_progress": []
        }
        
        try:
            async for session in get_session():
                # Verificar que el usuario existe
                user_query = select(User).where(User.id == user_id)
                user_result = await session.execute(user_query)
                user = user_result.scalars().first()
                
                if not user:
                    self.logger.error(f"Usuario {user_id} no existe en la base de datos. No se pueden obtener logros.")
                    return result
                
                # Obtener logros del usuario
                query = select(UserAchievement).options(
                    selectinload(UserAchievement.achievement)
                ).where(UserAchievement.user_id == user_id)
                query_result = await session.execute(query)
                user_achievements = query_result.scalars().all()
                
                # Organizar por estado
                for user_achievement in user_achievements:
                    achievement = user_achievement.achievement
                    
                    achievement_data = {
                        "id": achievement.id,
                        "key": achievement.key,
                        "name": achievement.name,
                        "description": achievement.description,
                        "category": achievement.category,
                        "difficulty": achievement.difficulty,
                        "progress": user_achievement.progress,
                        "rewards": {
                            "points": achievement.points_reward,
                            "items": achievement.item_rewards
                        },
                        "completed_at": user_achievement.completed_at.isoformat() if user_achievement.completed_at else None
                    }
                    
                    if user_achievement.is_completed:
                        result["completed"].append(achievement_data)
                    else:
                        result["in_progress"].append(achievement_data)
                
                # Agregar logros disponibles pero no iniciados
                all_query = select(Achievement).where(
                    ~Achievement.id.in_([ua.achievement_id for ua in user_achievements])
                )
                all_result = await session.execute(all_query)
                available_achievements = all_result.scalars().all()
                
                for achievement in available_achievements:
                    # No mostrar logros ocultos
                    if achievement.is_hidden:
                        continue
                    
                    achievement_data = {
                        "id": achievement.id,
                        "key": achievement.key,
                        "name": achievement.name,
                        "description": achievement.description,
                        "category": achievement.category,
                        "difficulty": achievement.difficulty,
                        "progress": 0.0,
                        "rewards": {
                            "points": achievement.points_reward,
                            "items": achievement.item_rewards
                        },
                        "completed_at": None
                    }
                    
                    result["in_progress"].append(achievement_data)
        
        except Exception as e:
            self.logger.error(f"Error al obtener logros del usuario: {e}")
        
        return result

    async def get_user_points(self, user_id: int) -> Dict[str, Any]:
        """
        Obtiene los puntos y estadísticas de un usuario.
        
        Args:
            user_id: ID del usuario.
            
        Returns:
            Diccionario con información de puntos.
        """
        result = {
            "current_points": 0,
            "total_earned": 0,
            "total_spent": 0,
            "stats": {},
            "level": 1,
            "next_level_points": 100,
            "progress_to_next_level": 0
        }
        
        # Primero intentar con caché en memoria
        if user_id in self.points:
            result["current_points"] = self.points[user_id]
        
        try:
            async for session in get_session():
                # Obtener usuario
                user_query = select(User).where(User.id == user_id)
                user_result = await session.execute(user_query)
                user = user_result.scalars().first()
                
                if not user:
                    self.logger.error(f"Usuario {user_id} no existe en la base de datos. No se pueden obtener puntos.")
                    return result
                
                result["level"] = user.level
                
                # Obtener puntos
                query = select(UserPoints).where(UserPoints.user_id == user_id)
                query_result = await session.execute(query)
                user_points = query_result.scalars().first()
                
                if user_points:
                    result["current_points"] = user_points.current_points
                    result["total_earned"] = user_points.total_earned
                    result["total_spent"] = user_points.total_spent
                    
                    # Estadísticas por categoría
                    result["stats"] = {
                        "from_messages": user_points.points_from_messages,
                        "from_reactions": user_points.points_from_reactions,
                        "from_missions": user_points.points_from_missions,
                        "from_dailygift": user_points.points_from_dailygift,
                        "from_minigames": user_points.points_from_minigames,
                        "from_narrative": user_points.points_from_narrative
                    }
                    
                    # Actualizar caché en memoria
                    self.points[user_id] = user_points.current_points
                
                # Calcular puntos para siguiente nivel
                current_level = result["level"]
                next_level_points = (current_level + 1) ** 2 * 100
                current_level_points = current_level ** 2 * 100
                points_needed = next_level_points - current_level_points
                
                result["next_level_points"] = next_level_points
                
                # Calcular progreso hacia el siguiente nivel
                if result["total_earned"] > current_level_points:
                    level_progress = result["total_earned"] - current_level_points
                    result["progress_to_next_level"] = min(100, (level_progress / points_needed) * 100)
        
        except Exception as e:
            self.logger.error(f"Error al obtener puntos del usuario: {e}")
        
        return result

    def get_points(self, user_id: int) -> int:
        """
        Consulta los puntos de un usuario (versión simple para compatibilidad).
        
        Args:
            user_id: ID del usuario.
            
        Returns:
            Puntos actuales.
        """
        return self.points.get(user_id, 0)

    async def handle_diana_validation_completed(self, event: DianaValidationCompletedEvent) -> None:
        """
        Maneja validaciones Diana completadas exitosamente.
        
        Args:
            event: Evento de validación Diana completada.
        """
        user_id = event.user_id 
        validation_type = event.validation_type
        score = event.score
        reward_data = event.reward_data
        
        self.logger.info(f"[Gamification] Validación Diana completada para {user_id}: {validation_type} (score: {score})")
        
        # Calcular puntos basados en el tipo de validación y score
        points_to_award = self._calculate_diana_validation_points(validation_type, score, reward_data)
        
        if points_to_award > 0:
            await self._award_points(user_id, points_to_award, event)
        
        # Verificar si debe desbloquear logros especiales de Diana
        await self._check_diana_validation_achievements(user_id, validation_type, score)
        
        # Actualizar progreso en misiones de validación Diana
        await self._update_missions_progress(user_id, "diana_validation_completed", 1, validation_type)

    async def handle_diana_validation_failed(self, event: DianaValidationFailedEvent) -> None:
        """
        Maneja validaciones Diana fallidas.
        
        Args:
            event: Evento de validación Diana fallida.
        """
        user_id = event.user_id
        validation_type = event.validation_type
        score = event.score
        
        self.logger.info(f"[Gamification] Validación Diana fallida para {user_id}: {validation_type} (score: {score})")
        
        # Otorgar puntos de consolación (menores)
        consolation_points = max(1, int(score * 2))  # Mínimo 1 punto
        await self._award_points(user_id, consolation_points, event)
        
        # Actualizar progreso en misiones de "intentos" de validación
        await self._update_missions_progress(user_id, "diana_validation_attempt", 1, validation_type)

    async def handle_narrative_validation_progress(self, event: NarrativeValidationProgressEvent) -> None:
        """
        Maneja progreso en validaciones narrativas.
        
        Args:
            event: Evento de progreso en validación narrativa.
        """
        user_id = event.user_id
        validation_type = event.validation_type
        progress_data = event.progress_data
        
        self.logger.debug(f"[Gamification] Progreso en validación narrativa para {user_id}: {validation_type}")
        
        # Otorgar puntos pequeños por progreso
        progress_points = 2
        await self._award_points(user_id, progress_points, event)
        
        # Actualizar progreso en misiones de participación narrativa
        await self._update_missions_progress(user_id, "narrative_validation_progress", 1, validation_type)

    def _calculate_diana_validation_points(self, validation_type: str, score: float, reward_data: Dict) -> int:
        """
        Calcula puntos a otorgar basado en el tipo de validación Diana y score.
        
        Args:
            validation_type: Tipo de validación
            score: Score obtenido
            reward_data: Datos adicionales de recompensa
            
        Returns:
            Puntos a otorgar
        """
        # Puntos base por tipo de validación
        base_points = {
            'level_1_to_2': 25,      # Validación de reacción
            'level_2_to_3': 40,      # Validación de observación  
            'level_3_to_vip': 60,    # Validación de perfil de deseo
            'level_5_to_6': 80       # Validación de empatía
        }
        
        # Obtener puntos base
        points = base_points.get(validation_type, 20)
        
        # Multiplicador basado en score (0.0 - 1.0)
        score_multiplier = max(0.5, min(2.0, score))  # Entre 0.5x y 2.0x
        
        # Bonus por datos de recompensa especiales
        bonus = 0
        if reward_data:
            if reward_data.get('reaction_type') == 'immediate':
                bonus += 5
            if reward_data.get('observation_type') == 'methodical':
                bonus += 10
            if reward_data.get('empathy_type') == 'genuine':
                bonus += 15
        
        final_points = int((points * score_multiplier) + bonus)
        return max(1, final_points)  # Mínimo 1 punto

    async def _check_diana_validation_achievements(self, user_id: int, validation_type: str, score: float) -> None:
        """
        Verifica logros especiales relacionados con validaciones Diana.
        
        Args:
            user_id: ID del usuario
            validation_type: Tipo de validación
            score: Score obtenido
        """
        try:
            async for session in get_session():
                # Buscar logros relacionados con validaciones Diana
                query = select(Achievement).where(
                    and_(
                        Achievement.criteria.contains({"type": "diana_validation"}),
                        or_(
                            Achievement.criteria.contains({"validation_type": validation_type}),
                            Achievement.criteria.contains({"validation_type": "any"})
                        )
                    )
                )
                result = await session.execute(query)
                achievements = result.scalars().all()
                
                for achievement in achievements:
                    # Verificar criterios específicos
                    criteria = achievement.criteria
                    
                    # Verificar score mínimo si está especificado
                    min_score = criteria.get('min_score', 0.0)
                    if score < min_score:
                        continue
                    
                    # Verificar si ya tiene el logro
                    user_achievement_query = select(UserAchievement).where(
                        and_(
                            UserAchievement.user_id == user_id,
                            UserAchievement.achievement_id == achievement.id
                        )
                    )
                    user_achievement_result = await session.execute(user_achievement_query)
                    user_achievement = user_achievement_result.scalars().first()
                    
                    if not user_achievement:
                        # Crear nuevo logro
                        user_achievement = UserAchievement(
                            user_id=user_id,
                            achievement_id=achievement.id,
                            is_completed=True,
                            progress=100.0,
                            completed_at=datetime.now(),
                            completion_data={
                                "validation_type": validation_type,
                                "score": score
                            }
                        )
                        session.add(user_achievement)
                        
                        # Otorgar recompensa
                        if achievement.points_reward > 0:
                            points_query = select(UserPoints).where(UserPoints.user_id == user_id)
                            points_result = await session.execute(points_query)
                            user_points = points_result.scalars().first()
                            
                            if user_points:
                                user_points.current_points += achievement.points_reward
                                user_points.total_earned += achievement.points_reward
                                
                                history_entry = {
                                    "timestamp": datetime.now().isoformat(),
                                    "amount": achievement.points_reward,
                                    "source": f"DianaValidationAchievement_{achievement.key}",
                                    "balance": user_points.current_points
                                }
                                user_points.points_history.append(history_entry)
                        
                        await session.commit()
                        self.logger.info(f"Usuario {user_id} desbloqueó logro Diana {achievement.key}")
                        
        except Exception as e:
            self.logger.error(f"Error verificando logros de validación Diana: {e}")
