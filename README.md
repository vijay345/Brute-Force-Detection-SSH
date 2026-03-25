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

Ip Address
<img width="758" height="332" alt="Ipa address(brute force)" src="https://github.com/user-attachments/assets/80e80f57-1966-4faa-ba57-d5b10140d12b" />


## Attack Simulation
Multiple failed SSH login attempts were generated using invalid credentials:

```bash
ssh fakeuser@10.0.2.15

<img width="788" height="432" alt="Fake user(Brute Force)" src="https://github.com/user-attachments/assets/0c1661e4-b1b1-4968-bdff-1991579fc8ae" />


Logs were monitored using:

sudo journalctl -u ssh | grep "Failed"

Findings:
Repeated failed login attempts
Same source IP: 10.0.2.15
Invalid usernames targeted
High frequency attempts

<img width="727" height="455" alt="Log entries (Brute Force)" src="https://github.com/user-attachments/assets/94a4cde9-4943-4d89-9631-95c32d933db6" />



Mitigation

Fail2Ban was used to block the malicious IP: sudo fail2ban-client set sshd banip 10.0.2.15

Results
Attacker IP successfully identified
IP banned using Fail2Ban
Verified via:

sudo fail2ban-client status sshd
sudo iptables -L -n
<img width="637" height="236" alt="Banned Attacker(Brute Force)" src="https://github.com/user-attachments/assets/66f5a7e4-24c7-4d00-8123-1a6b45184cdf" />


Key Learnings
Log analysis for intrusion detection
Identifying brute force attack patterns
Implementing defensive controls
Understanding Fail2Ban and SSH security
