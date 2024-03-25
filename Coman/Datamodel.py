from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base


# Define SQLAlchemy model
Base = declarative_base()


class UserData(Base):
    __tablename__ = 'user_data'
    patient_id = Column(String(50), ForeignKey('patient_details.patient_id', ondelete='CASCADE'), primary_key=True)
    password = Column(String(50))
    salt = Column(String(50))   

class PatientDetails(Base):
    __tablename__ = 'patient_details'
    patient_id = Column(String(50), primary_key=True)
    username = Column(String(50))
    email = Column(String(50), unique=True)
    dob = Column(DateTime)
    gender = Column(String(2))
    mobile = Column(String(10), unique=True)
    rtype = Column(String(20))
    education = Column(String(50))
    ssn = Column(String(20), unique=True)
    insuranceurl = Column(String(100))
    activestat = Column(Boolean, default=False,nullable=False)