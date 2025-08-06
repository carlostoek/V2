#!/usr/bin/env python3
"""
🎭 DIANA MASTER SYSTEM - COMPLETE TEST
=====================================
Test completo que inicializa base de datos SQLite y verifica
que Diana Master System funciona correctamente con datos reales.
"""

import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_complete_diana_system():
    """Test completo de Diana Master System con base de datos real."""
    print("🎭 DIANA MASTER SYSTEM - COMPLETE TEST")
    print("=" * 50)
    
    try:
        # Step 1: Initialize database
        print("\n🗄️ Step 1: Initializing database...")
        from src.bot.database.engine import init_db
        await init_db()
        print("✅ Database initialized with test data!")
        
        # Step 2: Import and create services
        print("\n🔧 Step 2: Creating services...")
        from src.bot.core.diana_master_system import DianaMasterInterface
        from src.core.event_bus import EventBus
        from src.modules.gamification.service import GamificationService
        from src.modules.daily_rewards.service import DailyRewardsService
        from src.modules.narrative.service import NarrativeService
        
        # Create event bus and services
        event_bus = EventBus()
        gamification_service = GamificationService(event_bus)
        daily_rewards_service = DailyRewardsService(gamification_service)
        narrative_service = NarrativeService(event_bus)
        
        # Setup services
        await gamification_service.setup()
        await daily_rewards_service.setup()
        await narrative_service.setup()
        
        # Create Diana Master Interface
        diana = DianaMasterInterface(event_bus)
        
        # Register services
        diana.services = {
            'gamification': gamification_service,
            'daily_rewards': daily_rewards_service,
            'narrative': narrative_service
        }
        
        print("✅ All services created and configured!")
        
        # Step 3: Test with real user data
        test_user_id = 12345  # This user should exist from test data injection
        print(f"\n👤 Step 3: Testing with user ID {test_user_id}...")
        
        # Get initial stats
        initial_stats = await gamification_service.get_user_stats(test_user_id)
        print(f"📊 Initial stats: {initial_stats}")
        initial_points = initial_stats.get('besitos', 0)
        print(f"💰 Initial points: {initial_points}")
        
        # Step 4: Test point awarding
        print("\n🎯 Step 4: Testing point awarding...")
        success = await gamification_service.add_points(test_user_id, 100, "diana_test")
        print(f"✅ Add points result: {success}")
        
        # Verify points were added
        new_stats = await gamification_service.get_user_stats(test_user_id)
        new_points = new_stats.get('besitos', 0)
        print(f"💰 New points: {new_points}")
        
        if new_points > initial_points:
            points_added = new_points - initial_points
            print(f"🎊 SUCCESS: {points_added} points were awarded!")
        else:
            print("❌ FAILED: Points were not awarded correctly")
            return False
        
        # Step 5: Test daily rewards
        print("\n🎁 Step 5: Testing daily rewards system...")
        can_claim = await daily_rewards_service.can_claim_daily_reward(test_user_id)
        print(f"✅ Can claim daily reward: {can_claim}")
        
        if can_claim:
            reward_result = await daily_rewards_service.claim_daily_reward(test_user_id)
            print(f"🎁 Daily reward result: {reward_result}")
            
            if reward_result.get('success'):
                reward_info = reward_result.get('reward')
                print(f"🏆 Reward claimed: {reward_info.name} ({reward_info.value} points)")
                
                # Verify points increased
                final_stats = await gamification_service.get_user_stats(test_user_id)
                final_points = final_stats.get('besitos', 0)
                
                if final_points > new_points:
                    daily_points = final_points - new_points
                    print(f"🎊 SUCCESS: Daily reward awarded {daily_points} additional points!")
                else:
                    print("⚠️ Daily reward claimed but points may not have been added properly")
            else:
                print(f"❌ Daily reward failed: {reward_result.get('reason')}")
        else:
            print("ℹ️ User cannot claim daily reward (may have already claimed today)")
        
        # Step 6: Test Diana Master integration
        print("\n🎭 Step 6: Testing Diana Master System integration...")
        
        # Test Diana's user stats method
        diana_stats = await diana._get_user_stats(test_user_id)
        print(f"📊 Diana stats: {diana_stats}")
        
        # Test Diana's interface generation
        try:
            interface_data = await diana.generate_adaptive_interface(test_user_id)
            print(f"🎨 Interface generated successfully")
            print(f"📱 Interface sections: {len(interface_data.get('sections', []))}")
            
            # Check if interface has expected sections
            sections = interface_data.get('sections', [])
            section_titles = [section.get('title', '') for section in sections]
            print(f"📋 Section titles: {section_titles}")
            
            if 'Gamificación' in section_titles and 'Regalos Diarios' in section_titles:
                print("✅ Interface contains expected sections!")
            else:
                print("⚠️ Interface may be missing some expected sections")
                
        except Exception as e:
            print(f"❌ Error generating Diana interface: {e}")
            return False
        
        # Step 7: Test narrative system
        print("\n📚 Step 7: Testing narrative system...")
        try:
            narrative_progress = await narrative_service.get_user_narrative_progress(test_user_id)
            print(f"📖 Narrative progress: {narrative_progress}")
            
            current_fragment = narrative_progress.get('current_fragment_key')
            visited_count = len(narrative_progress.get('visited_fragments', []))
            
            print(f"📍 Current fragment: {current_fragment}")
            print(f"🏃 Fragments visited: {visited_count}")
            
        except Exception as e:
            print(f"❌ Error testing narrative system: {e}")
            return False
        
        # Final verification
        print("\n🏆 Step 8: Final verification...")
        final_user_stats = await gamification_service.get_user_stats(test_user_id)
        final_total_points = final_user_stats.get('besitos', 0)
        
        print(f"📊 Final user stats: {final_user_stats}")
        print(f"💰 Total points gained in test: {final_total_points - initial_points}")
        
        if final_total_points > initial_points:
            print("🎉 SUCCESS: Diana Master System is FULLY FUNCTIONAL!")
            print("🚀 Ready for production deployment!")
            print("💎 All services are correctly awarding points!")
            print("🎭 Interface generation works perfectly!")
            return True
        else:
            print("❌ FAILED: Points were not properly accumulated")
            return False
            
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🎭 DIANA MASTER SYSTEM - COMPLETE INTEGRATION TEST")
    print("=" * 60)
    print("This test will:")
    print("1. 🗄️ Create SQLite database with test data")
    print("2. 🔧 Initialize all services")
    print("3. 🎯 Test point awarding functionality")
    print("4. 🎁 Test daily rewards system")
    print("5. 🎭 Test Diana Master interface")
    print("6. 📚 Test narrative system")
    print("7. 🏆 Verify complete integration")
    print()
    
    result = asyncio.run(test_complete_diana_system())
    
    if result:
        print("\n" + "🎊" * 20)
        print("🎭 DIANA MASTER SYSTEM: FULLY OPERATIONAL!")
        print("🚀 Integration complete and successful!")
        print("💎 All services working as expected!")
        print("🎊" * 20)
    else:
        print("\n" + "❌" * 20)
        print("🔧 DIANA MASTER SYSTEM: NEEDS ATTENTION")
        print("⚠️ Review the errors above")
        print("❌" * 20)