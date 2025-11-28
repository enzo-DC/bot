"""
Client pour l'API Vera (fact-checking)
"""
import httpx
import logging

from models.content import VeraRequest, VeraResponse

logger = logging.getLogger("telegram_bot")

class VeraClient:
    def __init__(self, api_url: str, api_key: str, timeout: int = 60):
        self.api_url = api_url
        self.timeout = timeout
        self.headers = {"X-API-Key": api_key, "Content-Type": "application/json"}
    
    async def verify_claim(self, user_id: str, query: str) -> VeraResponse:
        request = VeraRequest(user_id=user_id, query=query)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream("POST", self.api_url, 
                                        json=request.to_dict(), headers=self.headers) as response:
                    response.raise_for_status()
                    chunks = [chunk async for chunk in response.aiter_text() if chunk]
                    return VeraResponse(raw_response="".join(chunks), success=True)
        except httpx.HTTPStatusError as e:
            return self._handle_error(e.response.status_code)
        except Exception as e:
            logger.error(f"Erreur Vera: {e}")
            return VeraResponse(raw_response="", success=False, error_message=str(e))
    
    def _handle_error(self, code: int) -> VeraResponse:
        msgs = {401: "API key invalide", 429: "Trop de requêtes", 500: "Erreur serveur"}
        return VeraResponse(raw_response="", success=False, 
                          error_message=msgs.get(code, f"Erreur {code}"))
    
    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.post(self.api_url, 
                                     json={"userId": "test", "query": "test"}, 
                                     headers=self.headers)
                return r.status_code in [200, 422]
        except:
            return False