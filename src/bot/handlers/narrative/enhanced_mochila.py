"""
Sistema de Mochila Mejorado

Handler mejorado para el comando /mochila que proporciona una interfaz
atractiva y funcional para explorar pistas narrativas con categorización,
conexiones y un sistema de descubrimiento inteligente.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from aiogram import types, Router
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup

from src.modules.narrative.service import NarrativeService
from src.modules.emotional.service import EmotionalService
from src.bot.handlers.narrative.contextual_responses import DianaContextualResponseSystem

logger = logging.getLogger(__name__)
router = Router()


class EnhancedMochilaSystem:
    """
    Sistema mejorado de gestión de mochila narrativa.
    
    Características:
    - Categorización inteligente de pistas
    - Sistema de conexiones entre pistas
    - Interfaz adaptativa según progreso
    - Integración con estado emocional de Diana
    - Sistema de descubrimiento de patrones
    """
    
    def __init__(self, 
                 narrative_service: NarrativeService,
                 emotional_service: EmotionalService,
                 diana_system: DianaContextualResponseSystem):
        self.narrative_service = narrative_service
        self.emotional_service = emotional_service
        self.diana_system = diana_system
        
        # Categorías de pistas
        self.lore_categories = {
            'characters': {
                'name': '👥 Personajes',
                'icon': '👤',
                'keywords': ['diana', 'lucien', 'personaje', 'historia personal']
            },
            'locations': {
                'name': '🏛️ Lugares',
                'icon': '📍',
                'keywords': ['club', 'lugar', 'ubicación', 'local']
            },
            'mysteries': {
                'name': '🔮 Misterios',
                'icon': '❓',
                'keywords': ['secreto', 'misterio', 'oculto', 'enigma']
            },
            'rituals': {
                'name': '🌙 Rituales',
                'icon': '🔯',
                'keywords': ['ritual', 'ceremonia', 'iniciación', 'tradición']
            },
            'symbols': {
                'name': '🦋 Símbolos',
                'icon': '🔱',
                'keywords': ['símbolo', 'marca', 'signo', 'emblema']
            }
        }
        
        # Cache de conexiones descubiertas
        self.discovered_connections: Dict[int, Dict[str, List[str]]] = {}
    
    async def show_mochila_hub(self, message: Message) -> None:
        """
        Muestra el hub principal de la mochila con interface mejorada.
        
        Args:
            message: Mensaje del comando /mochila
        """
        user_id = message.from_user.id
        
        try:
            # Obtener pistas del usuario
            lore_pieces = await self.narrative_service.get_user_lore_pieces(user_id)
            
            if not lore_pieces:
                await self._show_empty_mochila(message)
                return
            
            # Categorizar pistas
            categorized_lore = self._categorize_lore_pieces(lore_pieces)
            
            # Generar respuesta contextual de Diana
            diana_response = await self.diana_system.generate_contextual_response(
                user_id=user_id,
                context_type='mochila_access',
                context_data={
                    'lore_count': len(lore_pieces),
                    'categories_found': len([cat for cat in categorized_lore.values() if cat])
                }
            )
            
            # Construir mensaje principal
            await self._display_mochila_hub(message, lore_pieces, categorized_lore, diana_response)
        
        except Exception as e:
            logger.error(f"Error mostrando mochila para usuario {user_id}: {e}")
            await message.answer(
                "🎒 *Error en la Mochila*\n\n"
                "Diana está reorganizando tus pistas... inténtalo de nuevo.",
                parse_mode="Markdown"
            )
    
    async def _show_empty_mochila(self, message: Message) -> None:
        """Muestra mensaje cuando la mochila está vacía."""
        user_id = message.from_user.id
        
        # Respuesta contextual de Diana para mochila vacía
        diana_response = await self.diana_system.generate_contextual_response(
            user_id=user_id,
            context_type='empty_mochila'
        )
        
        empty_message = (
            "🎒 **Tu Mochila Narrativa**\n\n"
            "✨ *Tu mochila está esperando ser llenada con secretos...*\n\n"
            f"🌙 *Diana susurra:* \"{diana_response}\"\n\n"
            "**¿Cómo obtener pistas?**\n"
            "🔸 Reacciona a mensajes en canales\n"
            "🔸 Completa misiones diarias\n"
            "🔸 Avanza en la narrativa principal\n"
            "🔸 Participa en trivias\n"
            "🔸 Explora profundamente en la historia\n\n"
            "💫 *Cada pista revela un fragmento del mundo de Diana*"
        )
        
        keyboard = InlineKeyboardBuilder()
        keyboard.button(text="📖 Ir a Historia", callback_data="diana:go_to_story")
        keyboard.button(text="🎮 Ver Misiones", callback_data="diana:go_to_missions")
        keyboard.button(text="⬅️ Menú Principal", callback_data="diana:back_to_main")
        keyboard.adjust(2, 1)
        
        await message.answer(
            empty_message,
            parse_mode="Markdown",
            reply_markup=keyboard.as_markup()
        )
    
    async def _display_mochila_hub(self, 
                                 message: Message,
                                 lore_pieces: List[Dict],
                                 categorized_lore: Dict,
                                 diana_response: str) -> None:
        """Muestra el hub principal con pistas categorizadas."""
        
        # Construir mensaje principal
        total_pieces = len(lore_pieces)
        categories_with_content = len([cat for cat in categorized_lore.values() if cat])
        
        hub_message = (
            "🎒 **Tu Mochila Narrativa**\n\n"
            f"✨ *Diana examina tus tesoros...*\n"
            f"\"{diana_response}\"\n\n"
            f"📊 **Estado de tu Colección:**\n"
            f"🗝️ Total de pistas: **{total_pieces}**\n"
            f"📁 Categorías descubiertas: **{categories_with_content}**\n"
            f"🔗 Conexiones encontradas: **{self._count_user_connections(message.from_user.id)}**\n\n"
        )
        
        # Agregar vista previa de categorías
        if categorized_lore:
            hub_message += "**🗂️ Tus Categorías:**\n"
            for category_key, pieces in categorized_lore.items():
                if pieces:
                    category_info = self.lore_categories[category_key]
                    hub_message += f"{category_info['icon']} {category_info['name']}: **{len(pieces)}** pistas\n"
        
        # Crear keyboard principal
        keyboard = self._create_mochila_hub_keyboard(categorized_lore, total_pieces)
        
        await message.answer(
            hub_message,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    
    def _create_mochila_hub_keyboard(self, 
                                   categorized_lore: Dict,
                                   total_pieces: int) -> InlineKeyboardMarkup:
        """Crea keyboard para el hub de mochila."""
        builder = InlineKeyboardBuilder()
        
        # Botones de categorías (solo mostrar las que tienen contenido)
        for category_key, pieces in categorized_lore.items():
            if pieces:
                category_info = self.lore_categories[category_key]
                builder.button(
                    text=f"{category_info['icon']} {category_info['name']} ({len(pieces)})",
                    callback_data=f"mochila:category:{category_key}"
                )
        
        # Fila separadora
        builder.row()
        
        # Opciones especiales
        if total_pieces >= 3:
            builder.button(
                text="🔗 Buscar Conexiones",
                callback_data="mochila:find_connections"
            )
        
        if total_pieces >= 5:
            builder.button(
                text="🧩 Análisis Profundo",
                callback_data="mochila:deep_analysis"
            )
        
        # Fila separadora
        builder.row()
        
        # Vista completa y navegación
        builder.button(
            text="📜 Ver Todas las Pistas",
            callback_data="mochila:view_all"
        )
        
        builder.button(
            text="🔍 Buscar Pista",
            callback_data="mochila:search"
        )
        
        # Fila final
        builder.row()
        builder.button(
            text="⬅️ Menú Principal",
            callback_data="diana:back_to_main"
        )
        
        return builder.as_markup()
    
    async def show_category_view(self, callback: CallbackQuery, category_key: str) -> None:
        """Muestra pistas de una categoría específica."""
        user_id = callback.from_user.id
        
        try:
            lore_pieces = await self.narrative_service.get_user_lore_pieces(user_id)
            categorized_lore = self._categorize_lore_pieces(lore_pieces)
            
            category_pieces = categorized_lore.get(category_key, [])
            
            if not category_pieces:
                await callback.answer("Esta categoría está vacía", show_alert=True)
                return
            
            category_info = self.lore_categories[category_key]
            
            # Generar respuesta contextual de Diana para la categoría
            diana_response = await self.diana_system.generate_contextual_response(
                user_id=user_id,
                context_type='category_exploration',
                context_data={
                    'category': category_info['name'],
                    'pieces_count': len(category_pieces)
                }
            )
            
            # Construir mensaje de categoría
            category_message = (
                f"{category_info['icon']} **{category_info['name']}**\n\n"
                f"💫 *Diana comenta:* \"{diana_response}\"\n\n"
                f"📊 **{len(category_pieces)} pistas en esta categoría:**\n\n"
            )
            
            # Mostrar pistas de la categoría con detalles
            for i, piece in enumerate(category_pieces[:5], 1):  # Mostrar máximo 5
                rarity = self._determine_piece_rarity(piece)
                category_message += (
                    f"{rarity['icon']} **{piece['title']}**\n"
                    f"📅 _{piece['unlocked_at'][:10]}_\n"
                    f"🔹 {piece['description'][:80]}{'...' if len(piece['description']) > 80 else ''}\n\n"
                )
            
            if len(category_pieces) > 5:
                category_message += f"... y **{len(category_pieces) - 5}** pistas más\n\n"
            
            # Crear keyboard para la categoría
            keyboard = self._create_category_keyboard(category_key, category_pieces)
            
            await callback.message.edit_text(
                category_message,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
            
            await callback.answer()
        
        except Exception as e:
            logger.error(f"Error mostrando categoría {category_key}: {e}")
            await callback.answer("Error al cargar categoría", show_alert=True)
    
    def _create_category_keyboard(self, 
                                category_key: str, 
                                pieces: List[Dict]) -> InlineKeyboardMarkup:
        """Crea keyboard para vista de categoría."""
        builder = InlineKeyboardBuilder()
        
        # Botones para pistas individuales (primeras 6)
        for piece in pieces[:6]:
            rarity = self._determine_piece_rarity(piece)
            builder.button(
                text=f"{rarity['icon']} {piece['title'][:20]}",
                callback_data=f"mochila:piece:{piece['key']}"
            )
        
        # Si hay más pistas, botón para ver todas
        if len(pieces) > 6:
            builder.row()
            builder.button(
                text=f"📜 Ver todas ({len(pieces)})",
                callback_data=f"mochila:category_full:{category_key}"
            )
        
        # Fila de opciones especiales
        builder.row()
        if len(pieces) >= 2:
            builder.button(
                text="🔗 Conectar en Categoría",
                callback_data=f"mochila:connect_category:{category_key}"
            )
        
        # Navegación
        builder.row()
        builder.button(
            text="⬅️ Volver a Mochila",
            callback_data="mochila:back_to_hub"
        )
        
        return builder.as_markup()
    
    async def show_piece_detail(self, callback: CallbackQuery, piece_key: str) -> None:
        """Muestra detalles completos de una pista específica."""
        user_id = callback.from_user.id
        
        try:
            lore_pieces = await self.narrative_service.get_user_lore_pieces(user_id)
            piece = next((p for p in lore_pieces if p['key'] == piece_key), None)
            
            if not piece:
                await callback.answer("Pista no encontrada", show_alert=True)
                return
            
            # Generar respuesta contextual de Diana para la pista específica
            diana_response = await self.diana_system.generate_contextual_response(
                user_id=user_id,
                context_type='piece_examination',
                context_data={
                    'piece_title': piece['title'],
                    'piece_source': piece['source']
                }
            )
            
            # Determinar rareza y conexiones
            rarity = self._determine_piece_rarity(piece)
            connections = await self._find_piece_connections(user_id, piece_key)
            
            # Construir mensaje detallado
            detail_message = (
                f"{rarity['icon']} **{piece['title']}**\n"
                f"✨ *{rarity['name']}*\n\n"
                f"📜 **Descripción completa:**\n"
                f"_{piece['description']}_\n\n"
                f"📊 **Detalles:**\n"
                f"🔹 Obtenida: {self._format_unlock_source(piece['source'])}\n"
                f"📅 Fecha: {piece['unlocked_at'][:10]}\n"
            )
            
            if connections:
                detail_message += f"🔗 Conexiones: **{len(connections)}** pistas relacionadas\n"
            
            detail_message += f"\n💫 *Diana examina la pista:*\n\"{diana_response}\""
            
            # Crear keyboard detallado
            keyboard = self._create_piece_detail_keyboard(piece_key, connections)
            
            await callback.message.edit_text(
                detail_message,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
            
            await callback.answer()
        
        except Exception as e:
            logger.error(f"Error mostrando detalle de pista {piece_key}: {e}")
            await callback.answer("Error al cargar detalles", show_alert=True)
    
    def _create_piece_detail_keyboard(self, 
                                    piece_key: str, 
                                    connections: List[str]) -> InlineKeyboardMarkup:
        """Crea keyboard para detalles de pista."""
        builder = InlineKeyboardBuilder()
        
        # Opciones de conexión
        if connections:
            builder.button(
                text=f"🔗 Ver Conexiones ({len(connections)})",
                callback_data=f"mochila:connections:{piece_key}"
            )
        
        # Análisis profundo de la pista
        builder.button(
            text="🔍 Análisis Profundo",
            callback_data=f"mochila:analyze:{piece_key}"
        )
        
        # Usar en historia (si aplica)
        builder.button(
            text="📖 Usar en Historia",
            callback_data=f"mochila:use_in_story:{piece_key}"
        )
        
        # Navegación
        builder.row()
        builder.button(
            text="⬅️ Volver a Mochila",
            callback_data="mochila:back_to_hub"
        )
        
        return builder.as_markup()
    
    async def find_connections(self, callback: CallbackQuery) -> None:
        """Busca y muestra conexiones entre pistas."""
        user_id = callback.from_user.id
        
        try:
            lore_pieces = await self.narrative_service.get_user_lore_pieces(user_id)
            
            if len(lore_pieces) < 2:
                await callback.answer("Necesitas al menos 2 pistas para buscar conexiones", show_alert=True)
                return
            
            # Buscar todas las conexiones posibles
            all_connections = await self._discover_all_connections(user_id, lore_pieces)
            
            # Generar respuesta de Diana
            diana_response = await self.diana_system.generate_contextual_response(
                user_id=user_id,
                context_type='connection_discovery',
                context_data={
                    'connections_found': len(all_connections),
                    'total_pieces': len(lore_pieces)
                }
            )
            
            # Construir mensaje de conexiones
            connections_message = (
                "🔗 **Red de Conexiones**\n\n"
                f"💫 *Diana analiza tus pistas:*\n\"{diana_response}\"\n\n"
                f"🧩 **{len(all_connections)} conexiones descubiertas:**\n\n"
            )
            
            # Mostrar conexiones más interesantes
            for i, connection in enumerate(all_connections[:5], 1):
                connections_message += (
                    f"{i}. **{connection['title']}**\n"
                    f"   🔸 {connection['description']}\n"
                    f"   📎 Conecta: {', '.join(connection['pieces'])}\n\n"
                )
            
            if len(all_connections) > 5:
                connections_message += f"... y **{len(all_connections) - 5}** conexiones más por descubrir\n\n"
            
            # Keyboard para conexiones
            keyboard = InlineKeyboardBuilder()
            keyboard.button(
                text="📊 Ver Mapa Completo",
                callback_data="mochila:connection_map"
            )
            keyboard.button(
                text="🎯 Análisis IA",
                callback_data="mochila:ai_analysis"
            )
            keyboard.row()
            keyboard.button(
                text="⬅️ Volver a Mochila",
                callback_data="mochila:back_to_hub"
            )
            
            await callback.message.edit_text(
                connections_message,
                parse_mode="Markdown",
                reply_markup=keyboard.as_markup()
            )
            
            await callback.answer()
        
        except Exception as e:
            logger.error(f"Error buscando conexiones: {e}")
            await callback.answer("Error al buscar conexiones", show_alert=True)
    
    def _categorize_lore_pieces(self, lore_pieces: List[Dict]) -> Dict[str, List[Dict]]:
        """Categoriza las pistas según palabras clave."""
        categorized = {category: [] for category in self.lore_categories.keys()}
        
        for piece in lore_pieces:
            # Analizar título y descripción para categorizar
            text_to_analyze = f"{piece['title']} {piece['description']}".lower()
            
            # Buscar en cada categoría
            best_category = 'mysteries'  # Categoría por defecto
            best_match_count = 0
            
            for category_key, category_info in self.lore_categories.items():
                match_count = sum(1 for keyword in category_info['keywords'] 
                                if keyword in text_to_analyze)
                
                if match_count > best_match_count:
                    best_match_count = match_count
                    best_category = category_key
            
            categorized[best_category].append(piece)
        
        return categorized
    
    def _determine_piece_rarity(self, piece: Dict) -> Dict[str, str]:
        """Determina la rareza de una pista basada en varios factores."""
        source = piece.get('source', 'unknown')
        title_length = len(piece.get('title', ''))
        desc_length = len(piece.get('description', ''))
        
        # Sistema de rareza basado en fuente y complejidad
        if source == 'level_up' or 'secreto' in piece.get('title', '').lower():
            return {'name': 'Legendary', 'icon': '⭐'}
        elif source == 'mission' or desc_length > 100:
            return {'name': 'Epic', 'icon': '💎'}
        elif source == 'reaction' or title_length > 20:
            return {'name': 'Rare', 'icon': '🔮'}
        else:
            return {'name': 'Common', 'icon': '📝'}
    
    async def _find_piece_connections(self, user_id: int, piece_key: str) -> List[str]:
        """Encuentra conexiones para una pista específica."""
        # Implementación simplificada - en la realidad sería más compleja
        lore_pieces = await self.narrative_service.get_user_lore_pieces(user_id)
        
        target_piece = next((p for p in lore_pieces if p['key'] == piece_key), None)
        if not target_piece:
            return []
        
        connections = []
        target_words = set(target_piece['title'].lower().split() + 
                         target_piece['description'].lower().split())
        
        for piece in lore_pieces:
            if piece['key'] == piece_key:
                continue
                
            piece_words = set(piece['title'].lower().split() + 
                            piece['description'].lower().split())
            
            # Si comparten palabras significativas, hay conexión
            common_words = target_words.intersection(piece_words)
            if len(common_words) >= 2:  # Al menos 2 palabras en común
                connections.append(piece['key'])
        
        return connections
    
    async def _discover_all_connections(self, user_id: int, lore_pieces: List[Dict]) -> List[Dict]:
        """Descubre todas las conexiones posibles entre pistas."""
        connections = []
        
        # Patrones de conexión predefinidos
        connection_patterns = {
            'character_connection': {
                'title': 'Conexión de Personaje',
                'description': 'Estas pistas revelan aspectos del mismo personaje',
                'keywords': ['diana', 'lucien']
            },
            'location_connection': {
                'title': 'Conexión de Lugar',
                'description': 'Estas pistas están relacionadas con el mismo lugar',
                'keywords': ['club', 'lugar', 'sala']
            },
            'temporal_connection': {
                'title': 'Conexión Temporal',
                'description': 'Estas pistas ocurrieron en secuencia temporal',
                'keywords': ['antes', 'después', 'entonces']
            }
        }
        
        # Buscar patrones en las pistas
        for pattern_key, pattern_info in connection_patterns.items():
            matching_pieces = []
            
            for piece in lore_pieces:
                text = f"{piece['title']} {piece['description']}".lower()
                if any(keyword in text for keyword in pattern_info['keywords']):
                    matching_pieces.append(piece['title'])
            
            if len(matching_pieces) >= 2:
                connections.append({
                    'title': pattern_info['title'],
                    'description': pattern_info['description'],
                    'pieces': matching_pieces[:3]  # Máximo 3 piezas por conexión
                })
        
        return connections
    
    def _count_user_connections(self, user_id: int) -> int:
        """Cuenta las conexiones descubiertas por el usuario."""
        return len(self.discovered_connections.get(user_id, {}))
    
    def _format_unlock_source(self, source: str) -> str:
        """Formatea la fuente de desbloqueo de manera legible."""
        source_mapping = {
            'reaction': '👍 Reacción en canal',
            'mission': '🎯 Misión completada',
            'daily': '🎁 Regalo diario',
            'trivia': '🧠 Respuesta correcta',
            'purchase': '🛒 Compra en tienda',
            'level_up': '⬆️ Subida de nivel',
            'exploration': '🔍 Exploración profunda'
        }
        return source_mapping.get(source, source.title())


# Los handlers están integrados en el sistema principal
# No necesitamos registro separado