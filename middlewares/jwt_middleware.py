from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from fastapi import Request
from utils.jwt_handler import verify_token

class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        excluded_paths = ["/docs", 
        "/openapi.json", 
        "/health", 
        "/metrics",
        "/api/v1/users/login", 
        "/api/v1/users/register", 
        "/api/v1/users/refresh", 
        "/api/v1/users/logout", 
        "/api/v1/users/verify-otp"
        ]
        
        # Normalize path by removing trailing slash for comparison
        request_path = request.url.path.rstrip("/") or "/"
        normalized_excluded = [p.rstrip("/") or "/" for p in excluded_paths]
        
        if request_path in normalized_excluded:
            return await call_next(request)
        
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"detail": "Missing or invalid Authorization header"})
        
        token = auth_header.split(" ")[1]
        payload = verify_token(token)
        
        if payload is None:
            return JSONResponse(status_code=401, content={"detail": "Invalid or expired token"})
            
        request.state.user = payload # Store user info in request state
        response = await call_next(request)
        return response
