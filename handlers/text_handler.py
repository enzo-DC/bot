"""
Handler pour les messages texte
"""
from telegram import Update
from telegram.ext import ContextTypes

from services.gemini_client import GeminiClient
from services.vera_client import VeraClient
from utils.logger import logger
from utils.formatters import (
    format_fact_check_response,
    format_error_message,
    format_processing_message
)
from utils.validators import extract_urls

async def handle_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    gemini_client: GeminiClient,
    vera_client: VeraClient
) -> None:
    """
    Traite un message texte
    
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
    text = message.text
    
    if not text:
        return
    
    if extract_urls(text):
        from handlers.link_handler import handle_link
        return await handle_link(update, context, gemini_client, vera_client)
    
    processing_msg = await message.reply_text(format_processing_message("texte"))
    
    try:
        analyzed = await gemini_client.analyze_text(text, user_id)
        
        if not analyzed.has_claims():
            await processing_msg.edit_text("ℹ️ Aucune affirmation factuelle détectée")
            return
        
        query = analyzed.get_primary_claim()
        if not query:
            await processing_msg.edit_text("ℹ️ Impossible d'extraire une affirmation vérifiable")
            return
        
        vera_response = await vera_client.verify_claim(user_id, query)
        
        if not vera_response.is_valid():
            await processing_msg.edit_text(format_error_message("vera_error"))
            return
        
        response = format_fact_check_response(
            analyzed.summary or text[:200],
            vera_response.raw_response,
            "texte",
            analyzed.claims
        )
        await processing_msg.edit_text(response)
        
    except Exception as e:
        logger.error(f"Erreur: {e}")
        await processing_msg.edit_text(format_error_message("processing_error"))