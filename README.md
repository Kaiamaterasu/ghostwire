# 👻 Ghostwire - Secure P2P Communication Suite

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-green.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

**🔒 Ultimate Encrypted Communication Tool**

Connect friends worldwide with military-grade encryption! Features interactive chat, CLI commands, daemon mode, steganography, and broadcast messaging.

[🚀 Quick Start](#-quick-start) • [📖 Documentation](#-documentation) • [🌍 International Setup](#-international-setup) • [🖼️ Steganography](#-steganography)

</div>

---

## ✨ Features

🌍 **Global Connectivity** - Works across different countries, networks, and WiFi connections  
🔐 **Triple-Key Security** - Military-grade AES encryption with triple-key authentication  
🖼️ **Advanced Steganography** - Hide secret messages inside innocent-looking images  
💬 **Real-time Chat** - Interactive chat rooms with private messaging support  
🌐 **Cross-Platform** - Windows, macOS, Linux compatible with multiple operation modes  
🚀 **High Performance** - Handles 100+ users efficiently with daemon mode support

## 🚀 Installation

### Quick Setup
```bash
git clone https://github.com/Kaiamaterasu/ghostwire.git
cd ghostwire
./install.sh
```

### Manual Install
```bash
pip install -r requirements.txt
chmod +x ghostwire
```

### Dependencies
```bash
pip install pycrypto pillow
```

## 📚 Quick Start Guide

> ⚠️ **CRITICAL for Room Creators**: You need TWO terminals - one to host the server, another to join the chat!

### 🏠 Creating a Room (2 Terminal Setup)

#### Terminal 1: Start the Server
```bash
# This terminal runs the server and shows logs
./ghostwire --enable --key1 secret1 --key2 secret2 --key3 secret3 --alias "my-chatroom"
```
**Output:**
```
[SERVER] Ghostwire 'my-chatroom' started on port 2222
[SERVER] Waiting for connections...
```

#### Terminal 2: Join as Room Creator
```bash
# Open a NEW terminal to actually chat
./ghostwire --create-user "admin"
```
**Output:**
```
[INFO] Connected to room as admin
[INFO] You are now in the room. Type messages to send. Ctrl+C to leave.
--------------------------------------------------
[admin]: 
```

### 👥 Others Joining Your Room

From their computer:
```bash
# Replace YOUR_IP with the server host's IP address
./ghostwire --create-user "alice" --host YOUR_IP --port 2222
```

Or if on same machine:
```bash
./ghostwire --create-user "bob"
```

## 💬 Interactive Chat Commands

Once in the chat room, you can use these commands:

### Basic Messaging
```bash
# Public message to everyone
[admin]: Hello everyone in the room!

# Private message to specific user
[admin]: @alice Hey, this is a private message just for you

# System will show: [PRIVATE from admin]: Hey, this is a private message just for you
```

### 🔍 Steganography Commands

#### Hide Message in Image
```bash
[admin]: /stealth vacation.jpg "This is my secret message" hidden.png mypassword @alice
```
**What happens:**
- Takes `vacation.jpg`
- Hides the message "This is my secret message" 
- Encrypts it with key "mypassword"
- Saves as `hidden.png`
- Notifies that alice should receive the file

#### Extract Hidden Message
```bash
[admin]: /extract hidden.png mypassword
```
**Output:**
```
✅ Message extracted successfully:
📝 Hidden message:
------------------------------
This is my secret message
------------------------------
🔓 Message decrypted with key: mypassword
```

#### Get Help
```bash
[admin]: /help
```
**Output:**
```
Commands:
  @username message     - Send private message
  /stealth image.jpg "message" output.png key @user - Hide message in image
  /extract image.png key - Extract message from image
  /help - Show this help
```

## 🖥️ Command-Line Only Usage

### Server Management
```bash
# Start basic server
./ghostwire --enable --key1 k1 --key2 k2 --key3 k3 --alias "work-team"

# Start on custom port
./ghostwire --enable --key1 k1 --key2 k2 --key3 k3 --alias "secret-room" --port 8080

# Start with initial admin user
./ghostwire --enable --key1 k1 --key2 k2 --key3 k3 --alias "meeting" --create-user "moderator"
```

### One-Shot Messaging
```bash
# Send message to everyone (after creating user account)
./ghostwire --send "Meeting starts in 5 minutes!" --all

# Send private message to specific user  
./ghostwire --send "Can you review the document?" --to "john"

# Using manual user specification
./ghostwire --send "Hello team" --user "manager" --all
```

### User Management
```bash
# List all connected and created users
./ghostwire --list-all

# Output example:
[USERS] Connected: alice, bob, charlie | Created: admin, alice, bob, charlie, john
```

### Steganography CLI Commands
```bash
# Hide message in image with encryption
./ghostwire --stealth-image photo.jpg --message "Server password: xyz123" --output innocent.png --key mypassword

# Extract message from image
./ghostwire --stealth-extract innocent.png --key mypassword

# Check how much text an image can hide
./ghostwire --stealth-capacity photo.jpg
# Output: 📊 Image capacity: 15000 characters
```

## 🔧 Advanced Features

### Multiple Operation Modes
```bash
# Show all available modes
./ghostwire --help-all

# Use daemon version for background operation
./ghostwire --version v2 --enable --key1 k1 --key2 k2 --key3 k3 --alias "room"

# Use interactive chat system
./ghostwire --version chat

# Use broadcast server
./ghostwire --version broadcast
```

## 🌍 Real-World Usage Examples

### 📋 Team Communication Scenario
```bash
# === ALICE (Team Lead) ===
# Terminal 1 - Start team server
./ghostwire --enable --key1 "project" --key2 "alpha" --key3 "2024" --alias "dev-team"

# Terminal 2 - Join as team lead
./ghostwire --create-user "alice_lead"

# In chat:
[alice_lead]: Good morning team! Daily standup in 15 minutes
[alice_lead]: @bob Can you review PR #123 before the meeting?
[alice_lead]: @charlie The API keys are in the vault

# === BOB (Developer) ===
./ghostwire --create-user "bob_dev" --host alice_ip

[bob_dev]: @alice_lead PR reviewed, found one issue in line 45
[bob_dev]: Will fix and re-submit after standup

# === CHARLIE (DevOps) ===  
./ghostwire --create-user "charlie_ops" --host alice_ip

[charlie_ops]: @alice_lead Got the API keys, deploying to staging now
```

### 🔐 Secure Information Sharing
```bash
# === SENDER ===
# Hide server credentials in innocent family photo
./ghostwire --stealth-image family_vacation.jpg \
  --message "Production Server: 192.168.1.100, User: admin, Pass: SecurePass123!" \
  --output family_photo.png \
  --key1 "company" --key2 "secure" --key3 "2024"

# Email the family_photo.png file normally...

# === RECEIVER ===  
# Extract the hidden server info
./ghostwire --stealth-extract family_photo.png \
  --key1 "company" --key2 "secure" --key3 "2024"

# Output:
# ✅ Message extracted successfully:
# 📝 Hidden message:
# ------------------------------
# Production Server: 192.168.1.100, User: admin, Pass: SecurePass123!
# ------------------------------
```

### 🏢 Remote Meeting Setup
```bash
# === MEETING HOST ===
# Terminal 1 - Start meeting room
./ghostwire --enable --key1 "quarterly" --key2 "meeting" --key3 "Q1" --alias "board-meeting" --port 9999

# Terminal 2 - Join as host
./ghostwire --create-user "ceo" --port 9999

[ceo]: Welcome everyone to Q1 board meeting
[ceo]: @cfo Please share the financial summary
[ceo]: /stealth budget_chart.png "Actual Q1 numbers: Revenue +15%, Costs -8%" confidential.png finance2024 @cfo

# === ATTENDEES ===
./ghostwire --create-user "cfo" --host meeting_server_ip --port 9999
./ghostwire --create-user "cto" --host meeting_server_ip --port 9999

[cfo]: @ceo Sharing detailed breakdown in the steganographic image
[cfo]: /extract confidential.png finance2024
```

### 🎮 Gaming Coordination
```bash
# === RAID LEADER ===
./ghostwire --enable --key1 "guild" --key2 "dragons" --key3 "raid" --alias "raid-night"

# === PLAYERS ===
./ghostwire --create-user "tank_warrior" --host raid_leader_ip
./ghostwire --create-user "healer_priest" --host raid_leader_ip
./ghostwire --create-user "dps_mage" --host raid_leader_ip

# In chat:
[raid_leader]: Dragon raid starts in 5 minutes! Everyone ready?
[tank_warrior]: Ready! Full consumables
[healer_priest]: @tank_warrior Got you covered, full mana
[dps_mage]: @raid_leader What's the strategy for phase 2?
[raid_leader]: @all Phase 2: tank holds aggro, DPS focuses adds, healer dispel poison
```

## ⚙️ Configuration & Customization

### Port Configuration
```bash
# Default port 2222
./ghostwire --enable --key1 k1 --key2 k2 --key3 k3 --alias "room"

# Custom port
./ghostwire --enable --key1 k1 --key2 k2 --key3 k3 --alias "room" --port 8080

# Join with custom port
./ghostwire --create-user "username" --port 8080
```

### Host Configuration
```bash
# Join local server
./ghostwire --create-user "username"

# Join remote server
./ghostwire --create-user "username" --host 192.168.1.100

# Join with both custom host and port
./ghostwire --create-user "username" --host example.com --port 8080
```

## 🖼️ Steganography Deep Dive

### Image Requirements
- **Best formats**: PNG (lossless), BMP
- **Avoid**: Heavily compressed JPEG
- **Capacity**: ~1 character per 8 pixels (3 RGB channels)
- **Example**: 400x300 image = 120,000 pixels = ~15,000 characters capacity

### Steganography Security Features
- **LSB (Least Significant Bit)** hiding technique
- **AES encryption** before hiding (when keys provided)
- **Invisible changes** to human eye
- **End marker** to detect message boundaries
- **Error detection** for corrupted images

### Advanced Steganography Examples
```bash
# Check image capacity before hiding large text
./ghostwire --stealth-capacity screenshot.png
# Output: 📊 Image capacity: 50000 characters

# Hide without encryption (not recommended)
./ghostwire --stealth-image input.jpg --message "public info" --output output.png --no-encrypt

# Hide with triple-key encryption
./ghostwire --stealth-image input.jpg --message "secret" --output output.png --key1 k1 --key2 k2 --key3 k3

# Extract with specific keys
./ghostwire --stealth-extract output.png --key1 k1 --key2 k2 --key3 k3
```

## 🔒 Security & Privacy

### Encryption Details
- **Algorithm**: AES-256-CBC mode
- **Key Generation**: Triple-key combination for enhanced security
- **Per-Message IV**: Unique initialization vector for each message
- **No Storage**: Messages never written to disk
- **Forward Secrecy**: Session keys don't compromise past communications

### Privacy Features
- **Private Messages**: `@username` messages only visible to recipient
- **Server Privacy**: Private messages not logged on server
- **Steganography**: Messages hidden in innocent-looking images
- **Key Security**: Multiple key combinations required

### Best Practices
```bash
# Use strong, unique keys
./ghostwire --enable --key1 "MyStr0ng!Key#1" --key2 "An0th3r$ecur3Key" --key3 "Th1rd@K3y2024"

# Regular key rotation
./ghostwire --enable --key1 "newkey1" --key2 "newkey2" --key3 "newkey3" --alias "room-v2"

# Secure key sharing (use steganography)
./ghostwire --stealth-image innocuous.jpg --message "keys: key1, key2, key3" --output shared.png
```

## 🛠️ Troubleshooting

### Connection Issues
```bash
# Check if port is already in use
netstat -tuln | grep :2222
sudo lsof -i :2222

# Try different port
./ghostwire --enable --key1 k1 --key2 k2 --key3 k3 --alias "room" --port 3333

# Check firewall settings
sudo ufw allow 2222
```

### Authentication Issues
```bash
# Ensure exact same keys on all devices
# Keys are case-sensitive!
./ghostwire --enable --key1 "ExactCase" --key2 "Matching" --key3 "Keys"

# Clear old configurations
rm -f /tmp/ghostwire_config.json /tmp/ghostwire_data.json /tmp/ghostwire_user.json
```

### Steganography Issues
```bash
# Check image capacity first
./ghostwire --stealth-capacity image.png
# 📊 Image capacity: 15000 characters

# Convert to PNG for better results  
convert image.jpg image.png

# Verify extraction with same keys used for hiding
./ghostwire --stealth-extract image.png --key1 same --key2 exact --key3 keys
```

### Performance Issues
```bash
# Use daemon mode for high-traffic scenarios
./ghostwire --version v2 --enable --key1 k1 --key2 k2 --key3 k3 --alias "high-traffic"

# Reduce image size for faster steganography
convert large.png -resize 50% smaller.png
```

## 🌐 International Network Setup Guide

> **🌍 Perfect for connecting friends across different countries and networks!**

### 📡 Step 1: Get Your Public IP Address

**Command Line Methods:**
```bash
# Method 1: Simple and fast
curl ifconfig.me

# Method 2: With location info
curl ipinfo.io

# Method 3: Using DNS
dig +short myip.opendns.com @resolver1.opendns.com

# Method 4: Alternative services
wget -qO- icanhazip.com
```

**Browser Methods:**
- Google: "what is my ip"
- Visit: whatismyipaddress.com
- Visit: ipinfo.io

### 🏠 Step 2: Understand Your Network Setup

```bash
# Check your network information
echo "Local IP: $(ip route get 1.1.1.1 | grep -oP 'src \K\S+')"
echo "Public IP: $(curl -s ifconfig.me)"
echo "Router IP: $(ip route | grep default | awk '{print $3}')"
```

### 🔧 Step 3: Router Configuration (For International Access)

#### Access Your Router
1. **Find Router IP**: Usually `192.168.1.1` or `192.168.0.1`
2. **Open Browser**: Navigate to `http://192.168.1.1`
3. **Login**: Use admin credentials (often on router label)

#### Add Port Forwarding Rule
**Location**: Look for "Port Forwarding", "Virtual Server", or "NAT" section

**Configuration:**
- **Service Name**: `Ghostwire`
- **External Port**: `2222`
- **Internal IP**: `192.168.1.XXX` (your computer's local IP)
- **Internal Port**: `2222`
- **Protocol**: `TCP`
- **Enable**: `Yes`

**Save and Reboot** your router.

### 🔒 Step 4: Firewall Configuration

```bash
# Linux (iptables)
sudo iptables -A INPUT -p tcp --dport 2222 -j ACCEPT

# Linux (UFW)
sudo ufw allow 2222/tcp

# Linux (firewalld)
sudo firewall-cmd --permanent --add-port=2222/tcp
sudo firewall-cmd --reload

# Windows (Command Prompt as Admin)
netsh advfirewall firewall add rule name="Ghostwire" dir=in action=allow protocol=TCP localport=2222

# macOS
# Go to System Preferences > Security & Privacy > Firewall > Options
# Add Ghostwire application
```

### 🧪 Step 5: Test Your Setup

```bash
# Test local port is open
netstat -tuln | grep :2222

# Test from external network (ask a friend to run this)
telnet YOUR_PUBLIC_IP 2222

# If telnet works, you'll see:
# Trying YOUR_PUBLIC_IP...
# Connected to YOUR_PUBLIC_IP.
```

### 🌍 Real-World International Setup Example

**Scenario**: Hari (India), Alex (UK), Jackson (USA)

#### Hari's Setup (Server Host in India)

```bash
# 1. Get network info
curl ifconfig.me  # Example output: 103.217.82.54
ip route get 1.1.1.1 | grep -oP 'src \K\S+'  # Example: 192.168.1.7

# 2. Configure router: Forward 103.217.82.54:2222 → 192.168.1.7:2222

# 3. Start server
./ghostwire --enable --key1 "mumbai2025" --key2 "taj_mahal" --key3 "india_secure" --alias "global-friends" --create-user "hari_india" --port 2222

# 4. Share with friends:
# IP: 103.217.82.54
# Port: 2222
# Keys: mumbai2025, taj_mahal, india_secure
```

#### Alex's Connection (From UK)

```bash
# Connect to Hari's server from UK
./ghostwire --key1 "mumbai2025" --key2 "taj_mahal" --key3 "india_secure" --create-user "alex_britain" --host 103.217.82.54 --port 2222

# Alex is now in interactive mode and can chat:
# [alex_britain]: Hello from London! Weather is rainy today 🌧️
# [alex_britain]: @hari_india Thanks for setting up this secure room!
```

#### Jackson's Connection (From USA)

```bash
# Connect to Hari's server from USA
./ghostwire --key1 "mumbai2025" --key2 "taj_mahal" --key3 "india_secure" --create-user "jackson_usa" --host 103.217.82.54 --port 2222

# Jackson joins the conversation:
# [jackson_usa]: Hey everyone! Greetings from California! 🇺🇸
# [jackson_usa]: @alex_britain @hari_india This encryption is amazing!
```

### 🔄 Switching Between CLI and Interactive Modes

#### From CLI to Interactive Mode
```bash
# Currently sending one-shot messages
./ghostwire --send "Hello everyone!" --all

# Switch to interactive mode (real-time chat)
./ghostwire --create-user "your_username" --host server_ip --port 2222
# Now you're in interactive mode with prompt: [your_username]: _
```

#### From Interactive to CLI Mode
```bash
# In interactive mode, press Ctrl+C to exit
# [your_username]: Ctrl+C
# [INFO] your_username leaving room...

# Now back to CLI mode
./ghostwire --send "Back to CLI!" --all
./ghostwire --list-all
```

### 🚨 Alternative Solutions (If Port Forwarding Fails)

#### Option 1: Use ngrok (Tunnel Service)
```bash
# Download and install ngrok
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar xvf ngrok-v3-stable-linux-amd64.tgz

# Start Ghostwire server locally
./ghostwire --enable --key1 k1 --key2 k2 --key3 k3 --alias "room" --port 2222

# In another terminal, create tunnel
./ngrok tcp 2222

# ngrok will give you a public URL like:
# tcp://0.tcp.ngrok.io:12345
# Share this with friends instead of your IP
```

#### Option 2: Use Different Ports
```bash
# Try common open ports
./ghostwire --enable --key1 k1 --key2 k2 --key3 k3 --alias "room" --port 80    # HTTP
./ghostwire --enable --key1 k1 --key2 k2 --key3 k3 --alias "room" --port 443   # HTTPS
./ghostwire --enable --key1 k1 --key2 k2 --key3 k3 --alias "room" --port 8080  # Alt HTTP
```

#### Option 3: VPN Setup
```bash
# Use a VPN service that provides static IPs
# Examples: NordVPN, ExpressVPN, etc.
# Connect all participants to the same VPN network
```

### 🛠️ Network Troubleshooting

#### Connection Refused Errors
```bash
# Check if server is running
ps aux | grep ghostwire

# Check if port is open locally
sudo netstat -tuln | grep :2222
sudo lsof -i :2222

# Test local connection first
./ghostwire --create-user "test" --host localhost --port 2222
```

#### Router/Firewall Issues
```bash
# Test if port forwarding works
# From external network:
nmap -p 2222 YOUR_PUBLIC_IP

# Should show:
# 2222/tcp open  unknown

# If shows 'filtered' or 'closed', check:
# 1. Router port forwarding settings
# 2. Local firewall rules
# 3. ISP blocking (some ISPs block certain ports)
```

#### ISP Restrictions
```bash
# Some ISPs block incoming connections
# Test with different ports:
./ghostwire --enable --key1 k1 --key2 k2 --key3 k3 --alias "room" --port 8080
./ghostwire --enable --key1 k1 --key2 k2 --key3 k3 --alias "room" --port 9999

# Or use the ngrok solution above
```

### 📊 Network Performance Tips

#### Optimize for International Connections
```bash
# Use daemon mode for better performance
./ghostwire --version v2 --enable --key1 k1 --key2 k2 --key3 k3 --alias "fast-room"

# Reduce image sizes for faster steganography
convert large_image.jpg -resize 50% optimized.jpg
./ghostwire --stealth-image optimized.jpg --message "text" --output hidden.png
```

#### Monitor Connection Quality
```bash
# Check connection to server
ping SERVER_IP

# Test bandwidth
# (From server machine)
iperf3 -s

# (From client machine)
iperf3 -c SERVER_IP
```

### 🔐 Security for International Use

#### Best Practices
```bash
# Use strong, unique keys for international rooms
./ghostwire --enable --key1 "MyCountry@2024!" --key2 "SecureComm#Global" --key3 "Friends&Family$Safe" --alias "international-room"

# Rotate keys regularly
# Share new keys via steganography:
./ghostwire --stealth-image innocent.jpg --message "New keys: key1_v2, key2_v2, key3_v2" --output update.png
```

#### Privacy Considerations
- **Private Messages**: Use `@username` for sensitive info
- **Steganography**: Hide critical data in images
- **Key Sharing**: Never share keys via unencrypted channels
- **Regular Updates**: Change keys periodically


## 🧪 Testing �26 Development

### Run Tests
```bash
# Basic functionality test
python test_basic.py

# Simple version test
python test_simple.py

# Requirements test
python test_requirements.py

# Steganography test
python test_steganography.py
```

### Development Mode
```bash
# Enable debug output
export GHOSTWIRE_DEBUG=1
./ghostwire --enable --key1 k1 --key2 k2 --key3 k3 --alias "debug-room"

# Test different versions
./ghostwire --version v1 --help
./ghostwire --version v2 --help
./ghostwire --version chat
```

## 📈 Performance & Limits

### Message Limits
- **Chat message size**: ~1KB per message
- **Steganography**: Limited by image capacity
- **Concurrent users**: ~100 users per server (tested)
- **Network bandwidth**: ~1Mbps for 10 active users

### Steganography Performance
- **Hiding time**: ~1-2 seconds for typical images
- **Extraction time**: ~0.5-1 seconds
- **Image size impact**: Minimal (~1-2 bytes per hidden character)

## 🤝 Contributing

### Development Setup
```bash
git clone https://github.com/Kaiamaterasu/ghostwire.git
cd ghostwire
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

### Testing Changes
```bash
# Run all tests
./run_tests.sh

# Test specific functionality
python test_simple.py
python test_steganography.py

# Manual testing
./ghostwire --help-all
```

### Contribution Guidelines
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests: `python test_requirements.py`
5. Update documentation if needed
6. Submit a pull request

### Feature Requests
- 🐛 Report bugs via GitHub Issues
- 💡 Suggest features via GitHub Discussions
- 📖 Improve documentation
- 🔄 Share with others

## 📞 Support & Community

### Getting Help
- 📚 **Documentation**: Check this README and in-code help
- 🐛 **Bug Reports**: GitHub Issues
- 💬 **Discussions**: GitHub Discussions
- 📧 **Contact**: Create an issue for support

### Commands for Quick Help
```bash
# Show all available options
./ghostwire --help-all

# Version-specific help
./ghostwire --version v1 --help
./ghostwire --version v2 --help

# Interactive mode help
./ghostwire --create-user "test"
# Then type: /help
```

## 💖 Support the Project

If Ghostwire helps you communicate securely, consider supporting its development:

[![PayPal](https://img.shields.io/badge/PayPal-Donate-blue?style=for-the-badge&logo=paypal)](https://www.paypal.com/paypalme/Poorna357)

**Other ways to help:**
- ⭐ Star this repository
- 🐛 Report bugs and issues
- 💡 Suggest new features
- 📖 Improve documentation
- 🔄 Share with friends and colleagues
- 🤝 Contribute code improvements

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

**Free for personal and commercial use, modification, and distribution.**

---

## 🎯 Quick Reference Card

### Essential Commands
```bash
# Start room (2 terminals needed!)
./ghostwire --enable --key1 k1 --key2 k2 --key3 k3 --alias "room"    # Terminal 1
./ghostwire --create-user "admin"                                     # Terminal 2

# Join room  
./ghostwire --create-user "username" --host IP

# Quick messaging
./ghostwire --send "message" --all                                    # To everyone
./ghostwire --send "message" --to "user"                             # Private

# Steganography
./ghostwire --stealth-image in.jpg --message "text" --output out.png # Hide
./ghostwire --stealth-extract out.png                                # Extract

# Interactive commands
@username message          # Private message
/stealth img "msg" out key # Hide in image  
/extract img key          # Extract from image
/help                     # Show help
```

---

## ❓ Frequently Asked Questions (FAQ)

### General Usage

**Q: Why do I need TWO terminals to create a room?**
A: Terminal 1 runs the server (shows logs), Terminal 2 lets you actually chat. This separation gives you control and visibility.

**Q: Can I use this across different countries?**
A: Yes! Follow the International Network Setup Guide above. You'll need to configure port forwarding on your router.

**Q: What's the difference between CLI and Interactive mode?**
A: CLI mode sends one message and exits. Interactive mode keeps you connected for real-time chat.

**Q: How secure is the encryption?**
A: We use AES-256-CBC with triple-key combination. Each message has a unique IV. Very secure when used properly.

### Technical Questions

**Q: Can I change the default port 2222?**
A: Yes! Use `--port 8080` (or any other port) in both server and client commands.

**Q: How many people can join one room?**
A: Tested with 100+ users. Performance depends on your network and hardware.

**Q: Do messages get saved anywhere?**
A: No! Messages are never written to disk for privacy. Private messages especially leave no traces.

**Q: Can I run multiple rooms on one computer?**
A: Yes! Use different ports: `--port 2222`, `--port 3333`, etc.

### Steganography Questions

**Q: What images work best for steganography?**
A: PNG and BMP (lossless formats). Avoid heavily compressed JPEG. Larger images can hide more text.

**Q: Can others detect hidden messages in my images?**
A: With proper tools, yes. But casual viewers won't notice anything. The changes are invisible to human eyes.

**Q: How much text can I hide in an image?**
A: Use `./ghostwire --stealth-capacity image.png` to check. Generally ~1 character per 8 pixels.

### Network Issues

**Q: Friends can't connect to my room. What's wrong?**
A: Most likely router port forwarding isn't set up. Follow Step 3 in the International Network Setup Guide.

**Q: Getting "Connection refused" errors?**
A: Check if the server is actually running (`ps aux | grep ghostwire`) and if the port is open (`netstat -tuln | grep :2222`).

**Q: My ISP blocks incoming connections. What can I do?**
A: Try the ngrok solution in the Alternative Solutions section, or use a VPN.

### Error Messages

**Q: "User not found" when sending private messages?**
A: The recipient hasn't joined the room yet, or you misspelled their username. Use `./ghostwire --list-all` to check.

**Q: "Failed to decrypt message" errors?**
A: All participants must use the exact same three keys (case-sensitive). Double-check your keys.

**Q: Steganography says "Image too small"?**
A: Your message is too long for the image. Use a larger image or shorter message.

### Platform-Specific

**Q: Does this work on Windows?**
A: Yes! Install Python 3.7+, run `pip install -r requirements.txt`, then use `python ghostwire` instead of `./ghostwire`.

**Q: Does this work on macOS?**
A: Yes! Same as Linux. You might need to install additional dependencies with Homebrew.

**Q: Can I use this on mobile?**
A: Not directly, but you could run it on a mobile Linux environment like Termux on Android.

---

## 🚨 Important Security Notes

### DO:
- ✅ Use strong, unique keys for each room
- ✅ Share keys securely (preferably via steganography)
- ✅ Use private messages (`@username`) for sensitive info
- ✅ Rotate keys periodically
- ✅ Test your setup before important communications

### DON'T:
- ❌ Share keys over unencrypted channels (email, SMS, etc.)
- ❌ Use simple or predictable keys
- ❌ Leave rooms running unnecessarily
- ❌ Trust public/shared networks for sensitive communications
- ❌ Reuse keys across different groups/purposes

### Emergency Key Sharing
If you must share new keys quickly:
```bash
# Hide new keys in an innocent image
./ghostwire --stealth-image vacation_photo.jpg --message "New keys: key1_v2, key2_v2, key3_v2, effective tomorrow" --output innocent_photo.png

# Share the innocent_photo.png via any normal method
```

---

**Made with ❤️ by [Kaiamaterasu](https://github.com/Kaiamaterasu)**

*"Secure communication for everyone, everywhere."* 🌍🔒

---

### 🏷️ Tags
`encryption` `p2p` `communication` `steganography` `privacy` `security` `chat` `messaging` `cross-platform` `international` `AES` `python`
