#!/usr/bin/env python3
"""
Test the incident wiki setup
"""
import sys
import os

def test_setup():
    print("🧪 Testing Incident Wiki Setup...\n")
    
    # Test 1: Check if incidents directory exists
    print("1️⃣  Checking incidents directory...")
    if os.path.isdir("incidents"):
        print("   ✅ incidents/ directory found")
        incident_files = [f for f in os.listdir("incidents") if f.endswith(".yaml")]
        print(f"   📄 Found {len(incident_files)} incident file(s)")
    else:
        print("   ❌ incidents/ directory not found")
        return False
    
    # Test 2: Try importing incident manager
    print("\n2️⃣  Testing incident manager...")
    try:
        sys.path.insert(0, "src")
        from incident_manager import IncidentManager
        print("   ✅ incident_manager imported successfully")
        
        manager = IncidentManager("incidents")
        incidents = manager.get_all_incidents()
        print(f"   📋 Loaded {len(incidents)} incident(s)")
        
        for incident_id, incident in incidents.items():
            print(f"      • {incident_id}: {incident.get('name', 'Unknown')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 3: Test search functionality
    print("\n3️⃣  Testing search...")
    try:
        results = manager.search("database")
        print(f"   ✅ Search found {len(results)} result(s)")
        for result in results:
            print(f"      • {result.get('name')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 4: Check Slack integration
    print("\n4️⃣  Checking Slack integration...")
    try:
        from slack_handler import SlackIncidentHandler
        
        if os.getenv("SLACK_BOT_TOKEN"):
            print("   ✅ SLACK_BOT_TOKEN found in environment")
            handler = SlackIncidentHandler()
            print("   ✅ Slack handler initialized successfully")
        else:
            print("   ⚠️  SLACK_BOT_TOKEN not set (optional for now)")
            print("      Set in .env to enable Slack integration")
    except ImportError:
        print("   ⚠️  slack-sdk not installed")
        print("      Run: pip install -r requirements.txt")
    except Exception as e:
        print(f"   ⚠️  {e}")
    
    # Test 5: CLI interface
    print("\n5️⃣  Testing CLI...")
    try:
        from cli import main
        print("   ✅ CLI module loaded successfully")
        print("   Try: python src/cli.py list")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "="*50)
    print("✅ Setup test complete!")
    print("="*50)
    print("\n📚 Next steps:")
    print("1. Add incidents to incidents/ directory")
    print("2. Test CLI: python src/cli.py list")
    print("3. Set up Slack: cp .env.example .env")
    print("4. Read USAGE.md for full documentation")
    
    return True


if __name__ == "__main__":
    success = test_setup()
    sys.exit(0 if success else 1)
