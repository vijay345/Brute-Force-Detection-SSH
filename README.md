# Brute-Force-Detection-SSH
Brute Force Attack Simulation 


# Brute Force Attack Detection using SSH Logs

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
Multiple failed SSH login attempts were generated using invalid credentials:

```bash
ssh fakeuser@10.0.2.15


Logs were monitored using:

sudo journalctl -u ssh | grep "Failed"

Findings:
Repeated failed login attempts
Same source IP: 10.0.2.15
Invalid usernames targeted
High frequency attempts



Mitigation

Fail2Ban was used to block the malicious IP: sudo fail2ban-client set sshd banip 10.0.2.15

Results
Attacker IP successfully identified
IP banned using Fail2Ban
Verified via:

sudo fail2ban-client status sshd
sudo iptables -L -n


Key Learnings
Log analysis for intrusion detection
Identifying brute force attack patterns
Implementing defensive controls
Understanding Fail2Ban and SSH security
