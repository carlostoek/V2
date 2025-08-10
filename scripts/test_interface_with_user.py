#!/usr/bin/env python3
"""
🎭 DIANA INTERFACE TESTER - Dynamic User Testing
================================================

Script para probar las interfaces dinámicas de Diana inyectando IDs específicos.
Muestra exactamente la misma interfaz que vería cada usuario según su perfil.

Funcionalidades:
- Inyectar cualquier ID de usuario y ver su interfaz
- Probar tanto interfaz de usuario como de admin
- Ver cómo cambian las interfaces según el perfil del usuario
- Mostrar el contexto completo que Diana detecta
- Comparar interfaces entre diferentes usuarios
"""

import asyncio
import sys
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any
import glob

# Add project root to path
sys.path.append(os.path.abspath('.'))

from src.core.event_bus import EventBus
from src.modules.gamification.service import GamificationService
from src.modules.narrative.service import NarrativeService
from src.modules.user.service import UserService
from src.modules.admin.service import AdminService
from src.modules.tariff.service import TariffService
from src.modules.daily_rewards.service import DailyRewardsService
from src.bot.database.engine import init_db

# Import Diana systems
from src.bot.core.diana_master_system import initialize_diana_master
from src.bot.core.diana_admin_master import initialize_diana_admin_master
from src.bot.core.diana_user_master_system import initialize_diana_user_system

