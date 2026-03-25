# 🔐 Brute Force Attack Detection using SSH Logs

> **Real-world brute force attack simulation, detection, automated response, and hardening recommendations using Kali Linux, Fail2Ban, and custom Bash/Python tooling.**

---

## 📌 Overview

This project demonstrates a full detection-and-response workflow for SSH brute force attacks — one of the most common initial access techniques documented in [MITRE ATT&CK T1110](https://attack.mitre.org/techniques/T1110/).

The lab covers:
- Simulating a credential brute force attack using `hydra`
- Detecting the attack via SSH auth logs and `journalctl`
- Automating detection with a custom Bash script
- Parsing and analysing logs with a Python script
- Mitigating and blocking the attacker using Fail2Ban
- Hardening recommendations to prevent recurrence

---

## 🧱 Environment

| Component       | Details                          |
|----------------|----------------------------------|
| OS             | Kali Linux (VirtualBox VM)       |
| Target         | Ubuntu 22.04 VM (OpenSSH Server) |
| Network        | Host-only / NAT adapter          |
| Attack tool    | Hydra, custom Bash loop          |
| Detection      | journalctl, auth.log, Python     |
| Mitigation     | Fail2Ban                         |

---

## 🗺️ Attack Flow Diagram

```
┌────────────────────┐         SSH Port 22          ┌──────────────────────┐
│  Attacker Machine  │ ───────────────────────────► │   Target SSH Server  │
│  (Kali Linux)      │   Multiple failed logins      │   (Ubuntu VM)        │
│  IP: 10.0.2.5      │ ◄─────────────────────────── │   IP: 10.0.2.15      │
└────────────────────┘   Auth failure responses      └──────────┬───────────┘
                                                                │
                                                   ┌────────────▼────────────┐
                                                   │  /var/log/auth.log      │
                                                   │  journalctl -u ssh      │
                                                   └────────────┬────────────┘
                                                                │
                                                   ┌────────────▼────────────┐
                                                   │  detect_bruteforce.sh   │
                                                   │  bruteforce_parser.py   │
                                                   └────────────┬────────────┘
                                                                │
                                                   ┌────────────▼────────────┐
                                                   │       Fail2Ban          │
                                                   │  Threshold: 5 fails     │
                                                   │  Window: 10 minutes     │
                                                   │  Ban duration: 1 hour   │
                                                   └────────────┬────────────┘
                                                                │
                                                   ┌────────────▼────────────┐
                                                   │  IP BANNED via iptables │
                                                   │  Alert logged           │
                                                   └─────────────────────────┘
```

---

## 🚨 Attack Simulation

### Step 1 — Start a brute force attack using Hydra

```bash
hydra -l root -P /usr/share/wordlists/rockyou.txt ssh://10.0.2.15 -t 4 -vV
```

Or using a simple Bash loop to generate rapid failed logins:

```bash
for i in {1..20}; do
  ssh fakeuser@10.0.2.15 -o StrictHostKeyChecking=no 2>/dev/null
done
```

This generates a burst of failed authentication events in the target's SSH logs.

---

## 🔍 Detection

### Step 2 — Check logs manually

```bash
# View failed SSH login attempts
sudo journalctl -u ssh | grep "Failed"

# Or directly from auth log
sudo grep "Failed password" /var/log/auth.log

# Count failures per IP
sudo grep "Failed password" /var/log/auth.log | awk '{print $11}' | sort | uniq -c | sort -rn
```

### Step 3 — Run automated detection script

```bash
chmod +x detect_bruteforce.sh
sudo ./detect_bruteforce.sh
```

### Step 4 — Run Python log parser for deeper analysis

```bash
python3 bruteforce_parser.py --log /var/log/auth.log --threshold 5
```

---

## 🔍 Findings

| Indicator               | Value                            |
|------------------------|----------------------------------|
| Attack type            | SSH Brute Force (T1110.001)      |
| Source IP              | 10.0.2.5                         |
| Target IP              | 10.0.2.15                        |
| Targeted usernames     | root, admin, fakeuser            |
| Failed attempts        | 20+ within 2 minutes             |
| Detection method       | journalctl + auth.log analysis   |
| MITRE ATT&CK mapping   | T1110 – Brute Force              |

---

## 🛡️ Mitigation

### Step 5 — Manually ban the attacker IP

```bash
sudo fail2ban-client set sshd banip 10.0.2.5
```

### Step 6 — Verify the ban

```bash
sudo fail2ban-client status sshd
sudo iptables -L -n | grep 10.0.2.5
```

### Fail2Ban Configuration Used (`/etc/fail2ban/jail.local`)

```ini
[sshd]
enabled  = true
port     = ssh
filter   = sshd
logpath  = /var/log/auth.log
maxretry = 5
findtime = 600
bantime  = 3600
```

- **maxretry**: 5 failed attempts triggers a ban
- **findtime**: within a 10-minute window
- **bantime**: IP banned for 1 hour

---

## 📸 Screenshots

### 🔴 Failed Login Attempts (Detection)
> Multiple failed SSH login attempts visible in journalctl output — a clear brute force pattern.

<img width="788" height="432" alt="Fake user(Brute Force)" src="https://github.com/user-attachments/assets/7299c29b-e24b-4920-94e0-0a624e68815f" />

---

### 🌐 Attacker IP Identification
> Repeated failed logins all originate from a single IP, confirming the attack source.

<img width="758" height="332" alt="Ipa address(brute force)" src="https://github.com/user-attachments/assets/107f09d9-d1dd-438b-bee9-fc50841c439a" />

---

### 🛡️ Fail2Ban Status (Active Mitigation)
> Fail2Ban sshd jail is active and monitoring for threshold violations.

<img width="589" height="245" alt="fail2ban status" src="https://github.com/user-attachments/assets/e82f6c8c-4a0d-412a-ab7c-e0b5cae6927d" />

---

### 🚫 Blocked IP (Verification)
> The attacker IP has been successfully banned and confirmed via Fail2Ban client.

<img width="637" height="236" alt="Banned Attacker(Brute Force)" src="https://github.com/user-attachments/assets/c4ac52a3-4d16-46b4-a93b-f07cca73f753" />


---

## 🧠 Lessons Learned

1. **SSH is an extremely common attack surface** — leaving it exposed on default port 22 with password auth enabled invites automated attacks within minutes of deployment.
2. **Log correlation is key** — a single failed login is noise; 20 failures from one IP in 2 minutes is a clear signal. Volume + velocity + single-source = brute force.
3. **Fail2Ban works, but it's reactive** — the attacker still got 5 attempts before being blocked. Proactive hardening (below) is essential.
4. **Automating detection matters** — manually reviewing logs doesn't scale. Even a simple bash script or Python parser adds enormous value in a real SOC environment.

---

## 🔒 Hardening Recommendations

| Recommendation                          | Command / Action                                      |
|----------------------------------------|-------------------------------------------------------|
| Disable SSH password authentication    | `PasswordAuthentication no` in `/etc/ssh/sshd_config` |
| Use SSH key-based authentication only  | `ssh-keygen` + `ssh-copy-id`                          |
| Change default SSH port                | `Port 2222` in `/etc/ssh/sshd_config`                 |
| Restrict SSH access by IP (firewall)   | `ufw allow from 10.0.2.5 to any port 22`              |
| Limit login attempts via sshd          | `MaxAuthTries 3` in `/etc/ssh/sshd_config`            |
| Enable two-factor authentication       | Google Authenticator PAM module                       |
| Monitor with SIEM (e.g. Splunk/ELK)    | Forward auth.log to centralised log aggregator        |

---

## 🛠️ Tools & Technologies

| Tool           | Purpose                                  |
|---------------|------------------------------------------|
| Kali Linux     | Attack simulation environment            |
| OpenSSH        | Target SSH service                       |
| Hydra          | Brute force attack tool                  |
| Fail2Ban       | Automated IP banning                     |
| journalctl     | Systemd log viewer                       |
| auth.log       | SSH authentication log source            |
| Bash           | Custom detection automation script       |
| Python 3       | Log parsing and analysis                 |
| iptables       | Firewall / IP blocking backend           |

---

## 📂 Project Structure

```
Brute-Force-Detection-SSH/
├── README.md                   # This file
├── detect_bruteforce.sh        # Bash detection & alerting script
├── bruteforce_parser.py        # Python log analysis script
├── jail.local                  # Fail2Ban configuration
└── screenshots/
    ├── failed_logins.png
    ├── attacker_ip.png
    ├── fail2ban_status.png
    └── banned_ip.png
```

---

## 🔗 References

- [MITRE ATT&CK T1110 – Brute Force](https://attack.mitre.org/techniques/T1110/)
- [Fail2Ban Documentation](https://www.fail2ban.org/wiki/index.php/Main_Page)
- [OpenSSH Hardening Guide](https://www.ssh.com/academy/ssh/sshd_config)
- [NIST SP 800-115 – Technical Guide to Information Security Testing](https://csrc.nist.gov/publications/detail/sp/800-115/final)

---

*Built as part of a cybersecurity portfolio. Conducted in an isolated lab environment. All simulations performed on machines I own and control.*
