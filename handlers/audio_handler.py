"""
Handler pour les fichiers audio et notes vocales
"""
from telegram import Update
from telegram.ext import ContextTypes
from pathlib import Path
import uuid

from services.gemini_client import GeminiClient
from services.vera_client import VeraClient
from config.settings import settings
from utils.logger import logger
from utils.formatters import format_fact_check_response, format_error_message, format_processing_message
from utils.validators import validate_file_size, ValidationError

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE,
                      gemini_client: GeminiClient, vera_client: VeraClient) -> None:
    message = update.message
    if not message or not message.from_user:
        return
    user_id = str(message.from_user.id)
    audio = message.audio or message.voice
    
    if not audio:
        await message.reply_text(format_error_message("processing_error"))
        return
    max_size = settings.max_audio_size_mb * 1024 * 1024
    if hasattr(audio, 'file_size') and audio.file_size and audio.file_size > max_size:
        await message.reply_text(format_error_message("file_too_large", f"Max: {settings.max_audio_size_mb}MB"))
        return
    
    processing_msg = await message.reply_text(format_processing_message("audio"))
    file_path = None
    
    try:
        file = await context.bot.get_file(audio.file_id)
        ext = "ogg" if message.voice else "mp3"
        file_path = settings.temp_download_path / f"{uuid.uuid4()}.{ext}"
        await file.download_to_drive(str(file_path))
        
        validate_file_size(file_path, settings.max_audio_size_mb)
        analyzed = await gemini_client.analyze_audio(file_path, user_id)
        
        if not analyzed.has_claims():
            text_preview = analyzed.extracted_text[:200] + "..." if analyzed.extracted_text else "Pas de transcription"
            await processing_msg.edit_text(f"ℹ️ Audio analysé\n\n💬 {text_preview}\n\nAucune affirmation détectée")
            return
        
        query = analyzed.get_primary_claim()
        if not query:
            await processing_msg.edit_text(format_error_message("processing_error"))
            return
        vera_response = await vera_client.verify_claim(user_id, query)
        
        if not vera_response.is_valid():
            await processing_msg.edit_text(format_error_message("vera_error"))
            return
        
        response = format_fact_check_response(analyzed.summary or "Audio", vera_response.raw_response, 
                                             "audio", analyzed.claims)
        await processing_msg.edit_text(response)
        
    except ValidationError as e:
        await processing_msg.edit_text(format_error_message("file_too_large", str(e)))
    except Exception as e:
        logger.error(f"Erreur: {e}")
        await processing_msg.edit_text(format_error_message("processing_error"))
    finally:
        if file_path and file_path.exists():
            file_path.unlink()