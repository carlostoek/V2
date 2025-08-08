#!/usr/bin/env python3
"""
🎭✨ DIANA INTERFACE SHOWCASE
============================

Script de demostración que muestra las capacidades dinámicas completas de Diana:
- Genera usuarios con perfiles específicos para mostrar diferentes interfaces
- Demuestra cómo Diana adapta su personalidad según el usuario
- Muestra la diferencia entre usuarios FREE vs VIP
- Exhibe las capacidades de mood detection y adaptive UI

Perfecto para demostraciones y testing de funcionalidades.
"""

import asyncio
import sys
import os
from datetime import datetime
import random

# Add project root to path
sys.path.append(os.path.abspath('.'))

from scripts.populate_random_users import DianaRandomUserGenerator
from scripts.test_interface_with_user import DianaInterfaceTester

class DianaInterfaceShowcase:
    """🎪 Showcase completo de las capacidades dinámicas de Diana"""
    
    def __init__(self):
        self.generator = DianaRandomUserGenerator()
        self.tester = DianaInterfaceTester()
    
    async def setup(self):
        """Configurar el showcase"""
        print("🎭✨ DIANA INTERFACE SHOWCASE - Configurando...")
        
        await self.generator.setup_services()
        await self.tester.setup_diana_ecosystem()
        
        print("✅ Showcase listo para demostración!")
    
    def create_demo_scenarios(self):
        """Crear escenarios de demostración específicos"""
        scenarios = [
            {
                "name": "🆕 Usuario Nuevo",
                "description": "Primer contacto con Diana",
                "profile_override": {
                    "level": 1,
                    "points": random.randint(0, 50),
                    "is_vip": False,
                    "consecutive_days": 0,
                    "narrative_progress": random.randint(0, 10),
                    "personality": "newcomer"
                }
            },
            {
                "name": "🎯 Usuario Activo FREE",
                "description": "Usuario comprometido buscando más",
                "profile_override": {
                    "level": random.randint(3, 5),
                    "points": random.randint(500, 1200),
                    "is_vip": False,
                    "consecutive_days": random.randint(3, 10),
                    "narrative_progress": random.randint(30, 60),
                    "personality": random.choice(["yearning", "devoted", "achiever"])
                }
            },
            {
                "name": "💎 Usuario VIP Reciente",
                "description": "Recién convertido al círculo VIP",
                "profile_override": {
                    "level": random.randint(4, 7),
                    "points": random.randint(800, 2000),
                    "is_vip": True,
                    "vip_level": "basic",
                    "consecutive_days": random.randint(5, 15),
                    "narrative_progress": random.randint(40, 75),
                    "personality": random.choice(["sophisticated", "devoted"])
                }
            },
            {
                "name": "👑 Usuario VIP Elite",
                "description": "Miembro del círculo íntimo de Diana",
                "profile_override": {
                    "level": random.randint(7, 10),
                    "points": random.randint(2000, 5000),
                    "is_vip": True,
                    "vip_level": "elite",
                    "consecutive_days": random.randint(15, 30),
                    "narrative_progress": random.randint(70, 100),
                    "personality": "sophisticated"
                }
            },
            {
                "name": "🎪 Usuario Explorador",
                "description": "Le encanta descubrir nuevas funciones",
                "profile_override": {
                    "level": random.randint(2, 6),
                    "points": random.randint(300, 1500),
                    "is_vip": random.choice([True, False]),
                    "consecutive_days": random.randint(1, 8),
                    "narrative_progress": random.randint(20, 50),
                    "personality": "explorer"
                }
            },
            {
                "name": "📖 Usuario Narrativo",
                "description": "Profundamente conectado con la historia",
                "profile_override": {
                    "level": random.randint(4, 8),
                    "points": random.randint(600, 2500),
                    "is_vip": random.choice([True, False]),
                    "consecutive_days": random.randint(10, 25),
                    "narrative_progress": random.randint(60, 95),
                    "personality": "storyteller"
                }
            }
        ]
        
        return scenarios
    
    async def generate_scenario_user(self, scenario):
        """Generar un usuario para un escenario específico"""
        # Generar perfil base aleatorio
        base_profile = self.generator.generate_random_user_profile()
        
        # Aplicar overrides del escenario
        profile = base_profile.copy()
        for key, value in scenario["profile_override"].items():
            profile[key] = value
        
        # Ajustar intimacy_level basado en VIP status y nivel
        if profile["is_vip"]:
            profile["intimacy_level"] = random.uniform(0.6, 0.95)
        else:
            profile["intimacy_level"] = random.uniform(0.1, 0.7)
        
        # Ajustar conversion_signals
        if not profile["is_vip"] and profile["level"] >= 3:
            profile["conversion_signals"] = random.randint(3, 10)
        else:
            profile["conversion_signals"] = random.randint(0, 5)
        
        return profile
    
    async def showcase_scenario(self, scenario, profile):
        """Mostrar un escenario específico"""
        user_id = profile["user_id"]
        
        print(f"\n{'🎭' * 30}")
        print(f"🎪 ESCENARIO: {scenario['name']}")
        print(f"📋 {scenario['description']}")
        print(f"{'─' * 80}")
        
        # Mostrar perfil del usuario
        vip_status = f"💎 VIP ({profile['vip_level']})" if profile["is_vip"] else "🆓 FREE"
        print(f"👤 Usuario: {profile['username']} (ID: {user_id})")
        print(f"📊 Perfil: Nivel {profile['level']} | {profile['points']} puntos | {vip_status}")
        print(f"🎭 Personalidad: {profile['personality']} | 🔥 Racha: {profile['consecutive_days']} días")
        print(f"📖 Narrativa: {profile['narrative_progress']:.1f}% | 💫 Intimidad: {profile['intimacy_level']:.2f}")
        
        # Generar y mostrar interface
        try:
            interface_data = await self.tester.generate_user_interface(user_id)
            
            print(f"\n🎭 CÓMO DIANA VE A ESTE USUARIO:")
            context = interface_data.get("context", {})
            
            if "diana_context" in context and "error" not in context["diana_context"]:
                diana_ctx = context["diana_context"]
                print(f"   🧠 Mood detectado: {diana_ctx.get('mood', 'N/A')}")
                print(f"   📈 Patrón engagement: {diana_ctx.get('engagement_pattern', 'N/A')}")
                print(f"   🎯 Score personalización: {diana_ctx.get('personalization_score', 0):.2f}")
            
            if "user_context" in context and "error" not in context["user_context"]:
                user_ctx = context["user_context"]
                print(f"   👑 Tier detectado: {user_ctx.get('tier', 'N/A')}")
                print(f"   🎪 Mood usuario: {user_ctx.get('mood', 'N/A')}")
                print(f"   📊 Señales conversión: {user_ctx.get('conversion_signals', 0)}")
            
            # Mostrar preview de la interfaz principal
            interfaces = interface_data.get("interfaces", {})
            if "user_main" in interfaces and "error" not in interfaces["user_main"]:
                interface = interfaces["user_main"]
                text = interface.get("text", "")
                
                print(f"\n💬 INTERFAZ QUE VERÁ EL USUARIO:")
                print(f"   📝 {interface['text_length']} caracteres de contenido personalizado")
                
                # Mostrar primeras líneas del texto
                lines = text.split('\n')[:4]
                for line in lines:
                    if line.strip():
                        print(f"   📄 {line[:90]}{'...' if len(line) > 90 else ''}")
                
                # Mostrar botones
                buttons = interface.get("keyboard_buttons", [])
                if buttons:
                    print(f"\n   🔘 BOTONES DISPONIBLES:")
                    for row_idx, row in enumerate(buttons[:3]):
                        button_texts = [btn['text'][:20] for btn in row]
                        print(f"      {' | '.join(button_texts)}")
                    if len(buttons) > 3:
                        print(f"      ... y {len(buttons) - 3} filas más de opciones")
            
            # Analizar qué hace única esta interfaz
            print(f"\n🎨 ELEMENTOS ÚNICOS DE ESTA INTERFAZ:")
            self._analyze_interface_uniqueness(scenario, profile, interface_data)
            
        except Exception as e:
            print(f"❌ Error generando interfaz: {e}")
    
    def _analyze_interface_uniqueness(self, scenario, profile, interface_data):
        """Analizar qué hace única esta interfaz"""
        uniqueness = []
        
        # Análisis basado en VIP status
        if profile["is_vip"]:
            uniqueness.append("💎 Acceso a contenido VIP exclusivo")
            uniqueness.append("👑 Trato preferencial de Diana")
            if profile["vip_level"] == "elite":
                uniqueness.append("⭐ Experiencias premium ultra-personalizadas")
        else:
            uniqueness.append("🎯 Elementos de conversión sutiles hacia VIP")
            uniqueness.append("🌟 Invitaciones al círculo íntimo")
        
        # Análisis basado en personalidad
        personality_features = {
            "newcomer": "🌱 Guías paso a paso y tutoriales integrados",
            "explorer": "🗺️ Múltiples opciones de exploración",
            "achiever": "🏆 Enfoque en logros y progreso",
            "collector": "💎 Énfasis en recompensas y coleccionables",
            "storyteller": "📖 Contenido narrativo rico y profundo",
            "sophisticated": "🎭 Lenguaje elegante y experiencias refinadas",
            "yearning": "🔥 Elementos que alimentan el deseo de más",
            "devoted": "💝 Reconocimiento de lealtad y dedicación"
        }
        
        personality = profile["personality"]
        if personality in personality_features:
            uniqueness.append(personality_features[personality])
        
        # Análisis basado en nivel de intimidad
        intimacy = profile["intimacy_level"]
        if intimacy >= 0.8:
            uniqueness.append("💕 Diana muestra vulnerabilidad calculada")
        elif intimacy >= 0.6:
            uniqueness.append("🌹 Diana comparte secretos personales")
        elif intimacy >= 0.4:
            uniqueness.append("💫 Diana demuestra interés genuino")
        else:
            uniqueness.append("🎭 Diana mantiene misterio y distancia elegante")
        
        # Análisis basado en progreso narrativo
        if profile["narrative_progress"] >= 80:
            uniqueness.append("📜 Acceso a capítulos finales de la historia")
        elif profile["narrative_progress"] >= 50:
            uniqueness.append("📖 Decisiones narrativas complejas disponibles")
        else:
            uniqueness.append("🌟 Introducción gradual a la narrativa")
        
        # Mostrar elementos únicos
        for element in uniqueness:
            print(f"      • {element}")
    
    async def run_complete_showcase(self):
        """Ejecutar showcase completo"""
        print("🎪✨ DIANA INTERFACE SHOWCASE - DEMOSTRACIÓN COMPLETA")
        print("=" * 80)
        print("Preparando demostración de las capacidades dinámicas de Diana...")
        
        scenarios = self.create_demo_scenarios()
        
        print(f"\n🎯 ESCENARIOS A DEMOSTRAR: {len(scenarios)}")
        for i, scenario in enumerate(scenarios, 1):
            print(f"   {i}. {scenario['name']} - {scenario['description']}")
        
        input(f"\n⏸️  Presiona ENTER para comenzar la demostración...")
        
        # Ejecutar cada escenario
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n🎬 DEMOSTRACIÓN {i}/{len(scenarios)}")
            
            # Generar usuario para este escenario
            profile = await self.generate_scenario_user(scenario)
            
            # Mostrar el escenario
            await self.showcase_scenario(scenario, profile)
            
            if i < len(scenarios):
                input(f"\n⏸️  Presiona ENTER para continuar al siguiente escenario...")
        
        print(f"\n🎉 ¡DEMOSTRACIÓN COMPLETADA!")
        print("=" * 80)
        print("🎭 RESUMEN DE CAPACIDADES DEMOSTRADAS:")
        print("✅ Adaptación dinámica de personalidad según perfil de usuario")
        print("✅ Detección automática de mood y contexto")
        print("✅ Interfaces diferenciadas para usuarios FREE vs VIP")
        print("✅ Elementos de conversión inteligentes y sutiles")
        print("✅ Personalización basada en progreso narrativo")
        print("✅ Niveles variables de intimidad con Diana")
        print("✅ Botones y opciones contextuales únicos")
        print("\n🚀 Diana Bot está listo para ofrecer experiencias únicas a cada usuario!")

async def main():
    """Función principal del showcase"""
    showcase = DianaInterfaceShowcase()
    await showcase.setup()
    
    print("\n🎪 OPCIONES DE DEMOSTRACIÓN:")
    print("1. 🎬 Showcase completo (todos los escenarios)")
    print("2. 🎲 Escenario aleatorio único")
    print("3. 🔧 Modo interactivo personalizado")
    
    choice = input("\n🎯 Selecciona una opción: ").strip()
    
    if choice == "1":
        await showcase.run_complete_showcase()
    elif choice == "2":
        scenarios = showcase.create_demo_scenarios()
        scenario = random.choice(scenarios)
        profile = await showcase.generate_scenario_user(scenario)
        await showcase.showcase_scenario(scenario, profile)
    elif choice == "3":
        print("🔧 Iniciando modo interactivo del tester...")
        await showcase.tester.interactive_testing_mode()
    else:
        print("🎬 Ejecutando showcase completo por defecto...")
        await showcase.run_complete_showcase()

if __name__ == "__main__":
    asyncio.run(main())