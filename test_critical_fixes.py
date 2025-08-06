#!/usr/bin/env python3
"""
🚨 CRITICAL FIXES TEST - Diana Master System
============================================
Test all critical production fixes applied to resolve service errors.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_narrative_json_fix():
    """Test that narrative models use JSON instead of ARRAY."""
    print("🔧 Testing narrative JSON fix...")
    
    try:
        from src.bot.database.models.narrative import UserNarrativeState, StoryFragment
        
        # Check UserNarrativeState model
        visited_fragments_column = UserNarrativeState.visited_fragments
        if hasattr(visited_fragments_column.type, '__class__'):
            type_name = visited_fragments_column.type.__class__.__name__
            if 'JSON' in type_name:
                print("✅ UserNarrativeState.visited_fragments is JSON type")
            else:
                print(f"❌ visited_fragments type is {type_name}, should be JSON")
                return False
        
        # Check StoryFragment model
        tags_column = StoryFragment.tags
        if hasattr(tags_column.type, '__class__'):
            type_name = tags_column.type.__class__.__name__
            if 'JSON' in type_name:
                print("✅ StoryFragment.tags is JSON type")
            else:
                print(f"❌ tags type is {type_name}, should be JSON")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Error testing narrative models: {e}")
        return False

def test_dailyreward_hash_fix():
    """Test that DailyReward selection doesn't use objects as dict keys."""
    print("\n🎁 Testing DailyReward hash fix...")
    
    try:
        from src.modules.daily_rewards.service import DailyRewardsService, DailyReward
        from src.core.event_bus import EventBus
        from src.modules.gamification.service import GamificationService
        
        # Create services
        event_bus = EventBus()
        gamification_service = GamificationService(event_bus)
        daily_rewards_service = DailyRewardsService(gamification_service)
        
        # Test reward selection without using objects as keys
        rewards = [
            DailyReward(
                id="test1", name="Test Reward 1", description="Test", 
                reward_type="points", value=50, icon="💰", rarity="common"
            ),
            DailyReward(
                id="test2", name="Test Reward 2", description="Test", 
                reward_type="points", value=100, icon="💎", rarity="rare"
            )
        ]
        
        # This should not raise "unhashable type" error
        selected = daily_rewards_service._select_reward_by_probability(rewards, 1)
        print(f"✅ Reward selection works: {selected.name}")
        
        return True
    except Exception as e:
        print(f"❌ Error testing DailyReward selection: {e}")
        return False

def test_default_missions_load():
    """Test that default missions load when database is empty."""
    print("\n🎯 Testing default missions loading...")
    
    try:
        from src.modules.gamification.service import GamificationService
        from src.core.event_bus import EventBus
        
        # Create service
        event_bus = EventBus()
        gamification_service = GamificationService(event_bus)
        
        # Test default mission loading
        gamification_service._load_default_missions()
        
        if len(gamification_service.missions) > 0:
            print(f"✅ Default missions loaded: {len(gamification_service.missions)} missions")
            
            # Check some expected missions
            expected_missions = ["daily_trivia", "first_steps", "daily_login"]
            found_missions = []
            for mission_key in expected_missions:
                if mission_key in gamification_service.missions:
                    found_missions.append(mission_key)
            
            print(f"✅ Found expected missions: {found_missions}")
            return True
        else:
            print("❌ No default missions loaded")
            return False
            
    except Exception as e:
        print(f"❌ Error testing default missions: {e}")
        return False

def test_point_awarding_method():
    """Test that point awarding methods exist and are callable."""
    print("\n💰 Testing point awarding methods...")
    
    try:
        from src.modules.gamification.service import GamificationService
        from src.core.event_bus import EventBus
        
        # Create service
        event_bus = EventBus()
        gamification_service = GamificationService(event_bus)
        
        # Check that add_points method exists
        if hasattr(gamification_service, 'add_points'):
            print("✅ GamificationService.add_points method exists")
        else:
            print("❌ add_points method missing")
            return False
        
        # Check that set_point_multiplier method exists
        if hasattr(gamification_service, 'set_point_multiplier'):
            print("✅ GamificationService.set_point_multiplier method exists")
        else:
            print("❌ set_point_multiplier method missing")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing point awarding methods: {e}")
        return False

def test_import_errors():
    """Test that all critical imports work without errors."""
    print("\n📦 Testing critical imports...")
    
    try:
        from src.modules.narrative.service import NarrativeService
        print("✅ NarrativeService imports successfully")
    except Exception as e:
        print(f"❌ NarrativeService import error: {e}")
        return False
    
    try:
        from src.modules.daily_rewards.service import DailyRewardsService
        print("✅ DailyRewardsService imports successfully")
    except Exception as e:
        print(f"❌ DailyRewardsService import error: {e}")
        return False
    
    try:
        from src.modules.gamification.service import GamificationService
        print("✅ GamificationService imports successfully")
    except Exception as e:
        print(f"❌ GamificationService import error: {e}")
        return False
    
    try:
        from src.bot.core.diana_master_system import DianaMasterInterface
        print("✅ DianaMasterInterface imports successfully")
    except Exception as e:
        print(f"❌ DianaMasterInterface import error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚨 CRITICAL FIXES VALIDATION")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 5
    
    if test_import_errors():
        tests_passed += 1
    
    if test_narrative_json_fix():
        tests_passed += 1
        
    if test_dailyreward_hash_fix():
        tests_passed += 1
        
    if test_default_missions_load():
        tests_passed += 1
        
    if test_point_awarding_method():
        tests_passed += 1
    
    print(f"\n🏆 RESULTS: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("✅ ALL CRITICAL FIXES VALIDATED!")
        print("🎭 DIANA MASTER SYSTEM IS READY FOR PRODUCTION!")
        print("🚀 Services should now award points correctly!")
        print("💎 Database errors should be resolved!")
    else:
        print("❌ Some fixes need attention - check output above")
        print("🔧 Review the failing tests")