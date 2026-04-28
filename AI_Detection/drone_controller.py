"""
drone_controller.py — DroneKit MAVLink Flight Controller
=========================================================
Controls the drone via ArduPilot / Pixhawk using DroneKit.
Handles: arming, takeoff, waypoint navigation, RTL.
"""

import time
import math
import logging
from dronekit import connect, VehicleMode, LocationGlobalRelative
from pymavlink import mavutil
from config import Config

log = logging.getLogger(__name__)


class DroneController:
    """Wrapper around DroneKit for autonomous mission control."""

    def __init__(self, connection_string: str):
        log.info(f"Connecting to drone on {connection_string} …")
        self.vehicle = connect(
            connection_string,
            baud=Config.BAUD_RATE,
            wait_ready=True,
        )
        log.info(f"Connected | Firmware: {self.vehicle.version}")

    # ── Pre-flight ─────────────────────────────────────────────────────────

    def pre_flight_check(self):
        """Verify GPS fix, battery, and EKF status before flight."""
        v = self.vehicle

        # Wait for GPS
        log.info("Waiting for GPS fix …")
        while v.gps_0.fix_type < 3:
            log.info(f"  GPS fix type: {v.gps_0.fix_type} (need 3D fix)")
            time.sleep(1)
        log.info(f"GPS 3D fix ✓  Satellites: {v.gps_0.satellites_visible}")

        # Battery check
        if v.battery.voltage and v.battery.voltage < 10.5:
            raise RuntimeError(
                f"Battery too low: {v.battery.voltage:.1f}V — charge before flight!"
            )
        log.info(f"Battery: {v.battery.voltage:.1f}V ✓")

        # EKF health
        if not v.ekf_ok:
            raise RuntimeError("EKF not healthy — check IMU and compass calibration.")
        log.info("EKF OK ✓")

    # ── Arm & Takeoff ──────────────────────────────────────────────────────

    def arm_and_takeoff(self, altitude: float):
        """
        Arm the vehicle in GUIDED mode and climb to target altitude.
        Waits until the vehicle reaches within 95% of the target altitude.
        """
        v = self.vehicle

        log.info("Setting mode to GUIDED …")
        v.mode = VehicleMode("GUIDED")
        time.sleep(2)

        log.info("Arming motors …")
        v.armed = True
        while not v.armed:
            log.info("  Waiting for arm …")
            time.sleep(1)
        log.info("Armed ✓")

        log.info(f"Taking off to {altitude} m …")
        v.simple_takeoff(altitude)

        # Wait until target altitude reached
        while True:
            current_alt = v.location.global_relative_frame.alt
            log.info(f"  Altitude: {current_alt:.1f} m")
            if current_alt >= altitude * 0.95:
                log.info("Target altitude reached ✓")
                break
            time.sleep(1)

    # ── Navigation ─────────────────────────────────────────────────────────

    def goto_location(self, lat: float, lon: float, alt: float):
        """
        Fly to (lat, lon, alt) and block until within ARRIVAL_RADIUS metres.
        """
        target = LocationGlobalRelative(lat, lon, alt)
        self.vehicle.simple_goto(target, groundspeed=Config.GROUNDSPEED)
        log.info(f"Heading to ({lat:.6f}, {lon:.6f}) at {alt} m …")

        ARRIVAL_RADIUS = 1.5  # metres

        while True:
            remaining = self._distance_to(lat, lon)
            log.info(f"  Distance to target: {remaining:.1f} m")
            if remaining < ARRIVAL_RADIUS:
                log.info("Waypoint reached ✓")
                break
            time.sleep(1)

    def _distance_to(self, target_lat: float, target_lon: float) -> float:
        """Haversine distance in metres from current position to target."""
        loc = self.vehicle.location.global_relative_frame
        lat1, lon1 = math.radians(loc.lat), math.radians(loc.lon)
        lat2, lon2 = math.radians(target_lat), math.radians(target_lon)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        )
        return 6371000 * 2 * math.asin(math.sqrt(a))

    # ── Return to Launch ───────────────────────────────────────────────────

    def return_to_launch(self):
        """Switch vehicle to RTL mode and wait for it to land."""
        log.info("RTL initiated …")
        self.vehicle.mode = VehicleMode("RTL")
        # Wait until on ground (armed flag clears)
        while self.vehicle.armed:
            alt = self.vehicle.location.global_relative_frame.alt
            log.info(f"  Descending … alt={alt:.1f} m")
            time.sleep(2)
        log.info("Landed and disarmed ✓")

    # ── Cleanup ────────────────────────────────────────────────────────────

    def disconnect(self):
        self.vehicle.close()
        log.info("Vehicle connection closed.")
