# from sqlalchemy import Column, Integer, String, func, Date
# from sqlalchemy.sql.sqltypes import DateTime
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import relationship, backref
# Base = declarative_base()
#
#
#
# class Contact(Base):
#     __tablename__ = "contacts"
#     id = Column(Integer, primary_key=True)
#     firstname = Column(String(50), nullable=False)
#     lastname = Column(String(50), nullable=False)
#     email = Column(String(50), nullable=False)
#     phone_number = Column(String(50), nullable=False)
#     date_of_birth = Column(Date, nullable=False)
#     description = Column(String(150), nullable=False)
#     created_at = Column('created_at', DateTime, default=func.now())
#     user = relationship("User", backref='contacts')
#
#     @property
#     def formatted_date_of_birth(self):
#         if self.date_of_birth:
#             return self.date_of_birth.strftime("%d-%m-%Y")
#         return None
#
#
# class User(Base):
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True)
#     username = Column(String(150), nullable=False, unique=False)
#     email = Column(String(150), nullable=False, unique=True)
#     password = Column(String(255), nullable=False)
#     created_at = Column('crated_at', DateTime, default=func.now())
#     avatar = Column(String(255), nullable=True)
#     refresh_token = Column(String(255), nullable=True)
#     contacts = relationship("Contact", backref='users')


from sqlalchemy import Column, Date, Integer, String, ForeignKey, Boolean
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
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
    user_id = Column(Integer, ForeignKey('users.id'), default=None)

    user = relationship("User", backref='contacts')

    @property
    def formatted_date_of_birth(self):
        if self.date_of_birth:
            return self.date_of_birth.strftime("%d-%m-%Y")
        return None


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(150), nullable=False, unique=False)
    email = Column(String(150), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column('created_at', DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    refresh_token = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
    bunned = Column(Boolean, default=False)
    ip = Column(String, unique=False, default="localhost")


