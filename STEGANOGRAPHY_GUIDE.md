# 🕵️ Ghostwire Steganography Guide 🖼️

## 🎯 What is Steganography?

Steganography is the art of hiding secret messages inside ordinary images. Unlike encryption which scrambles data, steganography hides data so well that nobody even knows there's a secret message! 🤫

## 🚀 Quick Start

### Basic Commands

```bash
# 📥 Hide a message in an image
ghostwire --stealth-image photo.jpg --message "Secret text" --output hidden.png

# 📤 Extract a hidden message 
ghostwire --stealth-extract hidden.png

# 📏 Check how much text an image can hide
ghostwire --stealth-capacity photo.jpg
```

## 🎮 Real-World Scenarios

### 🔐 Scenario 1: Encrypted Corporate Communications

**Situation**: You need to send confidential merger information through public channels.

```bash
# Step 1: Prepare your image (company logo or innocent photo)
# Step 2: Hide encrypted message
ghostwire --stealth-image company_logo.png \
  --message "Merger approved. Announce Monday 9 AM EST" \
  --output newsletter_image.png \
  --key "corporate2024"

# Step 3: Send the "innocent" image via email/social media
# Step 4: Recipient extracts the message
ghostwire --stealth-extract newsletter_image.png --key "corporate2024"
```

**Output**: 
```
✅ Message extracted successfully:
📝 Hidden message:
--------------------------------------------------
Merger approved. Announce Monday 9 AM EST
--------------------------------------------------
🔓 Message decrypted with steganography key
```

### 🌍 Scenario 2: Journalist Source Protection

**Situation**: A journalist needs to receive sensitive information from a whistleblower.

```bash
# Whistleblower hides document location in vacation photo
ghostwire --stealth-image vacation_beach.jpg \
  --message "Documents in locker 247, Central Station, key under red bench" \
  --output beach_memories.png \
  --key "whistleblower_safe"

# Journalist extracts the information
ghostwire --stealth-extract beach_memories.png --key "whistleblower_safe"
```

### 🎯 Scenario 3: Event Coordination

**Situation**: Organizing a surprise party and need to coordinate without spoiling the surprise.

```bash
# Hide party details in a meme
ghostwire --stealth-image funny_meme.jpg \
  --message "Surprise party Saturday 7 PM, bring cake, Sarah's house" \
  --output totally_innocent_meme.png

# Friends extract the details
ghostwire --stealth-extract totally_innocent_meme.png
```

## 📋 Image Requirements & Best Practices

### ✅ Supported Image Formats
- **PNG** (Recommended) - Lossless compression
- **JPG/JPEG** - Works but may have compression artifacts
- **BMP** - Good for large messages
- **TIFF** - Professional quality

### 📏 Capacity Calculator

| Image Size | Max Message Length |
|------------|-------------------|
| 100x100 px | ~3,750 characters |
| 500x500 px | ~93,750 characters |
| 1920x1080 px | ~777,600 characters |
| 4K (3840x2160) | ~3.1 million characters |

**Formula**: `(width × height × 3) ÷ 8 = max characters`

### 🎨 Image Selection Tips

**✅ GOOD Images:**
- Photos with lots of detail and texture
- Images with natural noise
- Complex patterns or landscapes
- Photos with many colors

**❌ AVOID:**
- Solid color backgrounds
- Simple graphics or logos
- Images that will be compressed again
- Images smaller than 200x200 pixels

## 🔧 Advanced Usage

### 🔐 Multi-layer Security

```bash
# Layer 1: Hide message in image
ghostwire --stealth-image source.jpg \
  --message "First layer: Check the blue folder" \
  --output layer1.png \
  --key "outer_key"

# Layer 2: Hide the first image in another image
ghostwire --stealth-image background.jpg \
  --message "file:layer1.png" \
  --output final_image.png \
  --key "inner_key"
```

### 📚 Batch Processing

```bash
# Hide multiple messages
for i in {1..5}; do
  ghostwire --stealth-image "source$i.jpg" \
    --message "Message number $i" \
    --output "hidden$i.png" \
    --key "batch_key_$i"
done
```

### 🌐 Integration with P2P Chat

