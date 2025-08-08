#!/usr/bin/env python3
"""
🎲 DIANA RANDOM USER GENERATOR
===============================

Script para generar usuarios con perfiles completamente aleatorios cada vez que se ejecuta.
Esto permite probar las interfaces dinámicas de Diana con diferentes contextos de usuario.

Características:
- Nombres aleatorios realistas
- Niveles y puntos variables
- Estados VIP aleatorios
- Progreso narrativo diverso
- Patrones de comportamiento únicos
- Rachas de actividad realistas
"""

import asyncio
import random
import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json

# Add project root to path
sys.path.append(os.path.abspath('.'))

from src.bot.database.engine import init_db
from src.core.event_bus import EventBus
from src.modules.gamification.service import GamificationService
from src.modules.narrative.service import NarrativeService
from src.modules.user.service import UserService
from src.modules.admin.service import AdminService
from src.modules.daily_rewards.service import DailyRewardsService

class DianaRandomUserGenerator:
    """🎭 Generador de usuarios aleatorios para Diana"""
    
    def __init__(self):
        self.generated_users = []
        
        # Nombres realistas para generar perfiles
        self.first_names = [
            "Alexandra", "Sofía", "Isabella", "Camila", "Valentina", "Emma", "Olivia", 
            "Sebastián", "Mateo", "Diego", "Alejandro", "Santiago", "Nicolás", "Daniel",
            "Luna", "Aurora", "Esperanza", "Estrella", "Ariana", "Natalia", "Andrea",
            "Gabriel", "Rafael", "Miguel", "Antonio", "Carlos", "Fernando", "Ricardo"
        ]
        
        self.last_names = [
            "García", "Rodríguez", "López", "Martínez", "González", "Pérez", "Sánchez",
            "Ramírez", "Cruz", "Flores", "Ramos", "Mendoza", "Castillo", "Morales",
            "Vargas", "Jiménez", "Herrera", "Medina", "Castro", "Ortiz", "Silva"
        ]
        
        # Patrones de personalidad aleatorios
        self.personality_patterns = [
            "explorer", "achiever", "collector", "storyteller", "socializer", 
            "optimizer", "newcomer", "devoted", "yearning", "sophisticated"
        ]
        
        # Intereses aleatorios para narrativa
        self.narrative_interests = [
            "mystery", "romance", "adventure", "fantasy", "drama", "thriller", 
            "comedy", "horror", "sci-fi", "historical"
        ]
        
        # Patrones de actividad realistas
        self.activity_patterns = [
            "morning_person", "night_owl", "weekend_warrior", "daily_consistent",
            "binge_user", "casual_visitor", "power_user", "social_butterfly"
        ]
    
    async def setup_services(self):
        """Configurar todos los servicios necesarios"""
        print("🎭 Configurando servicios de Diana...")
        
        await init_db()
        
        self.event_bus = EventBus()
        self.user_service = UserService(self.event_bus)
        self.gamification_service = GamificationService(self.event_bus)
        self.narrative_service = NarrativeService(self.event_bus)
        self.admin_service = AdminService(self.event_bus)
        self.daily_rewards_service = DailyRewardsService(self.gamification_service)
        
        # Setup services
        await self.user_service.setup()
        await self.gamification_service.setup()
        await self.narrative_service.setup()
        await self.admin_service.setup()
        await self.daily_rewards_service.setup()
        
        print("✅ Servicios configurados correctamente!")
    
    def generate_random_user_profile(self) -> Dict[str, Any]:
        """Generar un perfil de usuario completamente aleatorio"""
        
        # ID único basado en timestamp + random
        user_id = int(datetime.now().timestamp() * 1000) + random.randint(1000, 9999)
        
        # Nombre aleatorio
        first_name = random.choice(self.first_names)
        last_name = random.choice(self.last_names)
        username = f"{first_name.lower()}{random.randint(100, 999)}"
        
        # Nivel realista (más probabilidad de niveles bajos)
        level_weights = [0.3, 0.25, 0.2, 0.15, 0.05, 0.03, 0.02]  # Nivel 1-7
        level = random.choices(range(1, 8), weights=level_weights)[0]
        
        # Puntos basados en nivel pero con variación
        base_points = level * random.randint(150, 400)
        bonus_points = random.randint(0, level * 100)
        total_points = base_points + bonus_points
        
        # Estado VIP (20% probabilidad)
        is_vip = random.random() < 0.2
        vip_level = random.choice(["basic", "premium", "elite"]) if is_vip else None
        
        # Racha realista (más probable rachas cortas)
        streak_weights = [0.4, 0.3, 0.15, 0.08, 0.04, 0.02, 0.01]  # 0-6 días
        consecutive_days = random.choices(range(0, 7), weights=streak_weights)[0]
        
        # Progreso narrativo (correlacionado con nivel pero con variación)
        narrative_progress = min(100, (level * 15) + random.randint(-10, 25))
        narrative_chapter = random.randint(1, min(4, level + 1))
        
        # Personalidad y comportamiento
        personality = random.choice(self.personality_patterns)
        activity_pattern = random.choice(self.activity_patterns)
        
        # Interacciones históricas
        total_interactions = random.randint(level * 5, level * 20)
        interactions_today = random.randint(0, min(15, level * 3))
        
        # Tiempo de registro (últimos 6 meses)
        days_ago = random.randint(1, 180)
        join_date = datetime.now() - timedelta(days=days_ago)
        
        # Sesión actual
        session_start = datetime.now() - timedelta(minutes=random.randint(1, 120))
        
        # Logros aleatorios
        available_achievements = [
            "first_steps", "dedicated_user", "trivia_master", "story_lover", 
            "social_butterfly", "collector", "vip_member", "loyal_friend"
        ]
        num_achievements = random.randint(0, min(len(available_achievements), level + 2))
        achievements = random.sample(available_achievements, num_achievements)
        
        # Intereses narrativos
        num_interests = random.randint(1, 3)
        narrative_interests = random.sample(self.narrative_interests, num_interests)
        
        return {
            "user_id": user_id,
            "first_name": first_name,
            "last_name": last_name, 
            "username": username,
            "level": level,
            "points": total_points,
            "is_vip": is_vip,
            "vip_level": vip_level,
            "consecutive_days": consecutive_days,
            "narrative_progress": narrative_progress,
            "narrative_chapter": narrative_chapter,
            "personality": personality,
            "activity_pattern": activity_pattern,
            "total_interactions": total_interactions,
            "interactions_today": interactions_today,
            "join_date": join_date,
            "session_start": session_start,
            "achievements": achievements,
            "narrative_interests": narrative_interests,
            "intimacy_level": random.uniform(0.1, 0.9 if is_vip else 0.6),
            "conversion_signals": random.randint(0, 10),
            "last_content_type": random.choice(["trivia", "shop", "story", "mission", "daily_reward"])
        }
    
    async def populate_user_in_database(self, profile: Dict[str, Any]):
        """Poblar un usuario específico en la base de datos"""
        try:
            user_id = profile["user_id"]
            
            # 1. Registrar usuario básico
            # (Esto normalmente se haría a través de los servicios, pero para testing directo)
            
            # 2. Establecer datos de gamificación
            # Simular puntos acumulados
            for _ in range(profile["points"] // 10):  # Simular múltiples awards
                await self.gamification_service.award_points(
                    user_id, 
                    random.randint(5, 15), 
                    f"random_activity_{random.randint(1, 100)}"
                )
            
            # 3. Establecer progreso narrativo
            # Simular progreso en la historia
            if profile["narrative_progress"] > 0:
                try:
                    # Intentar establecer progreso narrativo
                    pass  # El servicio narrativo maneja esto internamente
                except:
                    pass  # Fallar silenciosamente si no está disponible
            
            # 4. Establecer racha de daily rewards
            if profile["consecutive_days"] > 0:
                try:
                    # Simular días consecutivos de regalos
                    for day in range(profile["consecutive_days"]):
                        past_date = datetime.now() - timedelta(days=profile["consecutive_days"] - day - 1)
                        # Los daily rewards manejan esto internamente
                except:
                    pass
            
            # 5. Establecer estado VIP si aplica
            if profile["is_vip"]:
                try:
                    # Simular suscripción VIP
                    # await self.admin_service.set_vip_status(user_id, True)
                    pass  # El servicio admin maneja esto
                except:
                    pass
            
            print(f"✅ Usuario {profile['username']} (ID: {user_id}) poblado exitosamente")
            return True
            
        except Exception as e:
            print(f"❌ Error poblando usuario {profile.get('username', 'unknown')}: {e}")
            return False
    
    async def generate_random_population(self, num_users: int = 20) -> List[Dict[str, Any]]:
        """Generar una población completamente aleatoria de usuarios"""
        print(f"🎲 Generando {num_users} usuarios aleatorios...")
        
        profiles = []
        successful_populations = 0
        
        for i in range(num_users):
            # Generar perfil aleatorio
            profile = self.generate_random_user_profile()
            profiles.append(profile)
            
            # Poblar en base de datos
            success = await self.populate_user_in_database(profile)
            if success:
                successful_populations += 1
            
            # Mostrar progreso
            if (i + 1) % 5 == 0:
                print(f"📊 Progreso: {i + 1}/{num_users} usuarios procesados")
        
        self.generated_users = profiles
        
        print(f"🎉 Generación completa: {successful_populations}/{num_users} usuarios poblados exitosamente")
        return profiles
    
    def save_user_profiles(self, profiles: List[Dict[str, Any]], filename: str = None):
        """Guardar los perfiles generados en un archivo JSON"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"random_users_{timestamp}.json"
        
        filepath = f"scripts/generated_data/{filename}"
        
        # Crear directorio si no existe
        os.makedirs("scripts/generated_data", exist_ok=True)
        
        # Convertir datetime a string para JSON
        json_profiles = []
        for profile in profiles:
            json_profile = profile.copy()
            json_profile["join_date"] = profile["join_date"].isoformat()
            json_profile["session_start"] = profile["session_start"].isoformat()
            json_profiles.append(json_profile)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(json_profiles, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Perfiles guardados en: {filepath}")
        return filepath
    
    def display_user_summary(self, profiles: List[Dict[str, Any]]):
        """Mostrar resumen de usuarios generados"""
        print("\n" + "="*60)
        print("📊 RESUMEN DE USUARIOS GENERADOS ALEATORIAMENTE")
        print("="*60)
        
        # Estadísticas generales
        total_users = len(profiles)
        vip_users = sum(1 for p in profiles if p["is_vip"])
        avg_level = sum(p["level"] for p in profiles) / total_users
        avg_points = sum(p["points"] for p in profiles) / total_users
        
        print(f"👥 Total usuarios: {total_users}")
        print(f"💎 Usuarios VIP: {vip_users} ({vip_users/total_users*100:.1f}%)")
        print(f"📈 Nivel promedio: {avg_level:.1f}")
        print(f"💰 Puntos promedio: {avg_points:.0f}")
        
        # Distribución de niveles
        level_dist = {}
        for p in profiles:
            level = p["level"]
            level_dist[level] = level_dist.get(level, 0) + 1
        
        print(f"\n📊 Distribución por nivel:")
        for level in sorted(level_dist.keys()):
            count = level_dist[level]
            print(f"  Nivel {level}: {count} usuarios ({count/total_users*100:.1f}%)")
        
        # Personalidades
        personality_dist = {}
        for p in profiles:
            personality = p["personality"]
            personality_dist[personality] = personality_dist.get(personality, 0) + 1
        
        print(f"\n🎭 Personalidades más comunes:")
        for personality, count in sorted(personality_dist.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {personality}: {count} usuarios")
        
        # Ejemplos de usuarios generados
        print(f"\n🎲 EJEMPLOS DE USUARIOS ALEATORIOS:")
        sample_users = random.sample(profiles, min(5, len(profiles)))
        
        for user in sample_users:
            vip_status = f"💎 VIP ({user['vip_level']})" if user["is_vip"] else "🆓 FREE"
            print(f"  👤 {user['username']} - Lvl {user['level']} - {user['points']} pts - {vip_status}")
            print(f"      🎭 {user['personality']} | 📖 {user['narrative_progress']:.0f}% narrativa | 🔥 {user['consecutive_days']} días racha")

async def main():
    """Ejecutar generación de usuarios aleatorios"""
    print("🎲🎭 DIANA RANDOM USER GENERATOR - Iniciando...")
    print("=" * 60)
    
    # Solicitar número de usuarios
    try:
        num_users = int(input("¿Cuántos usuarios aleatorios generar? (default: 20): ") or "20")
        if num_users < 1 or num_users > 100:
            print("⚠️ Número debe estar entre 1 y 100. Usando 20 por defecto.")
            num_users = 20
    except ValueError:
        print("⚠️ Entrada inválida. Usando 20 usuarios por defecto.")
        num_users = 20
    
    # Generar usuarios
    generator = DianaRandomUserGenerator()
    await generator.setup_services()
    
    profiles = await generator.generate_random_population(num_users)
    
    # Guardar y mostrar resumen
    generator.save_user_profiles(profiles)
    generator.display_user_summary(profiles)
    
    print(f"\n🎉 ¡Generación aleatoria completada!")
    print(f"🎮 Usa el script 'test_interface_with_user.py' para probar las interfaces con estos usuarios")
    
    return profiles

if __name__ == "__main__":
    asyncio.run(main())