#!/usr/bin/env python3
"""
🚀 DIANA QUICK DEMO
===================

Demostración rápida de 2 minutos mostrando las capacidades dinámicas de Diana.
Perfecto para mostrar las funcionalidades sin configuración compleja.
"""

import asyncio
import random
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath('.'))

from scripts.populate_random_users import DianaRandomUserGenerator
from scripts.test_interface_with_user import DianaInterfaceTester

async def quick_demo():
    """Demo rápido de 2 minutos"""
    print("🎭✨ DIANA BOT - DEMO RÁPIDO DE INTERFACES DINÁMICAS")
    print("=" * 60)
    print("⏱️  Demo de 2 minutos mostrando la magia de Diana")
    
    # Setup
    print("\n🔧 Configurando Diana...")
    generator = DianaRandomUserGenerator()
    tester = DianaInterfaceTester()
    
    await generator.setup_services()
    await tester.setup_diana_ecosystem()
    
    print("✅ Diana lista para la demo!")
    
    # Generar 3 usuarios con perfiles muy diferentes
    demo_users = []
    
    # Usuario 1: Newbie
    print("\n🎯 Generando usuario NEWBIE...")
    newbie = generator.generate_random_user_profile()
    newbie.update({
        "level": 1,
        "points": 15,
        "is_vip": False,
        "personality": "newcomer",
        "intimacy_level": 0.15,
        "username": "newbie_demo"
    })
    demo_users.append(("🆕 USUARIO NEWBIE", newbie))
    
    # Usuario 2: VIP Elite
    print("🎯 Generando usuario VIP ELITE...")
    elite = generator.generate_random_user_profile()
    elite.update({
        "level": 8,
        "points": 3500,
        "is_vip": True,
        "vip_level": "elite",
        "personality": "sophisticated",
        "intimacy_level": 0.92,
        "consecutive_days": 25,
        "username": "elite_demo"
    })
    demo_users.append(("👑 USUARIO VIP ELITE", elite))
    
    # Usuario 3: FREE buscando upgrade
    print("🎯 Generando usuario FREE ACTIVO...")
    active_free = generator.generate_random_user_profile()
    active_free.update({
        "level": 5,
        "points": 1200,
        "is_vip": False,
        "personality": "yearning",
        "intimacy_level": 0.68,
        "conversion_signals": 8,
        "consecutive_days": 12,
        "username": "active_demo"
    })
    demo_users.append(("🎯 USUARIO FREE ACTIVO", active_free))
    
    print("✅ 3 usuarios demo generados!")
    
    # Mostrar las diferencias
    print("\n" + "🎭" * 20)
    print("🎪 OBSERVA CÓMO DIANA CAMBIA CON CADA USUARIO")
    print("🎭" * 20)
    
    for i, (title, profile) in enumerate(demo_users, 1):
        print(f"\n{'='*60}")
        print(f"👤 DEMO {i}/3: {title}")
        print(f"{'='*60}")
        
        # Mostrar perfil básico
        vip_status = f"💎 VIP ({profile['vip_level']})" if profile["is_vip"] else "🆓 FREE"
        print(f"📊 {profile['username']} - Nivel {profile['level']} - {vip_status}")
        print(f"💫 Personalidad: {profile['personality']} | Intimidad: {profile['intimacy_level']:.2f}")
        
        # Generar interfaz
        user_id = profile["user_id"]
        interface_data = await tester.generate_user_interface(user_id)
        
        # Mostrar contexto de Diana
        context = interface_data.get("context", {})
        if "diana_context" in context and "error" not in context["diana_context"]:
            diana_ctx = context["diana_context"]
            print(f"🧠 Diana detecta: {diana_ctx.get('mood', 'N/A')} | Engagement: {diana_ctx.get('engagement_pattern', 'N/A')}")
        
        # Mostrar interfaz
        interfaces = interface_data.get("interfaces", {})
        if "user_main" in interfaces and "error" not in interfaces["user_main"]:
            interface = interfaces["user_main"]
            text = interface.get("text", "")
            
            # Mostrar primeras líneas significativas
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            significant_lines = [line for line in lines if len(line) > 20][:3]
            
            print(f"\n💬 DIANA LE DICE:")
            for line in significant_lines:
                # Limpiar tags HTML para mostrar
                clean_line = line.replace('<b>', '').replace('</b>', '').replace('<i>', '').replace('</i>', '')
                print(f"   📝 {clean_line[:80]}{'...' if len(clean_line) > 80 else ''}")
            
            # Mostrar botones únicos
            buttons = interface.get("keyboard_buttons", [])
            unique_buttons = []
            for row in buttons:
                for btn in row:
                    if btn['text'] not in ['🔄 Actualizar', '🔙 Volver']:
                        unique_buttons.append(btn['text'])
            
            print(f"\n🔘 OPCIONES ÚNICAS PARA ESTE USUARIO:")
            for btn in unique_buttons[:4]:
                print(f"   • {btn}")
            if len(unique_buttons) > 4:
                print(f"   • ... y {len(unique_buttons)-4} opciones más")
        
        if i < len(demo_users):
            input(f"\n⏸️  Presiona ENTER para ver el siguiente usuario...")
    
    # Resumen final
    print(f"\n{'🎉' * 20}")
    print("✨ ¡DEMO COMPLETADA! ✨")
    print("🎉" * 20)
    
    print("\n🎭 LO QUE ACABAS DE VER:")
    print("✅ Diana detecta automáticamente el perfil de cada usuario")
    print("✅ Adapta su personalidad y lenguaje según el contexto")
    print("✅ Ofrece opciones y contenido únicos para cada persona")
    print("✅ Los usuarios VIP reciben trato preferencial")
    print("✅ Los usuarios FREE ven elementos de conversión sutiles")
    print("✅ Cada interfaz es única y personalizada")
    
    print("\n🚀 DIANA BOT NUNCA ES LA MISMA DOS VECES!")
    print("🎪 Cada usuario vive una experiencia completamente diferente")
    
    return True

async def main():
    """Ejecutar demo rápido"""
    try:
        await quick_demo()
    except KeyboardInterrupt:
        print("\n👋 Demo interrumpida. ¡Hasta luego!")
    except Exception as e:
        print(f"❌ Error en demo: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)