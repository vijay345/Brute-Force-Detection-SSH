# Brute-Force-Detection-SSH
Brute Force Attack Simulation 


# 🔐 Brute Force Attack Detection using SSH Logs

## 📌 Overview
This project demonstrates detection and mitigation of a brute force attack on an SSH service using system logs and Fail2Ban.

---

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

📸 Screenshots
---
🛡️ Ip Address:

<img width="758" height="332" alt="Ipa address(brute force)" src="https://github.com/user-attachments/assets/ebb4d042-c282-423c-afe0-63f45a6e46b5" />

🔴 Failed Login Attempts:

<img width="727" height="455" alt="Log entries (Brute Force)" src="https://github.com/user-attachments/assets/e7ad0694-1f0b-4766-a098-477fbc6e8bd4" />

🛡️ Fail2Ban Status:

<img width="788" height="432" alt="Fake user(Brute Force)" src="https://github.com/user-attachments/assets/7596ffb2-b685-470d-b1f0-656cc635715f" />

🚫 Blocked IP:

<img width="637" height="236" alt="Banned Attacker(Brute Force)" src="https://github.com/user-attachments/assets/b8443875-7868-49b8-b9b1-69c5a507c892" />
