import logging
import json
from io import BytesIO
import exifread
from PIL import Image
from geopy.geocoders import Nominatim
from PyPDF2 import PdfReader
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from datetime import datetime
import time

# === Config ===
TOKEN = ""
BOT_OWNER_ID = 0
UPI_ID = ""
USER_DB_FILE = "users.json"
REQUIRED_CHANNELS = ["@yourchannel1", "@yourchannel2"]

logging.basicConfig(level=logging.INFO)
geolocator = Nominatim(user_agent="meta-bot")

# === Load / Save Users ===
def load_users():
    try:
        with open(USER_DB_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_users(data):
    with open(USER_DB_FILE, 'w') as f:
        json.dump(data, f, indent=2)

users_data = load_users()

# === Premium Check ===
def is_paid(user_id):
    return users_data.get(str(user_id), {}).get("premium", False)

# === Force Join ===
def is_user_joined_all(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    for channel in REQUIRED_CHANNELS:
        try:
            member = context.bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status not in ("member", "administrator", "creator"):
                return False
        except:
            return False
    return True

def send_force_join_message(update: Update):
    buttons = [[InlineKeyboardButton(f"📢 Join", url=f"https://t.me/{c[1:]}")] for c in REQUIRED_CHANNELS]
    buttons.append([InlineKeyboardButton("✅ I’ve Joined", callback_data="refresh_join")])
    update.message.reply_text("🚫 Please join the required channels to continue:", reply_markup=InlineKeyboardMarkup(buttons))

def refresh_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    if is_user_joined_all(update, context):
        query.edit_message_text("✅ Channels joined. Now send your file.")
    else:
        query.answer("❌ You haven't joined all channels.", show_alert=True)

# === Guess Source ===
def guess_source(name, width=None, height=None):
    if not name: return "Unknown"
    name = name.lower()
    if "whatsapp" in name or name.startswith("img-"): return "WhatsApp"
    if "telegram" in name or name.startswith("photo"): return "Telegram"
    if "screenshot" in name: return "Screenshot"
    if "insta" in name: return "Instagram"
    if width and height and width == height: return "Likely Profile Picture"
    return "Unknown"

# === Extract Image Metadata ===
def extract_image_metadata(bio, name=None):
    tags = exifread.process_file(bio)
    data = []
    width = height = None

    try:
        bio.seek(0)
        img = Image.open(bio)
        width, height = img.size
        data.append(f"📐 Resolution: {width} x {height}")
    except:
        pass

    if "Image Make" in tags:
        data.append(f"📸 Camera: {tags['Image Make']} {tags.get('Image Model', '')}")
    if "EXIF DateTimeOriginal" in tags:
        data.append(f"📅 Date: {tags['EXIF DateTimeOriginal']}")
    if "GPS GPSLatitude" in tags and "GPS GPSLongitude" in tags:
        try:
            lat_vals = tags["GPS GPSLatitude"].values
            lon_vals = tags["GPS GPSLongitude"].values
            lat = float(lat_vals[0].num) + float(lat_vals[1].num)/60 + float(lat_vals[2].num)/3600
            lon = float(lon_vals[0].num) + float(lon_vals[1].num)/60 + float(lon_vals[2].num)/3600
            location = geolocator.reverse(f"{lat}, {lon}")
            loc_text = location.address if location else "Unknown"
            data.append(f"📍 Location: {loc_text}\n🌐 https://maps.google.com/?q={lat},{lon}")
        except: pass

    if name:
        guessed = guess_source(name, width, height)
        data.append(f"🕵️‍♂️ Guessed Source: {guessed}")

    return "\n".join(data) if data else "⚠️ No metadata found."

# === Extract PDF Metadata ===
def extract_pdf_metadata(bio):
    try:
        reader = PdfReader(bio)
        info = reader.metadata
        return "\n".join([
            f"📄 PDF Metadata:",
            f"• Title: {info.title or 'N/A'}",
            f"• Author: {info.author or 'N/A'}",
            f"• Subject: {info.subject or 'N/A'}",
            f"• Created: {info.creation_date or 'N/A'}",
            f"• Pages: {len(reader.pages)}"
        ])
    except:
        return "❌ Could not read PDF metadata."

# === Clean Metadata ===
def clean_metadata(bio):
    try:
        img = Image.open(bio)
        out = BytesIO()
        img.save(out, format="JPEG", exif=b"")
        out.seek(0)
        return out
    except:
        return None

# === /start ===
def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_id = str(user.id)

    update.message.reply_text(
        f"👋 Hello {user.first_name}!\n\n"
        "🤖 Welcome to Metadata Inspector Bot\n"
        "Send an image or PDF (as file) to get hidden metadata.\n"
        "Use /cleanmeta to remove sensitive data (Premium only)"
    )

    if user_id not in users_data:
        users_data[user_id] = {
            "name": user.full_name,
            "username": user.username or "N/A",
            "premium": False
        }
        save_users(users_data)
        context.bot.send_message(BOT_OWNER_ID, f"🆕 New user:\n👤 {user.full_name}\n🔗 @{user.username or 'N/A'}\n🆔 {user.id}")

# === Handle File ===
def handle_doc(update: Update, context: CallbackContext):
    if not is_user_joined_all(update, context):
        return send_force_join_message(update)

    uid = str(update.message.from_user.id)
    doc = update.message.document
    bio = BytesIO()
    doc.get_file().download(out=bio)
    bio.seek(0)

    if users_data.get(uid, {}).get("awaiting_payment"):
        caption = f"Payment from @{users_data[uid].get('username')} (ID: {uid})"
        context.bot.send_document(BOT_OWNER_ID, doc.file_id, caption=caption)
        users_data[uid]["awaiting_payment"] = False
        save_users(users_data)
        update.message.reply_text("✅ Payment received. Please wait for approval.")
        return

    if doc.mime_type.startswith("image"):
        text = extract_image_metadata(bio, doc.file_name)
    elif doc.mime_type == "application/pdf":
        text = extract_pdf_metadata(bio)
    else:
        text = "⚠️ Only images and PDFs are supported."

    update.message.reply_text(text)

# === /cleanmeta ===
def cleanmeta(update: Update, context: CallbackContext):
    if not is_user_joined_all(update, context):
        return send_force_join_message(update)

    uid = str(update.message.from_user.id)
    today = str(datetime.now().date())
    user = users_data.get(uid, {})

    if not user.get("premium", False):
        if user.get("last_clean") != today:
            user["last_clean"] = today
            user["count"] = 0
        if user.get("count", 0) >= 3:
            markup = InlineKeyboardMarkup([[InlineKeyboardButton("💰 Buy Premium", callback_data="buy")]])
            update.message.reply_text("⛔ Daily clean limit reached.\nUpgrade to Premium for unlimited access.", reply_markup=markup)
            return
        user["count"] = user.get("count", 0) + 1
        users_data[uid] = user
        save_users(users_data)

    msg = update.message.reply_to_message
    if not msg or not msg.document or not msg.document.mime_type.startswith("image"):
        return update.message.reply_text("⚠️ Reply to an image file to clean its metadata.")

    doc = msg.document.get_file()
    bio = BytesIO()
    doc.download(out=bio)
    bio.seek(0)
    cleaned = clean_metadata(bio)
    if cleaned:
        update.message.reply_document(cleaned, filename="cleaned.jpg", caption="✅ Metadata removed.")
    else:
        update.message.reply_text("❌ Failed to clean image.")

# === /unblock ===
def unblock(update: Update, context: CallbackContext):
    if update.message.from_user.id != BOT_OWNER_ID: return
    if not context.args: return
    uid = context.args[0]
    users_data[uid]["premium"] = True
    save_users(users_data)
    context.bot.send_message(uid, "🎉 You’ve been upgraded to Premium!")
    update.message.reply_text(f"✅ User {uid} is now Premium.")

# === /block ===
def block(update: Update, context: CallbackContext):
    if update.message.from_user.id != BOT_OWNER_ID: return
    if not context.args: return
    uid = context.args[0]
    users_data[uid]["premium"] = False
    save_users(users_data)
    context.bot.send_message(uid, "⚠️ Your Premium access has been removed.")
    update.message.reply_text(f"🚫 User {uid} is no longer Premium.")

# === /users ===
def users(update: Update, context: CallbackContext):
    if update.message.from_user.id != BOT_OWNER_ID: return
    total = len(users_data)
    paid = sum(1 for u in users_data.values() if u.get("premium"))
    update.message.reply_text(f"📊 Total Users: {total}\n💎 Premium: {paid}")

# === /broadcast ===
def broadcast(update: Update, context: CallbackContext):
    if update.message.from_user.id != BOT_OWNER_ID: return
    reply = update.message.reply_to_message
    if not reply:
        return update.message.reply_text("⚠️ Reply to a message to broadcast.")
    sent, failed = 0, 0
    for uid in users_data:
        try:
            context.bot.forward_message(chat_id=int(uid), from_chat_id=update.message.chat_id, message_id=reply.message_id)
            sent += 1
            time.sleep(5)
        except:
            failed += 1
    update.message.reply_text(f"📤 Broadcast done.\n✅ Sent: {sent}\n❌ Failed: {failed}")

# === Buy Callback ===
def buy_callback(update: Update, context: CallbackContext):
    uid = str(update.callback_query.from_user.id)
    users_data[uid]["awaiting_payment"] = True
    save_users(users_data)
    context.bot.send_message(uid, f"💰 Send ₹100 to {UPI_ID} via UPI and reply with screenshot.")
    update.callback_query.answer()

# === Main ===
def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("cleanmeta", cleanmeta))
    dp.add_handler(CommandHandler("unblock", unblock))
    dp.add_handler(CommandHandler("block", block))
    dp.add_handler(CommandHandler("users", users))
    dp.add_handler(CommandHandler("broadcast", broadcast))
    dp.add_handler(CallbackQueryHandler(buy_callback, pattern="buy"))
    dp.add_handler(CallbackQueryHandler(refresh_callback, pattern="refresh_join"))
    dp.add_handler(MessageHandler(Filters.document, handle_doc))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()