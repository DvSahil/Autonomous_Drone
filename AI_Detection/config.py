"""
config.py — Mission Configuration
===================================
Edit these values before each flight.
"""


class Config:
    # ── Drone connection ───────────────────────────────────────────────────
    # Serial port for Pixhawk/APM connected to Raspberry Pi
    DRONE_CONNECTION = "/dev/ttyAMA0"   # UART on Raspberry Pi GPIO
    # DRONE_CONNECTION = "/dev/ttyUSB0"  # USB-to-Serial adapter
    # DRONE_CONNECTION = "tcp:127.0.0.1:5760"  # SITL simulator

    BAUD_RATE = 57600

    # ── Flight parameters ──────────────────────────────────────────────────
    TARGET_ALTITUDE = 10.0  # metres — cruise altitude
    SCAN_ALTITUDE   = 3.0   # metres — descend to this for QR scan
    GROUNDSPEED     = 5.0   # m/s

    # ── QR waypoint (GPS coordinates of QR target) ─────────────────────────
    # Replace with actual competition site coordinates
    QR_WAYPOINT_LAT = 24.453884   # Example: Abu Dhabi
    QR_WAYPOINT_LON = 54.377344

    # ── Camera ─────────────────────────────────────────────────────────────
    CAMERA_INDEX      = 0    # 0 = first USB webcam on Raspberry Pi
    SCAN_TIMEOUT_SEC  = 30   # seconds to attempt QR scan before giving up
    FRAME_SAVE_PATH   = "scanned_qr.jpg"

    # ── Servo (egg drop mechanism) ─────────────────────────────────────────
    SERVO_GPIO_PIN   = 18   # BCM pin connected to servo signal wire
    SERVO_LOCKED_DC  = 7.5  # duty cycle — payload locked (neutral)
    SERVO_OPEN_DC    = 12.0 # duty cycle — release payload
    SERVO_PWM_FREQ   = 50   # Hz (standard for RC servos)

    # ── Judge data endpoint ────────────────────────────────────────────────
    # HTTP POST endpoint run by judges to receive QR data
    JUDGE_SERVER_URL = "http://192.168.1.100:5000/receive_qr"

    # Optional: also email the data
    JUDGE_EMAIL      = "judges@addc-competition.com"
    SMTP_SERVER      = "smtp.gmail.com"
    SMTP_PORT        = 587
    SENDER_EMAIL     = "your_team@gmail.com"
    SENDER_PASSWORD  = "your_app_password"   # Use Gmail App Password

    # ── Team info (included with every submission) ─────────────────────────
    TEAM_NAME        = "Team Name"
    TEAM_ID          = "ADDC-2024-XXX"
