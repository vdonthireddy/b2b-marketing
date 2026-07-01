from fastapi import Depends, HTTPException, status
from app.models.user import User, UserRole
from app.middleware.auth import get_current_user


def require_role(*allowed_roles: UserRole):
    """Dependency factory that restricts access to specific roles.

    Usage:
        @router.get("/admin-only", dependencies=[Depends(require_role(UserRole.ADMIN))])
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {[r.value for r in allowed_roles]}",
            )
        return current_user
    return role_checker


# Convenience dependencies
require_admin = require_role(UserRole.ADMIN)
require_editor = require_role(UserRole.ADMIN, UserRole.EDITOR)
require_viewer = require_role(UserRole.ADMIN, UserRole.EDITOR, UserRole.VIEWER)
