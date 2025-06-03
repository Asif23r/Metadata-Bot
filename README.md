Metadata Inspector Bot

A powerful Telegram bot to extract & clean metadata from images and PDF files. Built using Python and Telegram Bot API.

  


---

🚀 Features

📸 Extract metadata from images (camera info, resolution, GPS location)

📄 Extract metadata from PDF files (title, author, created date, etc.)

🧹 Clean EXIF metadata from images (Premium only)

💰 Premium system with daily 3 cleanmeta limit for free users

🔐 No image is saved — processed in memory only

🔍 Detects source of image (e.g., WhatsApp, Telegram, Screenshot)

📲 Force users to join two Telegram channels before using bot

👑 Admin commands to block/unblock users, broadcast messages, view stats



---

📦 Installation

1. Clone the Repository

git clone https://github.com/Asif23r/Asif23r.git
cd Asif23r

2. Install Dependencies

pip install -r requirements.txt

3. Configure the Bot

Open bot.py and replace these values:

TOKEN = "YOUR_BOT_TOKEN"
BOT_OWNER_ID = 123456789
UPI_ID = "your-upi@upi"
CHANNEL_IDS = ["@yourchannel1", "@yourchannel2"]

Or use a config.py file and import values from it.

4. Run the Bot

python bot.py


---

🛠 Admin Commands

/start – welcome message

/cleanmeta – clean metadata from replied image (limit: 3/day)

/unblock <user_id> – give Premium access

/block <user_id> – revoke Premium access

/users – see total users & premium

/broadcast – reply to any message to broadcast to all users



---

🔐 Security

This bot does not save or log any image

Metadata is removed using Pillow (PIL)

All processing is done in-memory (RAM)


🧠 Logic:

Image file received as document

EXIF tags stripped using PIL

Cleaned image is returned to user



---

📞 Contact

Developer: @RaazXdev

Support Channel: @appifycreations



---

📃 License

This project is licensed under the MIT License - see the LICENSE file for details.

