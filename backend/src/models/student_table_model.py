import uuid
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import DateTime, func
from datetime import date, datetime

class Student(SQLModel, table=True):
    __tablename__ = "students"

    std_id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str = Field(nullable=False)
    email: str = Field(unique=True)
    password_hash: str = Field(default=None, nullable=False)
    phone_number: str = Field(nullable=True)
    dob: date = Field(nullable=True)
    gender: str = Field(nullable=True)
    address: str = Field(nullable=True)
    standard: str = Field(nullable=True)
    profile_pic_url: str = Field(nullable=True)
    is_active: bool = Field(default=False)
    role: str = Field(default="user", nullable=False)

    # Timestamp fields
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
        )
    )

    def __repr__(self):
        return f"<Student: {self.name}>"
