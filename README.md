# Merchant Settlement Incidents Wiki

A searchable wiki for managing merchant settlement incidents with YAML-based incident files and Slack integration.

## 🎯 Overview

This is a centralized incident management system that allows you to:
- **Define incidents** as YAML files with structured troubleshooting steps
- **Search quickly** by incident name, ID, or aliases
- **Get instant Slack alerts** when incidents are triggered
- **Follow runbooks** for consistent resolution procedures
- **Track SLAs** to ensure timely incident response

## 🚀 Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Add environment variables** (for Slack):
   ```bash
   cp .env.example .env
   # Edit .env with your Slack bot token
   ```

3. **Search for incidents**:
   ```bash
   python src/cli.py list                    # Show all incidents
   python src/cli.py search database         # Search by keyword
   python src/cli.py show db-connection-timeout  # Show full details
   ```

4. **Send to Slack**:
   ```bash
   python src/cli.py slack db-connection-timeout
   ```

## 📁 Project Structure

```
incidents/                           # Incident YAML files
├── example-database-connection-timeout.yaml
└── example-payment-processing-failure.yaml

src/
├── incident_manager.py             # Search and retrieval
├── slack_handler.py                # Slack integration
└── cli.py                          # Command-line interface
```

## 📖 Full Documentation

See [USAGE.md](USAGE.md) for complete documentation on:
- Creating incidents
- Email notification setup
- Slack integration setup (optional)
- CLI reference
- Python API
- Best practices

## 🔑 Key Features

✅ **YAML-Based** - Human-readable incident definitions  
✅ **Searchable** - Find incidents by name, ID, or aliases  
✅ **Email Alerts** - Send formatted incident details via email (no Slack required!)  
✅ **Slack Integration** - Optional: send incident details directly to Slack  
✅ **Runbooks** - Step-by-step troubleshooting procedures  
✅ **SLA Tracking** - Monitor resolution times  
✅ **CLI & API** - Both command-line and programmatic interfaces

## 💡 Example

```yaml
---
name: "Database Connection Timeout"
id: "db-connection-timeout"
severity: "critical"
description: "Database connection pool exhausted"
triggers:
  - "High API latency"
  - "Error: connection timeout"
troubleshooting:
  - step: "Check active connections"
    command: "SELECT COUNT(*) FROM pg_stat_activity;"
runbook: |
  1. Check database metrics
  2. Kill idle connections if needed
  3. Escalate if persistent
escalation:
  level_1: "Check dashboard"
  level_2: "Contact DBA"
  level_3: "Start incident response"
slack_notification: true
resolution_time_sla: 15
```

## 🚨 When Triggered

1. Monitoring system detects incident
2. Calls: `handler.send_incident_alert("db-connection-timeout")`
3. Slack message sent with full incident details
4. Team follows runbook to resolve
5. Issue tracked against SLA

---

👉 **Get started**: Follow the Quick Start above and see [USAGE.md](USAGE.md) for detailed setup
