from typing import Dict, List, Optional, Set, Union
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from sqlalchemy.orm import selectinload

from src.core.interfaces.IEventBus import IEventBus
from src.core.interfaces.ICoreService import ICoreService
from src.modules.events import (
    UserStartedBotEvent, 
    PointsAwardedEvent, 
    NarrativeProgressionEvent, 
    PieceUnlockedEvent, 
    MissionCompletedEvent,
    LevelUpEvent
)
from src.bot.database.models.narrative import StoryFragment, NarrativeChoice, UserNarrativeState
from src.bot.database.models.user import User
from src.bot.database.engine import get_session

# Configurar logger
logger = logging.getLogger(__name__)

class NarrativeService(ICoreService):
    """
    Servicio para manejar la lógica de la narrativa.
    
    Responsabilidades:
    - Gestionar fragmentos de historia
    - Seguir progreso narrativo de usuarios
    - Entregar contenido narrativo basado en eventos
    - Gestionar sistema de pistas (LorePieces)
    """

    def __init__(self, event_bus: IEventBus):
        self._event_bus = event_bus
        self.story_fragments_to_send: Dict[int, str] = {}
        self._fragments_cache: Dict[str, StoryFragment] = {}
        self._starting_fragment_key: Optional[str] = None

    async def setup(self) -> None:
        """Suscribe el servicio a los eventos relevantes y carga configuración inicial."""
        self._event_bus.subscribe(UserStartedBotEvent, self.handle_user_started)
        self._event_bus.subscribe(PointsAwardedEvent, self.handle_points_awarded)
        self._event_bus.subscribe(MissionCompletedEvent, self.handle_mission_completed)
        self._event_bus.subscribe(LevelUpEvent, self.handle_level_up)
        
        # Inicializar el fragmento inicial
        # Este es el fragmento que se mostrará a los usuarios nuevos
        await self._init_starting_fragment()
    
    async def _init_starting_fragment(self) -> None:
        """Identifica y almacena el fragmento inicial de la narrativa."""
        try:
            async for session in get_session():
                query = select(StoryFragment).where(
                    and_(
                        StoryFragment.level_required == 1,
                        StoryFragment.key.like("welcome_%")
                    )
                ).limit(1)
                
                result = await session.execute(query)
                fragment = result.scalars().first()
                
                if fragment:
                    self._starting_fragment_key = fragment.key
                    logger.info(f"Fragmento inicial identificado: {fragment.key}")
                else:
                    logger.warning("No se encontró un fragmento inicial. Los usuarios nuevos no recibirán narrativa.")
                    self._starting_fragment_key = "default_welcome"
        except Exception as e:
            logger.error(f"Error al inicializar fragmento inicial: {e}")
            self._starting_fragment_key = "default_welcome"

    async def handle_user_started(self, event: UserStartedBotEvent) -> None:
        """
        Entrega un mensaje de bienvenida al usuario y configura su estado narrativo inicial.
        
        Args:
            event: Evento que contiene información del usuario que inició el bot.
        """
        user_id = event.user_id
        logger.info(f"[Narrative] Entregando mensaje de bienvenida a {user_id}.")
        
        if self._starting_fragment_key:
            # Asignar fragmento de bienvenida
            self.story_fragments_to_send[user_id] = self._starting_fragment_key
            
            # Configurar estado narrativo del usuario
            await self._ensure_user_narrative_state(user_id, self._starting_fragment_key)
        else:
            logger.warning(f"No hay fragmento inicial configurado para el usuario {user_id}")
            self.story_fragments_to_send[user_id] = "welcome_story_fragment"

    async def handle_points_awarded(self, event: PointsAwardedEvent) -> None:
        """
        Gestiona la entrega de fragmentos narrativos cuando se otorgan puntos.
        
        Args:
            event: Evento que contiene información de los puntos otorgados.
        """
        user_id = event.user_id
        
        # Si los puntos son por una reacción
        if event.source_event == "ReactionAddedEvent":
            logger.info(f"[Narrative] Entregando fragmento por reacción a {user_id}.")
            
            # Buscar un fragmento adecuado basado en el nivel del usuario
            fragment_key = await self._get_appropriate_fragment(user_id, "reaction")
            
            if fragment_key:
                self.story_fragments_to_send[user_id] = fragment_key
                
                # Desbloquear una pista aleatoria (LorePiece) si aplica
                await self._maybe_unlock_lore_piece(user_id, "reaction")
            else:
                self.story_fragments_to_send[user_id] = "reaction_story_fragment"
                
        # Se pueden agregar más fuentes de puntos aquí
        elif event.source_event == "UserStartedBotEvent":
            # Ya manejado en handle_user_started
            pass
        elif event.source_event == "MissionCompletedEvent":
            # Buscar un fragmento para misiones completadas
            fragment_key = await self._get_appropriate_fragment(user_id, "mission")
            
            if fragment_key:
                self.story_fragments_to_send[user_id] = fragment_key
                
                # Las misiones tienen alta probabilidad de desbloquear pistas
                await self._maybe_unlock_lore_piece(user_id, "mission", high_chance=True)
                
    async def handle_mission_completed(self, event: MissionCompletedEvent) -> None:
        """
        Gestiona la entrega de fragmentos narrativos cuando se completa una misión.
        
        Args:
            event: Evento que contiene información de la misión completada.
        """
        user_id = event.user_id
        mission_id = event.mission_id
        
        logger.info(f"[Narrative] Procesando misión completada para {user_id}: {mission_id}")
        
        # Buscar un fragmento adecuado para misiones
        fragment_key = await self._get_appropriate_fragment(user_id, "mission")
        
        if fragment_key:
            self.story_fragments_to_send[user_id] = fragment_key
            logger.info(f"[Narrative] Asignando fragmento {fragment_key} por misión completada")
            
            # Las misiones tienen alta probabilidad de desbloquear pistas
            await self._maybe_unlock_lore_piece(user_id, "mission", high_chance=True)
        else:
            logger.warning(f"[Narrative] No se encontró fragmento para misión de usuario {user_id}")
            
    async def handle_level_up(self, event: LevelUpEvent) -> None:
        """
        Gestiona la progresión narrativa cuando un usuario sube de nivel.
        
        Args:
            event: Evento que contiene información del nuevo nivel.
        """
        user_id = event.user_id
        new_level = event.new_level
        
        logger.info(f"[Narrative] Usuario {user_id} subió al nivel {new_level}")
        
        # Desbloquear fragmentos especiales basados en el nivel
        if new_level >= 2:
            # Nivel 2 desbloquea nuevo personaje o área
            fragment_key = await self._get_level_specific_fragment(user_id, new_level)
            if fragment_key:
                self.story_fragments_to_send[user_id] = fragment_key
                logger.info(f"[Narrative] Asignando fragmento de nivel {new_level}: {fragment_key}")
                
                # Nivel nuevo siempre desbloquea una pista
                await self._maybe_unlock_lore_piece(user_id, "level_up", high_chance=True)
                
    async def _get_level_specific_fragment(self, user_id: int, level: int) -> Optional[str]:
        """
        Obtiene un fragmento específico para un nivel.
        
        Args:
            user_id: ID del usuario.
            level: Nivel del usuario.
            
        Returns:
            Clave del fragmento específico para el nivel o None si no existe.
        """
        try:
            async for session in get_session():
                # Buscar fragmentos para el nivel específico
                query = select(StoryFragment).where(
                    and_(
                        StoryFragment.level_required == level,
                        StoryFragment.tags.contains(["level_up"])
                    )
                ).limit(1)
                
                result = await session.execute(query)
                fragment = result.scalars().first()
                
                if fragment:
                    return fragment.key
                
                # Si no hay fragmento específico, usar uno genérico
                fallback_query = select(StoryFragment).where(
                    and_(
                        StoryFragment.level_required <= level,
                        StoryFragment.tags.contains(["progression"])
                    )
                ).limit(1)
                
                fallback_result = await session.execute(fallback_query)
                fallback_fragment = fallback_result.scalars().first()
                
                if fallback_fragment:
                    return fallback_fragment.key
                
                return None
                
        except Exception as e:
            logger.error(f"Error al obtener fragmento para nivel: {e}")
            return None
    
    async def _ensure_user_narrative_state(self, user_id: int, current_fragment_key: str) -> None:
        """
        Asegura que el usuario tenga un estado narrativo, creándolo si no existe.
        
        Args:
            user_id: ID del usuario.
            current_fragment_key: Clave del fragmento actual.
        """
        try:
            async for session in get_session():
                # Verificar si el usuario ya tiene un estado narrativo
                query = select(UserNarrativeState).where(UserNarrativeState.user_id == user_id)
                result = await session.execute(query)
                state = result.scalars().first()
                
                if not state:
                    # Crear nuevo estado narrativo
                    state = UserNarrativeState(
                        user_id=user_id,
                        current_fragment_key=current_fragment_key,
                        visited_fragments=[current_fragment_key],
                        decisions_made={},
                        narrative_items={},
                        narrative_variables={}
                    )
                    session.add(state)
                    await session.commit()
                    logger.info(f"Estado narrativo creado para usuario {user_id}")
                else:
                    logger.debug(f"El usuario {user_id} ya tiene estado narrativo")
        except Exception as e:
            logger.error(f"Error al configurar estado narrativo: {e}")
    
    async def _get_appropriate_fragment(self, user_id: int, context_type: str) -> Optional[str]:
        """
        Obtiene un fragmento apropiado para el usuario basado en su nivel y contexto.
        
        Args:
            user_id: ID del usuario.
            context_type: Tipo de contexto para el fragmento (reaction, mission, etc).
            
        Returns:
            Clave del fragmento seleccionado o None si no se encuentra.
        """
        try:
            async for session in get_session():
                # Obtener nivel del usuario
                user_query = select(User).where(User.id == user_id)
                user_result = await session.execute(user_query)
                user = user_result.scalars().first()
                
                if not user:
                    logger.warning(f"Usuario {user_id} no encontrado para seleccionar fragmento")
                    return None
                
                user_level = user.level
                is_vip = user.is_vip
                
                # Obtener fragmentos ya vistos
                state_query = select(UserNarrativeState).where(UserNarrativeState.user_id == user_id)
                state_result = await session.execute(state_query)
                state = state_result.scalars().first()
                
                visited_fragments = set(state.visited_fragments) if state else set()
                
                # Buscar fragmentos apropiados
                query = select(StoryFragment).where(
                    and_(
                        StoryFragment.level_required <= user_level,
                        StoryFragment.is_vip_only == False if not is_vip else True,
                        StoryFragment.tags.contains([context_type])
                    )
                )
                
                result = await session.execute(query)
                fragments = result.scalars().all()
                
                # Filtrar fragmentos ya vistos y seleccionar uno
                available_fragments = [f for f in fragments if f.key not in visited_fragments]
                
                if available_fragments:
                    # Priorizar fragmentos que tienen recompensas
                    reward_fragments = [f for f in available_fragments if f.reward_besitos > 0]
                    
                    if reward_fragments:
                        selected = reward_fragments[0]
                    else:
                        selected = available_fragments[0]
                    
                    # Actualizar fragmentos visitados
                    if state:
                        visited_fragments.add(selected.key)
                        await session.execute(
                            update(UserNarrativeState)
                            .where(UserNarrativeState.user_id == user_id)
                            .values(visited_fragments=list(visited_fragments))
                        )
                        await session.commit()
                    
                    return selected.key
                
                # Si todos los fragmentos ya fueron vistos, volver a usar uno aleatorio
                if fragments:
                    return fragments[0].key
                
                return None
        except Exception as e:
            logger.error(f"Error al obtener fragmento apropiado: {e}")
            return None
    
    async def _maybe_unlock_lore_piece(self, user_id: int, context_type: str, high_chance: bool = False) -> bool:
        """
        Posiblemente desbloquea una pista narrativa (LorePiece) para el usuario.
        
        Args:
            user_id: ID del usuario.
            context_type: Tipo de contexto (reaction, mission, etc).
            high_chance: Si debe tener alta probabilidad de desbloqueo.
            
        Returns:
            True si se desbloqueó una pista, False en caso contrario.
        """
        import random
        
        # Probabilidad de desbloqueo
        chance = 0.7 if high_chance else 0.3
        
        if random.random() > chance:
            return False
        
        try:
            async for session in get_session():
                # Obtener estado narrativo del usuario
                query = select(UserNarrativeState).where(UserNarrativeState.user_id == user_id)
                result = await session.execute(query)
                state = result.scalars().first()
                
                if not state:
                    logger.warning(f"No se encontró estado narrativo para usuario {user_id}")
                    return False
                
                # Verificar si hay pistas para desbloquear
                # Las pistas están en narrative_items bajo la clave "lore_pieces"
                narrative_items = state.narrative_items
                current_lore_pieces = narrative_items.get("lore_pieces", {})
                
                # Generar una nueva pista
                # En un sistema real, estas vendrían de una tabla en la base de datos
                lore_piece_candidates = {
                    "historia_diana": "Fragmento sobre el origen de Diana",
                    "misterio_kinkys": "Historia del club Los Kinkys",
                    "secreto_lucien": "El pasado oculto de Lucien",
                    "simbolo_mariposa": "El significado de la mariposa",
                    "ritual_iniciacion": "El ritual de iniciación al círculo interno"
                }
                
                # Filtrar las pistas que ya tiene el usuario
                available_pieces = {k: v for k, v in lore_piece_candidates.items() 
                                    if k not in current_lore_pieces}
                
                if not available_pieces:
                    logger.info(f"Usuario {user_id} ya tiene todas las pistas disponibles")
                    return False
                
                # Seleccionar una pista aleatoria
                piece_key = random.choice(list(available_pieces.keys()))
                piece_description = available_pieces[piece_key]
                
                # Agregar la pista al inventario del usuario
                current_lore_pieces[piece_key] = {
                    "title": piece_key.replace("_", " ").title(),
                    "description": piece_description,
                    "unlocked_at": str(datetime.now()),
                    "source": context_type
                }
                
                narrative_items["lore_pieces"] = current_lore_pieces
                
                # Actualizar en la base de datos
                await session.execute(
                    update(UserNarrativeState)
                    .where(UserNarrativeState.user_id == user_id)
                    .values(narrative_items=narrative_items)
                )
                await session.commit()
                
                # Emitir evento de desbloqueo de pista
                piece_event = PieceUnlockedEvent(
                    user_id=user_id,
                    piece_id=piece_key,
                    unlock_method=context_type
                )
                await self._event_bus.publish(piece_event)
                
                logger.info(f"Pista '{piece_key}' desbloqueada para usuario {user_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error al desbloquear pista: {e}")
            return False
    
    async def get_user_fragment(self, user_id: int) -> Optional[Dict]:
        """
        Obtiene el fragmento actual del usuario con sus opciones.
        
        Args:
            user_id: ID del usuario.
            
        Returns:
            Diccionario con los datos del fragmento y sus opciones, o None si no existe.
        """
        try:
            async for session in get_session():
                # Obtener estado narrativo del usuario
                query = select(UserNarrativeState).where(UserNarrativeState.user_id == user_id)
                result = await session.execute(query)
                state = result.scalars().first()
                
                if not state or not state.current_fragment_key:
                    logger.warning(f"Usuario {user_id} no tiene fragmento actual")
                    return None
                
                # Obtener fragmento con opciones
                fragment_query = select(StoryFragment).options(
                    selectinload(StoryFragment.choices)
                ).where(StoryFragment.key == state.current_fragment_key)
                
                fragment_result = await session.execute(fragment_query)
                fragment = fragment_result.scalars().first()
                
                if not fragment:
                    logger.warning(f"Fragmento {state.current_fragment_key} no encontrado")
                    return None
                
                # Convertir a diccionario para devolver
                return {
                    "key": fragment.key,
                    "title": fragment.title,
                    "character": fragment.character,
                    "text": fragment.text,
                    "level_required": fragment.level_required,
                    "is_vip_only": fragment.is_vip_only,
                    "choices": [
                        {
                            "id": choice.id,
                            "text": choice.text,
                            "target_fragment_key": choice.target_fragment_key,
                            "required_items": choice.required_items
                        }
                        for choice in fragment.choices
                    ]
                }
        
        except Exception as e:
            logger.error(f"Error al obtener fragmento del usuario: {e}")
            return None
    
    async def get_user_lore_pieces(self, user_id: int) -> List[Dict]:
        """
        Obtiene las pistas narrativas (LorePieces) desbloqueadas por el usuario.
        
        Args:
            user_id: ID del usuario.
            
        Returns:
            Lista de pistas desbloqueadas.
        """
        try:
            async for session in get_session():
                # Obtener estado narrativo del usuario
                query = select(UserNarrativeState).where(UserNarrativeState.user_id == user_id)
                result = await session.execute(query)
                state = result.scalars().first()
                
                if not state:
                    logger.warning(f"Usuario {user_id} no tiene estado narrativo")
                    return []
                
                # Obtener pistas del usuario
                narrative_items = state.narrative_items
                lore_pieces = narrative_items.get("lore_pieces", {})
                
                # Convertir a lista para devolver
                return [
                    {
                        "key": key,
                        "title": data["title"],
                        "description": data["description"],
                        "unlocked_at": data["unlocked_at"],
                        "source": data["source"]
                    }
                    for key, data in lore_pieces.items()
                ]
        
        except Exception as e:
            logger.error(f"Error al obtener pistas del usuario: {e}")
            return []
    
    async def make_narrative_choice(self, user_id: int, choice_id: int) -> bool:
        """
        Registra una elección narrativa del usuario y actualiza su estado.
        
        Args:
            user_id: ID del usuario.
            choice_id: ID de la opción elegida.
            
        Returns:
            True si la elección fue procesada correctamente, False en caso contrario.
        """
        try:
            async for session in get_session():
                # Obtener la opción elegida
                choice_query = select(NarrativeChoice).options(
                    selectinload(NarrativeChoice.fragment)
                ).where(NarrativeChoice.id == choice_id)
                
                choice_result = await session.execute(choice_query)
                choice = choice_result.scalars().first()
                
                if not choice:
                    logger.warning(f"Opción {choice_id} no encontrada")
                    return False
                
                # Obtener estado narrativo del usuario
                state_query = select(UserNarrativeState).where(UserNarrativeState.user_id == user_id)
                state_result = await session.execute(state_query)
                state = state_result.scalars().first()
                
                if not state:
                    logger.warning(f"Usuario {user_id} no tiene estado narrativo")
                    return False
                
                # Verificar si el usuario está en el fragmento correcto
                if state.current_fragment_key != choice.fragment.key:
                    logger.warning(f"Usuario {user_id} no está en el fragmento correcto")
                    return False
                
                # Actualizar el estado narrativo
                # 1. Actualizar fragmento actual
                # 2. Registrar la decisión
                # 3. Agregar fragmento objetivo a visitados
                
                decisions_made = state.decisions_made
                fragment_decisions = decisions_made.get(choice.fragment.key, [])
                fragment_decisions.append(choice.id)
                decisions_made[choice.fragment.key] = fragment_decisions
                
                visited_fragments = set(state.visited_fragments)
                visited_fragments.add(choice.target_fragment_key)
                
                await session.execute(
                    update(UserNarrativeState)
                    .where(UserNarrativeState.user_id == user_id)
                    .values(
                        current_fragment_key=choice.target_fragment_key,
                        decisions_made=decisions_made,
                        visited_fragments=list(visited_fragments)
                    )
                )
                await session.commit()
                
                # Emitir evento de progresión narrativa
                progression_event = NarrativeProgressionEvent(
                    user_id=user_id,
                    fragment_id=choice.target_fragment_key,
                    choices_made=decisions_made
                )
                await self._event_bus.publish(progression_event)
                
                logger.info(f"Usuario {user_id} eligió opción {choice_id}, avanzando a {choice.target_fragment_key}")
                return True
                
        except Exception as e:
            logger.error(f"Error al procesar elección narrativa: {e}")
            return False

# Importación de datetime ya está al principio del archivo