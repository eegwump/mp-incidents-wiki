# Email Notification Setup Guide

Complete guide to set up email notifications for incident alerts. Perfect if you can't add a bot to your organizational Slack!

## 📋 Why Email?

✅ Works independently - no Slack bot required  
✅ Works alongside Slack - send to both  
✅ Beautiful HTML emails with full incident details  
✅ Supports multiple recipients  
✅ Multiple email providers supported  
✅ Easy to integrate with any monitoring system  

## 🚀 Quick Setup (5 minutes)

### 1. Choose Your Email Provider

#### Option A: Gmail (Recommended)
```
EMAIL_PROVIDER=gmail
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
```

#### Option B: Custom SMTP Server
```
EMAIL_PROVIDER=smtp
SMTP_HOST=your-smtp.example.com
SMTP_PORT=587
```

#### Option C: SendGrid (requires SendGrid account)
```
EMAIL_PROVIDER=sendgrid
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
```

### 2. Get Your Credentials

**For Gmail:**
1. Go to https://myaccount.google.com/security
2. Enable 2-Factor Authentication (if not already enabled)
3. Search for "App passwords"
4. Select "Mail" and "Windows Computer" (or your device)
5. Copy the generated 16-character password

**For Custom SMTP:**
1. Get your SMTP server address and port from your admin
2. Get your email username and password

**For SendGrid:**
1. Create account at https://sendgrid.com
2. Create an API key from Settings → API Keys
3. Use `apikey` as username and the key as password

### 3. Configure .env File

```bash
cp .env.example .env
```

Edit `.env` and fill in email settings:

```
# Email Configuration
EMAIL_PROVIDER=gmail
EMAIL_FROM=incidents@example.com
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-16-char-app-password

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587

# Default email recipients (comma-separated)
INCIDENT_EMAIL_RECIPIENTS=team@example.com,oncall@example.com
```

### 4. Test Email Configuration

```bash
python3 test_setup.py
```

Should show:
```
✅ incident_manager imported successfully
```

### 5. Send a Test Email

```bash
python3 src/cli.py email db-connection-timeout "your-email@example.com"
```

You should receive a beautifully formatted incident email! 📧

## 📧 Usage Examples

### Send incident to default recipients (from .env)
```bash
python3 src/cli.py email db-connection-timeout
```

### Send to specific email address
```bash
python3 src/cli.py email db-connection-timeout "oncall@example.com"
```

### Send to multiple recipients
```bash
python3 src/cli.py email db-connection-timeout "team@example.com,oncall@example.com,manager@example.com"
```

### Search and email results
```bash
python3 src/cli.py email-search "database"
python3 src/cli.py email-search "payment" "team@example.com"
```

## 🌐 Web API Endpoints

### Send incident via email (API)
```bash
curl -X POST http://localhost:5000/api/email/alert \
  -H "Content-Type: application/json" \
  -d '{
    "incident_id": "db-connection-timeout",
    "recipients": ["team@example.com", "oncall@example.com"]
  }'
```

## 📨 Email Webhook Integration

Integrate with your monitoring system (Datadog, New Relic, etc.):

```bash
# From your monitoring system webhook, call:
python3 src/cli.py email db-connection-timeout "your-email@example.com"
```

Or via HTTP POST:
```bash
curl -X POST http://your-server.com/webhook/incident \
  -H "Content-Type: application/json" \
  -d '{
    "incident_id": "db-connection-timeout",
    "severity": "critical"
  }'
```

The webhook handler will automatically send emails if configured in the YAML.

## 🔧 Python Integration

```python
from src.email_handler import EmailHandler

# Initialize handler
handler = EmailHandler()

# Send to default recipients (from .env)
handler.send_incident_alert("db-connection-timeout")

# Send to specific recipients
handler.send_incident_alert(
    "db-connection-timeout",
    ["team@example.com", "oncall@example.com"]
)

# Search and email results
handler.send_search_results("database", ["team@example.com"])
```

## 🏗️ Incident YAML Configuration

Add email notification settings to your incident YAML files:

```yaml
---
name: "My Incident"
id: "my-incident"

# Slack notification (optional)
slack_notification: true
notify_channels:
  - "#incidents"

# Email notification (optional or instead of Slack)
email_notification: true
email_recipients:
  - "team@example.com"
  - "oncall@example.com"
```

