import logging
import requests
from typing import Dict, List
from django.conf import settings

logger = logging.getLogger(__name__)


class AlertService:
    def __init__(self):
        self.slack_webhook = settings.SLACK_WEBHOOK_URL
        self.slack_enabled = settings.SLACK_ENABLED

    def send_slack_alert(self, message: str, blocks: List[Dict] = None) -> bool:
        """Send alert to Slack channel"""
        if not self.slack_enabled or not self.slack_webhook:
            logger.info("Slack notifications disabled - no webhook configured")
            return False

        try:
            payload = {'text': message}
            if blocks:
                payload['blocks'] = blocks

            response = requests.post(self.slack_webhook, json=payload)
            response.raise_for_status()
            logger.info(f"Slack alert sent successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
            return False

    def notify_issue_detected(self, issue_data: Dict) -> None:
        """Send notification about detected sensitive data"""
        if not self.slack_enabled:
            return

        # Color coding based on severity
        color_emoji = {
            'CRITICAL': '🔴🔴🔴',
            'HIGH': '🟠🟠',
            'MEDIUM': '🟡',
            'LOW': '🟢'
        }

        emoji = color_emoji.get(issue_data.get('severity'), '⚠️')

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} {issue_data.get('severity')} Severity Issue Detected!"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*📄 Document:*\n{issue_data.get('document_name')}"},
                    {"type": "mrkdwn", "text": f"*📊 Table:*\n{issue_data.get('table_name')}"},
                    {"type": "mrkdwn", "text": f"*📝 Column:*\n{issue_data.get('column_name')}"},
                    {"type": "mrkdwn", "text": f"*🔍 Pattern:*\n{issue_data.get('pattern_type')}"},
                    {"type": "mrkdwn", "text": f"*⚠️ Severity:*\n{issue_data.get('severity')}"},
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🔑 Detected Value:*\n`{issue_data.get('detected_value')}`"
                }
            },
            {
                "type": "context",
                "elements": [
                    {"type": "mrkdwn", "text": "🕐 Action required: Review and remediate this issue"}
                ]
            }
        ]

        self.send_slack_alert(f"Security Alert: {issue_data.get('pattern_type')} found", blocks)

    def notify_remediation(self, remediation_data: Dict) -> None:
        """Send notification about remediation action taken"""
        if not self.slack_enabled:
            logger.info("Slack disabled - skipping remediation notification")
            return

        # Map action to emoji and color
        action_emoji = {
            'resolve': '✅',
            'ignore': '🚫',
            'in_progress': '⏳'
        }

        action_color = {
            'resolve': 'good',
            'ignore': 'warning',
            'in_progress': 'warning'
        }

        emoji = action_emoji.get(remediation_data.get('action'), '📝')

        # Get issue details if available
        issue_id = remediation_data.get('issue_id')
        action = remediation_data.get('action')
        new_status = remediation_data.get('new_status')
        issue_details = remediation_data.get('issue_details', {})

        # Create message blocks
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} Remediation Action Taken"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Action:*\n{action.upper()}"},
                    {"type": "mrkdwn", "text": f"*Issue ID:*\n#{issue_id}"},
                    {"type": "mrkdwn", "text": f"*New Status:*\n{new_status}"},
                ]
            }
        ]

        # Add issue details if available
        if issue_details:
            blocks.append({
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Document:*\n{issue_details.get('document_name', 'N/A')}"},
                    {"type": "mrkdwn", "text": f"*Pattern:*\n{issue_details.get('pattern_type', 'N/A')}"},
                    {"type": "mrkdwn", "text": f"*Severity:*\n{issue_details.get('severity', 'N/A')}"},
                ]
            })

        # Add resolution note if present
        if remediation_data.get('note'):
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Note:* {remediation_data.get('note')}"
                }
            })

        blocks.append({
            "type": "context",
            "elements": [
                {"type": "mrkdwn", "text": "🕐 Action logged in audit trail"}
            ]
        })

        message = f"Remediation: {action} - Issue #{issue_id} marked as {new_status}"
        self.send_slack_alert(message, blocks)