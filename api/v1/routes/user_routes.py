from fastapi import APIRouter, Depends, HTTPException, Request, Response
from controllers.user_controller import UserController
from schemas.user_schema import UserCreate, UserResponse, UserLogin, RegisterResponse, OTPVerifyRequest
from middlewares.auth_validate import UserValidationSchema
from middlewares.rate_limiter import rate_limit
from db.session import get_db
from sqlalchemy.orm import Session

router = APIRouter()
controller = UserController()

# Cookie settings
REFRESH_TOKEN_COOKIE_NAME = "refresh_token"
REFRESH_TOKEN_MAX_AGE = 7 * 24 * 60 * 60  # 7 days in seconds


@router.post(
    "/register",
    response_model=RegisterResponse,
    summary="Register a new user",
    description="Initiate registration by sending OTP to email. If email already has pending registration, resends OTP."
)
# @rate_limit("3/hour")  # Prevent spam registrations
async def register_user(request: Request, user: UserValidationSchema, db: Session = Depends(get_db)):
    """Initiate registration with OTP verification."""
    return controller.initiate_registration(user.email, user.password, db)


@router.post(
    "/verify-otp",
    response_model=UserResponse,
    summary="Verify OTP and complete registration",
    description="Verify the OTP code to complete user registration."
)
@rate_limit("5/minute")  # Prevent OTP brute force
async def verify_otp(request: Request, otp_request: OTPVerifyRequest, db: Session = Depends(get_db)):
    """Verify OTP and create user account."""
    return controller.verify_otp(otp_request.pending_registration_id, otp_request.otp, db)


@router.post(
    "/login",
    summary="Login and get tokens",
    description="Authenticate with email and password. Access token in response, refresh token in HttpOnly cookie."
)
@rate_limit("5/minute")  # Prevent brute force login
async def login_for_access_token(request: Request, response: Response, form_data: UserLogin, db: Session = Depends(get_db)):
    """Login and get access token. Refresh token is set as HttpOnly cookie."""
    tokens = controller.login_user(form_data, db)
    
    # Set refresh token as HttpOnly cookie
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE_NAME,
        value=tokens["refresh_token"],
        max_age=REFRESH_TOKEN_MAX_AGE,
        httponly=True,      # Cannot be accessed by JavaScript
        secure=False,       # Set to True in production (HTTPS only)
        samesite="lax",     # CSRF protection
        path="/"  # Send cookie to all routes
    )
    
    # Return only access token in response body
    return {
        "access_token": tokens["access_token"],
        "token_type": tokens["token_type"]
    }


@router.post(
    "/refresh",
    summary="Refresh access token",
    description="Get a new access token using the refresh token from cookie."
)
@rate_limit("10/minute")  # Normal refresh usage
async def refresh_token(request: Request, db: Session = Depends(get_db)):
    """Get a new access token using refresh token from cookie."""
    refresh_token_value = request.cookies.get(REFRESH_TOKEN_COOKIE_NAME)
    if not refresh_token_value:
        raise HTTPException(status_code=401, detail="Refresh token not found")
    
    return controller.refresh_access_token(refresh_token_value, db)


@router.post(
    "/logout",
    summary="Logout and clear refresh token",
    description="Revoke the refresh token and clear the cookie."
)
async def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    """Logout by revoking refresh token and clearing cookie."""
    refresh_token_value = request.cookies.get(REFRESH_TOKEN_COOKIE_NAME)
    
    if refresh_token_value:
        controller.logout_user(refresh_token_value, db)
    
    # Clear the cookie
    response.delete_cookie(
        key=REFRESH_TOKEN_COOKIE_NAME,
        path="/"
    )
    
    return {"message": "Successfully logged out"}


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID"
)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user details by ID."""
    user = controller.get_user_by_id(user_id, db)
    return {"id": user.id, "email": user.email}

