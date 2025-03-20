
import os
from fastapi import  HTTPException, status
from sqlmodel import Session, select
from src.models.student_table_model import Student
from src.schemas.student_schemas import UserCreate,CreateAdmin
from src.utilitiies.crope_image import crop_image
from src.security.jwtutilities import generate_password_hash

# Ensure the upload directory exists
UPLOAD_DIR = "static/uploads/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class StudentServices:
  
    async def get_all_students_ser(self, session: Session, offset: int, limit: int):
        statement = select(Student).order_by(Student.created_at).offset(offset).limit(limit)
        students = session.exec(statement).all()
        return students or []
    
    async def get_a_students_ser(self, std_id: str, session: Session):
        student = session.get(Student, std_id)
        if not student:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")
        return student
  
    async def create_a_students_ser(self, std_data: UserCreate, session: Session):
        statement = select(Student).where(Student.email == std_data.email)
        db_student = session.exec(statement).first()
        if db_student:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Student already exists.")
        std_data_dic = std_data.model_dump()
        new_std_dict = Student(**std_data_dic)
        new_std_dict.password_hash = generate_password_hash(std_data_dic['password'])
        new_std_dict.role = 'user'
        session.add(new_std_dict)
        session.commit()
        session.refresh(new_std_dict)
        return new_std_dict
    
    async def update_a_students_ser(self, std_id: str, std_data: UserCreate, session: Session):
        student = await self.get_a_students_ser(std_id, session)
        student_data = std_data.model_dump(exclude_unset=True)
        student.sqlmodel_update(student_data)
        session.add(student)
        session.commit()
        session.refresh(student)
        return student
  
    async def delete_a_students_ser(self, std_id: str, session: Session):
        student = await self.get_a_students_ser(std_id, session)
        session.delete(student)
        session.commit()
        return student
  
    async def update_student_picture(self, std_id: str, file_name: str, session: Session):
        file_path = f"{UPLOAD_DIR}{file_name}"
        # Crop the uploaded image
        cropped_file_path = crop_image(file_path)

        # Get the student from the database
        student = await self.get_a_students_ser(std_id, session)
        
        # Delete the old profile picture if it exists
        if student.profile_pic_url:
            old_file_path = student.profile_pic_url.lstrip("/")
            full_old_file_path = os.path.join(os.getcwd(), old_file_path)
            if os.path.exists(full_old_file_path):
                os.remove(full_old_file_path)

        # Update the profile picture URL in the database
        student.profile_pic_url = f"/{cropped_file_path}"
        session.add(student)
        session.commit()
        session.refresh(student)
        
        return student
    
    async def get_student_by_email_ser(self,std_email:str,session:Session):
        print("*******************INSIDE get_student_by_email_ser****************")
        statement = select(Student).where(Student.email == std_email)   
        student = session.exec(statement).first()
        if not student:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Student not found with email:{std_email}")
        return student 
    
    async def create_admin_ser(self,std_data:CreateAdmin,session:Session):
        std_data_dic = std_data.model_dump()
        new_std_dict = Student(**std_data_dic)
        new_std_dict.password_hash = generate_password_hash(std_data_dic['password'])
        new_std_dict.role = 'admin'
        session.add(new_std_dict)
        session.commit()
        session.refresh(new_std_dict)
        return new_std_dict
    
   
        
