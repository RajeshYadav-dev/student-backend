import os
import shutil
import uuid
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlmodel import Session
from src.models.student_table_model import Student
from src.database.redis import add_jti_to_blocklist
from src.security.dependency import AccessTokenBearer, RefreshTokenBearer,RoleChecker, get_current_user_ser
from src.services.student_services import StudentServices
from src.database.student_database import get_session
from src.schemas.student_schemas import UserCreate, UserLogin, UserUpdate, UserShow, CreateAdmin
from typing import List
from src.security.jwtutilities import verify_password,create_access_token
from datetime import timedelta
from src.config import Config
from fastapi.responses import JSONResponse
from datetime import datetime
from src.security.dependency import AccessTokenBearer


# Ensure uploads directory exists
UPLOAD_DIR = "static/uploads/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

student_router = APIRouter()
services = StudentServices()
access_token_bearer = AccessTokenBearer()

# role_checker = RoleChecker(["admin"])


@student_router.get("/", response_model=List[UserShow])
async def get_all_students(session: Session = Depends(get_session), offset: int = 0, limit:int = Query(default=10,lte=10),details:AccessTokenBearer=Depends(access_token_bearer),_:Student=Depends(RoleChecker(["admin",]))):
    students = await services.get_all_students_ser(session, offset, limit)
    if not students:
        return []
    return students

@student_router.get("/{std_id}", response_model=UserShow)
async def get_a_student(std_id: str, session: Session = Depends(get_session),details:AccessTokenBearer=Depends(access_token_bearer),_:Student=Depends(RoleChecker(["admin","user"]))):
    student = await services.get_a_students_ser(std_id, session)
    return student

@student_router.post("/", response_model=UserShow,)
async def create_a_student(std_data: UserCreate, session: Session = Depends(get_session),_:Student=Depends(RoleChecker(["admin","user"]))):
    student = await services.create_a_students_ser(std_data, session)
    return student

@student_router.put("/{std_id}", response_model=UserShow)
async def update_a_student(std_id: str, std_data: UserUpdate, session: Session = Depends(get_session),details:AccessTokenBearer=Depends(access_token_bearer),_:Student=Depends(RoleChecker(["admin","user"]))):
    student = await services.update_a_students_ser(std_id, std_data, session)
    return student

@student_router.delete("/{std_id}", response_model=dict)
async def delete_a_student(std_id: str, session: Session = Depends(get_session),details:AccessTokenBearer=Depends(access_token_bearer),
_:Student=Depends(RoleChecker(["admin"]))):
    await services.delete_a_students_ser(std_id, session)
    return {"message": "Student deleted"}

@student_router.post("/{std_id}/upload",)
async def upload_profile_pic(std_id: str, file: UploadFile = File(...),session: Session = Depends(get_session),details:AccessTokenBearer=Depends(access_token_bearer),_:Student=Depends(RoleChecker(["admin","user"]))):
    file_ext = file.filename.split(".")[-1]
    file_name = f"{std_id}_{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, file_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    await services.update_student_picture(std_id, file_name, session)
    file_url = f"/static/uploads/{file_name}"
    return {"profile_pic_url": file_url}

@student_router.post("/login")
async def login_student(login_data: UserLogin, session: Session = Depends(get_session)):
    email = login_data.email
    password = login_data.password
    print(login_data)
    student = await services.get_student_by_email_ser(email, session)

    if student is not None:
        password_valid = verify_password(password, student.password_hash)

        if password_valid:  # ✅ Ensure this block contains the return statement
            access_token = create_access_token(
                user_data={
                    'email': student.email,
                    'std_id': student.std_id,
                    'role': student.role
                }
            )
            refresh_token = create_access_token(
                user_data={
                    'email': student.email,
                    'std_id': student.std_id
                },
                refresh=True,
                expiry=timedelta(days=Config.REFRESH_TOKEN_EXPIRY)
            )

            return JSONResponse(  # ✅ Move this inside the `if password_valid` block
                content={
                    "message": "Login successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "student": {
                        "email": student.email,
                        "std_id": student.std_id
                    }
                }
            )

    # If the email is not found or the password is invalid, return error
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Email or Password")
  
   


@student_router.get("/refresh_token") 
async def get_refresh_token(token_details:dict=Depends(RefreshTokenBearer)):
    expiry_timestamp = token_details['exp']
    if datetime.fromtimestamp(expiry_timestamp>datetime.now()):
        new_access_token = create_access_token(user_data=token_details['student'])
        return JSONResponse(
            content={
                "new_access_token":new_access_token
            }
        )
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid Or Expired Token ")  

@student_router.post("/logout")
async def revoked_token(token_detail:dict=Depends(AccessTokenBearer())):
    jti = token_detail['jti']
    await add_jti_to_blocklist(jti)
    return JSONResponse(content={
    "message":"Logout Successfully.",
    },
     status_code=status.HTTP_200_OK                 
    )
          
              
@student_router.get("/user/me", response_model=UserShow)
async def get_current_user_route(user: Student = Depends(get_current_user_ser),_:Student=Depends(RoleChecker(["admin","user"]))):
    return user     

@student_router.post("/create_admin", response_model=UserShow)
async def create_admin(std_data: CreateAdmin, session: Session = Depends(get_session)):
    student = await services.create_admin_ser(std_data, session)
    return student       