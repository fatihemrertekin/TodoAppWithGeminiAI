from .database import Base # relative import
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey


class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    completed = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id")) # ForeignKey ile users tablosundan gelen id'yi alıyoruz. Bu sayede her bir todo'nun sahibi belirlenmiş oluyor.
                                                       # One To Many çünkü bir kullanıcının birden fazla todo'su olabilir.

# migration


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True) # hesap aktif mi gibi bir kullanım için tanımlandı.
    role = Column(String)
    phone_number = Column(String)