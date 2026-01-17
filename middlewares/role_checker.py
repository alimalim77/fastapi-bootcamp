from fastapi import HTTPException, Request


class RoleChecker:
    """
    Dependency to check if the current user has one of the allowed roles.
    
    Usage:
        @router.delete("/", dependencies=[Depends(RoleChecker(["admin"]))])
        def delete_item():
            ...
    """
    
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, request: Request):
        user = getattr(request.state, "user", None)
        if not user:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        user_role = user.get("role", "user")
        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=403, 
                detail=f"Access denied. Required role: {self.allowed_roles}"
            )
        return True
