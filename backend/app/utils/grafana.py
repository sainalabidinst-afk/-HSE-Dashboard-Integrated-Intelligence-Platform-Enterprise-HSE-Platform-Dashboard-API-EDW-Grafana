"""
Grafana Live Integration for HSE Platform
Real-time data streaming to Grafana via:
1. PostgreSQL datasource (for historical data)
2. InfluxDB (for time-series IoT data)
3. Grafana Live API (for push-based real-time)
"""

from datetime import datetime
from typing import Dict, Any, List
import json


class GrafanaLiveIntegration:
    """Integration with Grafana for real-time monitoring."""

    def __init__(self, grafana_url: str, api_key: str):
        self.grafana_url = grafana_url.rstrip("/")
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def send_frame(self, channel: str, data: Dict[str, Any]) -> bool:
        """
        Send data frame to Grafana Live.
        Channel format: hse:{site_id}:{metric_type}
        """
        try:
            import websockets
            import asyncio

            async def send():
                uri = f"{self.grafana_url}/api/live/push/hse/{channel}"
                async with websockets.connect(uri, extra_headers=self.headers) as ws:
                    frame = {
                        "time": int(datetime.utcnow().timestamp() * 1000),
                        "data": data,
                    }
                    await ws.send(json.dumps(frame))

            asyncio.run(send())
            return True
        except Exception as e:
            print(f"Grafana Live send error: {e}")
            return False

    def send_alert(self, site_id: str, alert_data: Dict[str, Any]):
        """Send alert to Grafana."""
        channel = f"{site_id}:alerts"
        self.send_frame(channel, alert_data)

    def send_environmental(self, site_id: str, env_data: Dict[str, Any]):
        """Send environmental data to Grafana."""
        channel = f"{site_id}:environmental"
        self.send_frame(channel, env_data)

    def send_ptw_status(self, site_id: str, ptw_data: Dict[str, Any]):
        """Send PTW status to Grafana."""
        channel = f"{site_id}:ptw"
        self.send_frame(channel, ptw_data)

    def send_incident(self, site_id: str, incident_data: Dict[str, Any]):
        """Send incident update to Grafana."""
        channel = f"{site_id}:incidents"
        self.send_frame(channel, incident_data)


class GrafanaProvisioning:
    """Grafana provisioning and configuration."""

    @staticmethod
    def get_datasource_config() -> Dict[str, Any]:
        """Get PostgreSQL datasource configuration."""
        return {
            "apiVersion": 1,
            "datasources": [
                {
                    "name": "HSE PostgreSQL",
                    "type": "postgres",
                    "url": "postgres:5432",
                    "user": "hse_reader",
                    "database": "hse_edw",
                    "isDefault": True,
                    "jsonData": {
                        "sslMode": "disable",
                        "maxOpenConns": 5,
                        "maxIdleConns": 5,
                        "connMaxLifetime": 300,
                    },
                    "secureJsonData": {
                        "password": "hse_reader_password",
                    },
                },
                {
                    "name": "HSE InfluxDB",
                    "type": "influxdb",
                    "url": "http://influxdb:8086",
                    "database": "hse_iot",
                    "isDefault": False,
                    "jsonData": {
                        "version": "Flux",
                        "organization": "hse",
                        "defaultBucket": "hse_sensors",
                    },
                    "secureJsonData": {
                        "token": "influxdb_token",
                    },
                },
            ],
        }

    @staticmethod
    def get_dashboard_provisioning() -> Dict[str, Any]:
        """Get dashboard provisioning configuration."""
        return {
            "apiVersion": 1,
            "providers": [
                {
                    "name": "HSE Dashboards",
                    "orgId": 1,
                    "folder": "HSE",
                    "type": "file",
                    "disableDeletion": False,
                    "updateIntervalSeconds": 10,
                    "allowUiUpdates": True,
                    "options": {
                        "path": "/etc/grafana/provisioning/dashboards/hse",
                    },
                },
            ],
        }

    @staticmethod
    def get_alert_notification_channels() -> Dict[str, Any]:
        """Get Grafana alert notification channel configuration."""
        return {
            "alertnotifiers": [
                {
                    "name": "hse-email-alerts",
                    "type": "email",
                    "settings": {
                        "addresses": "${ALERT_EMAIL_RECIPIENTS}",
                        "singleEmail": False,
                    },
                },
                {
                    "name": "hse-telegram-alerts",
                    "type": "telegram",
                    "settings": {
                        "bottoken": "${TELEGRAM_BOT_TOKEN}",
                        "chatid": "${TELEGRAM_CHAT_ID}",
                    },
                },
                {
                    "name": "hse-webhook",
                    "type": "webhook",
                    "settings": {
                        "url": "http://backend:8000/api/alerts/webhook",
                        "httpMethod": "POST",
                    },
                },
            ]
        }
