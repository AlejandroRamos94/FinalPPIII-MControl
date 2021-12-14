from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
	__tablename__ = 'user'

	id = Column(Integer, primary_key=True)
	username = Column(String(50), nullable=False)
	pw_hash = Column(String(250), nullable=False)
	email = Column(String(250), nullable=False)

class Paths(Base):
	__tablename__ = 'rutas'
	id = Column(Integer, primary_key=True)
	directorio = Column(String,nullable=False)
	usuarioId = Column(Integer, ForeignKey('user.id'))

engine = create_engine('postgresql://alermpp:ramoscpii@localhost/usuarios')
Base.metadata.create_all(engine)