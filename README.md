<p align="center">
  <img src="https://readme-typing-svg.demolab.com/?lines=Metadata+Inspector+Bot;Extract+%26+Clean+Metadata+Easily!&center=true&width=500&height=45">
</p>

<h1 align="center">🔍 Metadata Inspector Bot</h1>

<p align="center">
  Telegram bot to extract image & PDF metadata and clean image EXIF info with one tap!
</p>

---

<p align="center">
  <a href="https://t.me/metadata_1bot"><img src="https://img.shields.io/badge/Add%20to-Telegram-blue?logo=telegram" alt="Telegram"></a>
  <img src="https://img.shields.io/badge/Python-3.9+-blue?logo=python">
  <img src="https://img.shields.io/badge/License-MIT-green">
</p>

---

## 📦 Features

✅ Extract metadata from:

- 🖼️ Images (EXIF, resolution, camera info, GPS)
- 📄 PDFs (title, author, dates, pages)

✅ Clean EXIF metadata from images (JPEG)

✅ Detect image source (e.g. WhatsApp, Telegram)

✅ GPS → Exact location on map (if present)

✅ 3 free cleanmeta/day (for non-premium users)

✅ Buy Premium via UPI (automated system)

✅ Force Join system for 2 channels

✅ Admin features:
- /unblock /block /users /broadcast
- Sends alert to owner on new user

---

## 🚀 How to Use

1. Start bot → @metadata_1bot  
2. Send any image or PDF as file  
3. Bot extracts & shows metadata  
4. To remove image metadata → reply image & use /cleanmeta  

---

## 🧠 Logic & Privacy

- No file is saved on disk  
- Processing done using Pillow + PyPDF2 in memory  
- GPS decoded using geopy  
- Clean image sent instantly to user  

🔐 Secure. Fast. Private.

---

## 🛠 Configuration

Edit config section in bot.py:

```python
TOKEN = "YOUR_BOT_TOKEN"
BOT_OWNER_ID = 123456789
UPI_ID = "your-upi@upi"
CHANNEL_IDS = ["@bot_hub_1", "@appifycreations"]
