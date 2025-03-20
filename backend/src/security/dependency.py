from typing import List
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session
from src.models.student_table_model import Student
from src.services.student_services import StudentServices
from src.database.redis import jti_token_in_blocklist  # Corrected import
from src.security.jwtutilities import decode_token
from src.database.student_database import get_session

class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        cred = await super().__call__(request)
        token = cred.credentials
        token_data = decode_token(token)

        if not self.validate_token(token):  # Corrected method name
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "This token is invalid or expired.",
                    "resolution": "Please get a new token.",
                },
            )

        if await jti_token_in_blocklist(token_data["jti"]):  # Fixed argument
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "This token is invalid or revoked.",
                    "resolution": "Please get a new token.",
                },
            )

        self.verify_token_data(token_data)
        return token_data

    def validate_token(self, token: str) -> bool:  # Fixed spelling
        token_data = decode_token(token)
        return token_data is not None

    def verify_token_data(self, token_data):
        raise NotImplementedError("Please override this method in child classes.")

class AccessTokenBearer(TokenBearer):
    print("*******************INSIDE AccessTokenBearer****************")
    def verify_token_data(self, token_data) -> None:
        if token_data and token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide a valid access token.",
            )

class RefreshTokenBearer(TokenBearer):
    print("*******************INSIDE RefreshTokenBearer****************")
    def verify_token_data(self, token_data) -> None:
        if token_data and not token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide a fresh access token.",
            )

async def get_current_user_ser(
    token_detail:dict = Depends(AccessTokenBearer()),
    session: Session=Depends(get_session)):
    print("*******************INSIDE CURRENT USER****************")
    std_email = token_detail['student']['email']
    student = await StudentServices().get_student_by_email_ser(std_email,session)
    return student


class RoleChecker:
    print("*******************INSIDE ROLE CHECKER****************")
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: Student = Depends(get_current_user_ser)) -> Student:
        if current_user.role in self.allowed_roles:
            return current_user  # ✅ Return user instead of True
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to perform this action"
        )
        