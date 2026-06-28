# 🚀 Getting Started with Incident Wiki

Welcome to your incident wiki! This guide will get you up and running in minutes.

## ⚡ Quick Start (5 minutes)

### 1. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 2. Test the Setup
```bash
python3 test_setup.py
```

You should see all 3 example incidents loaded ✅

### 3. Search for Incidents
```bash
python3 src/cli.py search database
python3 src/cli.py list
```

### 4. View a Runbook
```bash
python3 src/cli.py runbook db-connection-timeout
```

## 📝 Create Your First Incident

1. Create a file: `incidents/my-incident-name.yaml`
2. Use this template:

```yaml
---
name: "My Incident Name"
id: "my-incident-id"
severity: "critical"  # or high, medium, low
description: "What is this incident about?"

triggers:
  - "What indicates this happened?"
  - "Common error message?"

troubleshooting:
  - step: "First thing to check"
    command: "sudo systemctl status myservice"
    description: "Check if service is running"
  
  - step: "Check logs"
    command: "tail -100 /var/log/myapp.log"
    description: "Look for recent errors"

escalation:
  level_1: "Check monitoring dashboard"
  level_2: "Contact on-call engineer"
  level_3: "Page manager"

runbook: |
  1. Check the status of the service
  2. Review recent error logs
  3. Restart service if needed
  4. If still broken, escalate
  5. Document what happened

slack_notification: true
notify_channels:
  - "#incidents"

resolution_time_sla: 15  # minutes
```

3. Search for it:
```bash
python3 src/cli.py search "my incident"
```

## 🔔 Slack Integration (Optional)

### Quick Setup (5 minutes)
1. Follow [SLACK_SETUP.md](SLACK_SETUP.md)
2. Copy `.env.example` to `.env`
3. Add your Slack bot token

### Send an Incident Alert
```bash
python3 src/cli.py slack my-incident-id
```

Or to a specific channel:
```bash
python3 src/cli.py slack my-incident-id "#critical-alerts"
```

## 📧 Email Notifications (Alternative to Slack)

Perfect if you can't add a bot to your organizational Slack!

### Quick Setup (5 minutes)
1. Follow [EMAIL_SETUP.md](EMAIL_SETUP.md)
2. Copy `.env.example` to `.env`
3. Add your email credentials (Gmail recommended)

### Send an Incident Alert
```bash
# Send to default recipients (from .env)
python3 src/cli.py email my-incident-id

# Send to specific address
python3 src/cli.py email my-incident-id "your-email@example.com"

# Send to multiple people
python3 src/cli.py email my-incident-id "team@example.com,oncall@example.com"
```

### Beautiful Email Format
Emails include:
- ✅ Incident name and severity (color-coded)
- ✅ Complete description
- ✅ All triggers
- ✅ Troubleshooting steps with commands
- ✅ Escalation path
- ✅ Full runbook
- ✅ Both HTML and plain text versions

## 🌐 Web API (Optional)

### Start the Server
```bash
python3 src/app.py
```

Server runs at `http://localhost:5000`

### API Endpoints

List all incidents:
```bash
curl http://localhost:5000/api/incidents
```

Search incidents:
```bash
curl "http://localhost:5000/api/search?q=database"
```

Get incident details:
```bash
curl http://localhost:5000/api/incidents/db-connection-timeout
```

Send Slack alert:
```bash
curl -X POST http://localhost:5000/api/slack/alert \
  -H "Content-Type: application/json" \
  -d '{"incident_id": "db-connection-timeout"}'
```

## 🐳 Docker (Optional)

### Build Image
```bash
docker build -t incident-wiki .
```

### Run with Docker Compose
```bash
docker-compose up
```

## 📚 Helpful Commands (Makefile)

```bash
make list              # List all incidents
make search q=database # Search incidents
make show id=<incident-id>  # Show details
make runbook id=<incident-id> # Show runbook
make slack id=<incident-id>  # Send to Slack
make serve             # Start web server
make clean             # Clean cache
```

## 🔍 Common Tasks

### Add a New Incident
```bash
# 1. Create YAML file
touch incidents/new-incident.yaml

# 2. Edit with your incident details

# 3. Test it
python3 src/cli.py search "new-incident"
```

### Update an Existing Incident
```bash
# 1. Edit the YAML file
vi incidents/db-connection-timeout.yaml

# 2. Search to verify
python3 src/cli.py show db-connection-timeout
```

### Find Incidents by Severity
```bash
# Check each incident
python3 src/cli.py list | grep -i critical
```

### Export Incident as JSON
```bash
python3 src/cli.py show db-connection-timeout > incident.json
```

## 📖 Full Documentation

- [README.md](README.md) - Project overview
- [USAGE.md](USAGE.md) - Complete feature documentation
- [SLACK_SETUP.md](SLACK_SETUP.md) - Detailed Slack integration guide

## 🎯 Typical Workflow

```
1. Incident occurs (e.g., database timeout)
   ↓
2. Monitoring system detects it
   ↓
3. Calls: python3 src/cli.py slack db-connection-timeout
   ↓
4. Slack alert sent to team with incident details
   ↓
5. Engineer follows runbook steps
   ↓
6. Issue resolved within SLA (15 minutes)
```

## 🆘 Troubleshooting

### "ModuleNotFoundError: No module named 'yaml'"
```bash
pip3 install -r requirements.txt
```

### "No incidents found"
Check the `incidents/` directory exists and has `.yaml` files

### "SLACK_BOT_TOKEN not set"
This is optional - set up Slack integration when ready
Follow [SLACK_SETUP.md](SLACK_SETUP.md)

3. 🔔 Set up notifications:
   - 📧 **Email** (recommended if no Slack access) - [EMAIL_SETUP.md](EMAIL_SETUP.md)
   - 💬 **Slack** (optional, requires bot) - [SLACK_SETUP.md](SLACK_SETUP.md)

Your monitoring system (Datadog, New Relic, etc.) can trigger:

```bash
# Example from Prometheus AlertManager
python3 src/cli.py slack {{ $incident_id }}
```

Or via webhook to the Flask API:
```bash
POST /webhook/incident
{
  "incident_id": "db-connection-timeout",
  "severity": "critical"
}
```

## 💡 Pro Tips

✅ **Keep runbooks updated** - Test them regularly  
✅ **Use aliases** - Add common error messages as aliases  
✅ **Set realistic SLAs** - Based on business impact  
✅ **Monitor certificate expiry** - Add SSL certificate incidents  
✅ **Document escalation** - Make clear who to contact  
✅ **Review regularly** - Update incidents as systems evolve  

## 🎓 Next Steps

1. ✅ You have a working incident wiki (you are here!)
2. 📝 Add your incidents to `incidents/` directory
3. 🔔 Set up Slack integration (follow SLACK_SETUP.md)
4. 🌐 Deploy Flask server to handle webhooks
5. 🔗 Integrate with your monitoring system

---, [EMAIL_SETUP.md](EMAIL_SETUP.md), or [SLACK_SETUP.md](SLACK_SETUP.md)

**Want email notifications?** Go to [EMAIL_SETUP.md](EMAIL_SETUP.md) - Perfect if you can't add a Slack bot!

**Want Slack integration(USAGE.md) or [SLACK_SETUP.md](SLACK_SETUP.md)

**Ready to integrate with Slack?** Go to [SLACK_SETUP.md](SLACK_SETUP.md)

**Want to see all features?** Check [USAGE.md](USAGE.md)
