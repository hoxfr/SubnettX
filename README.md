# 🛡️ SubnettX: Zero-Trust Dual-Vector Attendance System

> **🏆 Achieved Top 30 & Ranked 1st in Phase 3 at our College Hackathon (BML Munjal University)!**

**🚀 Live Demo:** https://thepentabytes.pythonanywhere.com/

SubnettX is a next-generation attendance and threat-monitoring system designed to completely eliminate proxy attendance. Legacy systems like manual roll calls, static QR codes, and GPS geofencing are easily bypassed. SubnettX solves this using a **Zero-Trust Dual-Vector Architecture**.

## ✨ How It Works (The 2 Vectors)

Instead of relying solely on digital verification, SubnettX combines digital cryptography with physical acoustic presence.

1. **👁️ Vector 1 (Optical):** A cryptographically secure, temporally rotating QR code displayed on the professor's screen. It changes every 3 seconds.
2. **🔊 Vector 2 (Acoustic):** An invisible, inaudible high-frequency **18.5kHz ultrasonic sound wave** broadcasted locally from the professor's laptop. 

To successfully mark attendance, the student's phone must optically scan the active QR token **AND** physically hear the ultrasonic beacon using the HTML5 Web Audio API. Screen sharing, WhatsApp photos, or Discord streams will instantly fail the acoustic handshake.

## 🚀 Key Features

* **Absolute Proof of Presence:** WhatsApp photo-sharing and Discord screen-shares strip high-frequency audio, making remote proxies impossible.
* **$0 Hardware Deployment:** Uses existing laptop speakers and student smartphone microphones. No extra beacons required.
* **Threat Dashboard:** Live security dashboard for professors to detect spoof attempts in real-time.
* **Smart Manual Fallback:** If a student faces genuine hardware issues, professors can manually override. To ensure transparency, the system automatically emails the HOD (Head of Department) a log of all manual overrides to prevent positive bias.
* **Daily Receipts:** Students receive daily attendance logs so records cannot be silently altered at the end of the semester.

## 🧠 Future Scope (System Evolution)
* **Native App Transition:** Moving from a Web MVP to a Native App to lock sessions to physical devices.
* **Biometric Anchoring:** Tying the attendance token to the device's secure hardware enclave (FaceID/Fingerprint) with a strict 3-minute session expiry to prevent students from sharing unlocked phones.

---
*Built with ❤️ during a 24-Hour Hackathon by First-Year BTech Students.*
