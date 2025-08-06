"""Servicio de tienda de besitos."""

import structlog
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

from ..gamification.service import GamificationService
from ...core.interfaces.ICoreService import ICoreService

logger = structlog.get_logger()

@dataclass
class ShopItem:
    """Representa un artículo de la tienda."""
    id: str
    name: str
    description: str
    price: int  # En besitos
    category: str
    icon: str
    available: bool = True
    stock: Optional[int] = None  # None = stock ilimitado
    vip_only: bool = False
    level_required: int = 0
    purchase_limit: Optional[int] = None  # Límite de compras por usuario
    
class ShopService(ICoreService):
    """Servicio para gestionar la tienda de besitos."""
    
    def __init__(self, gamification_service: GamificationService):
        self.gamification_service = gamification_service
        self._items = self._initialize_shop_items()
        self._user_purchases = {}  # Tracking de compras por usuario
        
    def _initialize_shop_items(self) -> Dict[str, ShopItem]:
        """Inicializa los artículos de la tienda."""
        items = {
            # === CATEGORÍA: NARRATIVA ===
    
    async def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get user stats for shop validation."""
        try:
            if hasattr(self.gamification_service, 'get_user_points'):
                points_data = await self.gamification_service.get_user_points(user_id)
                return {
                    'total_points': points_data.get('current_points', 0),
                    'level': self._calculate_level_from_points(points_data.get('current_points', 0)),
                    'is_vip': False  # TODO: Get from user service
                }
            else:
                return {'total_points': 0, 'level': 1, 'is_vip': False}
        except:
            return {'total_points': 0, 'level': 1, 'is_vip': False}
    
    def _calculate_level_from_points(self, points: int) -> int:
        """Calculate user level from points."""
        if points < 100:
            return 1
        elif points < 400:
            return 2
        elif points < 900:
            return 3
        elif points < 1600:
            return 4
        elif points < 2500:
            return 5
        else:
            return min(10, 5 + (points - 2500) // 1000)
            "hint_basic": ShopItem(
                id="hint_basic",
                name="🔍 Pista Básica",
                description="Obtén una pista para avanzar en la narrativa actual",
                price=50,
                category="narrativa",
                icon="🔍"
            ),
            "hint_premium": ShopItem(
                id="hint_premium", 
                name="💎 Pista Premium",
                description="Pista exclusiva que revela secretos importantes",
                price=150,
                category="narrativa",
                icon="💎",
                vip_only=True
            ),
            "fragment_unlock": ShopItem(
                id="fragment_unlock",
                name="📜 Desbloquear Fragmento",
                description="Desbloquea un fragmento narrativo especial",
                price=200,
                category="narrativa",
                icon="📜",
                level_required=5
            ),
            
            # === CATEGORÍA: GAMIFICACIÓN ===
            "double_points": ShopItem(
                id="double_points",
                name="⚡ Puntos Dobles",
                description="Duplica tus puntos por 24 horas",
                price=300,
                category="gamificacion",
                icon="⚡",
                purchase_limit=1  # Una vez al día
            ),
            "mission_skip": ShopItem(
                id="mission_skip",
                name="⏭️ Saltar Misión",
                description="Completa automáticamente una misión activa",
                price=100,
                category="gamificacion", 
                icon="⏭️"
            ),
            "extra_daily": ShopItem(
                id="extra_daily",
                name="🎁 Regalo Extra",
                description="Obtén un regalo diario adicional",
                price=75,
                category="gamificacion",
                icon="🎁"
            ),
            
            # === CATEGORÍA: VIP ===
            "vip_access_day": ShopItem(
                id="vip_access_day",
                name="👑 Acceso VIP (1 día)",
                description="Acceso VIP temporal por 24 horas",
                price=500,
                category="vip",
                icon="👑"
            ),
            "auction_bid": ShopItem(
                id="auction_bid",
                name="🏆 Ficha de Subasta",
                description="Ficha para participar en subastas exclusivas",
                price=250,
                category="vip",
                icon="🏆",
                vip_only=True
            ),
            
            # === CATEGORÍA: ESPECIALES ===
            "mystery_box": ShopItem(
                id="mystery_box",
                name="📦 Caja Misteriosa",
                description="Contiene recompensas aleatorias sorpresa",
                price=400,
                category="especiales",
                icon="📦",
                stock=10  # Stock limitado
            ),
            "username_highlight": ShopItem(
                id="username_highlight",
                name="✨ Destacar Nombre",
                description="Tu nombre aparecerá destacado por 7 días",
                price=350,
                category="especiales",
                icon="✨",
                level_required=10
            )
        }
        
        logger.info(f"Tienda inicializada con {len(items)} artículos")
        return items
    
    async def get_shop_items(
        self, 
        user_id: int, 
        category: Optional[str] = None,
        vip_only: bool = False
    ) -> List[ShopItem]:
        """
        Obtiene los artículos disponibles en la tienda para un usuario.
        
        Args:
            user_id: ID del usuario
            category: Filtrar por categoría específica
            vip_only: Solo mostrar artículos VIP
            
        Returns:
            Lista de artículos disponibles
        """
        # Obtener información del usuario
        user_stats = await self.gamification_service.get_user_stats(user_id)
        user_level = user_stats.get('level', 0)
        user_points = user_stats.get('total_points', 0)
        is_vip = user_stats.get('is_vip', False)
        
        available_items = []
        
        for item in self._items.values():
            # Filtros básicos
            if not item.available:
                continue
                
            if category and item.category != category:
                continue
                
            if vip_only and not item.vip_only:
                continue
                
            # Verificar requisitos del usuario
            if item.vip_only and not is_vip:
                continue
                
            if item.level_required > user_level:
                continue
                
            # Verificar límites de compra
            if item.purchase_limit:
                user_purchases = self._get_user_purchases(user_id)
                today_purchases = self._count_today_purchases(
                    user_purchases, item.id
                )
                if today_purchases >= item.purchase_limit:
                    continue
                    
            # Verificar stock
            if item.stock is not None and item.stock <= 0:
                continue
                
            available_items.append(item)
        
        # Ordenar por categoría y precio
        available_items.sort(key=lambda x: (x.category, x.price))
        
        logger.debug(
            f"Usuario {user_id}: {len(available_items)} artículos disponibles"
        )
        return available_items
    
    async def get_item_by_id(self, item_id: str) -> Optional[ShopItem]:
        """Obtiene un artículo por su ID."""
        return self._items.get(item_id)
    
    async def can_purchase(self, user_id: int, item_id: str) -> Dict[str, Any]:
        """
        Verifica si un usuario puede comprar un artículo.
        
        Args:
            user_id: ID del usuario
            item_id: ID del artículo
            
        Returns:
            Dict con información de validación
        """
        item = await self.get_item_by_id(item_id)
        if not item:
            return {
                "can_purchase": False,
                "reason": "Artículo no encontrado"
            }
        
        # Verificar disponibilidad básica
        if not item.available:
            return {
                "can_purchase": False,
                "reason": "Artículo no disponible"
            }
            
        # Verificar stock
        if item.stock is not None and item.stock <= 0:
            return {
                "can_purchase": False,
                "reason": "Sin stock disponible"
            }
        
        # Obtener stats del usuario
        user_stats = await self.gamification_service.get_user_stats(user_id)
        user_points = user_stats.get('total_points', 0)
        user_level = user_stats.get('level', 0)
        is_vip = user_stats.get('is_vip', False)
        
        # Verificar puntos suficientes
        if user_points < item.price:
            return {
                "can_purchase": False,
                "reason": f"Necesitas {item.price - user_points} besitos más"
            }
        
        # Verificar nivel requerido
        if item.level_required > user_level:
            return {
                "can_purchase": False,
                "reason": f"Necesitas nivel {item.level_required}"
            }
            
        # Verificar acceso VIP
        if item.vip_only and not is_vip:
            return {
                "can_purchase": False,
                "reason": "Solo disponible para usuarios VIP"
            }
            
        # Verificar límite de compras
        if item.purchase_limit:
            user_purchases = self._get_user_purchases(user_id)
            today_purchases = self._count_today_purchases(
                user_purchases, item_id
            )
            if today_purchases >= item.purchase_limit:
                return {
                    "can_purchase": False,
                    "reason": "Límite diario alcanzado"
                }
        
        return {
            "can_purchase": True,
            "reason": "Compra disponible"
        }
    
    async def purchase_item(self, user_id: int, item_id: str) -> Dict[str, Any]:
        """
        Realiza la compra de un artículo.
        
        Args:
            user_id: ID del usuario
            item_id: ID del artículo
            
        Returns:
            Resultado de la compra
        """
        # Verificar si puede comprar
        validation = await self.can_purchase(user_id, item_id)
        if not validation["can_purchase"]:
            return {
                "success": False,
                "reason": validation["reason"]
            }
        
        item = await self.get_item_by_id(item_id)
        
        try:
            # Descontar puntos
            await self.gamification_service.spend_points(user_id, item.price)
            
            # Reducir stock si aplica
            if item.stock is not None:
                item.stock -= 1
                
            # Registrar compra
            self._record_purchase(user_id, item_id)
            
            # Aplicar efectos del artículo
            effect_result = await self._apply_item_effect(user_id, item)
            
            logger.info(
                f"Usuario {user_id} compró {item_id} por {item.price} besitos"
            )
            
            return {
                "success": True,
                "item": item,
                "effect": effect_result,
                "remaining_points": await self._get_user_points(user_id)
            }
            
        except Exception as e:
            logger.error(f"Error en compra {item_id} para usuario {user_id}: {e}")
            return {
                "success": False,
                "reason": "Error interno en la compra"
            }
    
    async def _apply_item_effect(self, user_id: int, item: ShopItem) -> Dict[str, Any]:
        """Aplica los efectos de un artículo comprado."""
        effects = []
        
        if item.id == "hint_basic":
            # Dar pista básica
            effects.append("💡 Has recibido una pista narrativa")
            
        elif item.id == "hint_premium":
            # Dar pista premium
            effects.append("💎 Has recibido una pista premium exclusiva")
            
        elif item.id == "fragment_unlock":
            # Desbloquear fragmento
            effects.append("📜 Fragmento narrativo desbloqueado")
            
        elif item.id == "double_points":
            # Activar multiplicador de puntos
            await self._activate_point_multiplier(user_id, 2.0, 24)
            effects.append("⚡ Puntos dobles activados por 24 horas")
            
        elif item.id == "mission_skip":
            # Completar misión automáticamente
            effects.append("⏭️ Misión completada automáticamente")
            
        elif item.id == "extra_daily":
            # Dar regalo extra
            extra_points = 100
            await self.gamification_service.add_points(user_id, extra_points)
            effects.append(f"🎁 Has recibido {extra_points} besitos extra")
            
        elif item.id == "vip_access_day":
            # Dar acceso VIP temporal
            await self._grant_temporary_vip(user_id, 1)
            effects.append("👑 Acceso VIP activado por 24 horas")
            
        elif item.id == "mystery_box":
            # Abrir caja misteriosa
            mystery_reward = await self._open_mystery_box(user_id)
            effects.extend(mystery_reward)
            
        elif item.id == "username_highlight":
            # Destacar nombre
            await self._activate_username_highlight(user_id, 7)
            effects.append("✨ Tu nombre estará destacado por 7 días")
        
        return {"effects": effects}
    
    async def _get_user_points(self, user_id: int) -> int:
        """Obtiene los puntos actuales de un usuario."""
        stats = await self.gamification_service.get_user_stats(user_id)
        return stats.get('total_points', 0)
    
    def _get_user_purchases(self, user_id: int) -> List[Dict]:
        """Obtiene el historial de compras de un usuario."""
        return self._user_purchases.get(user_id, [])
    
    def _count_today_purchases(self, purchases: List[Dict], item_id: str) -> int:
        """Cuenta las compras de hoy para un artículo específico."""
        today = datetime.now().date()
        count = 0
        
        for purchase in purchases:
            if (purchase['item_id'] == item_id and 
                purchase['date'].date() == today):
                count += 1
                
        return count
    
    def _record_purchase(self, user_id: int, item_id: str) -> None:
        """Registra una compra en el historial."""
        if user_id not in self._user_purchases:
            self._user_purchases[user_id] = []
            
        self._user_purchases[user_id].append({
            'item_id': item_id,
            'date': datetime.now(),
            'price': self._items[item_id].price
        })
    
    async def _activate_point_multiplier(
        self, 
        user_id: int, 
        multiplier: float, 
        hours: int
    ) -> None:
        """Activa un multiplicador de puntos temporal."""
        # Integrar con el sistema de gamificación
        await self.gamification_service.set_point_multiplier(
            user_id, multiplier, hours
        )
    
    async def _grant_temporary_vip(self, user_id: int, days: int) -> None:
        """Otorga acceso VIP temporal."""
        # Integrar con el sistema de roles/usuarios
        expiry_date = datetime.now() + timedelta(days=days)
        # TODO: Implementar en UserService
        pass
    
    async def _open_mystery_box(self, user_id: int) -> List[str]:
        """Abre una caja misteriosa y devuelve recompensas aleatorias."""
        import random
        
        possible_rewards = [
            ("200 besitos extra", lambda: self.gamification_service.add_points(user_id, 200)),
            ("Pista narrativa especial", lambda: None),
            ("Multiplicador x3 por 2 horas", lambda: self._activate_point_multiplier(user_id, 3.0, 2)),
            ("Fragmento narrativo raro", lambda: None),
            ("500 besitos extra", lambda: self.gamification_service.add_points(user_id, 500)),
        ]
        
        # Seleccionar 1-3 recompensas aleatorias
        num_rewards = random.randint(1, 3)
        selected = random.sample(possible_rewards, num_rewards)
        
        effects = []
        for reward_text, reward_func in selected:
            effects.append(f"🎁 {reward_text}")
            if reward_func:
                await reward_func()
        
        return effects
    
    async def _activate_username_highlight(self, user_id: int, days: int) -> None:
        """Activa el destacado de nombre por un período."""
        # Integrar con sistema de usuarios
        # TODO: Implementar en UserService
        pass
    
    async def get_categories(self) -> List[str]:
        """Obtiene todas las categorías disponibles."""
        categories = list(set(item.category for item in self._items.values()))
        return sorted(categories)
    
    async def get_shop_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de la tienda."""
        total_items = len(self._items)
        available_items = sum(1 for item in self._items.values() if item.available)
        vip_items = sum(1 for item in self._items.values() if item.vip_only)
        
        return {
            "total_items": total_items,
            "available_items": available_items, 
            "vip_items": vip_items,
            "categories": await self.get_categories()
        }