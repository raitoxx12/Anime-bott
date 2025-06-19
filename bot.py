import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# === CONFIG ===
BOT_TOKEN = "6822633489:AAEBQWl94eDTWqRMRwdhoEyElWETF6DFuPE"
OWNER_ID = 5525952879

# === TEMP STORAGE ===
hashtag_data = {}
temp_files = []

# === HANDLERS ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tags = list(hashtag_data.keys())
    if tags:
        await update.message.reply_text("Available hashtags:\n" + "\n".join(tags))
    else:
        await update.message.reply_text("No hashtags available yet.")

async def show_hashtags(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tags = list(hashtag_data.keys())
    if tags:
        await update.message.reply_text("Available hashtags:\n" + "\n".join(tags))
    else:
        await update.message.reply_text("No hashtags available.")

async def handle_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        # Only owner can upload files
        return

    message = update.message
    if message.document:
        temp_files.append((message.document.file_id, message.document.file_name))
    elif message.video:
        temp_files.append((message.video.file_id, "video.mp4"))
    elif message.audio:
        temp_files.append((message.audio.file_id, message.audio.file_name))

async def handle_hashtag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global temp_files
    tag = update.message.text.strip()

    if not tag.startswith("#"):
        return

    if update.effective_user.id == OWNER_ID and temp_files:
        hashtag_data.setdefault(tag, [])
        hashtag_data[tag].extend(temp_files)
        await update.message.reply_text(f"Saved {len(temp_files)} files under {tag}.")
        temp_files = []
    else:
        if tag in hashtag_data:
            for file_id, name in hashtag_data[tag]:
                try:
                    await update.message.reply_document(file_id, caption=name)
                except Exception:
                    continue
        else:
            await update.message.reply_text("No files found under that hashtag.")

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^//"), show_hashtags))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.VIDEO | filters.AUDIO, handle_files))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^#"), handle_hashtag))

    print("Bot is running...")
    await app.run_polling()

if __name__ == '__main__':
    import asyncio
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.get_event_loop().run_until_complete(main())
