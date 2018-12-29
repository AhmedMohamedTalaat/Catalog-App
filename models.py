from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from passlib.apps import custom_app_context as pwd_context

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    email = Column(String(50), nullable=False)
    # psw_hash = Column(String(64))
    #
    # def hash_password(self, psw):
    #     self.psw_hash = pwd_context.encrypt(psw)
    #
    # def verity_password(self, psw):
    #     return pwd_context.verify(psw, self.psw_hash)


class Categories(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    name = Column(String(45), nullable=False)
    user = relationship(User)

    @property
    def serialize(self):
        return {'id': self.id,
                'name': self.name}


class Items(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    cate_id = Column(Integer, ForeignKey('categories.id'))
    name = Column(String(45), nullable=False)
    description = Column(String(100), nullable=True)
    cate = relationship(Categories)

    @property
    def serialize(self):
        return {'id': self.id,
                'name': self.name,
                'description': self.description}


engine = create_engine("sqlite:///catalogApp.db")
Base.metadata.create_all(engine)
