#!/usr/bin/env python3
"""
Command-line interface for incident wiki
Usage: python src/cli.py <command> [args]
"""
import sys
from incident_manager import IncidentManager

try:
    from slack_handler import SlackIncidentHandler
    SLACK_AVAILABLE = True
except ImportError:
    SLACK_AVAILABLE = False

try:
    from email_handler import EmailHandler
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False


def print_usage():
    """Print CLI usage information."""
    print("""
📚 Incident Wiki CLI

Usage: python src/cli.py <command> [args]

Commands:
  list                          List all incidents
  search <query>                Search incidents by name/ID/alias
  show <incident-id>            Show full incident details
  runbook <incident-id>         Show incident runbook
  slack <incident-id> [channel] Send incident to Slack
  slack-search <query>          Search and send results to Slack
  email <incident-id> [recipients] Send incident via email
  email-search <query>          Search and send results via email

Examples:
  python src/cli.py list
  python src/cli.py search database
  python src/cli.py show db-connection-timeout
  python src/cli.py runbook payment-processing-failure
  python src/cli.py slack db-connection-timeout
  python src/cli.py email db-connection-timeout
  python src/cli.py email db-connection-timeout "team@example.com,oncall@example.com"
    """)


def main():
    if len(sys.argv) < 2:
        print_usage()
        return
    
    command = sys.argv[1]
    manager = IncidentManager()
    
    if command == "list":
        print("\n📋 All Incidents:\n")
        incidents = manager.get_all_incidents()
        if not incidents:
            print("  No incidents found")
        else:
            for incident_id, incident in incidents.items():
                severity = incident.get("severity", "unknown")
                print(f"  • {incident_id}")
                print(f"    {incident.get('name', 'Unknown')}")
                print(f"    Severity: {severity}")
                print()
    
    elif command == "search":
        if len(sys.argv) < 3:
            print("❌ Missing search query")
            return
        query = " ".join(sys.argv[2:])
        results = manager.search(query)
        
        if not results:
            print(f"❌ No incidents found matching '{query}'")
        else:
            print(f"\n🔍 Search Results for '{query}':\n")
            for incident in results:
                print(manager.get_incident_summary(incident))
    
    elif command == "show":
        if len(sys.argv) < 3:
            print("❌ Missing incident ID")
            return
        incident_id = sys.argv[2]
        incident = manager.get_incident(incident_id)
        
        if not incident:
            print(f"❌ Incident '{incident_id}' not found")
        else:
            import json
            print("\n" + json.dumps(incident, indent=2))
    
    elif command == "runbook":
        if len(sys.argv) < 3:
            print("❌ Missing incident ID")
            return
        incident_id = sys.argv[2]
        incident = manager.get_incident(incident_id)
        
        if not incident:
            print(f"❌ Incident '{incident_id}' not found")
        else:
            print(f"\n📖 Runbook for {incident.get('name', 'Unknown')}:\n")
            print(manager.get_incident_runbook(incident))
    
    elif command == "slack":
        if not SLACK_AVAILABLE:
            print("❌ Slack integration not available. Install slack-sdk: pip install slack-sdk")
            return
        
        if len(sys.argv) < 3:
            print("❌ Missing incident ID")
            return
        
        incident_id = sys.argv[2]
        channel = sys.argv[3] if len(sys.argv) > 3 else None
        
        try:
            handler = SlackIncidentHandler()
            handler.send_incident_alert(incident_id, channel)
        except ValueError as e:
            print(f"❌ {e}")
    
    elif command == "slack-search":
        if not SLACK_AVAILABLE:
            print("❌ Slack integration not available. Install slack-sdk: pip install slack-sdk")
            return
        
        if len(sys.argv) < 3:
            print("❌ Missing search query")
            return
        
        query = " ".join(sys.argv[2:])
        channel = sys.argv[-1] if len(sys.argv) > 3 and sys.argv[-1].startswith("#") else None
        
        try:
            handler = SlackIncidentHandler()
            handler.send_search_results(query, channel)
        except ValueError as e:
            print(f"❌ {e}")
    
    elif command == "email":
        if not EMAIL_AVAILABLE:
            print("❌ Email integration not available. Install dependencies: pip install -r requirements.txt")
            return
        
        if len(sys.argv) < 3:
            print("❌ Missing incident ID")
            return
        
        incident_id = sys.argv[2]
        recipients = None
        
        if len(sys.argv) > 3:
            recipients = [r.strip() for r in sys.argv[3].split(",")]
        
        try:
            handler = EmailHandler()
            handler.send_incident_alert(incident_id, recipients)
        except ValueError as e:
            print(f"❌ {e}")
            return
    
    elif command == "email-search":
        if not EMAIL_AVAILABLE:
            print("❌ Email integration not available. Install dependencies: pip install -r requirements.txt")
            return
        
        if len(sys.argv) < 3:
            print("❌ Missing search query")
            return
        
        query = " ".join(sys.argv[2:])
        recipients = None
        
        if len(sys.argv) > 3 and "@" in sys.argv[-1]:
            recipients = [r.strip() for r in sys.argv[-1].split(",")]
        
        try:
            handler = EmailHandler()
            handler.send_search_results(query, recipients)
        except ValueError as e:
            print(f"❌ {e}")
            return
    
    else:
        print(f"❌ Unknown command: {command}")
        print_usage()


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
