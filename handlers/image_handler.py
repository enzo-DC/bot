"""
Handler pour les images
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

async def handle_image(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    gemini_client: GeminiClient,
    vera_client: VeraClient
) -> None:
    """
    Traite une image
    
    Args:
        update: Update Telegram
        context: Contexte du bot
        gemini_client: Client Gemini
        vera_client: Client Vera
    """
    message = update.message
    
    if not message or not message.from_user:
        return
    
    user_id = str(message.from_user.id)
    photo = message.photo[-1] if message.photo else None
    
    if not photo:
        await message.reply_text(format_error_message("processing_error"))
        return
    
    processing_msg = await message.reply_text(format_processing_message("image"))
    file_path = None
    
    try:
        file = await context.bot.get_file(photo.file_id)
        file_path = settings.temp_download_path / f"{uuid.uuid4()}.jpg"
        await file.download_to_drive(str(file_path))
        
        validate_file_size(file_path, settings.max_image_size_mb)
        analyzed = await gemini_client.analyze_image(file_path, user_id)
        
        if not analyzed.has_claims():
            await processing_msg.edit_text("ℹ️ Aucune affirmation détectée")
            return
        
        query = analyzed.get_primary_claim()
        
        if not query:
            await processing_msg.edit_text("ℹ️ Aucune affirmation détectée")
            return
        
        vera_response = await vera_client.verify_claim(user_id, query)
        
        if not vera_response.is_valid():
            await processing_msg.edit_text(format_error_message("vera_error"))
            return
        
        response = format_fact_check_response(
            analyzed.summary or "Image",
            vera_response.raw_response,
            "image",
            analyzed.claims
        )
        
        await processing_msg.edit_text(response)
        logger.info(f"Analyse image terminée pour {user_id}")
        
    except ValidationError as e:
        await processing_msg.edit_text(format_error_message("file_too_large", str(e)))
    except Exception as e:
        logger.error(f"Erreur: {e}")
        await processing_msg.edit_text(format_error_message("processing_error"))
    finally:
        if file_path and file_path.exists():
            file_path.unlink()