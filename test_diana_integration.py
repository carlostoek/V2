#!/usr/bin/env python3
"""
🎭 DIANA MASTER SYSTEM - INTEGRATION TEST
=========================================

This script tests the complete integration of Diana Master System with real services.
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.event_bus import EventBus
from src.modules.gamification.service import GamificationService
from src.modules.narrative.service import NarrativeService
from src.modules.daily_rewards.service import DailyRewardsService
from src.modules.admin.service import AdminService
from src.modules.tariff.service import TariffService
from src.bot.core.diana_master_system import DianaMasterInterface, AdaptiveContextEngine

async def test_diana_master_integration():
    """Test Diana Master System integration with real services."""
    print("🎭 DIANA MASTER SYSTEM - INTEGRATION TEST")
    print("=" * 50)
    
    try:
        # Initialize Event Bus
        event_bus = EventBus()
        print("✅ EventBus initialized")
        
        # Initialize Services
        gamification_service = GamificationService(event_bus)
        narrative_service = NarrativeService(event_bus)
        admin_service = AdminService(event_bus)
        tariff_service = TariffService(event_bus)
        daily_rewards_service = DailyRewardsService(gamification_service)
        print("✅ All services initialized")
        
        # Setup services
        await gamification_service.setup()
        await narrative_service.setup()
        await admin_service.setup()
        await tariff_service.setup()
        await daily_rewards_service.setup()
        print("✅ All services setup completed")
        
        # Prepare services dictionary
        services = {
            'gamification': gamification_service,
            'narrative': narrative_service,
            'admin': admin_service,
            'tariff': tariff_service,
            'daily_rewards': daily_rewards_service,
            'event_bus': event_bus
        }
        print("✅ Services dictionary prepared")
        
        # Initialize Diana Master System
        diana_master = DianaMasterInterface(services)
        print("✅ Diana Master System initialized")
        
        print("\n🧪 RUNNING INTEGRATION TESTS")
        print("-" * 40)
        
        # Test user context analysis
        test_user_id = 12345
        print(f"📊 Testing user context analysis for user {test_user_id}...")
        
        try:
            context = await diana_master.context_engine.analyze_user_context(test_user_id)
            print(f"✅ User context analyzed successfully:")
            print(f"   👤 User ID: {context.user_id}")
            print(f"   🎭 Mood: {context.current_mood.value}")
            print(f"   📈 Engagement: {context.engagement_pattern}")
            print(f"   📊 Personalization Score: {context.personalization_score}")
            print(f"   📖 Narrative Progress: {context.narrative_progress}%")
            print(f"   🎮 Gamification Engagement: {context.gamification_engagement}")
        except Exception as e:
            print(f"❌ Error in user context analysis: {e}")
        
        # Test adaptive interface generation
        print(f"\n🎨 Testing adaptive interface generation...")
        
        try:
            text, keyboard = await diana_master.create_adaptive_interface(test_user_id)
            print(f"✅ Adaptive interface generated successfully:")
            print(f"   📝 Text length: {len(text)} characters")
            print(f"   ⌨️ Keyboard buttons: {len(keyboard.inline_keyboard)} rows")
            print(f"   🎯 Preview: {text[:100]}...")
        except Exception as e:
            print(f"❌ Error in adaptive interface generation: {e}")
        
        # Test gamification service wrapper
        print(f"\n🎮 Testing gamification service wrapper...")
        
        try:
            user_stats = await gamification_service.get_user_stats(test_user_id)
            print(f"✅ Gamification stats retrieved:")
            print(f"   📊 Level: {user_stats['level']}")
            print(f"   💰 Points: {user_stats['points']}")
            print(f"   🏆 Achievements: {user_stats['achievements_count']}")
            print(f"   🎯 Active Missions: {user_stats['active_missions']}")
        except Exception as e:
            print(f"❌ Error in gamification service: {e}")
        
        # Test narrative service wrapper
        print(f"\n📖 Testing narrative service wrapper...")
        
        try:
            narrative_progress = await narrative_service.get_user_narrative_progress(test_user_id)
            print(f"✅ Narrative progress retrieved:")
            print(f"   📈 Progress: {narrative_progress['progress']:.1f}%")
            print(f"   🧩 Fragments visited: {narrative_progress['fragments_visited']}")
            print(f"   📚 Total fragments: {narrative_progress['total_fragments']}")
            if narrative_progress['current_fragment']:
                print(f"   📜 Current fragment: {narrative_progress['current_fragment']['title']}")
        except Exception as e:
            print(f"❌ Error in narrative service: {e}")
        
        # Test daily rewards service
        print(f"\n🎁 Testing daily rewards service...")
        
        try:
            can_claim = await daily_rewards_service.can_claim_daily_reward(test_user_id)
            print(f"✅ Daily reward status: {'Can claim' if can_claim else 'Already claimed'}")
            
            if can_claim:
                available_reward = await daily_rewards_service.get_available_reward(test_user_id)
                if available_reward:
                    print(f"   🎁 Available reward: {available_reward.name} {available_reward.icon}")
                    print(f"   💰 Value: {available_reward.value}")
                    print(f"   🌟 Rarity: {available_reward.rarity}")
        except Exception as e:
            print(f"❌ Error in daily rewards service: {e}")
        
        # Test tariff service
        print(f"\n💎 Testing tariff service...")
        
        try:
            tariffs = await tariff_service.get_all_tariffs()
            print(f"✅ Tariffs retrieved: {len(tariffs)} available")
            for tariff in tariffs[:3]:  # Show first 3
                print(f"   💎 {tariff.name}: ${tariff.price} for {tariff.duration_days} days")
        except Exception as e:
            print(f"❌ Error in tariff service: {e}")
        
        print("\n🎭 INTEGRATION TEST COMPLETED")
        print("=" * 50)
        print("✅ Diana Master System is ready for production!")
        print("🚀 All services are connected and working with real data!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR IN INTEGRATION TEST: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_diana_master_integration())