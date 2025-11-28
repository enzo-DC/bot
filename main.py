"""
Bot Telegram de Fact-Checking
Point d'entrée principal
"""
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from config.settings import settings
from services.gemini_client import GeminiClient
from services.vera_client import VeraClient
import logging

from handlers.text_handler import handle_text
from handlers.image_handler import handle_image
from handlers.video_handler import handle_video
from handlers.audio_handler import handle_audio
from handlers.link_handler import handle_link
from handlers.document_handler import handle_document

logger = logging.getLogger("telegram_bot")
gemini_client = None
vera_client = None

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    await update.message.reply_text(
        "👋 Bot de Fact-Checking\n\n"
        "Envoyez du texte, images, vidéos, audios ou liens pour vérification !\n\n"
        "/help - Aide\n/about - À propos"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    await update.message.reply_text(
        "📚 Aide\n\n"
        "✅ Textes\n✅ Images (OCR)\n✅ Vidéos (transcription)\n"
        "✅ Audio\n✅ Liens web\n✅ Documents (PDF, TXT)\n\n"
        "Limites:\nImages: 10MB\nVidéos: 50MB\nAudio: 20MB"
    )

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    await update.message.reply_text(
        "ℹ️ Bot Fact-Checking v1.0\n\n"
        "🧠 Google Gemini + Vera API\n"
        "🔒 Données temporaires, supprimées après analyse"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    
    if not message:
        return
    
    if gemini_client is None or vera_client is None:
        await message.reply_text("❌ Bot en cours d'initialisation. Réessayez.")
        return
    
    if message.text and any(w.startswith(('http://', 'https://')) for w in message.text.split()):
        await handle_link(update, context, gemini_client, vera_client)
    elif message.text:
        await handle_text(update, context, gemini_client, vera_client)
    elif message.photo:
        await handle_image(update, context, gemini_client, vera_client)
    elif message.video:
        await handle_video(update, context, gemini_client, vera_client)
    elif message.audio or message.voice:
        await handle_audio(update, context, gemini_client, vera_client)
    elif message.document:
        await handle_document(update, context, gemini_client, vera_client)
    else:
        await message.reply_text("❌ Type non supporté. /help pour plus d'infos")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Erreur: {context.error}", exc_info=context.error)
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text("❌ Erreur inattendue. Réessayez.")

async def post_init(application: Application) -> None:
    global gemini_client, vera_client
    logger.info("Init clients...")
    
    gemini_client = GeminiClient(settings.gemini_api_key, settings.gemini_model)
    vera_client = VeraClient(settings.vera_api_url, settings.vera_api_key, settings.vera_timeout)
    
    if await vera_client.health_check():
        logger.info("✅ Vera OK")
    else:
        logger.warning("⚠️ Vera failed")
    logger.info("✅ Bot ready")

def main() -> None:
    logger.info("🚀 Starting bot...")
    
    app = Application.builder().token(settings.telegram_bot_token).post_init(post_init).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(MessageHandler(
        filters.TEXT | filters.PHOTO | filters.VIDEO | filters.AUDIO | 
        filters.VOICE | filters.Document.ALL, handle_message
    ))
    app.add_error_handler(error_handler)
    
    logger.info("✅ Polling...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("🛑 Stopped")
    except Exception as e:
        logger.critical(f"❌ Critical: {e}", exc_info=True)