"""
Formatage des réponses pour Telegram
"""
from typing import Optional

def format_fact_check_response(
    content_summary: str,
    vera_response: str,
    content_type: str = "texte",
    claims: Optional[list[str]] = None
) -> str:
    """
    Formate la réponse complète du fact-checking
    
    Args:
        content_summary: Résumé du contenu analysé
        vera_response: Réponse de Vera
        content_type: Type de contenu analysé
        claims: Liste des affirmations vérifiées
        
    Returns:
        Message formaté pour Telegram (Markdown)
    """
    
    emojis = {
        "texte": "📝",
        "image": "🖼️",
        "video": "🎬",
        "audio": "🎵",
        "lien": "🔗"
    }
    
    emoji = emojis.get(content_type, "📄")
    
    parts = [f"{emoji} *Analyse*\n━━━━━━━━━━━━━━━━\n"]
    
    # Résumé du contenu
    if content_summary:
        parts.append(f"📋 {content_summary}\n\n")
    
    # Affirmations détectées
    if claims:
        parts.append("🎯 *Affirmations :*\n")
        for i, claim in enumerate(claims[:2], 1):  # Max 2 affirmations
            parts.append(f"{i}. _{claim}_\n")
        parts.append("\n")
    
    # Résultat du fact-checking
    parts.append(f"🔍 *Vérification :*\n{vera_response}")
    
    return "".join(parts)

def format_error_message(error_type: str, details: Optional[str] = None) -> str:
    """
    Formate un message d'erreur convivial
    
    Args:
        error_type: Type d'erreur
        details: Détails additionnels
        
    Returns:
        Message d'erreur formaté
    """
    
    errors = {
        "file_too_large": "❌ Fichier trop volumineux",
        "unsupported_format": "❌ Format non supporté",
        "vera_error": "❌ Service indisponible",
        "processing_error": "❌ Erreur de traitement",
    }
    
    msg = errors.get(error_type, "❌ Erreur")
    
    if details:
        msg += f"\n_{details}_"
    
    return msg

def format_processing_message(content_type: str) -> str:
    """
    Message indiquant que le traitement est en cours
    
    Args:
        content_type: Type de contenu en cours de traitement
        
    Returns:
        Message formaté
    """
    
    msgs = {
        "image": "🖼️ Analyse...",
        "video": "🎬 Transcription...",
        "audio": "🎵 Transcription...",
        "lien": "🔗 Extraction..."
    }
    
    return msgs.get(content_type, "⏳ Traitement...")