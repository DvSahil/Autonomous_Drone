"""
ADDC Drone QR Scanner - Main Controller
========================================
Autonomous drone mission:
  1. Fly to QR code location
  2. Scan QR code using OpenCV + webcam
  3. Send QR data to judges
  4. Drop egg using servo motor
  5. Return to home

Hardware: Raspberry Pi + Flight Controller (ArduPilot/MAVLink)
"""

import time
import logging
from config import Config
from drone_controller import DroneController
from qr_scanner import QRScanner
from servo_controller import ServoController
from data_sender import DataSender

# ── Logging setup ──────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("mission.log"),
    ],
)
log = logging.getLogger(__name__)


def run_mission():
    """Execute the full autonomous drone mission."""

    log.info("=" * 55)
    log.info("  ADDC DRONE QR SCANNER MISSION STARTING")
    log.info("=" * 55)

    # ── Initialise all modules ─────────────────────────────────────────────
    drone   = DroneController(connection_string=Config.DRONE_CONNECTION)
    scanner = QRScanner(camera_index=Config.CAMERA_INDEX)
    servo   = ServoController(pin=Config.SERVO_GPIO_PIN)
    sender  = DataSender(
        judge_url=Config.JUDGE_SERVER_URL,
        judge_email=Config.JUDGE_EMAIL,
    )

    try:
        # ── PHASE 1: Pre-flight checks ─────────────────────────────────────
        log.info("Phase 1: Pre-flight checks …")
        drone.pre_flight_check()
        servo.self_test()           # Verify servo moves correctly
        scanner.verify_camera()     # Ensure webcam is accessible
        log.info("All systems GO ✓")

        # ── PHASE 2: Arm & take off ────────────────────────────────────────
        log.info("Phase 2: Arming and taking off …")
        drone.arm_and_takeoff(altitude=Config.TARGET_ALTITUDE)
        log.info(f"Hovering at {Config.TARGET_ALTITUDE} m ✓")

        # ── PHASE 3: Fly to QR waypoint ────────────────────────────────────
        log.info("Phase 3: Flying to QR scan location …")
        drone.goto_location(
            lat=Config.QR_WAYPOINT_LAT,
            lon=Config.QR_WAYPOINT_LON,
            alt=Config.TARGET_ALTITUDE,
        )
        log.info("Arrived at QR location ✓")

        # ── PHASE 4: Descend to scan altitude ─────────────────────────────
        log.info(f"Phase 4: Descending to scan altitude {Config.SCAN_ALTITUDE} m …")
        drone.goto_location(
            lat=Config.QR_WAYPOINT_LAT,
            lon=Config.QR_WAYPOINT_LON,
            alt=Config.SCAN_ALTITUDE,
        )
        time.sleep(2)  # Let the drone stabilise

        # ── PHASE 5: Scan QR code ──────────────────────────────────────────
        log.info("Phase 5: Scanning QR code …")
        qr_data = scanner.scan(
            timeout=Config.SCAN_TIMEOUT_SEC,
            save_frame=True,
        )

        if qr_data:
            log.info(f"QR data decoded: {qr_data}")
        else:
            log.warning("QR scan timed out — using fallback value.")
            qr_data = "QR_SCAN_FAILED"

        # ── PHASE 6: Send data to judges ───────────────────────────────────
        log.info("Phase 6: Sending QR data to judges …")
        sender.send(qr_data=qr_data, image_path=scanner.last_frame_path)
        log.info("Data sent to judges ✓")

        # ── PHASE 7: Drop egg ──────────────────────────────────────────────
        log.info("Phase 7: Dropping egg via servo …")
        servo.release_payload()
        time.sleep(1)
        log.info("Egg dropped ✓")

        # ── PHASE 8: Return to launch ──────────────────────────────────────
        log.info("Phase 8: Returning to launch …")
        drone.return_to_launch()
        log.info("Mission complete ✓")

    except KeyboardInterrupt:
        log.warning("Mission interrupted by operator — initiating RTL …")
        drone.return_to_launch()

    except Exception as exc:
        log.error(f"Mission ABORT: {exc}", exc_info=True)
        drone.return_to_launch()

    finally:
        scanner.release()
        servo.cleanup()
        drone.disconnect()
        log.info("All resources released. Mission ended.")


if __name__ == "__main__":
    run_mission()
