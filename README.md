# 🚁 Autonomous Drone QR Detection System (ADDC Project)

## 📌 Overview

This project presents an autonomous drone system developed for ADDC, designed to navigate to a target location, detect and decode a QR code using onboard vision processing, transmit the extracted data to judges, perform a payload drop using a servo mechanism, and return to the starting position. The system integrates computer vision, embedded systems, and drone control logic into a complete workflow.

---

## 🎯 Objective

The main objective of this project is to build an autonomous drone capable of:

* Navigating to a predefined QR location
* Detecting and decoding QR codes in real time
* Sending decoded data to judges or a remote system
* Performing a payload drop using a servo motor
* Returning safely to the base location

---

## 🧠 System Workflow

1. The drone takes off and moves autonomously toward the target QR location
2. A camera mounted on the drone captures live video feed
3. OpenCV processes the frames and detects the QR code
4. The QR code is decoded and the data is extracted
5. Extracted data is transmitted to the judges through a communication interface
6. A servo motor is activated to drop the payload (egg)
7. The drone completes its task and returns to the base

---

## 🔄 Workflow Summary

Autonomous Navigation → Camera Input → QR Detection → Data Extraction → Data Transmission → Servo Activation → Return to Base

---

## ⚙️ Technologies Used

* Python for implementation
* OpenCV for computer vision and QR detection
* Raspberry Pi as onboard processing unit
* Servo motor for payload dropping mechanism
* Drone flight controller (such as PX4 or ArduPilot)
* Wireless communication for data transmission

---

## 📂 Project Structure

AI_Detection → Contains QR detection and vision-related logic
ROS → Contains system architecture and future ROS integration
Images → Includes captured images and detection results
Documentation → Project report and technical explanation
WORKINGLINKS → References, demo links, and resources

---

## 🧪 Key Features

* Real-time QR code detection using onboard camera
* Lightweight processing suitable for Raspberry Pi
* Automated payload drop mechanism
* Modular design for integration with autonomous navigation
* Expandable architecture for ROS-based systems

---

## 📡 Data Transmission

The decoded QR data is transmitted to the judges using a network-based communication system. This can be implemented using HTTP requests or any wireless protocol depending on system setup.

---

## 🚀 Applications

* Autonomous delivery systems
* Drone-based inspection and identification
* Smart logistics and warehouse automation
* Search and rescue operations
* Defense and surveillance systems

---

## 🔮 Future Improvements

* Full integration with ROS 2 for modular control
* GPS-based navigation and waypoint planning
* AI-based object detection using advanced models
* Real-time telemetry dashboard
* Improved payload mechanism and accuracy

---

## 👨‍💻 Author

Mohammad Sahil Khan

---

## 📢 Note

This project demonstrates a complete integration of vision-based detection and drone-based task execution. The system is designed with a modular approach so that each component such as perception, control, and actuation can be further improved and scaled for real-world applications.
