# Slack Integration Setup Guide

Complete step-by-step guide to set up Slack integration for the Incident Wiki.

## 📋 Prerequisites

- A Slack workspace where you have admin access
- Slack app creation permissions

## 🔧 Step 1: Create a Slack App

1. Go to [https://api.slack.com/apps](https://api.slack.com/apps)
2. Click **"Create New App"**
3. Select **"From scratch"**
4. Enter name: **"Incident Wiki"**
5. Select your workspace
6. Click **"Create App"**

You're now in the app configuration page.

## 🔑 Step 2: Get Your Tokens

1. In the left sidebar, click **"OAuth & Permissions"**
2. Under "Tokens and URLs", you'll see:
   - **Bot User OAuth Token** (starts with `xoxb-`)
   - Copy this token

3. Scroll up to **"Scopes"** section
4. Under "Bot Token Scopes", click **"Add an OAuth Scope"**
5. Add these scopes:
   - `chat:write` - Send messages
   - `channels:read` - Read channel information (optional)

6. After adding scopes, you'll see a new token generated
7. Copy the **Bot User OAuth Token** and save it

## 🔐 Step 3: Get Your Signing Secret

1. Go back to the app page
2. In the left sidebar, click **"Basic Information"**
3. Look for **"App Credentials"** section
4. Find **"Signing Secret"** and copy it

## 📝 Step 4: Configure Environment Variables

1. Create a `.env` file in the project root:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your credentials:
   ```
   SLACK_BOT_TOKEN=xoxb-your-bot-token-here
   SLACK_SIGNING_SECRET=your-signing-secret-here
   INCIDENTS_CHANNEL=incidents
   ```

3. **DO NOT commit `.env` to git** (it's in .gitignore)

## 🚀 Step 5: Install App to Your Workspace

1. In the Slack app configuration, go to **"OAuth & Permissions"**
2. Click **"Install to Workspace"**
3. Review permissions and click **"Allow"**

The app will now appear in your Slack workspace.

## 💬 Step 6: Add Bot to Channels

In any Slack channel where you want incident alerts:

1. Type: `/invite @Incident Wiki`
2. Press Enter

Or manually:

1. Click the channel name at the top
2. Go to "Members" or "Details"
3. Click "Add apps"
4. Search for "Incident Wiki"
5. Click to add it

## ✅ Step 7: Test the Integration

From the project directory:

```bash
# List incidents
python src/cli.py list

# Send a test alert
python src/cli.py slack db-connection-timeout

# Or send to specific channel
python src/cli.py slack db-connection-timeout "#critical-alerts"
```

You should see the incident formatted message in your Slack channel!

## 🌐 Step 8: Set Up Web Server (Optional)

To receive webhooks from your monitoring system:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Flask server
python src/app.py
```

The API will be available at `http://localhost:5000`

### Monitoring System Integration

In your monitoring system (e.g., Datadog, New Relic, Prometheus):

1. Create a webhook to: `http://your-server.com/webhook/incident`
2. Configure payload:
   ```json
   {
       "incident_id": "db-connection-timeout",
       "severity": "critical",
       "message": "Database connection timeout detected"
   }
   ```

When an alert fires, it will:
1. Receive the webhook
2. Look up the incident definition
3. Send formatted alert to Slack

## 🐛 Troubleshooting

### "Token invalid or expired"
- Go to [https://api.slack.com/apps](https://api.slack.com/apps)
- Select your app
- Regenerate the token if needed
- Update `.env`

### "Bot not in channel"
- Invite the bot to the channel (see Step 6)
- Or check permissions in app settings

### "Permission denied"
- Go to "OAuth & Permissions"
- Verify you have these scopes: `chat:write`, `channels:read`
- Reinstall app if needed

### "Message formatting looks wrong"
- Check Slack version (requires recent Slack client)
- Verify the YAML incident file has correct format

## 📊 Advanced: Automated Alerts

### Docker Compose Setup

```yaml
version: '3'
services:
  incident-wiki:
    build: .
    ports:
      - "5000:5000"
    environment:
      - SLACK_BOT_TOKEN=${SLACK_BOT_TOKEN}
      - SLACK_SIGNING_SECRET=${SLACK_SIGNING_SECRET}
    volumes:
      - ./incidents:/app/incidents
```

### Systemd Service

```ini
[Unit]
Description=Incident Wiki
After=network.target

[Service]
Type=simple
User=appuser
WorkingDirectory=/opt/incident-wiki
ExecStart=/usr/bin/python3 src/app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## 🔗 API Endpoints

Once the Flask server is running:

- `GET /api/incidents` - List all incidents
- `GET /api/incidents/<id>` - Get incident details
- `GET /api/search?q=query` - Search incidents
- `POST /api/slack/alert` - Send Slack alert
- `POST /webhook/incident` - Receive incident webhook

## 📚 Example: Datadog Integration

In Datadog, create a webhook:

1. Monitors → New Monitor
2. Select monitor type
3. Under "Notify", add custom webhook:
   ```
   https://your-domain.com/webhook/incident
   ```

4. Configure JSON body:
   ```json
   {
     "incident_id": "db-connection-timeout",
     "severity": "critical",
     "message": "{{alert.message}}"
   }
   ```

## ✨ Best Practices

- ✅ Store tokens in `.env`, never in code
- ✅ Use separate channels for different severity levels
- ✅ Test integration in #test-channel first
- ✅ Document incident escalation paths clearly
- ✅ Review and update incidents regularly
- ✅ Keep runbooks current and tested

---

Need help? Check [USAGE.md](../USAGE.md) for more information.
