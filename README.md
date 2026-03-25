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

Ip Address:
https://github.com/vijay345/Brute-Force-Detection-SSH/blob/main/Ipa%20address(brute%20force).png

## Attack Simulation
Multiple failed SSH login attempts were generated using invalid credentials:

ssh fakeuser@10.0.2.15
https://github.com/vijay345/Brute-Force-Detection-SSH/blob/main/Fake%20user(Brute%20Force).png


Logs were monitored using:

sudo journalctl -u ssh | grep "Failed"

Findings:
Repeated failed login attempts
Same source IP: 10.0.2.15
Invalid usernames targeted
High frequency attempts
https://github.com/vijay345/Brute-Force-Detection-SSH/blob/main/Log%20entries%20(Brute%20Force).png


Mitigation:

Fail2Ban was used to block the malicious IP: sudo fail2ban-client set sshd banip 10.0.2.15

Results:
Attacker IP successfully identified
IP banned using Fail2Ban
Verified via:

sudo fail2ban-client status sshd
sudo iptables -L -n

https://github.com/vijay345/Brute-Force-Detection-SSH/blob/main/Banned%20Attacker(Brute%20Force).png


Key Learnings:

Log analysis for intrusion detection, 
Identifying brute force attack patterns, 
Implementing defensive controls, 
Understanding Fail2Ban and SSH security.
