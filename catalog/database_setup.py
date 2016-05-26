from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from config import DB_STRING, DB_ECHO

from sqlalchemy.engine import Engine
from sqlalchemy import event

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
    
Base = declarative_base()

class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    items = relationship("Item", back_populates="category", cascade="all,delete-orphan")
    
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", cascade="none")
    
    def __repr__(self):
        return "<Category(id='%s', name='%s', user_id='%s')>" % (
            self.id, self.name, user_id)

    @property
    def serialize(self):
        return {
            'id' : self.id,
            'name' : self.name,
            'user_id' : self.user_id
        }
        
class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    category_id = Column(Integer, ForeignKey('categories.id', ondelete="cascade"))
    category = relationship("Category", back_populates="items")
    
    user_id = Column(Integer, ForeignKey('users.id', ondelete="cascade"))
    user = relationship("User")

    def __repr__(self):
        return "<Item(id='%s', name='%s', user_id='%s', category='%s', description='%s')>" % ( 
            self.id, self.name, user_id, self.category.name, self.description)

    @property
    def serialize(self):
        return {
            'id' : self.id,
            'name' : self.name,
            'description' : self.description,
            'category_id' : self.category_id,
            'user_id' : self.user_id
        }

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    google_id = Column(String)
    picture = Column(String)  
    
    def __repr__(self):
        return "<User(id='%s', name='%s', google_id='%s', picture='%s')>" % (
            self.id, self.name, self.google_id, self.picture)
    
    @property
    def serialize(self):
        return {
            'id' : self.id,
            'name' : self.name,
            'google_id' : self.google_id,
            'picture' : self.picture
        }

# Re-build the database
if __name__ == "__main__":
    engine = create_engine(DB_STRING, echo=DB_ECHO)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
