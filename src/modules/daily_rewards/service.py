"""Servicio de regalos diarios."""

import structlog
import random
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from ..gamification.service import GamificationService
from ...core.interfaces.ICoreService import ICoreService

logger = structlog.get_logger()

class RewardType(Enum):
    """Tipos de recompensas disponibles."""
    POINTS = "points"
    MULTIPLIER = "multiplier"
    HINT = "hint"
    FRAGMENT = "fragment"
    SPECIAL = "special"
    VIP_TEMP = "vip_temp"

@dataclass
class DailyReward:
    """Representa una recompensa diaria."""
    id: str
    name: str
    description: str
    reward_type: RewardType
    value: int
    icon: str
    rarity: str  # common, rare, epic, legendary
    vip_only: bool = False
    level_required: int = 0
    
@dataclass
class RewardClaim:
    """Representa una reclamación de recompensa."""
    user_id: int
    reward_id: str
    claim_date: datetime
    consecutive_days: int
    
class DailyRewardsService(ICoreService):
    """Servicio para gestionar regalos diarios."""
    
    def __init__(self, gamification_service: GamificationService):
        self.gamification_service = gamification_service
        self._rewards = self._initialize_rewards()
        self._user_claims = {}  # user_id -> RewardClaim
        self._consecutive_streaks = {}  # user_id -> days
        
    async def setup(self) -> None:
        """Inicializa el servicio de recompensas diarias."""
        # Nothing to setup for now - all data is in memory
        logger.info("DailyRewardsService initialized successfully")
        
    def _initialize_rewards(self) -> Dict[str, DailyReward]:
        """Inicializa las recompensas disponibles."""
        rewards = {
            # === RECOMPENSAS COMUNES ===
            "daily_basic": DailyReward(
                id="daily_basic",
                name="Besitos Diarios",
                description="Una pequeña cantidad de besitos para empezar el día",
                reward_type=RewardType.POINTS,
                value=50,
                icon="💋",
                rarity="common"
            ),
            "daily_medium": DailyReward(
                id="daily_medium",
                name="Besitos Generosos",
                description="Una buena cantidad de besitos para continuar tu aventura",
                reward_type=RewardType.POINTS,
                value=100,
                icon="💕",
                rarity="common"
            ),
            
            # === RECOMPENSAS RARAS ===
            "daily_multiplier": DailyReward(
                id="daily_multiplier",
                name="Multiplicador x2",
                description="Duplica tus puntos por 2 horas",
                reward_type=RewardType.MULTIPLIER,
                value=2,
                icon="⚡",
                rarity="rare"
            ),
            "daily_big_points": DailyReward(
                id="daily_big_points",
                name="Bonanza de Besitos",
                description="Una gran cantidad de besitos",
                reward_type=RewardType.POINTS,
                value=250,
                icon="💝",
                rarity="rare"
            ),
            "daily_hint": DailyReward(
                id="daily_hint",
                name="Pista Misteriosa",
                description="Una pista para avanzar en la narrativa",
                reward_type=RewardType.HINT,
                value=1,
                icon="🔍",
                rarity="rare"
            ),
            
            # === RECOMPENSAS ÉPICAS ===
            "daily_fragment": DailyReward(
                id="daily_fragment",
                name="Fragmento Especial",
                description="Un fragmento narrativo único",
                reward_type=RewardType.FRAGMENT,
                value=1,
                icon="📜",
                rarity="epic",
                level_required=5
            ),
            "daily_super_multiplier": DailyReward(
                id="daily_super_multiplier",
                name="Multiplicador x3",
                description="Triplica tus puntos por 3 horas",
                reward_type=RewardType.MULTIPLIER,
                value=3,
                icon="⚡⚡",
                rarity="epic",
                level_required=10
            ),
            "daily_massive_points": DailyReward(
                id="daily_massive_points",
                name="Lluvia de Besitos",
                description="Una cantidad masiva de besitos",
                reward_type=RewardType.POINTS,
                value=500,
                icon="💎",
                rarity="epic",
                level_required=15
            ),
            
            # === RECOMPENSAS LEGENDARIAS ===
            "daily_vip_temp": DailyReward(
                id="daily_vip_temp",
                name="Acceso VIP Temporal",
                description="Acceso VIP por 24 horas",
                reward_type=RewardType.VIP_TEMP,
                value=1,
                icon="👑",
                rarity="legendary",
                level_required=20
            ),
            "daily_mega_multiplier": DailyReward(
                id="daily_mega_multiplier",
                name="Multiplicador x5",
                description="Quintuplica tus puntos por 1 hora",
                reward_type=RewardType.MULTIPLIER,
                value=5,
                icon="🌟",
                rarity="legendary",
                level_required=25
            ),
            
            # === RECOMPENSAS VIP EXCLUSIVAS ===
            "vip_daily_premium": DailyReward(
                id="vip_daily_premium",
                name="Regalo VIP Premium",
                description="Recompensa exclusiva para usuarios VIP",
                reward_type=RewardType.POINTS,
                value=300,
                icon="👑💋",
                rarity="rare",
                vip_only=True
            ),
            "vip_special_fragment": DailyReward(
                id="vip_special_fragment",
                name="Fragmento VIP Exclusivo",
                description="Un fragmento narrativo solo para VIP",
                reward_type=RewardType.FRAGMENT,
                value=1,
                icon="👑📜",
                rarity="epic",
                vip_only=True
            )
        }
        
        logger.info(f"Sistema de regalos diarios inicializado con {len(rewards)} recompensas")
        return rewards
    
    async def can_claim_daily_reward(self, user_id: int) -> bool:
        """
        Verifica si un usuario puede reclamar el regalo diario.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            True si puede reclamar, False si ya lo hizo hoy
        """
        today = datetime.now().date()
        
        if user_id in self._user_claims:
            last_claim = self._user_claims[user_id]
            return last_claim.claim_date.date() != today
            
        return True
    
    async def get_available_reward(self, user_id: int) -> Optional[DailyReward]:
        """
        Obtiene la recompensa disponible para un usuario.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Recompensa disponible o None si ya reclamó hoy
        """
        if not await self.can_claim_daily_reward(user_id):
            return None
        
        # Obtener estadísticas del usuario
        user_stats = await self.gamification_service.get_user_stats(user_id)
        user_level = user_stats.get('level', 0)
        is_vip = user_stats.get('is_vip', False)
        
        # Obtener racha consecutiva
        consecutive_days = self._get_consecutive_streak(user_id)
        
        # Determinar pool de recompensas disponibles
        available_rewards = []
        
        for reward in self._rewards.values():
            # Verificar requisitos básicos
            if reward.vip_only and not is_vip:
                continue
                
            if reward.level_required > user_level:
                continue
                
            available_rewards.append(reward)
        
        if not available_rewards:
            # Fallback a recompensa básica
            return self._rewards.get("daily_basic")
        
        # Seleccionar recompensa basada en probabilidades y racha
        selected_reward = self._select_reward_by_probability(
            available_rewards, 
            consecutive_days
        )
        
        logger.debug(
            f"Recompensa diaria para usuario {user_id}: {selected_reward.id} "
            f"(racha: {consecutive_days} días)"
        )
        
        return selected_reward
    
    def _select_reward_by_probability(
        self, 
        available_rewards: List[DailyReward], 
        consecutive_days: int
    ) -> DailyReward:
        """Selecciona una recompensa basada en probabilidades y racha."""
        
        # Probabilidades base por rareza
        base_probabilities = {
            "common": 60,
            "rare": 25,
            "epic": 10,
            "legendary": 5
        }
        
        # Bonificación por racha consecutiva
        streak_bonus = min(consecutive_days * 2, 20)  # Máximo 20% de bonificación
        
        # Ajustar probabilidades (Fixed: Use reward.id as key instead of reward object)
        probabilities = {}
        reward_map = {}  # Map reward.id to reward object
        
        for reward in available_rewards:
            base_prob = base_probabilities.get(reward.rarity, 10)
            
            # Aumentar probabilidad de recompensas mejores con la racha
            if reward.rarity in ["epic", "legendary"]:
                final_prob = base_prob + streak_bonus
            else:
                final_prob = base_prob
                
            probabilities[reward.id] = final_prob  # Use hashable reward.id as key
            reward_map[reward.id] = reward  # Keep mapping to reward object
        
        # Selección ponderada
        total_weight = sum(probabilities.values())
        rand_num = random.uniform(0, total_weight)
        
        current_weight = 0
        for reward_id, weight in probabilities.items():
            current_weight += weight
            if rand_num <= current_weight:
                return reward_map[reward_id]  # Return the reward object
        
        # Fallback
        return available_rewards[0]
    
    async def claim_daily_reward(self, user_id: int) -> Dict[str, Any]:
        """
        Reclama el regalo diario para un usuario.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Resultado de la reclamación
        """
        # Verificar que puede reclamar
        if not await self.can_claim_daily_reward(user_id):
            return {
                "success": False,
                "reason": "Ya has reclamado tu regalo diario hoy"
            }
        
        # Obtener recompensa disponible
        reward = await self.get_available_reward(user_id)
        if not reward:
            return {
                "success": False,
                "reason": "No hay recompensas disponibles"
            }
        
        try:
            # Calcular racha consecutiva
            consecutive_days = self._update_consecutive_streak(user_id)
            
            # Aplicar la recompensa
            effect_result = await self._apply_reward_effect(user_id, reward)
            
            # Registrar la reclamación
            claim = RewardClaim(
                user_id=user_id,
                reward_id=reward.id,
                claim_date=datetime.now(),
                consecutive_days=consecutive_days
            )
            self._user_claims[user_id] = claim
            
            logger.info(
                f"Usuario {user_id} reclamó regalo diario: {reward.id} "
                f"(racha: {consecutive_days} días)"
            )
            
            return {
                "success": True,
                "reward": reward,
                "consecutive_days": consecutive_days,
                "effect": effect_result,
                "next_claim_available": datetime.now() + timedelta(days=1)
            }
            
        except Exception as e:
            logger.error(f"Error al reclamar regalo diario para usuario {user_id}: {e}")
            return {
                "success": False,
                "reason": "Error interno al procesar la recompensa"
            }
    
    async def _apply_reward_effect(self, user_id: int, reward: DailyReward) -> Dict[str, Any]:
        """Aplica los efectos de una recompensa."""
        effects = []
        
        if reward.reward_type == RewardType.POINTS:
            await self.gamification_service.add_points(user_id, reward.value)
            effects.append(f"💋 +{reward.value} besitos")
            
        elif reward.reward_type == RewardType.MULTIPLIER:
            duration_hours = 2 if reward.value == 2 else 3 if reward.value == 3 else 1
            await self._activate_point_multiplier(user_id, reward.value, duration_hours)
            effects.append(f"⚡ Multiplicador x{reward.value} por {duration_hours}h")
            
        elif reward.reward_type == RewardType.HINT:
            # Integrar con sistema narrativo
            effects.append("🔍 Pista narrativa desbloqueada")
            
        elif reward.reward_type == RewardType.FRAGMENT:
            # Integrar con sistema narrativo
            effects.append("📜 Fragmento narrativo desbloqueado")
            
        elif reward.reward_type == RewardType.VIP_TEMP:
            await self._grant_temporary_vip(user_id, 1)
            effects.append("👑 Acceso VIP por 24 horas")
            
        elif reward.reward_type == RewardType.SPECIAL:
            # Efectos especiales personalizados
            special_effects = await self._apply_special_effect(user_id, reward)
            effects.extend(special_effects)
        
        return {"effects": effects}
    
    async def _activate_point_multiplier(
        self, 
        user_id: int, 
        multiplier: float, 
        hours: int
    ) -> None:
        """Activa un multiplicador de puntos temporal."""
        # Integrar con sistema de gamificación
        await self.gamification_service.set_point_multiplier(
            user_id, multiplier, hours
        )
    
    async def _grant_temporary_vip(self, user_id: int, days: int) -> None:
        """Otorga acceso VIP temporal."""
        # Integrar con sistema de roles/usuarios
        expiry_date = datetime.now() + timedelta(days=days)
        # TODO: Implementar en UserService
        pass
    
    async def _apply_special_effect(self, user_id: int, reward: DailyReward) -> List[str]:
        """Aplica efectos especiales personalizados."""
        effects = []
        
        # Aquí se pueden agregar efectos especiales únicos
        # Por ejemplo: desbloquear contenido especial, dar acceso temporal a funciones, etc.
        
        return effects
    
    def _get_consecutive_streak(self, user_id: int) -> int:
        """Obtiene la racha consecutiva actual de un usuario."""
        return self._consecutive_streaks.get(user_id, 0)
    
    def _update_consecutive_streak(self, user_id: int) -> int:
        """Actualiza y devuelve la racha consecutiva de un usuario."""
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        if user_id in self._user_claims:
            last_claim_date = self._user_claims[user_id].claim_date.date()
            
            if last_claim_date == yesterday:
                # Continúa la racha
                self._consecutive_streaks[user_id] = self._consecutive_streaks.get(user_id, 0) + 1
            elif last_claim_date == today:
                # Ya reclamó hoy (no debería pasar)
                pass
            else:
                # Se rompió la racha
                self._consecutive_streaks[user_id] = 1
        else:
            # Primera vez
            self._consecutive_streaks[user_id] = 1
        
        return self._consecutive_streaks[user_id]
    
    async def get_user_daily_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Obtiene estadísticas de regalos diarios de un usuario.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Estadísticas del usuario
        """
        consecutive_days = self._get_consecutive_streak(user_id)
        can_claim = await self.can_claim_daily_reward(user_id)
        
        # Calcular tiempo hasta próximo regalo
        next_claim_time = None
        if not can_claim and user_id in self._user_claims:
            last_claim = self._user_claims[user_id].claim_date
            next_claim_time = last_claim.replace(
                hour=0, minute=0, second=0, microsecond=0
            ) + timedelta(days=1)
        
        # Estadísticas históricas (simplificado)
        total_claimed = 1 if user_id in self._user_claims else 0
        
        return {
            "can_claim_today": can_claim,
            "consecutive_days": consecutive_days,
            "total_claimed": total_claimed,
            "next_claim_time": next_claim_time,
            "best_streak": consecutive_days  # Simplificado
        }
    
    async def get_reward_by_id(self, reward_id: str) -> Optional[DailyReward]:
        """Obtiene una recompensa por su ID."""
        return self._rewards.get(reward_id)
    
    async def get_all_rewards(self) -> List[DailyReward]:
        """Obtiene todas las recompensas disponibles."""
        return list(self._rewards.values())
    
    async def get_streak_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtiene el ranking de rachas consecutivas.
        
        Args:
            limit: Número máximo de usuarios
            
        Returns:
            Lista ordenada de usuarios con sus rachas
        """
        leaderboard = []
        
        for user_id, streak in self._consecutive_streaks.items():
            if streak > 0:  # Solo usuarios con racha activa
                leaderboard.append({
                    "user_id": user_id,
                    "consecutive_days": streak
                })
        
        # Ordenar por racha descendente
        leaderboard.sort(key=lambda x: x["consecutive_days"], reverse=True)
        
        return leaderboard[:limit]
    
    async def reset_user_streak(self, user_id: int) -> None:
        """Resetea la racha de un usuario (uso administrativo)."""
        if user_id in self._consecutive_streaks:
            del self._consecutive_streaks[user_id]
        logger.info(f"Racha resetada para usuario {user_id}")
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas generales del sistema."""
        total_rewards = len(self._rewards)
        active_streaks = len([s for s in self._consecutive_streaks.values() if s > 0])
        total_users_claimed = len(self._user_claims)
        
        # Distribución por rareza
        rarity_distribution = {}
        for reward in self._rewards.values():
            rarity_distribution[reward.rarity] = rarity_distribution.get(reward.rarity, 0) + 1
        
        return {
            "total_rewards": total_rewards,
            "active_streaks": active_streaks,
            "total_users_claimed": total_users_claimed,
            "rarity_distribution": rarity_distribution,
            "longest_streak": max(self._consecutive_streaks.values()) if self._consecutive_streaks else 0
        }