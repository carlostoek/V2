#!/usr/bin/env python3
"""
🎭 Diana UX Enhancements Integration Test
========================================

Quick test script to verify all UX enhancement components
are properly integrated and functioning correctly.
"""

import asyncio
import sys
from datetime import datetime
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, '/home/carlostoek/repos/dianabot/V2')

# Test imports
try:
    from src.bot.core.diana_user_ux_enhancer import create_diana_ux_enhancer
    from src.bot.core.diana_personality_engine import create_diana_personality_engine
    from src.bot.core.diana_conversion_optimizer import create_diana_conversion_optimizer
    from src.bot.utils.enhanced_error_handler import create_diana_error_handler
    from src.bot.middleware.user_experience import create_user_experience_middleware
    
    print("✅ All UX enhancement imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

class MockServices:
    """Mock services for testing"""
    
    def __init__(self):
        self.services = {
            'gamification': MockGamificationService(),
            'admin': MockAdminService(),
            'narrative': MockNarrativeService(),
            'event_bus': MockEventBus()
        }
    
    def get(self, service_name):
        return self.services.get(service_name)
    
    def __getitem__(self, key):
        return self.services.get(key)

class MockGamificationService:
    """Mock gamification service"""
    
    async def get_user_stats(self, user_id: int):
        return {
            'level': 3,
            'points': 150,
            'streak': 5,
            'total_interactions': 25,
            'achievements_count': 2,
            'active_missions': ['daily_login', 'explore_features']
        }

class MockAdminService:
    """Mock admin service"""
    
    async def is_vip_user(self, user_id: int):
        # Test user 12345 is VIP for testing
        return user_id == 12345
    
    async def send_admin_notification(self, message: str):
        print(f"📢 Admin Notification: {message[:100]}...")
        return True

class MockNarrativeService:
    """Mock narrative service"""
    
    async def get_user_progress(self, user_id: int):
        return {'level': 2, 'progress': 0.4}
    
    async def get_user_narrative_progress(self, user_id: int):
        return {'progress': 0.6, 'chapter': 'Getting to Know Diana'}

class MockEventBus:
    """Mock event bus"""
    
    async def publish(self, event):
        print(f"📡 Event Published: {type(event).__name__}")

async def test_ux_enhancer():
    """Test UX Enhancer functionality"""
    print("\n🧪 Testing UX Enhancer...")
    
    try:
        services = MockServices()
        ux_enhancer = create_diana_ux_enhancer(services)
        
        # Test user preference analysis
        preferences = await ux_enhancer.analyze_user_ux_preferences(12345)
        print(f"✅ UX Preferences analyzed: {preferences.preferred_navigation.value}")
        
        # Test keyboard enhancement
        enhanced_keyboard = ux_enhancer.enhance_main_keyboard(
            original_keyboard=None,
            user_id=12345,
            tier="FREE",
            ux_preferences=preferences
        )
        
        print(f"✅ Enhanced keyboard generated with {len(enhanced_keyboard.inline_keyboard)} rows")
        
        # Test contextual help
        help_message = ux_enhancer.get_contextual_help_message("main", preferences)
        if help_message:
            print(f"✅ Contextual help generated: {help_message[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ UX Enhancer test failed: {e}")
        return False

async def test_personality_engine():
    """Test Personality Engine functionality"""
    print("\n🎭 Testing Personality Engine...")
    
    try:
        services = MockServices()
        personality_engine = create_diana_personality_engine(services)
        
        # Test personality context creation
        context = await personality_engine.get_personality_context(12345)
        print(f"✅ Personality context created: {context.relationship_stage.value}")
        
        # Test Diana message generation
        greeting = personality_engine.generate_diana_message(12345, "greetings")
        print(f"✅ Diana greeting generated: {greeting[:80]}...")
        
        # Test Lucien insight
        lucien_insight = personality_engine.generate_lucien_insight(12345, "observation")
        print(f"✅ Lucien insight generated: {lucien_insight[:60]}...")
        
        # Test tone adaptation
        tone = personality_engine.adapt_personality_for_context(12345, "conversion")
        print(f"✅ Personality tone adapted: {tone.value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Personality Engine test failed: {e}")
        return False

async def test_conversion_optimizer():
    """Test Conversion Optimizer functionality"""
    print("\n💎 Testing Conversion Optimizer...")
    
    try:
        services = MockServices()
        optimizer = create_diana_conversion_optimizer(services)
        
        # Test conversion readiness analysis
        opportunity = await optimizer.analyze_conversion_readiness(12345)
        print(f"✅ Conversion opportunity analyzed: {opportunity.intent_level.value} ({opportunity.confidence_score:.2f})")
        
        # Test event tracking
        optimizer.track_conversion_event(12345, "vip_info_viewed")
        print("✅ Conversion event tracked")
        
        # Test analytics
        analytics = optimizer.get_conversion_analytics()
        print(f"✅ Conversion analytics generated: {analytics}")
        
        return True
        
    except Exception as e:
        print(f"❌ Conversion Optimizer test failed: {e}")
        return False

async def test_error_handler():
    """Test Error Handler functionality"""
    print("\n🛡️ Testing Error Handler...")
    
    try:
        services = MockServices()
        error_handler = create_diana_error_handler(services)
        
        # Test error handling
        test_error = Exception("Test service unavailable")
        message, keyboard = await error_handler.handle_error(
            error=test_error,
            user_id=12345,
            user_action="test_action",
            context_data={'test': True}
        )
        
        print(f"✅ Error handled gracefully: {message[:80]}...")
        print(f"✅ Recovery keyboard generated with {len(keyboard.inline_keyboard)} options")
        
        # Test analytics
        analytics = error_handler.get_error_analytics(12345)
        print(f"✅ Error analytics generated: {analytics}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error Handler test failed: {e}")
        return False

async def test_middleware():
    """Test User Experience Middleware"""
    print("\n🌟 Testing User Experience Middleware...")
    
    try:
        services = MockServices()
        middleware = create_user_experience_middleware(services)
        
        print("✅ User Experience Middleware created successfully")
        
        # Test onboarding status
        onboarding_status = middleware.get_user_onboarding_status(12345)
        print(f"✅ Onboarding status retrieved: {onboarding_status}")
        
        # Test conversion signal tracking
        middleware.add_conversion_signal(12345, "vip_interest")
        print("✅ Conversion signal added")
        
        return True
        
    except Exception as e:
        print(f"❌ Middleware test failed: {e}")
        return False

async def run_integration_tests():
    """Run complete integration test suite"""
    print("🎭 Diana UX Enhancements - Integration Test Suite")
    print("=" * 55)
    
    tests = [
        ("UX Enhancer", test_ux_enhancer),
        ("Personality Engine", test_personality_engine),
        ("Conversion Optimizer", test_conversion_optimizer),
        ("Error Handler", test_error_handler),
        ("Experience Middleware", test_middleware)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 55)
    print("🎯 Test Results Summary:")
    print("=" * 55)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:20} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All UX Enhancement systems are working correctly!")
        print("🚀 Bot is ready for enhanced user experiences!")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please review the issues above.")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = asyncio.run(run_integration_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        sys.exit(1)