class DianaInterfaceTester:
    """🎭 Tester de interfaces dinámicas de Diana"""
    
    def __init__(self):
        self.services = {}
        self.diana_systems = {}
        self.available_users = []
    
    async def setup_diana_ecosystem(self):
        """Configurar todo el ecosistema Diana"""
        print("🎭 Configurando ecosistema Diana completo...")
        
        # Initialize database
        await init_db()
        
        # Create services
        event_bus = EventBus()
        user_service = UserService(event_bus)
        gamification_service = GamificationService(event_bus)
        narrative_service = NarrativeService(event_bus)
        admin_service = AdminService(event_bus)
        tariff_service = TariffService(event_bus)
        daily_rewards_service = DailyRewardsService(gamification_service)
        
        # Setup services
        await user_service.setup()
        await gamification_service.setup()
        await narrative_service.setup()
        await admin_service.setup()
        await tariff_service.setup()
        await daily_rewards_service.setup()
        
        # Services dictionary
        self.services = {
            'gamification': gamification_service,
            'admin': admin_service,
            'narrative': narrative_service,
            'user': user_service,
            'tariff': tariff_service,
            'event_bus': event_bus,
            'daily_rewards': daily_rewards_service
        }
        
        # Initialize Diana systems
        self.diana_systems = {
            'master': initialize_diana_master(self.services),
            'admin': initialize_diana_admin_master(self.services),
            'user': initialize_diana_user_system(self.services)
        }
        
        print("✅ Ecosistema Diana configurado correctamente!")
    
    async def load_available_users(self):
        """Cargar usuarios disponibles desde archivos generados"""
        users = []
        
        # Buscar archivos de usuarios generados
        data_files = glob.glob("scripts/generated_data/random_users_*.json")
        
        if data_files:
            # Cargar el archivo más reciente
            latest_file = max(data_files, key=os.path.getctime)
            
            try:
                with open(latest_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    users.extend(data)
                
                print(f"📁 Cargados {len(users)} usuarios desde {latest_file}")
            except Exception as e:
                print(f"⚠️ Error cargando archivo {latest_file}: {e}")
        
        # Agregar usuarios de ejemplo si no hay datos
        if not users:
            users = [
                {"user_id": 12345, "username": "demo_user", "level": 3, "points": 450, "is_vip": False},
                {"user_id": 67890, "username": "vip_user", "level": 6, "points": 1200, "is_vip": True},
                {"user_id": 11111, "username": "newbie", "level": 1, "points": 25, "is_vip": False},
                {"user_id": 99999, "username": "admin_test", "level": 10, "points": 5000, "is_vip": True}
            ]
            print(f"🎭 Usando {len(users)} usuarios de ejemplo")
        
        self.available_users = users
        return users
    
    async def get_user_context_analysis(self, user_id: int) -> Dict[str, Any]:
        """Obtener análisis completo del contexto de usuario"""
        analysis = {
            "basic_stats": {},
            "diana_context": {},
            "admin_context": {},
            "interface_predictions": {}
        }
        
        try:
            # Stats básicos de gamificación
            if 'gamification' in self.services:
                stats = await self.services['gamification'].get_user_stats(user_id)
                analysis["basic_stats"] = stats
        
            # Contexto de Diana Master (con mood detection)
            if self.diana_systems.get('master'):
                try:
                    context = await self.diana_systems['master'].context_engine.analyze_user_context(user_id)
                    analysis["diana_context"] = {
                        "mood": context.current_mood.value if hasattr(context.current_mood, 'value') else str(context.current_mood),
                        "engagement_pattern": context.engagement_pattern,
                        "personalization_score": context.personalization_score,
                        "narrative_progress": context.narrative_progress,
                        "gamification_engagement": context.gamification_engagement
                    }
                except Exception as e:
                    analysis["diana_context"] = {"error": str(e)}
            
            # Contexto de Diana User (con tier detection)
            if self.diana_systems.get('user'):
                try:
                    user_context = await self.diana_systems['user'].get_user_context(user_id)
                    analysis["user_context"] = {
                        "tier": user_context.tier.value if hasattr(user_context.tier, 'value') else str(user_context.tier),
                        "mood": user_context.mood.value if hasattr(user_context.mood, 'value') else str(user_context.mood),
                        "narrative_level": user_context.narrative_level,
                        "intimacy_level": user_context.intimacy_level,
                        "conversion_signals": user_context.conversion_signals
                    }
                except Exception as e:
                    analysis["user_context"] = {"error": str(e)}
            
            # Permisos de admin
            if self.diana_systems.get('admin'):
                try:
                    is_admin = await self.diana_systems['admin'].check_admin_permission(user_id)
                    if is_admin:
                        permission_level = await self.diana_systems['admin'].get_admin_permission_level(user_id)
                        analysis["admin_context"] = {
                            "is_admin": True,
                            "permission_level": permission_level.value if hasattr(permission_level, 'value') else str(permission_level)
                        }
                    else:
                        analysis["admin_context"] = {"is_admin": False}
                except Exception as e:
                    analysis["admin_context"] = {"error": str(e)}
        
        except Exception as e:
            analysis["error"] = str(e)
        
        return analysis
    
    async def generate_user_interface(self, user_id: int) -> Dict[str, Any]:
        """Generar la interfaz que vería un usuario específico"""
        result = {
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "interfaces": {},
            "context": {}
        }
        
        try:
            # Análisis de contexto
            result["context"] = await self.get_user_context_analysis(user_id)
            
            # Interface de usuario (sistema principal)
            if self.diana_systems.get('user'):
                try:
                    text, keyboard = await self.diana_systems['user'].create_user_main_interface(user_id)
                    result["interfaces"]["user_main"] = {
                        "text": text,
                        "keyboard_buttons": self._extract_keyboard_buttons(keyboard),
                        "text_length": len(text),
                        "has_keyboard": keyboard is not None
                    }
                except Exception as e:
                    result["interfaces"]["user_main"] = {"error": str(e)}
            
            # Interface de admin (si tiene permisos)
            if self.diana_systems.get('admin'):
                try:
                    text, keyboard = await self.diana_systems['admin'].create_admin_main_interface(user_id)
                    result["interfaces"]["admin_main"] = {
                        "text": text,
                        "keyboard_buttons": self._extract_keyboard_buttons(keyboard),
                        "text_length": len(text),
                        "has_keyboard": keyboard is not None
                    }
                except Exception as e:
                    result["interfaces"]["admin_main"] = {"error": str(e)}
            
            # Interface adaptativa del master system
            if self.diana_systems.get('master'):
                try:
                    text, keyboard = await self.diana_systems['master'].create_adaptive_interface(user_id, "test")
                    result["interfaces"]["master_adaptive"] = {
                        "text": text,
                        "keyboard_buttons": self._extract_keyboard_buttons(keyboard),
                        "text_length": len(text),
                        "has_keyboard": keyboard is not None
                    }
                except Exception as e:
                    result["interfaces"]["master_adaptive"] = {"error": str(e)}
        
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _extract_keyboard_buttons(self, keyboard) -> list:
        """Extraer texto de botones del teclado para análisis"""
        if not keyboard or not hasattr(keyboard, 'inline_keyboard'):
            return []
        
        buttons = []
        for row in keyboard.inline_keyboard:
            row_buttons = []
            for button in row:
                row_buttons.append({
                    "text": button.text,
                    "callback_data": button.callback_data
                })
            buttons.append(row_buttons)
        
        return buttons
    
    def display_interface_preview(self, interface_data: Dict[str, Any]):
        """Mostrar preview de la interfaz generada"""
        user_id = interface_data["user_id"]
        context = interface_data.get("context", {})
        interfaces = interface_data.get("interfaces", {})
        
        print(f"\n{'='*80}")
        print(f"🎭 INTERFAZ DINÁMICA PARA USUARIO ID: {user_id}")
        print(f"{'='*80}")
        
        # Mostrar contexto detectado
        if "basic_stats" in context:
            stats = context["basic_stats"]
            print(f"📊 STATS BÁSICOS:")
            print(f"   Nivel: {stats.get('level', 'N/A')} | Puntos: {stats.get('points', 'N/A')} | Racha: {stats.get('streak', 'N/A')}")
        
        if "diana_context" in context and "error" not in context["diana_context"]:
            diana_ctx = context["diana_context"]
            print(f"🎭 CONTEXTO DIANA:")
            print(f"   Mood: {diana_ctx.get('mood', 'N/A')} | Engagement: {diana_ctx.get('engagement_pattern', 'N/A')}")
            print(f"   Personalización: {diana_ctx.get('personalization_score', 0):.2f} | Narrativa: {diana_ctx.get('narrative_progress', 0):.1f}%")
        
        if "user_context" in context and "error" not in context["user_context"]:
            user_ctx = context["user_context"]
            print(f"👤 CONTEXTO USUARIO:")
            print(f"   Tier: {user_ctx.get('tier', 'N/A')} | Mood: {user_ctx.get('mood', 'N/A')}")
            print(f"   Intimidad: {user_ctx.get('intimacy_level', 0):.2f} | Conversión: {user_ctx.get('conversion_signals', 0)}")
        
        if "admin_context" in context:
            admin_ctx = context["admin_context"]
            if admin_ctx.get("is_admin"):
                print(f"👑 ADMIN: Sí ({admin_ctx.get('permission_level', 'N/A')})")
            else:
                print(f"👤 ADMIN: No")
        
        print(f"\n{'─'*80}")
        
        # Mostrar interfaces
        for interface_name, interface_data in interfaces.items():
            if "error" in interface_data:
                print(f"❌ {interface_name.upper()}: Error - {interface_data['error']}")
                continue
                
            print(f"🎪 INTERFAZ {interface_name.upper()}:")
            print(f"   📝 Texto: {interface_data['text_length']} caracteres")
            print(f"   ⌨️ Botones: {len(interface_data.get('keyboard_buttons', []))} filas")
            
            # Preview del texto (primeras 3 líneas)
            text = interface_data.get('text', '')
            preview_lines = text.split('\n')[:3]
            for line in preview_lines:
                if line.strip():
                    print(f"      {line[:100]}{'...' if len(line) > 100 else ''}")
            
            # Preview de botones
            buttons = interface_data.get('keyboard_buttons', [])
            if buttons:
                print(f"   🔘 Botones disponibles:")
                for row_idx, row in enumerate(buttons[:2]):  # Solo primeras 2 filas
                    button_texts = [btn['text'] for btn in row]
                    print(f"      Fila {row_idx + 1}: {' | '.join(button_texts)}")
                if len(buttons) > 2:
                    print(f"      ... y {len(buttons) - 2} filas más")
            
            print()
    
    async def interactive_testing_mode(self):
        """Modo interactivo para probar diferentes usuarios"""
        print("🎮 MODO INTERACTIVO - Testing de Interfaces Dinámicas")
        print("=" * 60)
        
        await self.load_available_users()
        
        while True:
            print(f"\n📋 Opciones:")
            print(f"1. 🎲 Probar usuario aleatorio")
            print(f"2. 🔍 Probar ID específico")
            print(f"3. 📊 Listar usuarios disponibles")
            print(f"4. 🔄 Comparar 2 usuarios")
            print(f"5. ❌ Salir")
            
            choice = input(f"\n🎯 Selecciona una opción: ").strip()
            
            if choice == "1":
                # Usuario aleatorio
                if self.available_users:
                    import random
                    random_user = random.choice(self.available_users)
                    user_id = random_user["user_id"]
                    print(f"🎲 Usuario aleatorio seleccionado: {random_user.get('username', 'N/A')} (ID: {user_id})")
                else:
                    user_id = random.randint(10000, 99999)
                    print(f"🎲 ID aleatorio generado: {user_id}")
                
                interface_data = await self.generate_user_interface(user_id)
                self.display_interface_preview(interface_data)
            
            elif choice == "2":
                # ID específico
                try:
                    user_id = int(input("🔢 Ingresa el ID del usuario: ").strip())
                    
                    interface_data = await self.generate_user_interface(user_id)
                    self.display_interface_preview(interface_data)
                    
                except ValueError:
                    print("❌ ID inválido. Debe ser un número.")
            
            elif choice == "3":
                # Listar usuarios disponibles
                if self.available_users:
                    print(f"\n📊 USUARIOS DISPONIBLES ({len(self.available_users)}):")
                    for i, user in enumerate(self.available_users[:20]):  # Solo primeros 20
                        vip_status = "💎 VIP" if user.get("is_vip") else "🆓 FREE"
                        print(f"   {i+1:2d}. ID {user['user_id']} - {user.get('username', 'N/A')} - Lvl {user.get('level', '?')} - {vip_status}")
                    
                    if len(self.available_users) > 20:
                        print(f"   ... y {len(self.available_users) - 20} usuarios más")
                else:
                    print("📭 No hay usuarios cargados. Ejecuta primero populate_random_users.py")
            
            elif choice == "4":
                # Comparar 2 usuarios
                try:
                    user_id_1 = int(input("🔢 ID del primer usuario: ").strip())
                    user_id_2 = int(input("🔢 ID del segundo usuario: ").strip())
                    
                    print("🔄 Generando interfaces...")
                    
                    interface_1 = await self.generate_user_interface(user_id_1)
                    interface_2 = await self.generate_user_interface(user_id_2)
                    
                    print(f"\n🆚 COMPARACIÓN DE INTERFACES:")
                    print(f"{'─'*40} VS {'─'*40}")
                    
                    self.display_interface_preview(interface_1)
                    print(f"{'='*80}")
                    self.display_interface_preview(interface_2)
                    
                except ValueError:
                    print("❌ IDs inválidos. Deben ser números.")
            
            elif choice == "5":
                print("👋 ¡Hasta luego!")
                break
            
            else:
                print("❌ Opción inválida. Intenta de nuevo.")
    
    async def batch_testing(self, user_ids: list):
        """Probar múltiples usuarios de una vez"""
        print(f"🔄 Probando interfaces para {len(user_ids)} usuarios...")
        
        results = []
        for i, user_id in enumerate(user_ids):
            print(f"📊 Procesando usuario {i+1}/{len(user_ids)}: ID {user_id}")
            
            interface_data = await self.generate_user_interface(user_id)
            results.append(interface_data)
            
            # Breve preview
            context = interface_data.get("context", {})
            diana_mood = context.get("diana_context", {}).get("mood", "N/A")
            user_tier = context.get("user_context", {}).get("tier", "N/A")
            
            print(f"   🎭 Mood: {diana_mood} | 👤 Tier: {user_tier}")
        
        return results

async def main():
    """Función principal"""
    print("🎭 DIANA INTERFACE TESTER - Iniciando...")
    print("Permite probar las interfaces dinámicas con IDs específicos")
    
    tester = DianaInterfaceTester()
    await tester.setup_diana_ecosystem()
    
    # Modo interactivo por defecto
    await tester.interactive_testing_mode()

if __name__ == "__main__":
    asyncio.run(main())