## 📊 What's in the Email?

Beautiful HTML emails include:

- ✅ Incident name and severity with color coding
- ✅ Complete description
- ✅ Triggers (what indicates the incident)
- ✅ Troubleshooting steps with commands
- ✅ Escalation path (who to contact at each level)
- ✅ Full runbook (step-by-step procedures)
- ✅ SLA information
- ✅ Plain text version for non-HTML clients

## 🚀 Advanced: Monitoring System Integration

### Datadog
1. Create a monitor
2. In notifications, add webhook:
   ```
   https://your-domain.com/webhook/incident
   ```

3. In webhook payload (JSON):
   ```json
   {
     "incident_id": "db-connection-timeout",
     "severity": "critical"
   }
   ```

### New Relic
Add webhook notification:
```
POST https://your-domain.com/webhook/incident
```

Payload:
```json
{
  "incident_id": "{{incident.id}}",
  "severity": "critical"
}
```

### Prometheus AlertManager
In `alertmanager.yml`:
```yaml
receivers:
  - name: 'incident-wiki'
    webhook_configs:
      - url: 'http://localhost:5000/webhook/incident'
```

## 🔒 Security Best Practices

**DO:**
- ✅ Store credentials in `.env` (gitignored)
- ✅ Use App Passwords (not your real password)
- ✅ Use environment variables in production
- ✅ Rotate credentials regularly
- ✅ Use TLS/SSL (port 587 instead of 25)

**DON'T:**
- ❌ Commit `.env` to git
- ❌ Hardcode passwords in code
- ❌ Use your real Gmail password
- ❌ Share credentials in messages
- ❌ Use unencrypted SMTP (port 25)

## 🐛 Troubleshooting

### "Email configuration incomplete"
Check `.env` has all required fields:
```
EMAIL_FROM=
EMAIL_USERNAME=
EMAIL_PASSWORD=
```

### "Authentication failed"
For Gmail:
- Verify you're using App Password, not regular password
- Check 2FA is enabled
- Generate new App Password in Google Account

For other providers:
- Verify username/password are correct
- Check SMTP host and port
- Try connecting with different port (465, 587, 25)

### "Email not received"
- Check spam/junk folder
- Verify recipient email addresses are correct
- Check email logs: `python3 test_setup.py`
- Try sending to your own email first

### "Connection timeout"
- Verify SMTP host is correct
- Check SMTP port (usually 587 or 465)
- Check firewall allows outbound connections
- For Gmail: use `smtp.gmail.com:587`

### "SSL/TLS errors"
- Use port 587 (starttls) instead of 465 (ssl)
- For custom SMTP, ask your admin for correct port
- Some corporate networks require additional setup

## 💡 Pro Tips

✅ **Test with your own email first** - Send a test before giving to team  
✅ **Use distribution lists** - Put team emails in one recipient group  
✅ **Combine with Slack** - Send to both for maximum notification  
✅ **Set up forwarding** - Forward incidents to a shared mailbox  
✅ **Archive incidents** - Keep emails for audit trail  
✅ **Include context** - Add ticket number or runbook link to incidents  

## 🔄 Using Both Slack and Email

You can use both simultaneously! Just configure both in `.env`:

```bash
# Slack configuration
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_SIGNING_SECRET=your-secret

# Email configuration
EMAIL_FROM=incidents@example.com
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
INCIDENT_EMAIL_RECIPIENTS=team@example.com
```

Then in your incident YAML:
```yaml
slack_notification: true
notify_channels:
  - "#incidents"

email_notification: true
email_recipients:
  - "team@example.com"
```

Both will be triggered automatically!

## 📚 Related Documentation

- [README.md](README.md) - Project overview
- [USAGE.md](USAGE.md) - All features
- [GETTING_STARTED.md](GETTING_STARTED.md) - Quick start
- [SLACK_SETUP.md](SLACK_SETUP.md) - Slack integration

---

**Ready to send incident emails?** Start with Step 1 above!

**Questions about Gmail App Passwords?** Go to https://support.google.com/accounts/answer/185833

**Need help with your email provider?** Check their SMTP documentation
