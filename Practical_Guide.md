# Practical Guide for Ghostwire Users 🚀

## 🔍 Common Scenarios

### Scenario 1: Secure Communication in a Team

Imagine you are a team leader in a remote company, and you start a secure communication room for all developers:

```bash
# Create a room for the team
./ghostwire --enable --key1 "dev" --key2 "team" --key3 "2024" --alias "dev-room"
```

All developers can send messages and share updates:

```bash
# Send a message to all in the team
./ghostwire --send "Sprint meeting at 3 PM" --user "team-lead" --all
```

### Scenario 2: Hidden Messages in Shared Imagery

You're a field agent who needs to send hidden messages in images:

```bash
# Embed a secret message in an image
./ghostwire --stealth-image mission.jpg --message "Safe house located at coordinates: 37.7749° N, 122.4194° W" --output safehouse.png --key alpha
```

To read the message, use:

```bash
# Extract message from steganographic image
./ghostwire --stealth-extract safehouse.png --key alpha
```

## 🛠️ Troubleshooting Guide

### Common Issues and Fixes

#### Issue: Unable to Start Server 🚫
- **Solution**: Check that the port is not used by another process.

```bash
# Find out what's using the port
sudo lsof -i :2222
```

#### Issue: Steganography Extraction Fails ❌
- **Solution**: Make sure the correct encryption key is used.
- Verify that the image file has not been modified since the message was embedded.

```bash
# Check image integrity
md5sum safehouse.png
```

#### Issue: Authentication of Keys
- **Solution**: Double-check and synchronize keys on all involved devices.

```bash
# Ensure consistency in keys
echo "Ensure all keys are consistent across devices."
```

## 📚 Further Learning Tips
- **Explore different versions**: Switch between daemon mode and chat mode based on user needs.
- **Practice steganography**: Embed and extract messages in images to get comfortable with the commands.
- **Experiment with encryption keys**: See how changing keys affects communication.

## 📞 Support
- For more help, check the [Wiki](https://github.com/Kaiamaterasu/ghostwire/wiki) or join the [Discussions](https://github.com/Kaiamaterasu/ghostwire/discussions).

Happy Secure Communicating! ✨
