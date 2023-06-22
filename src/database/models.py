from sqlalchemy import Column, Integer, String, func, Date
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True)
    firstname = Column(String(50), nullable=False)
    lastname = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    phone_number = Column(String(50), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    description = Column(String(150), nullable=False)
    created_at = Column('created_at', DateTime, default=func.now())

    @property
    def formatted_date_of_birth(self):
        if self.date_of_birth:
            return self.date_of_birth.strftime("%d-%m-%Y")
        return None
