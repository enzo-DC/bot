"""
Client pour l'API Google Gemini
"""
import google.generativeai as genai
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json
import re
import logging

from models.content import AnalyzedContent, ContentType, ClaimType

logger = logging.getLogger("telegram_bot")

class GeminiClient:
    """Client pour interagir avec l'API Gemini"""
    
    def __init__(self, api_key: str, model_name: str):
        """Initialise le client Gemini"""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.executor = ThreadPoolExecutor(max_workers=3)
        logger.info(f"Gemini init: {model_name}")
    
    async def analyze_text(self, text: str, user_id: str) -> AnalyzedContent:
        """
        Analyse un texte pour identifier les affirmations factuelles
        
        Args:
            text: Texte à analyser
            user_id: ID de l'utilisateur
            
        Returns:
            Contenu analysé
        """
        logger.info(f"Analyse de texte pour user {user_id}")
        
        prompt = f"""Analyse et trouve affirmations factuelles.
Texte: {text}
JSON: {{"summary": "...", "claims": ["..."], "claim_type": "factual|opinion|unknown"}}"""
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(self.executor, self.model.generate_content, prompt)
            result = self._parse_json(response.text)
            
            return AnalyzedContent(
                content_type=ContentType.TEXT, user_id=user_id, extracted_text=text,
                summary=result.get("summary"), claims=result.get("claims", []),
                claim_type=ClaimType(result.get("claim_type", "unknown"))
            )
        except Exception as e:
            logger.error(f"Erreur Gemini: {e}")
            return AnalyzedContent(content_type=ContentType.TEXT, user_id=user_id, 
                                 extracted_text=text, claims=[text])
    
    async def analyze_image(self, image_path: Path, user_id: str) -> AnalyzedContent:
        """
        Analyse une image (OCR + détection d'affirmations)
        
        Args:
            image_path: Chemin vers l'image
            user_id: ID de l'utilisateur
            
        Returns:
            Contenu analysé
        """
        logger.info(f"Analyse d'image pour user {user_id}: {image_path}")
        
        prompt = """Extrait texte et affirmations. JSON: {"extracted_text": "...", "claims": ["..."]}"""
        try:
            loop = asyncio.get_event_loop()
            
            # Lire l'image en bytes
            def read_image():
                with open(str(image_path), 'rb') as f:
                    image_data = f.read()
                return {
                    'mime_type': 'image/jpeg',
                    'data': image_data
                }
            
            img_data = await loop.run_in_executor(self.executor, read_image)
            response = await loop.run_in_executor(
                self.executor, 
                lambda: self.model.generate_content([prompt, img_data])
            )
            result = self._parse_json(response.text)
            
            return AnalyzedContent(
                content_type=ContentType.IMAGE, user_id=user_id,
                extracted_text=result.get("extracted_text"),
                claims=result.get("claims", []),
                claim_type=ClaimType(result.get("claim_type", "unknown"))
            )
        except Exception as e:
            logger.error(f"Erreur image: {e}")
            raise
    
    async def analyze_video(self, video_path: Path, user_id: str) -> AnalyzedContent:
        """
        Analyse une vidéo (transcription audio + analyse visuelle)
        
        Args:
            video_path: Chemin vers la vidéo
            user_id: ID de l'utilisateur
            
        Returns:
            Contenu analysé
        """
        logger.info(f"Analyse de vidéo pour user {user_id}: {video_path}")
        
        prompt = """Transcris et analyse. JSON: {"transcription": "...", "claims": ["..."]}"""
        return await self._analyze_media(video_path, user_id, ContentType.VIDEO, prompt)
    
    async def analyze_audio(self, audio_path: Path, user_id: str) -> AnalyzedContent:
        """
        Analyse un fichier audio (transcription)
        
        Args:
            audio_path: Chemin vers l'audio
            user_id: ID de l'utilisateur
            
        Returns:
            Contenu analysé
        """
        logger.info(f"Analyse audio pour user {user_id}: {audio_path}")
        
        prompt = """Transcris et trouve affirmations. JSON: {"transcription": "...", "claims": ["..."]}"""
        return await self._analyze_media(audio_path, user_id, ContentType.AUDIO, prompt)
    
    async def extract_from_url(self, url: str, user_id: str) -> AnalyzedContent:
        """
        Extrait le contenu d'une URL et l'analyse
        
        Args:
            url: URL à analyser
            user_id: ID de l'utilisateur
            
        Returns:
            Contenu analysé
        """
        logger.info(f"Extraction URL pour user {user_id}: {url}")
        
        prompt = f"""Analyse {url}. JSON: {{"extracted_text": "...", "claims": ["..."]}}"""
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(self.executor, self.model.generate_content, prompt)
            result = self._parse_json(response.text)
            
            return AnalyzedContent(
                content_type=ContentType.LINK, user_id=user_id,
                extracted_text=result.get("extracted_text"),
                claims=result.get("claims", [])
            )
        except Exception as e:
            logger.error(f"Erreur URL: {e}")
            raise
    async def _analyze_media(self, path: Path, user_id: str, content_type: ContentType, prompt: str):
        try:
            loop = asyncio.get_event_loop()
            
            # Lire le fichier en bytes
            def read_file():
                with open(str(path), 'rb') as f:
                    file_data = f.read()
                
                # Déterminer le mime_type
                ext = path.suffix.lower()
                mime_types = {
                    '.mp3': 'audio/mpeg',
                    '.ogg': 'audio/ogg',
                    '.mp4': 'video/mp4',
                    '.avi': 'video/x-msvideo',
                    '.mov': 'video/quicktime'
                }
                mime_type = mime_types.get(ext, 'application/octet-stream')
                
                return {
                    'mime_type': mime_type,
                    'data': file_data
                }
            
            file_data = await loop.run_in_executor(self.executor, read_file)
            response = await loop.run_in_executor(
                self.executor,
                lambda: self.model.generate_content([prompt, file_data])
            )
            result = self._parse_json(response.text)
            
            return AnalyzedContent(
                content_type=content_type, user_id=user_id,
                extracted_text=result.get("transcription"),
                claims=result.get("claims", [])
            )
        except Exception as e:
            logger.error(f"Erreur media: {e}")
            raise
    
    def _parse_json(self, text: str) -> dict:
        cleaned = re.sub(r'^```json\s*|\s*```$', '', text.strip())
        try:
            return json.loads(cleaned)
        except:
            return {}