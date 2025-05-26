from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .auth_handler import decode_jwt

class JWTBearer(HTTPBearer):
    """JWT Bearer authentication"""
    
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)
    
    async def __call__(self, request: Request) -> str:
        """Extract and validate the JWT token"""
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, 
                    detail="Invalid authentication scheme"
                )
            
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, 
                    detail="Invalid token or expired token"
                )
            
            return credentials.credentials
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Invalid authorization code"
            )
    
    def verify_jwt(self, token: str) -> bool:
        """Verify JWT token is valid"""
        isTokenValid: bool = False
        
        try:
            payload = decode_jwt(token)
            if payload:
                isTokenValid = True
        except:
            pass
        
        return isTokenValid
