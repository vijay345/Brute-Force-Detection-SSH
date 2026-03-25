# Brute-Force-Detection-SSH
Brute Force Attack Simulation 


# 🔐 Brute Force Attack Detection using SSH Logs

## 📌 Overview
This project demonstrates detection and mitigation of a brute force attack on an SSH service using system logs and Fail2Ban.

## 🧠 Analysis Summary

The attack was identified as a brute force attempt based on repeated failed SSH login attempts from a single IP address within a short time frame. The attacker was identified and blocked using Fail2Ban.


## 🛠 Tools & Technologies
- Kali Linux
- OpenSSH
- Fail2Ban
- Journalctl

---

## 🚨 Attack Simulation
Multiple failed SSH login attempts were generated:

ssh fakeuser@10.0.2.15

🔍 Detection
---
sudo journalctl -u ssh | grep "Failed"

🔍Findings:
---
- Multiple failed login attempts
- Same source IP: 10.0.2.15
- High frequency attempts

🛡️ Mitigation
---
sudo fail2ban-client set sshd banip 10.0.2.15


## 📸 Screenshots

---

### 🔴 Failed Login Attempts (Detection)
<img width="727" height="455" alt="Log entries (Brute Force)" src="https://github.com/user-attachments/assets/e7ad0694-1f0b-4766-a098-477fbc6e8bd4" />

This shows multiple failed SSH login attempts, indicating a brute force attack pattern.

---

### 🌐 Attacker IP Identification
<img width="758" height="332" alt="IP address (Brute Force)" src="https://github.com/user-attachments/assets/ebb4d042-c282-423c-afe0-63f45a6e46b5" />

The repeated login attempts originate from a single IP address, confirming the attack source.

---

### 🛡️ Fail2Ban Status (Mitigation)
<img width="589" height="245" alt="fail2ban status" src="https://github.com/user-attachments/assets/80669e86-e409-458c-a69d-ec8c2b32d01b" />

Fail2Ban was used to identify and ban the malicious IP after multiple failed attempts.

---

### 🚫 Blocked IP (Verification)
<img width="637" height="236" alt="Banned Attacker (Brute Force)" src="https://github.com/user-attachments/assets/b8443875-7868-49b8-b9b1-69c5a507c892" />

This confirms the attacker IP has been successfully blocked from further access.
