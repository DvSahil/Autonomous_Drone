"""
judge_server.py — Judges' Receiver Server
==========================================
Run this script on the judges' laptop/PC.
It receives QR data from the drone via HTTP POST
and displays it in the terminal + saves to a log file.

Usage:
  pip install flask
  python judge_server.py
"""

import os
import time
import json
from flask import Flask, request, jsonify

app = Flask(__name__)
SAVE_DIR = "received_data"
os.makedirs(SAVE_DIR, exist_ok=True)


@app.route("/receive_qr", methods=["POST"])
def receive_qr():
    """Endpoint that receives QR data from the drone."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    # ── Parse incoming data ────────────────────────────────────────────────
    if request.content_type and "multipart" in request.content_type:
        # Received with image attachment
        team_name = request.form.get("team_name", "Unknown")
        team_id   = request.form.get("team_id",   "Unknown")
        qr_data   = request.form.get("qr_data",   "")
        recv_time = request.form.get("timestamp",  timestamp)

        # Save image if provided
        if "image" in request.files:
            img_file = request.files["image"]
            img_path = os.path.join(SAVE_DIR, f"{team_id}_{timestamp.replace(':', '-')}.jpg")
            img_file.save(img_path)
            print(f"  📷 Image saved → {img_path}")
    else:
        # JSON payload
        data      = request.get_json(force=True) or {}
        team_name = data.get("team_name", "Unknown")
        team_id   = data.get("team_id",   "Unknown")
        qr_data   = data.get("qr_data",   "")
        recv_time = data.get("timestamp",  timestamp)

    # ── Display to judges ──────────────────────────────────────────────────
    print("\n" + "=" * 55)
    print(f"  📡  QR DATA RECEIVED  [{timestamp}]")
    print("=" * 55)
    print(f"  Team:  {team_name} ({team_id})")
    print(f"  Time:  {recv_time}")
    print(f"  Data:  {qr_data}")
    print("=" * 55 + "\n")

    # ── Log to file ────────────────────────────────────────────────────────
    log_entry = {
        "received_at": timestamp,
        "team_name":   team_name,
        "team_id":     team_id,
        "qr_data":     qr_data,
        "sent_at":     recv_time,
    }
    log_path = os.path.join(SAVE_DIR, "submissions.jsonl")
    with open(log_path, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    return jsonify({"status": "ok", "message": "QR data received"}), 200


@app.route("/submissions", methods=["GET"])
def list_submissions():
    """Quick overview of all received submissions."""
    log_path = os.path.join(SAVE_DIR, "submissions.jsonl")
    if not os.path.exists(log_path):
        return jsonify([]), 200
    entries = []
    with open(log_path) as f:
        for line in f:
            entries.append(json.loads(line.strip()))
    return jsonify(entries), 200


if __name__ == "__main__":
    print("=" * 55)
    print("  ADDC QR DATA RECEIVER — Judge Server")
    print("  Listening on http://0.0.0.0:5000")
    print("  POST endpoint: /receive_qr")
    print("=" * 55)
    app.run(host="0.0.0.0", port=5000, debug=False)
