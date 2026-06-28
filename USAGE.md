# Incident Wiki

A simple, searchable wiki for managing incidents with YAML-based incident files. Integrates with Slack to instantly send incident information when alerts are triggered.

## 🎯 Features

- **YAML-Based Incidents**: Define incidents with structured information
- **Fast Search**: Search by incident name, ID, aliases, or description
- **Slack Integration**: Automatically send incident details to Slack channels
- **CLI Interface**: Command-line tools for searching and managing incidents
- **Easy Escalation**: Predefined escalation paths and SLAs
- **Runbooks**: Step-by-step troubleshooting procedures for each incident

## 📁 Project Structure

```
mp-incidents-wiki/
├── incidents/                          # Incident YAML files
│   ├── example-database-connection-timeout.yaml
│   └── example-payment-processing-failure.yaml
├── src/
│   ├── incident_manager.py            # Core search and retrieval
│   ├── slack_handler.py               # Slack integration
│   └── cli.py                         # Command-line interface
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment variables template
└── README.md
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

```bash
cp .env.example .env
# Edit .env and add your Slack bot token and signing secret
```

### 3. Create Your First Incident

Create a new YAML file in the `incidents/` directory. Example structure:

```yaml
---
name: "Your Incident Name"
id: "unique-incident-id"
severity: "critical"  # critical, high, medium, low
description: "What is this incident about?"
aliases:
  - "Alternative name"
  - "Another way to refer to it"

triggers:
  - "What indicates this incident is happening?"
  - "Common error messages or conditions"

troubleshooting:
  - step: "First thing to check"
    command: "Any command to run"
    description: "What to look for"
  
  - step: "Second thing"
    url: "Link to relevant resource"
    description: "What this tells you"

escalation:
  level_1: "Initial response (team member)"
  level_2: "Secondary response (team lead)"
  level_3: "Critical response (manager)"

runbook: |
  1. Check X
  2. If problem found, do Y
  3. Escalate if needed
  
slack_notification: true
notify_channels:
  - "#incidents"
  - "#your-team"

resolution_time_sla: 15  # minutes
```

## 📖 Usage

### CLI Commands

List all incidents:
```bash
python src/cli.py list
```

Search for incidents:
```bash
python src/cli.py search database
python src/cli.py search "payment"
```

Show full incident details:
```bash
python src/cli.py show db-connection-timeout
```

Get incident runbook:
```bash
python src/cli.py runbook db-connection-timeout
```

### Slack Integration

Send incident to Slack:
```bash
python src/cli.py slack db-connection-timeout
python src/cli.py slack db-connection-timeout "#critical-alerts"
```

Search and send results to Slack:
```bash
python src/cli.py slack-search database
```

### Python Integration

```python
from src.incident_manager import IncidentManager
from src.slack_handler import SlackIncidentHandler

# Search for incidents
manager = IncidentManager("incidents")
results = manager.search("database")
for incident in results:
    print(manager.get_incident_summary(incident))

# Send to Slack
handler = SlackIncidentHandler()
handler.send_incident_alert("db-connection-timeout")
handler.send_search_results("payment issues")
```

## 🔗 Slack Integration Setup

### 1. Create a Slack App

1. Go to https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. Name it "Incident Wiki" and select your workspace

### 2. Enable Bot Token Scopes

1. Go to "OAuth & Permissions"
2. Add these scopes:
   - `chat:write`
   - `chat:write.public`
   - `channels:read`

### 3. Get Your Token

1. Copy the "Bot User OAuth Token" (starts with `xoxb-`)
2. Add it to `.env` as `SLACK_BOT_TOKEN`

### 4. Install App to Workspace

1. Go to "Install App" and click "Install to Workspace"
2. Add the signing secret to `.env` as `SLACK_SIGNING_SECRET`

### 5. Invite Bot to Channels

In your Slack channels, type:
```
/invite @incident-wiki
```

## 🔍 Incident YAML Schema

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| name | ✅ | string | Human-readable incident name |
| id | ✅ | string | Unique identifier (lowercase, hyphens) |
| severity | ✅ | string | critical, high, medium, low |
| description | ✅ | string | What this incident is about |
| aliases | ❌ | array | Alternative names to search by |
| triggers | ✅ | array | What indicates this incident |
| troubleshooting | ✅ | array | Steps to diagnose and resolve |
| escalation | ✅ | object | Escalation path by level |
| runbook | ✅ | string | Complete step-by-step procedure |
| slack_notification | ❌ | boolean | Enable Slack alerts (default: false) |
| notify_channels | ❌ | array | Channels to notify |
| resolution_time_sla | ❌ | number | Minutes to resolve (SLA) |
| impact | ❌ | string | Business impact description |

## 🛠️ Advanced: Slack Bot Integration

For automated alerts when incidents are detected, integrate this with your monitoring system:

```python
from src.slack_handler import SlackIncidentHandler

# In your alert handler
handler = SlackIncidentHandler()
if alert_type == "database_timeout":
    handler.send_incident_alert("db-connection-timeout", "#critical-alerts")
```

## 📝 Best Practices

- **ID Convention**: Use lowercase, hyphenated IDs (e.g., `db-connection-timeout`)
- **Aliases**: Add common names, error messages, and abbreviations
- **Runbooks**: Keep steps concise and actionable
- **SLA**: Set realistic resolution times based on incident severity
- **Testing**: Test Slack integration before relying on it

## 🔄 Example Workflow

1. An incident occurs (e.g., database connection timeout)
2. Your monitoring system detects it
3. Calls `handler.send_incident_alert("db-connection-timeout")`
4. Incident Wiki sends formatted alert to `#incidents` and `#engineering`
5. On-call engineer clicks "View Runbook" and follows steps
6. Issue resolved within SLA

## 📚 Example Incidents

Two example incidents are included:
- `example-database-connection-timeout.yaml` - Database connection pool issue
- `example-payment-processing-failure.yaml` - Payment processor failure

Use these as templates when creating new incidents.

## 🤝 Contributing

To add a new incident:
1. Create a YAML file in `incidents/` directory
2. Name it after the incident ID with `.yaml` extension
3. Follow the schema above
4. Test with: `python src/cli.py search <your-incident-name>`

## 📄 License

[Your License]
