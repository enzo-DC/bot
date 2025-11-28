"""
Handler pour les liens/URLs
"""
from telegram import Update
from telegram.ext import ContextTypes

from services.gemini_client import GeminiClient
from services.vera_client import VeraClient
from utils.logger import logger
from utils.formatters import format_fact_check_response, format_error_message, format_processing_message
from utils.validators import extract_urls

async def handle_link(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    gemini_client: GeminiClient,
    vera_client: VeraClient
) -> None:
    """
    Traite un message contenant des URLs
    
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
    text = message.text or message.caption or ""
    
    urls = extract_urls(text)
    if not urls:
        await message.reply_text(format_error_message("invalid_url"))
        return
    
    url = urls[0]
    processing_msg = await message.reply_text(format_processing_message("lien"))
    
    try:
        analyzed = await gemini_client.extract_from_url(url, user_id)
        
        if not analyzed.extracted_text:
            await processing_msg.edit_text("⚠️ Contenu inaccessible\n\nEssayez de copier le texte directement")
            return
        
        if not analyzed.has_claims():
            await processing_msg.edit_text(f"ℹ️ Contenu analysé\n\n{analyzed.summary or 'Contenu web'}\n\nAucune affirmation détectée")
            return
        
        query = analyzed.get_primary_claim()
        if not query:
            await processing_msg.edit_text("ℹ️ Contenu analysé\n\nAucune affirmation vérifiable détectée")
            return
        
        vera_response = await vera_client.verify_claim(user_id, query)
        
        if not vera_response.is_valid():
            await processing_msg.edit_text(format_error_message("vera_error"))
            return
        
        response = format_fact_check_response(
            analyzed.summary or "Web",
            vera_response.raw_response,
            "lien",
            analyzed.claims
        )
        response += f"\n\n🔗 Source: {url}"
        await processing_msg.edit_text(response)
        
    except Exception as e:
        logger.error(f"Erreur: {e}")
        await processing_msg.edit_text(format_error_message("processing_error"))