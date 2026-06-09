from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import assemblyai as aai
from deep_translator import GoogleTranslator
from flask import Flask
import threading
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
AAI_API_KEY = os.getenv("AAI_API_KEY")

aai.settings.api_key = AAI_API_KEY


async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("Voice received. Processing...")

    voice = await update.message.voice.get_file()
    await voice.download_to_drive("voice.ogg")

    try:
        config = aai.TranscriptionConfig(
            language_detection=True
        )

        transcriber = aai.Transcriber()

        transcript = transcriber.transcribe(
            "voice.ogg",
            config=config
        )

        text = transcript.text

        if not text:
            await update.message.reply_text(
                "Could not transcribe audio."
            )
            return

        detected = transcript.json_response.get(
            "language_code",
            ""
        )

        # Russian -> English
        if detected.startswith("ru"):

            translated = GoogleTranslator(
                source="ru",
                target="en"
            ).translate(text)

            await update.message.reply_text(
                f"English:\n{translated}"
            )

        # Hindi -> Russian
        elif detected.startswith("hi"):

            translated = GoogleTranslator(
                source="hi",
                target="ru"
            ).translate(text)

            await update.message.reply_text(
                f"Russian:\n{translated}"
            )

        else:
            await update.message.reply_text(
                f"Detected language: {detected}\n\n{text}"
            )

    except Exception as e:
        await update.message.reply_text(
            f"Error: {e}"
        )


# Telegram bot
app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(
    MessageHandler(filters.VOICE, voice_handler)
)


# Flask server for Render
web = Flask(__name__)


@web.route("/")
def home():
    return "Victoria Bot is running!"


def run_web():
    port = int(os.environ.get("PORT", 10000))
    web.run(host="0.0.0.0", port=port)


def run_bot():
    print("Bot started")
    app.run_polling()


threading.Thread(target=run_web).start()

run_bot()
