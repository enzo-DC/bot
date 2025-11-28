"""
Validateurs pour URLs, fichiers, etc.
"""
import re
from urllib.parse import urlparse
from pathlib import Path
import magic
from config.settings import settings
from utils.logger import logger

class ValidationError(Exception):
    """Erreur de validation personnalisée"""
    pass

def is_valid_url(url: str) -> bool:
    """
    Vérifie si une URL est valide
    
    Args:
        url: URL à valider
        
    Returns:
        True si valide, False sinon
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
    except Exception:
        return False

def extract_urls(text: str) -> list[str]:
    """
    Extrait toutes les URLs d'un texte
    
    Args:
        text: Texte contenant potentiellement des URLs
        
    Returns:
        Liste des URLs trouvées
    """
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    urls = re.findall(url_pattern, text)
    return [url for url in urls if is_valid_url(url)]

def validate_file_size(file_path: Path, max_size_mb: int = None) -> bool:
    """
    Vérifie la taille d'un fichier
    
    Args:
        file_path: Chemin du fichier
        max_size_mb: Taille max en MB (None = utiliser settings)
        
    Returns:
        True si taille acceptable
        
    Raises:
        ValidationError si fichier trop gros
    """
    if max_size_mb is None:
        max_size_mb = settings.max_file_size_mb
    
    file_size = file_path.stat().st_size
    max_size_bytes = max_size_mb * 1024 * 1024
    
    if file_size > max_size_bytes:
        raise ValidationError(
            f"Fichier trop volumineux: {file_size / (1024*1024):.2f} MB "
            f"(max: {max_size_mb} MB)"
        )
    
    return True

def get_mime_type(file_path: Path) -> str:
    """
    Détecte le type MIME d'un fichier
    
    Args:
        file_path: Chemin du fichier
        
    Returns:
        Type MIME (ex: 'image/jpeg')
    """
    try:
        mime = magic.Magic(mime=True)
        return mime.from_file(str(file_path))
    except Exception as e:
        logger.warning(f"Impossible de détecter le MIME type: {e}")
        # Fallback basé sur l'extension
        ext_to_mime = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.mp4': 'video/mp4',
            '.mp3': 'audio/mpeg',
            '.ogg': 'audio/ogg',
        }
        return ext_to_mime.get(file_path.suffix.lower(), 'application/octet-stream')

def validate_media_type(file_path: Path, media_type: str, accepted_formats: list) -> bool:
    """
    Valide qu'un fichier correspond au type de média attendu
    
    Args:
        file_path: Chemin du fichier
        media_type: Type attendu ('image', 'video', 'audio')
        accepted_formats: Liste des formats acceptés
        
    Returns:
        True si valide
        
    Raises:
        ValidationError si type invalide
    """
    mime_type = get_mime_type(file_path)
    
    if mime_type not in accepted_formats:
        raise ValidationError(f"Format {mime_type} non supporté")
    
    return True

def sanitize_filename(filename: str) -> str:
    """
    Nettoie un nom de fichier pour éviter les problèmes
    
    Args:
        filename: Nom de fichier original
        
    Returns:
        Nom de fichier nettoyé
    """
    # Supprimer les caractères dangereux
    filename = re.sub(r'[^\w\s\-\.]', '', filename)
    # Limiter la longueur
    if len(filename) > 200:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:190] + (f'.{ext}' if ext else '')
    
    return filename