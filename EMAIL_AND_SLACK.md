# Email & Slack Integration Summary

Your incident wiki now supports **both email and Slack notifications**! Choose one or use both.

## 🎯 Quick Comparison

| Feature | Email | Slack |
|---------|-------|-------|
| **Requires bot setup** | ❌ No | ✅ Yes (organizational Slack) |
| **Setup time** | 5 minutes | 10 minutes |
| **Beautiful formatting** | ✅ HTML emails | ✅ Formatted messages |
| **Works without Slack access** | ✅ Yes | ❌ No |
| **Multiple recipients** | ✅ Yes | ✅ Yes (channels) |
| **Integrates with monitoring** | ✅ Yes | ✅ Yes |

## 📧 Email Setup (Recommended for you!)

**Perfect for your situation** - no need to add a bot to organizational Slack!

### 1. Quick Setup (5 minutes)
```bash
cp .env.example .env
```

### 2. Choose Email Provider

**Gmail (Recommended):**
```
EMAIL_PROVIDER=gmail
EMAIL_FROM=incidents@example.com
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-16-char-app-password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
INCIDENT_EMAIL_RECIPIENTS=team@example.com,oncall@example.com
```

**Other providers:** See [EMAIL_SETUP.md](EMAIL_SETUP.md)

### 3. Send Incidents via Email

```bash
# Send to default recipients
python3 src/cli.py email db-connection-timeout

# Send to specific person
python3 src/cli.py email db-connection-timeout "your-email@example.com"

# Send to multiple people
python3 src/cli.py email db-connection-timeout "team@example.com,oncall@example.com"

# Search and email results
python3 src/cli.py email-search "database"
```

### 4. Update Your Incidents

Add to your YAML incident files:
```yaml
email_notification: true
email_recipients:
  - "team@example.com"
  - "oncall@example.com"
```

## 💬 Slack Setup (Optional)

If you have bot access later, see [SLACK_SETUP.md](SLACK_SETUP.md)

## 📨 What Email Recipients Get

Beautiful, fully formatted emails with:
- 🚨 Incident name and severity (color-coded)
- 📝 Complete description
- 🔥 Triggers (what indicates the incident)
- 🔧 Troubleshooting steps with commands
- 📞 Escalation path
- 📖 Full runbook
- ⏱️ SLA information

## 🌐 Web API for Email

Start the Flask server:
```bash
python3 src/app.py
```

Send incident via API:
```bash
curl -X POST http://localhost:5000/api/email/alert \
  -H "Content-Type: application/json" \
  -d '{
    "incident_id": "db-connection-timeout",
    "recipients": ["team@example.com", "oncall@example.com"]
  }'
```

## 🔄 Monitoring System Integration

**Datadog → Email Alerts:**
```
Webhook URL: https://your-server.com/webhook/incident
Payload:
{
  "incident_id": "db-connection-timeout",
  "severity": "critical"
}
```

The webhook will automatically send emails based on your incident YAML config!

## 🚀 Using Both Email AND Slack

Configure both in `.env`:
```
# Slack
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_SIGNING_SECRET=your-secret

# Email
EMAIL_FROM=incidents@example.com
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
INCIDENT_EMAIL_RECIPIENTS=team@example.com
```

In your incident YAML:
```yaml
slack_notification: true
notify_channels:
  - "#incidents"

email_notification: true
email_recipients:
  - "team@example.com"
```

Both will trigger automatically!

## 🔒 Security Tips

✅ Store `.env` in `.gitignore` (already done)
✅ Use App Passwords, not real passwords
✅ Use TLS/STARTTLS (port 587, not 25)
✅ Rotate credentials regularly
❌ Never commit `.env` to git

## 📁 Files Modified/Created

```
incidents/
├── example-database-connection-timeout.yaml    (added email config)
├── example-payment-processing-failure.yaml     (added email config)
└── ssl-certificate-expired.yaml                (added email config)

src/
├── email_handler.py        ✨ NEW - Email sending
├── cli.py                  ✏️ UPDATED - Added email commands
├── app.py                  ✏️ UPDATED - Added email API endpoint
└── slack_handler.py        (unchanged)

.env.example               ✏️ UPDATED - Email configuration template
EMAIL_SETUP.md            ✨ NEW - Email setup guide
requirements.txt          ✏️ UPDATED - Added email dependencies
```

## 🎯 Next Steps

1. **Copy .env.example to .env**
   ```bash
   cp .env.example .env
   ```

2. **Add your email configuration** (Gmail recommended)
   - Get App Password from Google Account
   - Add to `.env`

3. **Test it out**
   ```bash
   python3 src/cli.py email db-connection-timeout "your-email@example.com"
   ```

4. **Add to your incidents**
   - Update YAML files with email recipients
   - Test each incident type

5. **Integrate with monitoring** (optional)
   - Set webhook URL in your monitoring system
   - Incidents will auto-email when alerts trigger

## 📚 Documentation

- [EMAIL_SETUP.md](EMAIL_SETUP.md) - Detailed email setup
- [SLACK_SETUP.md](SLACK_SETUP.md) - Slack integration (optional)
- [USAGE.md](USAGE.md) - All features
- [GETTING_STARTED.md](GETTING_STARTED.md) - Quick start

## ✨ What You Have Now

✅ YAML-based incident definitions
✅ Fast search by name/ID/aliases
✅ **Email notifications** (works independently!)
✅ Slack integration (optional)
✅ Beautiful formatted alerts
✅ Runbooks and troubleshooting steps
✅ SLA tracking
✅ Web API with webhooks
✅ CLI commands
✅ Docker support

## 🎉 You're All Set!

Your incident wiki is ready to send incident details via email, even without organizational Slack access. Start with email, add Slack later if you get bot access.

**Get started:**
```bash
cp .env.example .env
# Edit .env with your email config
python3 src/cli.py email db-connection-timeout "your-email@example.com"
```

Questions? Check [EMAIL_SETUP.md](EMAIL_SETUP.md) or [USAGE.md](USAGE.md)!