```bash
# Start chat room
ghostwire --enable --key1 k1 --key2 k2 --key3 k3 --alias "secure-room"

# In interactive mode, use steganography commands:
# /stealth image.jpg "secret message" output.png mykey @username
# /extract hidden.png mykey
```

## 🚨 Error Solutions & Troubleshooting

### ❌ "Image too small to hide the message"

**Problem**: Your message is too long for the image.

**Solutions**:
```bash
# Check capacity first
ghostwire --stealth-capacity small_image.jpg

# Option 1: Use a larger image
# Option 2: Shorten your message
# Option 3: Compress your message
echo "Long message here" | gzip | base64
```

### ❌ "No hidden message found or message corrupted"

**Problem**: The image doesn't contain a hidden message or it's corrupted.

**Solutions**:
```bash
# Verify the image hasn't been modified
md5sum original_hidden.png
md5sum downloaded_hidden.png

# Check if you're using the right key
ghostwire --stealth-extract image.png --key "try_different_key"

# Verify image format (convert if needed)
convert image.jpg image.png
```

### ❌ "Decryption failed"

**Problem**: Wrong encryption key used.

**Solutions**:
```bash
# Double-check the key
# Try without encryption (if it was hidden without key)
ghostwire --stealth-extract image.png

# Verify key spelling and case sensitivity
```

### ❌ "PIL/Pillow not found"

**Problem**: Missing image processing library.

**Solution**:
```bash
pip install Pillow
# or
pip install -r requirements.txt
```

## 🛡️ Security Best Practices

### 🔐 Key Management
- Use unique keys for each message
- Never reuse keys across different communications
- Store keys separately from images
- Use memorable but complex passphrases

### 📁 File Handling
- Delete original images after hiding messages
- Use secure file deletion tools
- Don't leave traces in command history
- Use temporary directories for processing

### 🌐 Distribution Methods
- Upload to multiple platforms to avoid suspicion
- Mix hidden images with normal images
- Use different file names and formats
- Consider timing of uploads

## 🧪 Testing & Verification

### 🔍 Test Your Setup

```bash
# Create test image
convert -size 500x500 xc:lightblue test_image.png

# Hide test message
ghostwire --stealth-image test_image.png \
  --message "This is a test message" \
  --output test_hidden.png \
  --key "test123"

# Extract and verify
ghostwire --stealth-extract test_hidden.png --key "test123"
```

### 📊 Capacity Testing

```bash
# Test maximum capacity
ghostwire --stealth-capacity test_image.png

# Test with long message
python3 -c "print('A' * 1000)" | \
  ghostwire --stealth-image test_image.png \
    --message "$(cat)" \
    --output test_long.png
```

## 🎨 Creative Applications

### 📸 Social Media Steganography
- Hide messages in Instagram photos
- Embed coordinates in travel photos
- Store backup passwords in profile pictures

### 🎮 Gaming Communities
- Hide game hints in screenshots
- Embed clan strategies in shared images
- Store achievement codes in gaming memes

### 📚 Educational Use
- Hide answers in study materials
- Embed additional information in textbook images
- Create digital treasure hunts

## 🚀 Pro Tips

1. **🎯 Image Quality**: Higher quality images hide messages better
2. **🔄 Format Conversion**: Convert JPEG to PNG before hiding messages
3. **📏 Size Matters**: Larger images = more hiding capacity
4. **🌈 Color Depth**: RGB images work better than grayscale
5. **🔒 Double Encryption**: Encrypt your message before hiding it
6. **🕰️ Timing**: Don't hide/extract messages immediately - wait random intervals
7. **📁 File Metadata**: Strip metadata from images before sharing

## 🆘 Emergency Procedures

### 🚨 If Compromise is Suspected

```bash
# Quick cleanup
rm -f *.png *.jpg /tmp/ghostwire_*
history -c

# Generate new keys
openssl rand -base64 32

# Change communication patterns
# Use different image types and platforms
```

### 🔄 Recovery Procedures

```bash
# If you forgot the key, try common variations
for key in "backup_key" "old_key" "emergency_key"; do
  ghostwire --stealth-extract suspicious_image.png --key "$key"
done
```

---

**Remember**: Steganography is powerful but requires practice. Start with test images and gradually move to real-world scenarios. Always prioritize security and have backup plans! 🛡️✨
