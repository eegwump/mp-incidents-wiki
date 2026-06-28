"""
Email Handler - Send incident information via email
Supports Gmail, SendGrid, AWS SES, and custom SMTP
"""
import os
import sys
import smtplib
from typing import Optional, List
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from jinja2 import Template

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from incident_manager import IncidentManager

load_dotenv()


EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background-color: #f44336; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .incident-title { font-size: 24px; font-weight: bold; }
        .severity { display: inline-block; padding: 5px 10px; border-radius: 3px; color: white; font-weight: bold; margin-top: 10px; }
        .critical { background-color: #d32f2f; }
        .high { background-color: #f57c00; }
        .medium { background-color: #fbc02d; }
        .low { background-color: #388e3c; }
        .section { margin: 20px 0; }
        .section-title { font-size: 16px; font-weight: bold; color: #f44336; border-bottom: 2px solid #f44336; padding-bottom: 10px; }
        .section-content { margin-top: 10px; }
        .trigger { background-color: #fafafa; padding: 10px; margin: 5px 0; border-left: 3px solid #f44336; }
        .step { background-color: #fafafa; padding: 10px; margin: 10px 0; border-left: 3px solid #2196F3; }
        .command { background-color: #263238; color: #aed581; padding: 10px; border-radius: 3px; margin: 10px 0; font-family: monospace; overflow-x: auto; }
        .escalation { background-color: #fff3e0; padding: 15px; border-radius: 5px; margin: 10px 0; }
        .escalation-level { margin: 10px 0; }
        .footer { text-align: center; color: #999; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; }
        .sla { background-color: #e8f5e9; padding: 10px; border-radius: 3px; color: #1b5e20; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="incident-title">🚨 {{ incident.name }}</div>
            <div class="severity {{ incident.severity }}">{{ incident.severity.upper() }}</div>
        </div>

        <div class="section">
            <div class="section-title">📝 Description</div>
            <div class="section-content">{{ incident.description }}</div>
        </div>

        <div class="section">
            <div class="section-title">⏱️ SLA</div>
            <div class="sla">Resolution Time: {{ incident.resolution_time_sla }} minutes</div>
        </div>

        <div class="section">
            <div class="section-title">🚨 Triggers</div>
            <div class="section-content">
                {% for trigger in incident.triggers %}
                <div class="trigger">{{ trigger }}</div>
                {% endfor %}
            </div>
        </div>

        <div class="section">
            <div class="section-title">🔧 Troubleshooting Steps</div>
            <div class="section-content">
                {% for step in incident.troubleshooting %}
                <div class="step">
                    <strong>Step:</strong> {{ step.step }}
                    {% if step.command %}
                    <div class="command">$ {{ step.command }}</div>
                    {% endif %}
                    {% if step.description %}
                    <strong>What to look for:</strong> {{ step.description }}
                    {% endif %}
                    {% if step.url %}
                    <strong>Reference:</strong> <a href="{{ step.url }}">{{ step.url }}</a>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
        </div>

        {% if incident.escalation %}
        <div class="section">
            <div class="section-title">📞 Escalation Path</div>
            <div class="escalation">
                {% if incident.escalation.level_1 %}
                <div class="escalation-level">
                    <strong>Level 1 (Immediate):</strong> {{ incident.escalation.level_1 }}
                </div>
                {% endif %}
                {% if incident.escalation.level_2 %}
                <div class="escalation-level">
                    <strong>Level 2 (Team Lead):</strong> {{ incident.escalation.level_2 }}
                </div>
                {% endif %}
                {% if incident.escalation.level_3 %}
                <div class="escalation-level">
                    <strong>Level 3 (Manager):</strong> {{ incident.escalation.level_3 }}
                </div>
                {% endif %}
            </div>
        </div>
        {% endif %}

        <div class="section">
            <div class="section-title">📖 Runbook</div>
            <div class="section-content" style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; white-space: pre-wrap; font-family: monospace;">{{ incident.runbook }}</div>
        </div>

        <div class="footer">
            <p>Incident Wiki - Automated Alert</p>
            <p>Incident ID: {{ incident.id }}</p>
            <p>Severity: {{ incident.severity.upper() }}</p>
        </div>
    </div>
</body>
</html>
"""


class EmailHandler:
    """Handle sending incident alerts via email"""

    def __init__(self):
        self.provider = os.getenv("EMAIL_PROVIDER", "gmail").lower()
        self.email_from = os.getenv("EMAIL_FROM")
        self.username = os.getenv("EMAIL_USERNAME")
        self.password = os.getenv("EMAIL_PASSWORD")
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.manager = IncidentManager()

        if not self.email_from or not self.username or not self.password:
            raise ValueError(
                "Email configuration incomplete. Set EMAIL_FROM, EMAIL_USERNAME, EMAIL_PASSWORD in .env"
            )

    def send_incident_alert(
        self, incident_id: str, recipients: Optional[List[str]] = None
    ) -> bool:
        """
        Send incident information via email.

        Args:
            incident_id: ID of the incident to send
            recipients: List of email addresses (defaults to INCIDENT_EMAIL_RECIPIENTS)
        """
        incident = self.manager.get_incident(incident_id)
        if not incident:
            print(f"❌ Incident '{incident_id}' not found")
            return False

        if not recipients:
            recipients_str = os.getenv("INCIDENT_EMAIL_RECIPIENTS", "")
            recipients = [r.strip() for r in recipients_str.split(",") if r.strip()]

        if not recipients:
            print("❌ No recipients specified")
            return False

        try:
            html_body = self._format_incident_html(incident)
            text_body = self._format_incident_text(incident)

            for recipient in recipients:
                self._send_email(
                    to_email=recipient,
                    subject=f"🚨 Incident Alert: {incident.get('name')} ({incident.get('severity').upper()})",
                    html_body=html_body,
                    text_body=text_body,
                )

            print(f"✅ Email sent to {len(recipients)} recipient(s)")
            return True
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return False

    def send_search_results(self, query: str, recipients: Optional[List[str]] = None) -> bool:
        """Search incidents and send results via email."""
        results = self.manager.search(query)

        if not recipients:
            recipients_str = os.getenv("INCIDENT_EMAIL_RECIPIENTS", "")
            recipients = [r.strip() for r in recipients_str.split(",") if r.strip()]

        if not recipients:
            print("❌ No recipients specified")
            return False

        if not results:
            print(f"❌ No incidents found matching '{query}'")
            return False

        try:
            html_body = self._format_search_results_html(query, results)
            text_body = self._format_search_results_text(query, results)

            for recipient in recipients:
                self._send_email(
                    to_email=recipient,
                    subject=f"🔍 Incident Search Results: {query}",
                    html_body=html_body,
                    text_body=text_body,
                )

            print(f"✅ Search results sent to {len(recipients)} recipient(s)")
            return True
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return False

    def _format_incident_html(self, incident: dict) -> str:
        """Format incident as HTML email body."""
        template = Template(EMAIL_TEMPLATE)
        return template.render(incident=incident)

    def _format_incident_text(self, incident: dict) -> str:
        """Format incident as plain text email body."""
        text = f"""
INCIDENT ALERT: {incident.get('name')}
Severity: {incident.get('severity', 'unknown').upper()}

DESCRIPTION:
{incident.get('description', 'N/A')}

TRIGGERS:
"""
        for trigger in incident.get("triggers", []):
            text += f"  • {trigger}\n"

        text += f"\nSLA: {incident.get('resolution_time_sla', 'N/A')} minutes\n"

        text += "\nTROUBLESHOOTING STEPS:\n"
        for i, step in enumerate(incident.get("troubleshooting", []), 1):
            text += f"\n{i}. {step.get('step', 'N/A')}\n"
            if step.get("command"):
                text += f"   Command: {step.get('command')}\n"
            if step.get("description"):
                text += f"   What to look for: {step.get('description')}\n"
            if step.get("url"):
                text += f"   Reference: {step.get('url')}\n"

        if incident.get("escalation"):
            text += "\nESCALATION PATH:\n"
            escalation = incident.get("escalation")
            if escalation.get("level_1"):
                text += f"  Level 1: {escalation.get('level_1')}\n"
            if escalation.get("level_2"):
                text += f"  Level 2: {escalation.get('level_2')}\n"
            if escalation.get("level_3"):
                text += f"  Level 3: {escalation.get('level_3')}\n"

        text += f"\nRUNBOOK:\n{incident.get('runbook', 'N/A')}\n"
        text += f"\n---\nIncident ID: {incident.get('id')}\n"

        return text

    def _format_search_results_html(self, query: str, results: list) -> str:
        """Format search results as HTML."""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #2196F3; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
        .incident {{ background-color: #fafafa; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #2196F3; }}
        .incident-name {{ font-size: 16px; font-weight: bold; }}
        .incident-id {{ color: #666; font-size: 12px; }}
        .severity {{ display: inline-block; padding: 3px 8px; border-radius: 3px; color: white; font-size: 12px; font-weight: bold; margin-top: 5px; }}
        .critical {{ background-color: #d32f2f; }}
        .high {{ background-color: #f57c00; }}
        .medium {{ background-color: #fbc02d; }}
        .low {{ background-color: #388e3c; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Search Results</h1>
            <p>Query: {query}</p>
            <p>Found {len(results)} result(s)</p>
        </div>
"""
        for result in results:
            severity = result.get("severity", "unknown")
            html += f"""
        <div class="incident">
            <div class="incident-name">{result.get("name", "Unknown")}</div>
            <div class="incident-id">ID: {result.get("id", "N/A")}</div>
            <p>{result.get("description", "N/A")}</p>
            <div class="severity {severity}">{severity.upper()}</div>
        </div>
"""
        html += """
    </div>
</body>
</html>
"""
        return html

    def _format_search_results_text(self, query: str, results: list) -> str:
        """Format search results as plain text."""
        text = f"SEARCH RESULTS FOR: {query}\n"
        text += f"Found {len(results)} result(s)\n\n"

        for result in results:
            text += f"• {result.get('name', 'Unknown')}\n"
            text += f"  ID: {result.get('id', 'N/A')}\n"
            text += f"  Severity: {result.get('severity', 'unknown').upper()}\n"
            text += f"  {result.get('description', 'N/A')}\n\n"

        return text

    def _send_email(self, to_email: str, subject: str, html_body: str, text_body: str) -> None:
        """Send email using configured provider."""
        if self.provider == "gmail":
            self._send_gmail(to_email, subject, html_body, text_body)
        elif self.provider == "smtp":
            self._send_smtp(to_email, subject, html_body, text_body)
        else:
            raise ValueError(f"Email provider '{self.provider}' not supported")

    def _send_gmail(self, to_email: str, subject: str, html_body: str, text_body: str) -> None:
        """Send email via Gmail SMTP."""
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.email_from
        msg["To"] = to_email

        msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.username, self.password)
            server.sendmail(self.email_from, to_email, msg.as_string())

        print(f"✅ Email sent to {to_email}")

    def _send_smtp(self, to_email: str, subject: str, html_body: str, text_body: str) -> None:
        """Send email via custom SMTP server."""
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.email_from
        msg["To"] = to_email

        msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            if self.smtp_port == 587:
                server.starttls()
            server.login(self.username, self.password)
            server.sendmail(self.email_from, to_email, msg.as_string())

        print(f"✅ Email sent to {to_email}")


if __name__ == "__main__":
    # Example usage (requires email configuration in .env)
    try:
        handler = EmailHandler()

        # Send specific incident
        # handler.send_incident_alert("db-connection-timeout")

        # Search and send results
        # handler.send_search_results("database")

        print("✅ Email handler initialized successfully")
    except ValueError as e:
        print(f"⚠️  {e}")
        print("Configure email in .env file to enable email integration")
