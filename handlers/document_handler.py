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

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE,
                         gemini_client: GeminiClient, vera_client: VeraClient) -> None:
    message = update.message
    if not message or not message.from_user:
        return
    
    user_id = str(message.from_user.id)
    doc = message.document
    
    if not doc:
        await message.reply_text(format_error_message("processing_error"))
        return
    
    allowed_types = ['application/pdf', 'text/plain', 'application/msword', 
                     'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    if doc.mime_type not in allowed_types:
        await message.reply_text(format_error_message("unsupported_format", "Formats: PDF, TXT, DOC, DOCX"))
        return
    if doc.file_size and doc.file_size > settings.max_file_size_mb * 1024 * 1024:
        await message.reply_text(format_error_message("file_too_large", f"Max: {settings.max_file_size_mb}MB"))
        return
    
    processing_msg = await message.reply_text(format_processing_message("document"))
    file_path = None
    
    try:
        file = await context.bot.get_file(doc.file_id)
        ext = Path(doc.file_name).suffix if doc.file_name else '.pdf'
        file_path = settings.temp_download_path / f"{uuid.uuid4()}{ext}"
        await file.download_to_drive(str(file_path))
        
        validate_file_size(file_path, settings.max_file_size_mb)
        
        if doc.mime_type == 'text/plain':
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            analyzed = await gemini_client.analyze_text(text, user_id)
        else:
            analyzed = await gemini_client.analyze_image(file_path, user_id)
        
        if not analyzed.has_claims():
            await processing_msg.edit_text("ℹ️ Aucune affirmation détectée dans le document")
            return
        
        query = analyzed.get_primary_claim()
        if not query:
            await processing_msg.edit_text("ℹ️ Aucune affirmation principale détectée dans le document")
            return
        vera_response = await vera_client.verify_claim(user_id, query)
        
        if not vera_response.is_valid():
            await processing_msg.edit_text(format_error_message("vera_error"))
            return
        
        response = format_fact_check_response(analyzed.summary or "Document", vera_response.raw_response,
                                             "document", analyzed.claims)
        await processing_msg.edit_text(response)
        
    except ValidationError as e:
        await processing_msg.edit_text(format_error_message("file_too_large", str(e)))
    except Exception as e:
        logger.error(f"Erreur: {e}")
        await processing_msg.edit_text(format_error_message("processing_error"))
    finally:
        if file_path and file_path.exists():
            file_path.unlink()