from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from config import DB_STRING, DB_ECHO

Base = declarative_base()

class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    items = relationship("Item")
    
    def __repr__(self):
        return "<Category(id='%s', name='%s')>" % (
            self.id, self.name)

class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    category_id = Column(Integer, ForeignKey('categories.id'))
    category = relationship("Category", back_populates="items")

    def __repr__(self):
        return "<Item(id='%s', name='%s', category='%s', description='%s')>" % ( 
            self.id, self.name, self.category.name, self.description)

# Re-build the database
if __name__ == "__main__":
    engine = create_engine(DB_STRING, echo=DB_ECHO)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
