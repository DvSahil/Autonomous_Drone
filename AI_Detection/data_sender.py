"""
data_sender.py — Send QR Data to Judges
=========================================
Submits the decoded QR code data via:
  1. HTTP POST to judge's server endpoint
  2. Email (SMTP / Gmail) with optional image attachment
"""

import json
import time
import logging
import smtplib
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from pathlib import Path
from config import Config

log = logging.getLogger(__name__)


class DataSender:
    """Sends QR scan results to judges via HTTP and/or email."""

    def __init__(self, judge_url: str, judge_email: str):
        self.judge_url   = judge_url
        self.judge_email = judge_email

    # ── Main send method ───────────────────────────────────────────────────

    def send(self, qr_data: str, image_path: str | None = None):
        """
        Send QR data using all available methods.
        Failures are logged but do not abort the mission.
        """
        payload = self._build_payload(qr_data)
        log.info(f"Submitting payload: {payload}")

        self._send_http(payload, image_path)
        self._send_email(qr_data, image_path)

    # ── HTTP POST ──────────────────────────────────────────────────────────

    def _send_http(self, payload: dict, image_path: str | None):
        """POST QR data (+ optional image) to the judge's server."""
        try:
            if image_path and Path(image_path).exists():
                with open(image_path, "rb") as img_file:
                    files = {"image": ("qr_frame.jpg", img_file, "image/jpeg")}
                    response = requests.post(
                        self.judge_url,
                        data=payload,
                        files=files,
                        timeout=15,
                    )
            else:
                response = requests.post(
                    self.judge_url,
                    json=payload,
                    timeout=15,
                )

            if response.status_code == 200:
                log.info(f"HTTP POST success: {response.text}")
            else:
                log.warning(
                    f"HTTP POST returned {response.status_code}: {response.text}"
                )

        except requests.exceptions.ConnectionError:
            log.error(
                "HTTP POST failed: Cannot reach judge server. "
                "Check Wi-Fi / network connection."
            )
        except requests.exceptions.Timeout:
            log.error("HTTP POST timed out after 15 s.")
        except Exception as exc:
            log.error(f"HTTP POST error: {exc}")

    # ── Email ──────────────────────────────────────────────────────────────

    def _send_email(self, qr_data: str, image_path: str | None):
        """Send QR result to judge's email via SMTP."""
        try:
            msg = MIMEMultipart()
            msg["From"]    = Config.SENDER_EMAIL
            msg["To"]      = self.judge_email
            msg["Subject"] = (
                f"[{Config.TEAM_NAME}] QR Scan Result — {time.strftime('%H:%M:%S')}"
            )

            body = (
                f"Team: {Config.TEAM_NAME} ({Config.TEAM_ID})\n"
                f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                f"QR Data:\n{qr_data}\n\n"
                "-- Sent by ADDC Drone Autonomous System --"
            )
            msg.attach(MIMEText(body, "plain"))

            # Attach scanned image if available
            if image_path and Path(image_path).exists():
                with open(image_path, "rb") as img_file:
                    img = MIMEImage(img_file.read(), name="qr_scan.jpg")
                    img.add_header(
                        "Content-Disposition", "attachment", filename="qr_scan.jpg"
                    )
                    msg.attach(img)
                    log.info("Image attached to email.")

            with smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.login(Config.SENDER_EMAIL, Config.SENDER_PASSWORD)
                smtp.sendmail(
                    Config.SENDER_EMAIL,
                    self.judge_email,
                    msg.as_string(),
                )
            log.info(f"Email sent to {self.judge_email} ✓")

        except smtplib.SMTPAuthenticationError:
            log.error(
                "Email authentication failed. "
                "Use a Gmail App Password (not your regular password)."
            )
        except smtplib.SMTPException as exc:
            log.error(f"SMTP error: {exc}")
        except Exception as exc:
            log.error(f"Email send error: {exc}")

    # ── Helpers ────────────────────────────────────────────────────────────

    def _build_payload(self, qr_data: str) -> dict:
        return {
            "team_name": Config.TEAM_NAME,
            "team_id":   Config.TEAM_ID,
            "qr_data":   qr_data,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }


# ── Standalone test ────────────────────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sender = DataSender(
        judge_url=Config.JUDGE_SERVER_URL,
        judge_email=Config.JUDGE_EMAIL,
    )
    sender.send(qr_data="TEST_QR_DATA_12345", image_path=None)
    print("Send test complete.")
