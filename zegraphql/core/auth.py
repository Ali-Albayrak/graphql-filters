
from typing import Any
from httpx import AsyncClient
from fastapi import HTTPException, Request
from strawberry.types import Info
from strawberry.permission import BasePermission

from .custom_exceptions import AuthorizationError
from .constants import AppConstants as AC
from .depends import GraphQLContext, set_current_user_data_contextvar
from .logger import log


class Protect(BasePermission):
    message = "User is not authorized for this operation"

    def __init__(self, required_roles: list[str]):
        self.required_roles = required_roles

    async def has_permission(self, source: Any, info: Info[GraphQLContext], **kwargs) -> bool:
        try:
            token = info.context.jwt

            try:
                is_valid, current_user_roles = await self.validate_token(token)
            except Exception as e:
                raise AuthorizationError("Token validation failed")

            if not is_valid:
                raise AuthorizationError("Invalid token")

            if not any(role in current_user_roles for role in self.required_roles):
                raise AuthorizationError("User not authorized to perform this action")
            
            set_current_user_data_contextvar(token, current_user_roles)

            return True
        except AuthorizationError as e:
            log.debug(f"Authorization Error: {e}")
            raise HTTPException(status_code=403, detail=str(e))
        except Exception as e:
            log.debug(AC.ERROR_TEMPLATE.format("has_permission", type(e), str(e)))
            log.error(f"Unkown Authorization Error, Check the logs. Error: {e}")
            raise HTTPException(status_code=500, detail=f"Unkown Authorization Error")
    
    def _extract_token_from_headers(self, headers: dict) -> str:
        token: str = headers.get('Authorization')
        if not token:
            raise AuthorizationError("No authorization token provided")

        if not token.startswith("Bearer "):
            raise AuthorizationError("Invalid Authorization format")

        return token.split("Bearer ")[1]

    async def validate_token(self, token: str) -> tuple[bool, list[str]]:
        try:
            log.debug(f"{token=}")
            async with AsyncClient() as client:
                request_data = {"roles": self.required_roles}
                response = await client.post(f"{AC.ZEAUTH_BASE_URL}/oauth/auth?token={token}", json=request_data)
                if response.status_code != 200:
                    return False, []
                data: dict = response.json()
                user_roles = data.get("allowed_roles", [])
                return True, user_roles
        except Exception as e:
            log.debug(AC.ERROR_TEMPLATE.format("validate_token", type(e), str(e)))
            log.error(f"Toekn validation failed: {e}")
            raise AuthorizationError("Token validation failed")
