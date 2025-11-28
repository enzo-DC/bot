"""
Modèles de données pour le contenu analysé
"""
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ContentType(Enum):
    """Types de contenu supportés"""
    TEXT = "texte"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    LINK = "lien"

class ClaimType(Enum):
    """Types d'affirmations"""
    FACTUAL = "factual"  # Affirmation factuelle
    OPINION = "opinion"  # Opinion
    UNKNOWN = "unknown"  # Non déterminé

@dataclass
class AnalyzedContent:
    """
    Contenu analysé par Gemini
    """
    # Métadonnées
    content_type: ContentType
    user_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Contenu extrait
    extracted_text: Optional[str] = None
    summary: Optional[str] = None
    language: Optional[str] = None
    
    # Affirmations détectées
    claims: List[str] = field(default_factory=list)
    claim_type: ClaimType = ClaimType.UNKNOWN
    
    # Contexte
    context: Optional[str] = None
    source_info: Optional[str] = None  # Ex: "Post Facebook", "Article de presse"
    
    # Métadonnées techniques
    file_path: Optional[str] = None
    url: Optional[str] = None
    
    def has_claims(self) -> bool:
        """Vérifie si des affirmations ont été détectées"""
        return len(self.claims) > 0
    
    def get_primary_claim(self) -> Optional[str]:
        """Retourne l'affirmation principale"""
        return self.claims[0] if self.claims else None
    
    def to_dict(self) -> dict:
        """Convertit en dictionnaire"""
        return {
            "content_type": self.content_type.value,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat(),
            "extracted_text": self.extracted_text,
            "summary": self.summary,
            "language": self.language,
            "claims": self.claims,
            "claim_type": self.claim_type.value,
            "context": self.context,
            "source_info": self.source_info,
        }

@dataclass
class VeraRequest:
    """
    Requête vers l'API Vera
    """
    user_id: str
    query: str
    
    def to_dict(self) -> dict:
        """Convertit en dictionnaire pour l'API"""
        return {"userId": self.user_id, "query": self.query}

@dataclass
class VeraResponse:
    """
    Réponse de l'API Vera
    """
    raw_response: str
    success: bool
    error_message: Optional[str] = None
    
    def is_valid(self) -> bool:
        """Vérifie si la réponse est valide"""
        return self.success and self.raw_response is not None