"""
qr_scanner.py — QR Code Scanner using OpenCV + pyzbar
=======================================================
Captures frames from a USB webcam and decodes QR codes.
Saves a snapshot of the decoded frame for judge submission.
"""

import cv2
import time
import logging
from pyzbar import pyzbar
from config import Config

log = logging.getLogger(__name__)


class QRScanner:
    """Scan QR codes from a webcam using OpenCV and pyzbar."""

    def __init__(self, camera_index: int = 0):
        self.camera_index     = camera_index
        self.cap              = None
        self.last_frame_path  = None

    # ── Setup ──────────────────────────────────────────────────────────────

    def verify_camera(self):
        """Open the camera briefly to confirm it is accessible."""
        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            raise RuntimeError(
                f"Cannot open camera index {self.camera_index}. "
                "Check USB webcam is connected to Raspberry Pi."
            )
        cap.release()
        log.info(f"Camera {self.camera_index} verified ✓")

    def _open_camera(self):
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            raise RuntimeError("Failed to open camera for scanning.")
        # Optional: set resolution for faster processing
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        log.info("Camera opened for scanning.")

    # ── Core scan logic ────────────────────────────────────────────────────

    def scan(self, timeout: float = 30, save_frame: bool = True) -> str | None:
        """
        Attempt to scan a QR code within `timeout` seconds.

        Returns:
            Decoded QR string on success, None on timeout.
        """
        self._open_camera()
        start = time.time()

        log.info(f"QR scanning started (timeout={timeout}s) …")

        while (time.time() - start) < timeout:
            ret, frame = self.cap.read()
            if not ret:
                log.warning("Camera read failed — skipping frame.")
                time.sleep(0.1)
                continue

            # ── Decode QR ─────────────────────────────────────────────────
            decoded = self._decode_frame(frame)
            if decoded:
                log.info(f"QR decoded successfully: {decoded}")
                if save_frame:
                    self._save_annotated_frame(frame, decoded)
                self.release()
                return decoded

            # ── Live preview (disable on headless Pi) ──────────────────────
            # cv2.imshow("QR Scanner", frame)
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break

            time.sleep(0.05)  # ~20 fps polling

        log.warning("QR scan timed out.")
        self.release()
        return None

    # ── Frame processing ───────────────────────────────────────────────────

    def _decode_frame(self, frame) -> str | None:
        """Try to decode any QR code in the given BGR frame."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Enhance contrast for low-light conditions
        gray = cv2.equalizeHist(gray)

        barcodes = pyzbar.decode(gray)
        for barcode in barcodes:
            if barcode.type == "QRCODE":
                data = barcode.data.decode("utf-8")
                return data

        return None

    def _save_annotated_frame(self, frame, decoded_text: str):
        """Draw bounding box + text on frame and save as JPEG."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        barcodes = pyzbar.decode(gray)

        for barcode in barcodes:
            if barcode.type == "QRCODE":
                (x, y, w, h) = barcode.rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
                label = f"QR: {decoded_text[:40]}"
                cv2.putText(
                    frame, label,
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (0, 255, 0), 2,
                )

        # Add timestamp overlay
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(
            frame, ts,
            (10, frame.shape[0] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5, (255, 255, 255), 1,
        )

        path = Config.FRAME_SAVE_PATH
        cv2.imwrite(path, frame)
        self.last_frame_path = path
        log.info(f"Annotated frame saved → {path}")

    # ── Cleanup ────────────────────────────────────────────────────────────

    def release(self):
        """Release camera and destroy any OpenCV windows."""
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None
        cv2.destroyAllWindows()
        log.info("Camera released.")


# ── Standalone test ────────────────────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scanner = QRScanner(camera_index=0)
    scanner.verify_camera()
    print("Hold a QR code in front of the camera …")
    result = scanner.scan(timeout=30, save_frame=True)
    if result:
        print(f"\n✅  QR Data: {result}")
        print(f"   Frame saved to: {scanner.last_frame_path}")
    else:
        print("\n❌  No QR code detected within timeout.")
