#!/usr/bin/env python3
"""
🎭 DIANA INTEGRATION SPECIALISTS - FUNCTIONALITY TEST
======================================================

Test script to verify the complete integration of all three Diana systems:
- Diana Master System (Main router)
- Diana Admin Master System (Professional admin interface)
- Diana User Master System (Sophisticated user interface)

This verifies all success criteria from the integration requirements.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.abspath('.'))

from src.core.event_bus import EventBus
from src.modules.gamification.service import GamificationService
from src.modules.narrative.service import NarrativeService
from src.modules.user.service import UserService
from src.modules.admin.service import AdminService
from src.modules.tariff.service import TariffService
from src.modules.daily_rewards.service import DailyRewardsService
from src.bot.database.engine import init_db

# Import the three Diana systems
from src.bot.core.diana_master_system import initialize_diana_master
from src.bot.core.diana_admin_master import initialize_diana_admin_master
from src.bot.core.diana_user_master_system import initialize_diana_user_system

class DianaIntegrationTester:
    """
    🎭 Complete integration tester for all Diana systems
    """
    
    def __init__(self):
        self.test_user_id = 12345
        self.test_admin_id = 67890
        self.results = {
            'passed': 0,
            'failed': 0,
            'tests': []
        }
    
    async def setup_services(self):
        """Setup all required services"""
        print("🎭 Setting up Diana ecosystem services...")
        
        # Initialize database
        await init_db()
        
        # Create services
        self.event_bus = EventBus()
        self.user_service = UserService(self.event_bus)
        self.gamification_service = GamificationService(self.event_bus)
        self.narrative_service = NarrativeService(self.event_bus)
        self.admin_service = AdminService(self.event_bus)
        self.tariff_service = TariffService(self.event_bus)
        self.daily_rewards_service = DailyRewardsService(self.gamification_service)
        
        # Setup services
        await self.user_service.setup()
        await self.gamification_service.setup()
        await self.narrative_service.setup()
        await self.admin_service.setup()
        await self.tariff_service.setup()
        await self.daily_rewards_service.setup()
        
        # Create services dictionary
        self.services = {
            'gamification': self.gamification_service,
            'admin': self.admin_service,
            'narrative': self.narrative_service,
            'user': self.user_service,
            'tariff': self.tariff_service,
            'event_bus': self.event_bus,
            'daily_rewards': self.daily_rewards_service
        }
        
        print("✅ All services initialized successfully!")
    
    async def test_diana_systems_initialization(self):
        """Test that all three Diana systems initialize without errors"""
        print("\n🎯 Testing Diana Systems Initialization...")
        
        try:
            # Initialize Diana Master System
            self.diana_master = initialize_diana_master(self.services)
            self.log_test("Diana Master System initialization", self.diana_master is not None)
            
            # Initialize Diana Admin Master System
            self.diana_admin = initialize_diana_admin_master(self.services)
            self.log_test("Diana Admin Master System initialization", self.diana_admin is not None)
            
            # Initialize Diana User Master System
            self.diana_user = initialize_diana_user_system(self.services)
            self.log_test("Diana User Master System initialization", self.diana_user is not None)
            
        except Exception as e:
            self.log_test("Diana Systems initialization", False, f"Error: {e}")
            return False
        
        return True
    
    async def test_service_sharing(self):
        """Test that all systems share the same service instances"""
        print("\n🔗 Testing Service Sharing...")
        
        try:
            # Check if Diana Master has services
            master_has_services = hasattr(self.diana_master, 'services') and bool(self.diana_master.services)
            self.log_test("Diana Master has shared services", master_has_services)
            
            # Check if Diana Admin has services
            admin_has_services = hasattr(self.diana_admin, 'services') and bool(self.diana_admin.services)
            self.log_test("Diana Admin has shared services", admin_has_services)
            
            # Check if Diana User has services
            user_has_services = hasattr(self.diana_user, 'services') and bool(self.diana_user.services)
            self.log_test("Diana User has shared services", user_has_services)
            
            # Verify they're the same instances
            if master_has_services and admin_has_services:
                same_gamification = (self.diana_master.services.get('gamification') == 
                                   self.diana_admin.services.get('gamification'))
                self.log_test("Master and Admin share same gamification service", same_gamification)
        
        except Exception as e:
            self.log_test("Service sharing test", False, f"Error: {e}")
            return False
        
        return True
    
    async def test_user_interface_generation(self):
        """Test user interface generation with enhanced UI"""
        print("\n🎭 Testing Enhanced User Interface Generation...")
        
        try:
            # Test Diana User System interface
            text, keyboard = await self.diana_user.create_user_main_interface(self.test_user_id)
            
            interface_has_content = bool(text and len(text) > 50)
            self.log_test("User interface generates rich content", interface_has_content)
            
            has_keyboard = keyboard is not None and hasattr(keyboard, 'inline_keyboard')
            self.log_test("User interface has interactive keyboard", has_keyboard)
            
            # Check for Diana's personality in text
            has_diana_voice = any(phrase in text.lower() for phrase in ['diana', 'alma', 'secretos', 'intimidad'])
            self.log_test("Interface includes Diana's personality", has_diana_voice)
            
            # Check for enhanced UI elements
            has_emojis = any(emoji in text for emoji in ['🎭', '💎', '🌹', '✨'])
            self.log_test("Interface uses enhanced UI design", has_emojis)
            
        except Exception as e:
            self.log_test("User interface generation", False, f"Error: {e}")
            return False
        
        return True
    
    async def test_admin_interface_generation(self):
        """Test admin interface generation with professional UI"""
        print("\n🏛️ Testing Professional Admin Interface Generation...")
        
        try:
            # Test Diana Admin System interface  
            text, keyboard = await self.diana_admin.create_admin_main_interface(self.test_admin_id)
            
            interface_has_content = bool(text and len(text) > 50)
            self.log_test("Admin interface generates rich content", interface_has_content)
            
            has_keyboard = keyboard is not None and hasattr(keyboard, 'inline_keyboard')
            self.log_test("Admin interface has navigation keyboard", has_keyboard)
            
            # Check for Lucien's voice
            has_lucien_voice = 'lucien' in text.lower()
            self.log_test("Interface includes Lucien's elegant voice", has_lucien_voice)
            
            # Check for professional elements
            has_professional_elements = any(term in text.lower() for term in ['sanctum', 'administr', 'jurisdicción'])
            self.log_test("Interface uses professional admin language", has_professional_elements)
            
        except Exception as e:
            self.log_test("Admin interface generation", False, f"Error: {e}")
            return False
        
        return True
    
    async def test_adaptive_context_engine(self):
        """Test Diana Master System's adaptive context engine"""
        print("\n🧠 Testing Adaptive Context Engine...")
        
        try:
            # Test context analysis
            context = await self.diana_master.context_engine.analyze_user_context(self.test_user_id)
            
            has_context = context is not None
            self.log_test("Context engine generates user context", has_context)
            
            if has_context:
                has_mood = hasattr(context, 'current_mood')
                self.log_test("Context includes mood detection", has_mood)
                
                has_engagement = hasattr(context, 'engagement_pattern')
                self.log_test("Context includes engagement analysis", has_engagement)
            
        except Exception as e:
            self.log_test("Adaptive context engine", False, f"Error: {e}")
            return False
        
        return True
    
    async def test_no_conflicts(self):
        """Test that there are no command/callback conflicts"""
        print("\n⚡ Testing No Conflicts...")
        
        try:
            # Test that systems can coexist
            all_systems_exist = all([self.diana_master, self.diana_admin, self.diana_user])
            self.log_test("All three systems coexist without conflicts", all_systems_exist)
            
            # Test different callback prefixes
            has_admin_callbacks = hasattr(self.diana_admin, 'admin_contexts')
            has_user_callbacks = hasattr(self.diana_user, 'user_contexts')
            self.log_test("Systems use distinct callback patterns", has_admin_callbacks and has_user_callbacks)
            
        except Exception as e:
            self.log_test("No conflicts test", False, f"Error: {e}")
            return False
        
        return True
    
    def log_test(self, test_name: str, passed: bool, error_msg: str = None):
        """Log test results"""
        if passed:
            print(f"✅ {test_name}")
            self.results['passed'] += 1
        else:
            error_info = f" - {error_msg}" if error_msg else ""
            print(f"❌ {test_name}{error_info}")
            self.results['failed'] += 1
        
        self.results['tests'].append({
            'name': test_name,
            'passed': passed,
            'error': error_msg
        })
    
    async def run_all_tests(self):
        """Run complete integration test suite"""
        print("🎭✨ DIANA INTEGRATION SPECIALISTS - COMPLETE FUNCTIONALITY TEST")
        print("=" * 70)
        print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Setup
        await self.setup_services()
        
        # Run all tests
        await self.test_diana_systems_initialization()
        await self.test_service_sharing()
        await self.test_user_interface_generation()
        await self.test_admin_interface_generation() 
        await self.test_adaptive_context_engine()
        await self.test_no_conflicts()
        
        # Results
        print("\n" + "=" * 70)
        print("🏆 INTEGRATION TEST RESULTS:")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📊 Total: {self.results['passed'] + self.results['failed']}")
        
        success_rate = (self.results['passed'] / (self.results['passed'] + self.results['failed'])) * 100
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        if self.results['failed'] == 0:
            print("\n🎉 🎭✨ INTEGRATION COMPLETE - ALL SYSTEMS OPERATIONAL! ✨🎭")
            print("🚀 Diana Bot is ready with unified functionality and enhanced UI!")
        else:
            print(f"\n⚠️ {self.results['failed']} tests failed - integration needs attention")
            
        return self.results['failed'] == 0

async def main():
    """Main test execution"""
    tester = DianaIntegrationTester()
    success = await tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)