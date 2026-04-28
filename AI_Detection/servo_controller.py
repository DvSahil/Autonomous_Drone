"""
servo_controller.py — Servo Motor Control for Egg Drop
========================================================
Uses RPi.GPIO PWM to control the servo that releases the egg.

Wiring:
  Servo Red   → Raspberry Pi 5V pin
  Servo Brown → Raspberry Pi GND
  Servo Orange (signal) → GPIO pin defined in config.py
"""

import time
import logging
try:
    import RPi.GPIO as GPIO
    RUNNING_ON_PI = True
except ImportError:
    RUNNING_ON_PI = False
    logging.warning("RPi.GPIO not found — running in simulation mode.")

from config import Config

log = logging.getLogger(__name__)


class ServoController:
    """Controls a PWM servo for the egg-drop payload release."""

    def __init__(self, pin: int):
        self.pin = pin
        self.pwm = None
        self._setup()

    # ── Setup ──────────────────────────────────────────────────────────────

    def _setup(self):
        if not RUNNING_ON_PI:
            log.info(f"[SIM] Servo setup on pin {self.pin}")
            return

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        self.pwm = GPIO.PWM(self.pin, Config.SERVO_PWM_FREQ)
        self.pwm.start(Config.SERVO_LOCKED_DC)   # Start in locked position
        time.sleep(0.5)
        log.info(f"Servo initialised on GPIO{self.pin} ✓")

    # ── Self-test ──────────────────────────────────────────────────────────

    def self_test(self):
        """
        Wiggle the servo slightly to confirm it is responding.
        Does NOT release payload — just verifies movement.
        """
        log.info("Servo self-test …")
        if not RUNNING_ON_PI:
            log.info("[SIM] Self-test passed (simulated).")
            return

        # Nudge slightly and return
        self.pwm.ChangeDutyCycle(Config.SERVO_LOCKED_DC + 0.5)
        time.sleep(0.4)
        self.pwm.ChangeDutyCycle(Config.SERVO_LOCKED_DC)
        time.sleep(0.4)
        log.info("Servo self-test passed ✓")

    # ── Payload release ────────────────────────────────────────────────────

    def release_payload(self, hold_seconds: float = 1.0):
        """
        Rotate servo to open position to release the egg,
        then return to locked position.
        """
        log.info("Opening servo — releasing payload …")
        if not RUNNING_ON_PI:
            log.info(f"[SIM] Servo open DC={Config.SERVO_OPEN_DC}")
            time.sleep(hold_seconds)
            log.info(f"[SIM] Servo locked DC={Config.SERVO_LOCKED_DC}")
            return

        self.pwm.ChangeDutyCycle(Config.SERVO_OPEN_DC)
        time.sleep(hold_seconds)          # Hold open so egg drops
        self.pwm.ChangeDutyCycle(Config.SERVO_LOCKED_DC)  # Return to safe
        time.sleep(0.5)
        log.info("Servo returned to locked position ✓")

    # ── Manual control ─────────────────────────────────────────────────────

    def set_angle(self, angle_deg: float):
        """
        Move servo to a specific angle (0–180°).
        Maps angle to duty cycle: 0° ≈ 2.5%, 90° ≈ 7.5%, 180° ≈ 12.5%
        """
        dc = 2.5 + (angle_deg / 180.0) * 10.0
        log.info(f"Servo → {angle_deg}° (DC={dc:.1f}%)")
        if self.pwm:
            self.pwm.ChangeDutyCycle(dc)

    # ── Cleanup ────────────────────────────────────────────────────────────

    def cleanup(self):
        if self.pwm:
            self.pwm.stop()
        if RUNNING_ON_PI:
            GPIO.cleanup()
        log.info("Servo GPIO cleaned up.")


# ── Standalone test ────────────────────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    servo = ServoController(pin=Config.SERVO_GPIO_PIN)
    servo.self_test()
    input("Press ENTER to release payload …")
    servo.release_payload()
    servo.cleanup()
    print("Done.")
