#!/usr/bin/env python3
"""
Khazad-dûm Alert and Notification System
Multi-channel notifications for critical trading system events
"""

import asyncio
import json
import os
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText, MIMEMultipart
from typing import Dict, List, Any, Optional
import requests
from dataclasses import dataclass
from enum import Enum


class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class Alert:
    """Alert data structure"""
    level: AlertLevel
    title: str
    message: str
    component: str
    timestamp: datetime
    data: Optional[Dict[str, Any]] = None


class NotificationChannel:
    """Base class for notification channels"""
    
    def __init__(self, name: str, enabled: bool = True):
        self.name = name
        self.enabled = enabled
    
    async def send(self, alert: Alert) -> bool:
        """Send notification through this channel"""
        raise NotImplementedError


class DiscordNotificationChannel(NotificationChannel):
    """Discord webhook notifications"""
    
    def __init__(self, webhook_url: str, enabled: bool = True):
        super().__init__("Discord", enabled)
        self.webhook_url = webhook_url
    
    async def send(self, alert: Alert) -> bool:
        if not self.enabled or not self.webhook_url:
            return False
        
        try:
            # Color coding for Discord
            colors = {
                AlertLevel.INFO: 0x0099ff,      # Blue
                AlertLevel.WARNING: 0xff9500,   # Orange  
                AlertLevel.CRITICAL: 0xff3366,  # Red
                AlertLevel.EMERGENCY: 0x9900ff  # Purple
            }
            
            # Icon mapping
            icons = {
                AlertLevel.INFO: "ℹ️",
                AlertLevel.WARNING: "⚠️",
                AlertLevel.CRITICAL: "🚨",
                AlertLevel.EMERGENCY: "💀"
            }
            
            embed = {
                "title": f"{icons[alert.level]} {alert.title}",
                "description": alert.message,
                "color": colors[alert.level],
                "fields": [
                    {"name": "Component", "value": alert.component, "inline": True},
                    {"name": "Level", "value": alert.level.value.upper(), "inline": True},
                    {"name": "Time", "value": alert.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC"), "inline": True}
                ],
                "footer": {"text": "Khazad-dûm Trading System"},
                "timestamp": alert.timestamp.isoformat()
            }
            
            # Add additional data if present
            if alert.data:
                for key, value in alert.data.items():
                    embed["fields"].append({
                        "name": key.replace("_", " ").title(),
                        "value": str(value),
                        "inline": True
                    })
            
            payload = {
                "username": "Khazad-dûm Monitor",
                "avatar_url": "https://cdn.discordapp.com/emojis/123456789.png",  # Optional
                "embeds": [embed]
            }
            
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            return response.status_code == 204
            
        except Exception as e:
            print(f"Discord notification failed: {e}")
            return False


class SlackNotificationChannel(NotificationChannel):
    """Slack webhook notifications"""
    
    def __init__(self, webhook_url: str, enabled: bool = True):
        super().__init__("Slack", enabled)
        self.webhook_url = webhook_url
    
    async def send(self, alert: Alert) -> bool:
        if not self.enabled or not self.webhook_url:
            return False
        
        try:
            # Color coding for Slack
            colors = {
                AlertLevel.INFO: "#0099ff",
                AlertLevel.WARNING: "#ff9500", 
                AlertLevel.CRITICAL: "#ff3366",
                AlertLevel.EMERGENCY: "#9900ff"
            }
            
            # Icon mapping
            icons = {
                AlertLevel.INFO: ":information_source:",
                AlertLevel.WARNING: ":warning:",
                AlertLevel.CRITICAL: ":rotating_light:",
                AlertLevel.EMERGENCY: ":skull:"
            }
            
            fields = [
                {"title": "Component", "value": alert.component, "short": True},
                {"title": "Level", "value": alert.level.value.upper(), "short": True},
                {"title": "Time", "value": alert.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC"), "short": True}
            ]
            
            # Add additional data
            if alert.data:
                for key, value in alert.data.items():
                    fields.append({
                        "title": key.replace("_", " ").title(),
                        "value": str(value),
                        "short": True
                    })
            
            payload = {
                "username": "Khazad-dûm Monitor",
                "icon_emoji": ":crossed_swords:",
                "attachments": [{
                    "color": colors[alert.level],
                    "title": f"{icons[alert.level]} {alert.title}",
                    "text": alert.message,
                    "fields": fields,
                    "footer": "Khazad-dûm Trading System",
                    "ts": int(alert.timestamp.timestamp())
                }]
            }
            
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            print(f"Slack notification failed: {e}")
            return False


class EmailNotificationChannel(NotificationChannel):
    """Email notifications via SMTP"""
    
    def __init__(self, smtp_host: str, smtp_port: int, username: str, 
                 password: str, from_email: str, to_emails: List[str], enabled: bool = True):
        super().__init__("Email", enabled)
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.to_emails = to_emails
    
    async def send(self, alert: Alert) -> bool:
        if not self.enabled or not self.to_emails:
            return False
        
        try:
            # Create email content
            subject = f"[{alert.level.value.upper()}] Khazad-dûm: {alert.title}"
            
            # HTML email template
            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; margin: 20px;">
                    <div style="border-left: 5px solid {'#ff3366' if alert.level in [AlertLevel.CRITICAL, AlertLevel.EMERGENCY] else '#ff9500'}; padding-left: 20px;">
                        <h2 style="color: #333;">🏺 Khazad-dûm Trading System Alert</h2>
                        <h3 style="color: {'#ff3366' if alert.level in [AlertLevel.CRITICAL, AlertLevel.EMERGENCY] else '#ff9500'};">{alert.title}</h3>
                        <p><strong>Level:</strong> {alert.level.value.upper()}</p>
                        <p><strong>Component:</strong> {alert.component}</p>
                        <p><strong>Time:</strong> {alert.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")}</p>
                        <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 15px 0;">
                            <p><strong>Message:</strong></p>
                            <p>{alert.message}</p>
                        </div>
            """
            
            # Add additional data
            if alert.data:
                html_body += "<p><strong>Additional Data:</strong></p><ul>"
                for key, value in alert.data.items():
                    html_body += f"<li><strong>{key.replace('_', ' ').title()}:</strong> {value}</li>"
                html_body += "</ul>"
            
            html_body += """
                    </div>
                    <hr style="margin: 30px 0;">
                    <p style="font-size: 12px; color: #666;">
                        This is an automated message from your Khazad-dûm trading system.<br>
                        Do not reply to this email.
                    </p>
                </body>
            </html>
            """
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.to_emails)
            
            # Plain text version
            text_body = f"""
Khazad-dûm Trading System Alert

Title: {alert.title}
Level: {alert.level.value.upper()}
Component: {alert.component}
Time: {alert.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")}

Message:
{alert.message}
            """
            
            if alert.data:
                text_body += "\nAdditional Data:\n"
                for key, value in alert.data.items():
                    text_body += f"- {key.replace('_', ' ').title()}: {value}\n"
            
            # Attach both versions
            msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Email notification failed: {e}")
            return False


class TelegramNotificationChannel(NotificationChannel):
    """Telegram bot notifications"""
    
    def __init__(self, bot_token: str, chat_id: str, enabled: bool = True):
        super().__init__("Telegram", enabled)
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
    
    async def send(self, alert: Alert) -> bool:
        if not self.enabled or not self.bot_token or not self.chat_id:
            return False
        
        try:
            # Icon mapping
            icons = {
                AlertLevel.INFO: "ℹ️",
                AlertLevel.WARNING: "⚠️",
                AlertLevel.CRITICAL: "🚨",
                AlertLevel.EMERGENCY: "💀"
            }
            
            # Format message for Telegram
            message = f"{icons[alert.level]} *{alert.title}*\n\n"
            message += f"📊 *Component:* {alert.component}\n"
            message += f"🚩 *Level:* {alert.level.value.upper()}\n"
            message += f"⏰ *Time:* {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
            message += f"💬 *Message:*\n{alert.message}\n"
            
            # Add additional data
            if alert.data:
                message += "\n📋 *Additional Info:*\n"
                for key, value in alert.data.items():
                    message += f"• *{key.replace('_', ' ').title()}:* {value}\n"
            
            message += "\n🏺 _Khazad-dûm Trading System_"
            
            # Send message
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(f"{self.api_url}/sendMessage", json=payload, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            print(f"Telegram notification failed: {e}")
            return False


class AlertManager:
    """Main alert management system"""
    
    def __init__(self):
        self.channels: List[NotificationChannel] = []
        self.alert_history: List[Alert] = []
        self.rate_limits: Dict[str, datetime] = {}
        
        # Load configuration from environment
        self._load_channels()
    
    def _load_channels(self):
        """Load notification channels from environment variables"""
        
        # Discord
        discord_webhook = os.getenv('DISCORD_WEBHOOK_URL')
        if discord_webhook:
            self.channels.append(DiscordNotificationChannel(discord_webhook))
        
        # Slack  
        slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
        if slack_webhook:
            self.channels.append(SlackNotificationChannel(slack_webhook))
        
        # Email
        smtp_host = os.getenv('SMTP_HOST')
        if smtp_host:
            self.channels.append(EmailNotificationChannel(
                smtp_host=smtp_host,
                smtp_port=int(os.getenv('SMTP_PORT', 587)),
                username=os.getenv('SMTP_USER', ''),
                password=os.getenv('SMTP_PASSWORD', ''),
                from_email=os.getenv('SMTP_FROM', ''),
                to_emails=[email.strip() for email in os.getenv('ALERT_EMAILS', '').split(',') if email.strip()]
            ))
        
        # Telegram
        telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        telegram_chat = os.getenv('TELEGRAM_CHAT_ID')
        if telegram_token and telegram_chat:
            self.channels.append(TelegramNotificationChannel(telegram_token, telegram_chat))
    
    def _should_send_alert(self, alert: Alert) -> bool:
        """Check if alert should be sent (rate limiting)"""
        
        # Always send critical and emergency alerts
        if alert.level in [AlertLevel.CRITICAL, AlertLevel.EMERGENCY]:
            return True
        
        # Rate limit other alerts (max 1 per 15 minutes per component)
        rate_key = f"{alert.component}:{alert.level.value}"
        now = datetime.utcnow()
        
        if rate_key in self.rate_limits:
            if now - self.rate_limits[rate_key] < timedelta(minutes=15):
                return False
        
        self.rate_limits[rate_key] = now
        return True
    
    async def send_alert(self, level: AlertLevel, title: str, message: str, 
                        component: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, bool]:
        """Send alert through all configured channels"""
        
        alert = Alert(
            level=level,
            title=title,
            message=message,
            component=component,
            timestamp=datetime.utcnow(),
            data=data
        )
        
        # Check rate limiting
        if not self._should_send_alert(alert):
            return {"rate_limited": True}
        
        # Store in history
        self.alert_history.append(alert)
        
        # Keep only last 100 alerts
        if len(self.alert_history) > 100:
            self.alert_history = self.alert_history[-100:]
        
        # Send through all channels
        results = {}
        tasks = []
        
        for channel in self.channels:
            if channel.enabled:
                tasks.append(self._send_with_retry(channel, alert))
        
        if tasks:
            channel_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(channel_results):
                channel_name = self.channels[i].name
                results[channel_name] = result if not isinstance(result, Exception) else False
        
        return results
    
    async def _send_with_retry(self, channel: NotificationChannel, alert: Alert, max_retries: int = 2) -> bool:
        """Send alert with retry logic"""
        
        for attempt in range(max_retries + 1):
            try:
                result = await channel.send(alert)
                if result:
                    return True
                    
            except Exception as e:
                print(f"Alert send attempt {attempt + 1} failed for {channel.name}: {e}")
                
                if attempt < max_retries:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        return False
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent alerts for dashboard display"""
        
        recent_alerts = self.alert_history[-limit:]
        return [
            {
                "level": alert.level.value,
                "title": alert.title,
                "message": alert.message,
                "component": alert.component,
                "timestamp": alert.timestamp.isoformat(),
                "data": alert.data
            }
            for alert in reversed(recent_alerts)
        ]


# Global alert manager instance
alert_manager = AlertManager()


# Convenience functions for common alerts
async def alert_system_health(health_status: str, details: Dict[str, Any] = None):
    """Send system health alert"""
    level = AlertLevel.INFO if health_status == "healthy" else \
           AlertLevel.WARNING if health_status == "degraded" else \
           AlertLevel.CRITICAL
    
    await alert_manager.send_alert(
        level=level,
        title=f"System Health: {health_status.upper()}",
        message=f"Trading system health status changed to {health_status}",
        component="system_health",
        data=details
    )


async def alert_trading_event(event_type: str, symbol: str, details: Dict[str, Any] = None):
    """Send trading event alert"""
    await alert_manager.send_alert(
        level=AlertLevel.INFO,
        title=f"Trading Event: {event_type}",
        message=f"Trading event '{event_type}' occurred for {symbol}",
        component="trading_engine", 
        data={"symbol": symbol, **(details or {})}
    )


async def alert_critical_error(error_message: str, component: str, details: Dict[str, Any] = None):
    """Send critical error alert"""
    await alert_manager.send_alert(
        level=AlertLevel.CRITICAL,
        title="Critical System Error",
        message=error_message,
        component=component,
        data=details
    )


async def alert_position_update(action: str, symbol: str, details: Dict[str, Any] = None):
    """Send position update alert"""
    level = AlertLevel.WARNING if action in ["stop_loss", "emergency_exit"] else AlertLevel.INFO
    
    await alert_manager.send_alert(
        level=level,
        title=f"Position {action.replace('_', ' ').title()}",
        message=f"Position {action} executed for {symbol}",
        component="position_management",
        data={"symbol": symbol, "action": action, **(details or {})}
    )