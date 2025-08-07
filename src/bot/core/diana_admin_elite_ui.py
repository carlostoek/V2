"""
🚀 DIANA ADMIN ELITE UI SYSTEM
==============================

Silicon Valley-grade UI components and design patterns for Diana Admin.
Elegant, responsive, and blazingly fast user interfaces.

Author: The Most Epic Silicon Valley Developer
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import json
import structlog

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

logger = structlog.get_logger()

# === ELITE UI THEME SYSTEM ===

class UITheme(Enum):
    """Elite UI themes for different contexts"""
    EXECUTIVE = "executive"  # Dark, professional
    VIBRANT = "vibrant"     # Colorful, energetic  
    MINIMAL = "minimal"     # Clean, focused
    GAMING = "gaming"       # Playful, gamified

@dataclass
class UIStyle:
    """UI styling configuration"""
    primary_emoji: str
    secondary_emoji: str
    accent_emoji: str
    separator: str
    header_style: str
    bullet_style: str
    success_color: str = "🟢"
    warning_color: str = "🟡"
    error_color: str = "🔴"
    info_color: str = "🔵"

# === THEME DEFINITIONS ===
THEMES = {
    UITheme.EXECUTIVE: UIStyle(
        primary_emoji="⭐",
        secondary_emoji="▫️",
        accent_emoji="🔹",
        separator="━" * 40,
        header_style="🎭",
        bullet_style="▪️"
    ),
    UITheme.VIBRANT: UIStyle(
        primary_emoji="✨",
        secondary_emoji="🌟",
        accent_emoji="💫",
        separator="═" * 40,
        header_style="🎨",
        bullet_style="🔸"
    ),
    UITheme.MINIMAL: UIStyle(
        primary_emoji="◦",
        secondary_emoji="·",
        accent_emoji="→",
        separator="─" * 40,
        header_style="□",
        bullet_style="•"
    ),
    UITheme.GAMING: UIStyle(
        primary_emoji="🎮",
        secondary_emoji="🕹️",
        accent_emoji="⚡",
        separator="▬" * 40,
        header_style="👾",
        bullet_style="🔹"
    )
}

# === ELITE UI COMPONENTS ===

class UIComponent:
    """Base class for all UI components"""
    
    def __init__(self, theme: UITheme = UITheme.EXECUTIVE):
        self.theme = theme
        self.style = THEMES[theme]
    
    def render(self) -> str:
        """Render component to string"""
        raise NotImplementedError

class HeaderComponent(UIComponent):
    """Elite header with animations and styling"""
    
    def __init__(self, title: str, subtitle: str = None, level: int = 1, theme: UITheme = UITheme.EXECUTIVE, animated: bool = True):
        super().__init__(theme)
        self.title = title
        self.subtitle = subtitle
        self.level = level
        self.animated = animated
    
    def render(self) -> str:
        """Render elegant header"""
        style = self.style
        
        if self.level == 1:
            # Main header with full styling
            header = f"{style.header_style} **{self.title.upper()}** {style.header_style}\n"
            if self.subtitle:
                header += f"{style.accent_emoji} _{self.subtitle}_\n"
            header += f"{style.separator}\n"
            
        elif self.level == 2:
            # Section header
            header = f"\n{style.primary_emoji} **{self.title}**\n"
            if self.subtitle:
                header += f"{style.secondary_emoji} {self.subtitle}\n"
                
        else:
            # Subsection header
            header = f"\n{style.accent_emoji} {self.title}"
            if self.subtitle:
                header += f" • {self.subtitle}"
            header += "\n"
        
        return header

class StatsCardComponent(UIComponent):
    """Elegant statistics card with visual indicators"""
    
    def __init__(self, title: str, stats: Dict[str, Any], theme: UITheme = UITheme.EXECUTIVE, compact: bool = False):
        super().__init__(theme)
        self.title = title
        self.stats = stats
        self.compact = compact
    
    def _format_stat_value(self, key: str, value: Any) -> str:
        """Format stat value with smart formatting"""
        if isinstance(value, (int, float)):
            if value >= 1000000:
                return f"{value/1000000:.1f}M"
            elif value >= 1000:
                return f"{value/1000:.1f}K"
            else:
                return str(value)
        elif isinstance(value, bool):
            return "✅" if value else "❌"
        elif isinstance(value, str):
            if len(value) > 20:
                return value[:17] + "..."
            return value
        else:
            return str(value)
    
    def _get_trend_indicator(self, key: str, value: Any) -> str:
        """Get trend indicator for metrics"""
        trend_indicators = {
            'users': '👥',
            'revenue': '💰',
            'points': '⭐',
            'active': '🔥',
            'growth': '📈',
            'conversion': '🎯',
            'engagement': '💫',
            'retention': '🔄'
        }
        
        for keyword, indicator in trend_indicators.items():
            if keyword in key.lower():
                return indicator
        
        return self.style.accent_emoji
    
    def render(self) -> str:
        """Render elegant stats card"""
        style = self.style
        
        if self.compact:
            # Compact horizontal layout
            stats_line = []
            for key, value in self.stats.items():
                formatted_value = self._format_stat_value(key, value)
                indicator = self._get_trend_indicator(key, value)
                stats_line.append(f"{indicator} {formatted_value}")
            
            return f"{style.primary_emoji} **{self.title}**\n{' • '.join(stats_line)}\n"
        
        else:
            # Full card layout
            card = f"\n{style.primary_emoji} **{self.title}**\n"
            card += f"{style.separator[:20]}\n"
            
            for key, value in self.stats.items():
                formatted_value = self._format_stat_value(key, value)
                indicator = self._get_trend_indicator(key, value)
                key_display = key.replace('_', ' ').title()
                card += f"{indicator} {key_display}: **{formatted_value}**\n"
            
            return card

class NavigationComponent(UIComponent):
    """Elite navigation with breadcrumbs and shortcuts"""
    
    def __init__(self, breadcrumbs: List[str], current_section: str = None, theme: UITheme = UITheme.EXECUTIVE):
        super().__init__(theme)
        self.breadcrumbs = breadcrumbs
        self.current_section = current_section
    
    def render(self) -> str:
        """Render elegant navigation breadcrumbs"""
        if not self.breadcrumbs:
            return ""
        
        style = self.style
        nav = f"\n{style.secondary_emoji} "
        nav += f" {style.accent_emoji} ".join(self.breadcrumbs)
        
        if self.current_section:
            nav += f" {style.accent_emoji} **{self.current_section}**"
        
        nav += "\n"
        return nav

class ActionGridComponent(UIComponent):
    """Elite action grid with smart layout"""
    
    def __init__(self, actions: List[Dict[str, str]], columns: int = 2, theme: UITheme = UITheme.EXECUTIVE):
        super().__init__(theme)
        self.actions = actions
        self.columns = columns
    
    def create_keyboard(self) -> InlineKeyboardMarkup:
        """Create elegant inline keyboard grid"""
        buttons = []
        row = []
        
        for i, action in enumerate(self.actions):
            button = InlineKeyboardButton(
                text=action["text"],
                callback_data=action["callback"]
            )
            row.append(button)
            
            # Create new row when reaching column limit or at end
            if len(row) == self.columns or i == len(self.actions) - 1:
                buttons.append(row)
                row = []
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)

class AlertComponent(UIComponent):
    """Elite alert component with different severity levels"""
    
    def __init__(self, message: str, alert_type: str = "info", title: str = None, theme: UITheme = UITheme.EXECUTIVE):
        super().__init__(theme)
        self.message = message
        self.alert_type = alert_type
        self.title = title
    
    def render(self) -> str:
        """Render styled alert"""
        style = self.style
        
        alert_icons = {
            "success": style.success_color,
            "warning": style.warning_color,
            "error": style.error_color,
            "info": style.info_color
        }
        
        icon = alert_icons.get(self.alert_type, style.info_color)
        
        alert = f"\n{icon} "
        if self.title:
            alert += f"**{self.title}**\n{style.bullet_style} "
        
        alert += f"{self.message}\n"
        return alert

class ProgressComponent(UIComponent):
    """Elite progress indicator with visual bars"""
    
    def __init__(self, label: str, current: int, total: int, theme: UITheme = UITheme.EXECUTIVE):
        super().__init__(theme)
        self.label = label
        self.current = current
        self.total = total
    
    def render(self) -> str:
        """Render progress bar"""
        if self.total == 0:
            percentage = 0
        else:
            percentage = (self.current / self.total) * 100
        
        # Create visual progress bar
        bar_length = 20
        filled_length = int(bar_length * percentage / 100)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        
        return f"{self.style.accent_emoji} **{self.label}**\n{bar} {percentage:.1f}% ({self.current}/{self.total})\n"

# === ELITE UI BUILDER ===

class EliteUIBuilder:
    """Silicon Valley-grade UI builder with fluent interface"""
    
    def __init__(self, theme: UITheme = UITheme.EXECUTIVE):
        self.theme = theme
        self.components = []
        self.keyboard_actions = []
    
    def header(self, title: str, subtitle: str = None, level: int = 1, animated: bool = True):
        """Add elegant header"""
        self.components.append(HeaderComponent(title, subtitle, level, self.theme, animated))
        return self
    
    def stats_card(self, title: str, stats: Dict[str, Any], compact: bool = False):
        """Add stats card"""
        self.components.append(StatsCardComponent(title, stats, self.theme, compact))
        return self
    
    def navigation(self, breadcrumbs: List[str], current_section: str = None):
        """Add navigation breadcrumbs"""
        self.components.append(NavigationComponent(breadcrumbs, current_section, self.theme))
        return self
    
    def alert(self, message: str, alert_type: str = "info", title: str = None):
        """Add alert"""
        self.components.append(AlertComponent(message, alert_type, title, self.theme))
        return self
    
    def progress(self, label: str, current: int, total: int):
        """Add progress indicator"""
        self.components.append(ProgressComponent(label, current, total, self.theme))
        return self
    
    def actions(self, actions: List[Dict[str, str]], columns: int = 2):
        """Add action grid"""
        self.keyboard_actions = actions
        self.columns = columns
        return self
    
    def build(self) -> Tuple[str, Optional[InlineKeyboardMarkup]]:
        """Build final UI"""
        # Render all components
        text = ""
        for component in self.components:
            text += component.render()
        
        # Create keyboard if actions exist
        keyboard = None
        if self.keyboard_actions:
            action_grid = ActionGridComponent(self.keyboard_actions, self.columns, self.theme)
            keyboard = action_grid.create_keyboard()
        
        return text.strip(), keyboard

# === PERFORMANCE UTILITIES ===

class UICache:
    """Smart UI caching for performance"""
    
    def __init__(self):
        self.cache = {}
        self.timestamps = {}
        self.ttl = 300  # 5 minutes default TTL
    
    def get(self, key: str) -> Optional[Tuple[str, InlineKeyboardMarkup]]:
        """Get cached UI"""
        if key not in self.cache:
            return None
        
        if datetime.now().timestamp() - self.timestamps[key] > self.ttl:
            del self.cache[key]
            del self.timestamps[key]
            return None
        
        return self.cache[key]
    
    def set(self, key: str, ui: Tuple[str, InlineKeyboardMarkup], ttl: int = None):
        """Cache UI"""
        self.cache[key] = ui
        self.timestamps[key] = datetime.now().timestamp()
        if ttl:
            # Custom TTL for this item
            pass
    
    def invalidate(self, pattern: str = None):
        """Invalidate cache entries"""
        if pattern:
            keys_to_remove = [k for k in self.cache.keys() if pattern in k]
            for key in keys_to_remove:
                del self.cache[key]
                del self.timestamps[key]
        else:
            self.cache.clear()
            self.timestamps.clear()

# Global UI cache instance
ui_cache = UICache()

# === QUICK BUILDERS FOR COMMON PATTERNS ===

def build_dashboard_ui(title: str, overview_stats: Dict[str, Any], detailed_stats: List[Dict[str, Any]], 
                      actions: List[Dict[str, str]], breadcrumbs: List[str] = None, 
                      theme: UITheme = UITheme.EXECUTIVE) -> Tuple[str, InlineKeyboardMarkup]:
    """Quick builder for dashboard UIs"""
    
    builder = EliteUIBuilder(theme)
    builder.header(title, "Real-time Dashboard", level=1, animated=True)
    
    if breadcrumbs:
        builder.navigation(breadcrumbs)
    
    # Overview stats card
    if overview_stats:
        builder.stats_card("System Overview", overview_stats, compact=True)
    
    # Detailed stats
    for stat_group in detailed_stats:
        if "title" in stat_group and "stats" in stat_group:
            builder.stats_card(stat_group["title"], stat_group["stats"])
    
    # Actions
    if actions:
        builder.actions(actions, columns=2)
    
    return builder.build()

def build_menu_ui(title: str, sections: List[Dict[str, Any]], breadcrumbs: List[str] = None,
                 theme: UITheme = UITheme.EXECUTIVE) -> Tuple[str, InlineKeyboardMarkup]:
    """Quick builder for menu UIs"""
    
    builder = EliteUIBuilder(theme)
    builder.header(title, "Administrative Control Center", level=1)
    
    if breadcrumbs:
        builder.navigation(breadcrumbs)
    
    # Convert sections to actions
    actions = []
    for section in sections:
        actions.append({
            "text": f"{section.get('icon', '▫️')} {section.get('title', 'Section')}",
            "callback": section.get('callback', 'admin:main')
        })
    
    builder.actions(actions, columns=2)
    
    return builder.build()

def build_stats_ui(title: str, stats_groups: List[Dict[str, Any]], actions: List[Dict[str, str]] = None,
                  breadcrumbs: List[str] = None, theme: UITheme = UITheme.EXECUTIVE) -> Tuple[str, InlineKeyboardMarkup]:
    """Quick builder for statistics UIs"""
    
    builder = EliteUIBuilder(theme)
    builder.header(title, "Advanced Analytics", level=1)
    
    if breadcrumbs:
        builder.navigation(breadcrumbs)
    
    # Add all stats groups
    for group in stats_groups:
        if "title" in group and "stats" in group:
            builder.stats_card(group["title"], group["stats"])
    
    # Add actions if provided
    if actions:
        builder.actions(actions, columns=2)
    
    return builder.build()

# === THEME SWITCHER ===

class ThemeManager:
    """Manage UI themes dynamically"""
    
    def __init__(self):
        self.user_themes = {}  # user_id -> theme
        self.default_theme = UITheme.EXECUTIVE
    
    def set_user_theme(self, user_id: int, theme: UITheme):
        """Set theme for specific user"""
        self.user_themes[user_id] = theme
        logger.info("Theme updated", user_id=user_id, theme=theme.value)
    
    def get_user_theme(self, user_id: int) -> UITheme:
        """Get theme for user"""
        return self.user_themes.get(user_id, self.default_theme)
    
    def get_theme_options(self) -> List[Dict[str, str]]:
        """Get available theme options"""
        return [
            {"text": "🎭 Executive", "callback": "admin:theme:executive"},
            {"text": "🎨 Vibrant", "callback": "admin:theme:vibrant"},
            {"text": "□ Minimal", "callback": "admin:theme:minimal"},
            {"text": "👾 Gaming", "callback": "admin:theme:gaming"}
        ]

# Global theme manager
theme_manager = ThemeManager()