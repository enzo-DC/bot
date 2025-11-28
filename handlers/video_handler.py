"""
Handler pour les vidéos
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

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE,
                      gemini_client: GeminiClient, vera_client: VeraClient) -> None:
    """
    Traite une vidéo
    
    Args:
        update: Update Telegram
        context: Contexte du bot
        gemini_client: Client Gemini
        vera_client: Client Vera
    """
    message = update.message
    if not message or not message.from_user:
        if message:
            await message.reply_text(format_error_message("processing_error"))
        return
    user_id = str(message.from_user.id)
    video = message.video
    
    if not video:
        await message.reply_text(format_error_message("processing_error"))
        return
    if video.file_size and video.file_size > settings.max_video_size_mb * 1024 * 1024:
        await message.reply_text(format_error_message("file_too_large", f"Max: {settings.max_video_size_mb}MB"))
        return
    
    processing_msg = await message.reply_text(format_processing_message("video") + "\n⚠️ Peut prendre 1-2 min")
    file_path = None
    
    try:
        file = await context.bot.get_file(video.file_id)
        ext = video.mime_type.split('/')[-1] if video.mime_type else 'mp4'
        file_path = settings.temp_download_path / f"{uuid.uuid4()}.{ext}"
        await file.download_to_drive(str(file_path))
        
        validate_file_size(file_path, settings.max_video_size_mb)
        analyzed = await gemini_client.analyze_video(file_path, user_id)
        
        if not analyzed.has_claims():
            text_preview = analyzed.extracted_text[:200] + "..." if analyzed.extracted_text else "Pas de transcription"
            await processing_msg.edit_text(f"ℹ️ Vidéo analysée\n\n💬 {text_preview}\n\nAucune affirmation détectée")
            return
        
        query = analyzed.get_primary_claim()
        if not query:
            await processing_msg.edit_text("ℹ️ Vidéo analysée\n\nAucune affirmation vérifiable trouvée")
            return
        
        vera_response = await vera_client.verify_claim(user_id, query)
        
        if not vera_response.is_valid():
            await processing_msg.edit_text(format_error_message("vera_error"))
            return
        
        response = format_fact_check_response(analyzed.summary or "Vidéo", vera_response.raw_response,
                                             "video", analyzed.claims)
        await processing_msg.edit_text(response)
        
    except ValidationError as e:
        await processing_msg.edit_text(format_error_message("file_too_large", str(e)))
    except Exception as e:
        logger.error(f"Erreur: {e}")
        await processing_msg.edit_text(format_error_message("processing_error"))
    finally:
        if file_path and file_path.exists():
            file_path.unlink()